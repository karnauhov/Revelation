"""Release verified idle build helpers without touching unrelated processes."""

import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import re
import subprocess
import time

from .core import ReleaseError, capture, hidden_flags, lock


class UniqueProcess(ctypes.Structure):
    _fields_ = [('pid', w.DWORD), ('started', w.FILETIME)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [('process', UniqueProcess), ('name', w.WCHAR * 256), ('service', w.WCHAR * 64),
                ('kind', w.DWORD), ('status', w.ULONG), ('session', w.DWORD), ('restartable', w.BOOL)]


def filetime(value):
    return value.dwLowDateTime | value.dwHighDateTime << 32


def locking_processes(path):
    api = ctypes.WinDLL('Rstrtmgr')
    api.RmStartSession.argtypes = [ctypes.POINTER(w.DWORD), w.DWORD, w.LPWSTR]
    api.RmRegisterResources.argtypes = [w.DWORD, w.UINT, ctypes.POINTER(w.LPCWSTR), w.UINT,
                                      ctypes.POINTER(UniqueProcess), w.UINT, ctypes.POINTER(w.LPCWSTR)]
    api.RmGetList.argtypes = [w.DWORD, ctypes.POINTER(w.UINT), ctypes.POINTER(w.UINT),
                            ctypes.POINTER(ProcessInfo), ctypes.POINTER(w.DWORD)]
    handle, key = w.DWORD(), ctypes.create_unicode_buffer(33)
    code = api.RmStartSession(ctypes.byref(handle), 0, key)
    if code:
        raise ctypes.WinError(code)
    try:
        files = (w.LPCWSTR * 1)(str(path))
        code = api.RmRegisterResources(handle, 1, files, 0, None, 0, None)
        if code:
            raise ctypes.WinError(code)
        needed, count, reason = w.UINT(), w.UINT(), w.DWORD()
        for _ in range(4):
            records = (ProcessInfo * count.value)() if count.value else None
            code = api.RmGetList(handle, ctypes.byref(needed), ctypes.byref(count), records, ctypes.byref(reason))
            if code == 0:
                return [{'pid': p.process.pid, 'started': filetime(p.process.started), 'name': p.name}
                        for p in (records or [])[:count.value]]
            if code != 234:
                raise ctypes.WinError(code)
            count.value = needed.value
        raise ReleaseError('Windows lock owners changed repeatedly; retry deletion')
    finally:
        api.RmEndSession(handle)


def process_details(pid):
    # The only interpolated value is an integer returned by Restart Manager.
    command = f'Get-CimInstance Win32_Process -Filter "ProcessId = {int(pid)}" | Select-Object ExecutablePath,CommandLine,CreationDate | ConvertTo-Json -Compress'
    output = capture(['powershell', '-NoProfile', '-Command', command])
    return json.loads(output) if output else {}


def command_arguments(command):
    shell = ctypes.WinDLL('shell32')
    shell.CommandLineToArgvW.argtypes = [w.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    shell.CommandLineToArgvW.restype = ctypes.POINTER(w.LPWSTR)
    count = ctypes.c_int()
    pointer = shell.CommandLineToArgvW(command, ctypes.byref(count))
    if not pointer:
        raise ctypes.WinError()
    try:
        return list(pointer[:count.value])
    finally:
        kernel = ctypes.WinDLL('kernel32')
        kernel.LocalFree.argtypes = [w.HLOCAL]
        kernel.LocalFree(ctypes.cast(pointer, w.HLOCAL))


def idle_gradle(details, pid):
    executable = Path(details.get('ExecutablePath') or '')
    if executable.name.lower() != 'java.exe':
        return False
    args = command_arguments(details.get('CommandLine') or '')
    if 'org.gradle.launcher.daemon.bootstrap.GradleDaemon' not in args or '-cp' not in args:
        return False
    classpath = args[args.index('-cp') + 1]
    if not re.fullmatch(r'gradle-daemon-main-[\d.]+\.jar', Path(classpath).name):
        return False
    cli = Path(classpath).parents[1] / 'bin/gradle.bat'
    if not cli.is_file():
        return False
    env = dict(os.environ, JAVA_HOME=str(executable.parents[1]))
    status = capture([cli, '--status'], cwd=cli.parent, env=env)
    return bool(re.search(r'^\s*' + str(int(pid)) + r'\s+IDLE\s', status, re.M))


def stop_same_process(owner):
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    api.OpenProcess.restype = w.HANDLE
    api.GetProcessTimes.argtypes = [w.HANDLE, *[ctypes.POINTER(w.FILETIME)] * 4]
    api.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
    api.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    api.CloseHandle.argtypes = [w.HANDLE]
    handle = api.OpenProcess(0x1000 | 0x100000 | 1, False, owner['pid'])
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        created, exited, kernel, user = (w.FILETIME() for _ in range(4))
        if not api.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
            raise ctypes.WinError(ctypes.get_last_error())
        if filetime(created) != owner['started']:
            raise ReleaseError('Lock owner PID was reused; process preserved')
        # Recheck IDLE immediately before acting on the same kernel handle.
        if not idle_gradle(process_details(owner['pid']), owner['pid']):
            raise ReleaseError('Gradle became active; retry deletion after its build finishes')
        if not api.TerminateProcess(handle, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        if api.WaitForSingleObject(handle, 5000) != 0:
            raise ReleaseError('Idle Gradle has not exited; retry deletion')
    finally:
        api.CloseHandle(handle)


def release_managed_jar(path, root):
    value = str(path)
    if value.startswith('\\\\?\\'):
        value = '\\\\' + value[8:] if value.startswith('\\\\?\\UNC\\') else value[4:]
    path, root = Path(value).resolve(), Path(root).resolve()
    if path.suffix.lower() != '.jar' or not path.is_relative_to(root):
        raise ReleaseError('Lock recovery is limited to JAR files in this managed build')
    owners = locking_processes(path)
    for owner in owners:
        if not idle_gradle(process_details(owner['pid']), owner['pid']):
            raise ReleaseError(f"Managed JAR is held by active/non-Gradle PID {owner['pid']}; process preserved")
    for owner in owners:
        stop_same_process(owner)
    return [o['pid'] for o in owners]


def adb_server_pid(port):
    # Identify the configured fork-server directly. Windows CIM TCP State can be
    # null even for a live ADB server, so it is not a reliable identity source.
    command = ("Get-CimInstance Win32_Process -Filter \"Name = 'adb.exe'\" | "
               "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
    output = capture(['powershell', '-NoProfile', '-Command', command])
    records = json.loads(output) if output else []
    records = records if isinstance(records, list) else [records]
    endpoints = ('tcp:' + str(port), 'tcp:localhost:' + str(port), 'tcp:127.0.0.1:' + str(port))
    pids = set()
    for record in records:
        args = command_arguments(record.get('CommandLine') or '')
        if ('fork-server' in args and 'server' in args and '-L' in args
                and args.index('-L') + 1 < len(args) and args[args.index('-L') + 1] in endpoints):
            pids.add(int(record['ProcessId']))
    return next(iter(pids)) if len(pids) == 1 else None


def release_idle_project_adb(config, root):
    """Stop only the configured non-global, verified, device-free ADB server."""
    port = config.get('adb_server_port')
    if type(port) is not int or not 1024 <= port <= 65535 or port == 5037 or not config.get('android_sdk'):
        return False
    root = Path(root).resolve()
    with lock(root / ('.adb-server-' + str(port) + '.lock')):
        pid = adb_server_pid(port)
        if not pid:
            return False
        details = process_details(pid)
        executable = Path(config['android_sdk']) / 'platform-tools/adb.exe'
        if Path(details.get('ExecutablePath') or '').resolve() != executable.resolve():
            return False
        args = command_arguments(details.get('CommandLine') or '')
        endpoint = args[args.index('-L') + 1] if '-L' in args and args.index('-L') + 1 < len(args) else None
        listeners = ('tcp:' + str(port), 'tcp:localhost:' + str(port), 'tcp:127.0.0.1:' + str(port))
        if ('fork-server' not in args or 'server' not in args or endpoint not in listeners or not details.get('CreationDate')):
            return False
        env = dict(os.environ, ANDROID_ADB_SERVER_PORT=str(port), ADB_SERVER_SOCKET='tcp:127.0.0.1:' + str(port))
        devices = capture([executable, '-P', str(port), 'devices'], cwd=root, env=env)
        if any(line.strip() and not line.startswith('List of devices') for line in devices.splitlines()):
            raise ReleaseError(f'Dedicated ADB port {port} has connected devices; server preserved')
        current = process_details(pid)
        if (adb_server_pid(port) != pid or current.get('CreationDate') != details['CreationDate']
                or current.get('ExecutablePath') != details.get('ExecutablePath')):
            raise ReleaseError('ADB identity changed during cleanup; process preserved')
        capture([executable, '-P', str(port), 'kill-server'], cwd=root, env=env)
        return True
