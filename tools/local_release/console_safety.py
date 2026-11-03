"""Native Windows preflight: no transient console shows or foreground steals."""

import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

_verified = None


def _gui_probe_source():
    leaf = '''import ctypes,json
k=ctypes.windll.kernel32
k.GetConsoleWindow.restype=ctypes.c_void_p
h=k.GetConsoleWindow()
print(json.dumps({'console':h,'visible':bool(ctypes.windll.user32.IsWindowVisible(ctypes.c_void_p(h or 0)))}))
'''
    cli = '''import ctypes,json,subprocess,sys,time
k=ctypes.windll.kernel32
k.GetConsoleWindow.restype=ctypes.c_void_p
h=k.GetConsoleWindow()
parent={'console':h,'visible':bool(ctypes.windll.user32.IsWindowVisible(ctypes.c_void_p(h or 0)))}
probe=LEAF_SOURCE
rows=[]
for _ in range(6):
 rows.append(json.loads(subprocess.check_output([sys.executable,'-c',probe],text=True)))
 subprocess.check_output(['git','--version'])
 subprocess.check_output(['cmd','/d','/c','ver'])
 time.sleep(.03)
print(json.dumps({'parent':parent,'children':rows,'executable':sys.executable}))
'''.replace('LEAF_SOURCE', repr(leaf))
    return '''import json,sys
from pathlib import Path
sys.path.insert(0, TOOLS_PATH)
from local_release.core import Context,atomic_json,capture
code=CLI_SOURCE
job=Path(sys.argv[1])/'releases/fixture/1.0.0+1'/('a'*40)
atomic_json(job/'job.json',{'schema':1,'sha':'a'*40,'run_id':'fixture','project':'fixture'})
ctx=Context(job,{})
ctx.workspace.mkdir(parents=True)
rows=[]
for _ in range(2):
 rows.append(json.loads(capture([str(Path(sys.executable).with_name('python.exe')),'-c',code])))
 rows.append(json.loads(ctx.command(['python','-c',code])))
atomic_json(Path(sys.argv[1])/'result.json',rows)
'''.replace('TOOLS_PATH', repr(str(Path(__file__).resolve().parents[1]))).replace('CLI_SOURCE', repr(cli))


def _is_descendant(pid, roots):
    from ctypes import wintypes
    class Entry(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('usage', wintypes.DWORD),
            ('pid', wintypes.DWORD), ('heap', ctypes.c_size_t),
            ('module', wintypes.DWORD), ('threads', wintypes.DWORD),
            ('parent', wintypes.DWORD), ('priority', wintypes.LONG),
            ('flags', wintypes.DWORD), ('name', wintypes.WCHAR * 260)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise OSError('Process snapshot unavailable')
    parents = {}
    try:
        entry = Entry()
        entry.size = ctypes.sizeof(entry)
        present = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while present:
            parents[entry.pid] = entry.parent
            present = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    seen = set()
    while pid and pid not in seen:
        if pid in roots:
            return True
        seen.add(pid)
        pid = parents.get(pid)
    return False


class ConsoleEvents:
    """Observe event handles only, without screenshots, titles or user input."""

    def __init__(self, roots=None):
        self.events = []
        self.roots = roots
        self.ready = threading.Event()
        self.finished = threading.Event()
        self.error = None

    def __enter__(self):
        def observe():
            from ctypes import wintypes
            user = ctypes.WinDLL('user32', use_last_error=True)
            callback_type = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, wintypes.DWORD,
                wintypes.HWND, wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
            user.SetWinEventHook.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE,
                callback_type, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
            user.SetWinEventHook.restype = ctypes.c_void_p
            user.UnhookWinEvent.argtypes = [ctypes.c_void_p]
            user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
            user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
            user.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                wintypes.UINT, wintypes.UINT, wintypes.UINT]

            @callback_type
            def received(hook, event, window, object_id, child_id, thread, time):
                if window and event in (3, 0x8002):  # FOREGROUND, OBJECT_SHOW
                    if self.roots is not None:
                        if event == 0x8002:
                            name = ctypes.create_unicode_buffer(128)
                            user.GetClassNameW(window, name, len(name))
                            if name.value not in ('ConsoleWindowClass', 'CASCADIA_HOSTING_WINDOW_CLASS'):
                                return
                        owner = wintypes.DWORD()
                        user.GetWindowThreadProcessId(window, ctypes.byref(owner))
                        try:
                            owned = _is_descendant(owner.value, self.roots)
                        except OSError as error:
                            self.error = str(error)
                            return
                        if not owned:
                            return
                    self.events.append((event, int(window)))

            hook = user.SetWinEventHook(3, 0x8002, None, received, 0, 0, 0)
            if not hook:
                self.error = 'Windows event hook unavailable'
            self.ready.set()
            try:
                message = wintypes.MSG()
                while hook and not self.finished.wait(.005):
                    while user.PeekMessageW(ctypes.byref(message), None, 0, 0, 1):
                        user.TranslateMessage(ctypes.byref(message))
                        user.DispatchMessageW(ctypes.byref(message))
            finally:
                if hook:
                    user.UnhookWinEvent(hook)

        self.thread = threading.Thread(target=observe, daemon=True)
        self.thread.start()
        if not self.ready.wait(5) or self.error:
            self.finished.set()
            raise RuntimeError(self.error or 'Windows event observer did not start')
        return self

    def __exit__(self, *args):
        self.finished.set()
        self.thread.join(timeout=5)


def verify_console_safety():
    """Refuse real background work unless the native descendant probe passes."""
    if os.name != 'nt':
        return {'required': False}
    global _verified
    if _verified is not None:
        return dict(_verified)
    from .core import Context, ReleaseError, cli_launch_options, hidden_flags
    options = cli_launch_options()
    # Inspect before creating anything. An unsafe primitive must not be tested
    # by repeatedly opening visible windows on the owner's desktop.
    startup = options.get('startupinfo')
    if (options.get('creationflags') != subprocess.CREATE_NEW_CONSOLE or startup is None
            or not startup.dwFlags & subprocess.STARTF_USESHOWWINDOW
            or startup.wShowWindow != subprocess.SW_HIDE):
        raise ReleaseError('Unsafe console creation policy; background launch refused')
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    if not pythonw.is_file():
        raise ReleaseError('Native pythonw console-safety probe is unavailable')
    with tempfile.TemporaryDirectory(prefix='ai11-console-safety-') as folder:
        root = Path(folder)
        script = root / 'probe.py'
        script.write_text(_gui_probe_source(), encoding='utf-8')
        with ConsoleEvents() as observation:
            process = subprocess.Popen([str(pythonw), str(script), str(root)],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=hidden_flags())
            try:
                code = process.wait(timeout=45)
            except BaseException:
                from .processes import terminate_tree
                terminate_tree(process)
                process.wait()
                raise
        result = root / 'result.json'
        if observation.error:
            raise ReleaseError('Native console event observation failed; background launch refused')
        if code != 0 or not result.is_file():
            raise ReleaseError('Native console-safety probe failed; background launch refused')
        rows = json.loads(result.read_text(encoding='utf-8'))
        handles = {row['parent']['console'] for row in rows}
        if len(rows) != 4 or not all(handles):
            raise ReleaseError('Console inheritance proof is incomplete')
        for row in rows:
            if (Path(row['executable']).name.lower() != 'python.exe'
                    or row['parent']['visible'] or len(row['children']) != 6
                    or any(child['visible'] or child['console'] != row['parent']['console']
                           for child in row['children'])):
                raise ReleaseError('CLI descendants have an unsafe console; background launch refused')
        relevant = [(event, handle) for event, handle in observation.events if handle in handles]
        if relevant:
            raise ReleaseError('Transient console show/foreground event detected; background launch refused')
        _verified = {'required': True, 'passed': True, 'cli_parents': 4, 'nested_cycles': 24,
                'visible_consoles': 0, 'transient_show_events': 0, 'foreground_steals': 0}
        return dict(_verified)
