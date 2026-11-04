"""Retain and upload the debug information from each signed Android build."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid
import zipfile

from ..core import ReleaseError, atomic_json, digest, read_json


ABI_SYMBOLS = {
    'armeabi-v7a': 'app.android-arm.symbols',
    'arm64-v8a': 'app.android-arm64.symbols',
    'x86_64': 'app.android-x64.symbols',
}
MAPPING_ASSET = 'assets/sentry-debug-meta.properties'
PLAY_MAPPING = 'BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map'


def mapping_uuid(path):
    # Match Sentry Gradle 6.25.0: Java nameUUIDFromBytes uses the R8 hash.
    with path.open('rb') as stream:
        header = stream.read(4096)
    match = re.search(rb'^# pg_map_hash: SHA-256 ([a-f0-9]{64})\r?$', header, re.M)
    if not match:
        raise ReleaseError('Missing R8 SHA-256 mapping header')
    return str(uuid.UUID(bytes=hashlib.md5(match[1], usedforsecurity=False).digest(), version=3))


def elf_info(ctx, path, *, packaged=False):
    output = ctx.command([ctx.config['sentry_cli'], 'debug-files', 'check', '--json', str(path)],
                         success_codes=(0, 1) if packaged else (0,))
    info = json.loads(output)
    variants = info.get('variants', [])
    if info.get('type') != 'elf' or len(variants) != 1 or not variants[0].get('code_id'):
        raise ReleaseError(f'Missing ELF build ID for {path.name}')
    if not packaged and not info.get('is_usable'):
        raise ReleaseError(f'No usable symbols for {path.name}')
    return {**variants[0], 'features': info.get('features', '')}


def retain(ctx, package, private):
    prefix = 'base/' if package.suffix == '.aab' else ''
    build = ctx.workspace / 'build/app'
    mapping = build / 'outputs/mapping/release/mapping.txt'
    merged = build / 'intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib'
    if not mapping.is_file() or not mapping.stat().st_size:
        raise ReleaseError(f'Missing R8 mapping for {package.name}')
    mapping_hash = digest(mapping)
    images = {}
    with zipfile.ZipFile(package) as archive, tempfile.TemporaryDirectory(dir=private) as temp:
        try:
            properties = archive.read(prefix + MAPPING_ASSET).decode('utf-8')
        except KeyError:
            raise ReleaseError(f'Missing Sentry R8 UUID in {package.name}') from None
        uuids = re.findall(r'^io\.sentry\.ProguardUuids=([a-f0-9-]{36})$', properties, re.M)
        if uuids != [mapping_uuid(mapping)]:
            raise ReleaseError(f'R8 mapping UUID does not match {package.name}')
        if PLAY_MAPPING in archive.namelist() and hashlib.sha256(archive.read(PLAY_MAPPING)).hexdigest() != mapping_hash:
            raise ReleaseError(f'Packaged R8 mapping differs from the retained mapping for {package.name}')
        native = re.compile(re.escape(prefix) + r'lib/([\w-]+)/(lib[\w.+-]+\.so)$')
        aot_abis = set()
        for name in archive.namelist():
            match = native.fullmatch(name)
            if not match:
                continue
            abi, library = match.groups()
            packaged = Path(temp) / library
            with archive.open(name) as source, packaged.open('wb') as target:
                shutil.copyfileobj(source, target)
            stripped = elf_info(ctx, packaged, packaged=True)
            if library == 'libapp.so':
                aot_abis.add(abi)
                symbol = private / 'aot' / ABI_SYMBOLS.get(abi, 'unsupported-abi')
                if not symbol.is_file():
                    raise ReleaseError(f'Missing AOT symbols for {package.name} {abi}')
                unstripped = elf_info(ctx, symbol)
            else:
                original = merged / abi / library
                if not original.is_file():
                    raise ReleaseError(f'Missing native symbols for {package.name} {abi}/{library}')
                unstripped = elf_info(ctx, original)
                target = private / 'ndk' / abi / library
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
            if any(stripped[key] != unstripped[key] for key in ('debug_id', 'code_id', 'arch')):
                raise ReleaseError(f'Symbols do not match {package.name} {abi}/{library}')
            images[f'{abi}/{library}'] = unstripped
        if aot_abis != ABI_SYMBOLS.keys():
            raise ReleaseError(f'Unexpected Dart AOT ABI set in {package.name}')
    shutil.copy2(mapping, private / 'mapping.txt')
    atomic_json(private / 'native-symbols.json', {'package_sha256': digest(package),
                'r8_uuid': uuids[0], 'mapping_sha256': mapping_hash, 'images': images})


def upload(ctx, root):
    receipts = {}
    mappings = {}
    ndk_ids = set()
    for target, artifact in zip(('apk', 'aab'), ctx.job['artifacts']):
        private = root / target
        try:
            receipt = read_json(private / 'native-symbols.json')
            mapping = private / 'mapping.txt'
            if receipt['package_sha256'] != digest(ctx.output / artifact) or receipt['mapping_sha256'] != digest(mapping):
                raise ReleaseError(f'Android symbol inputs changed for {target}')
            previous = mappings.setdefault(receipt['r8_uuid'], mapping)
            if digest(previous) != receipt['mapping_sha256']:
                raise ReleaseError('Different R8 mappings share a Sentry UUID')
            for name, info in receipt['images'].items():
                if not name.endswith('/libapp.so'):
                    ndk_ids.add(info['debug_id'])
        except (OSError, KeyError, ValueError) as error:
            raise ReleaseError(f'Missing or invalid Android symbol inputs for {target}') from error
        receipts[target] = receipt
    cli = ctx.config['sentry_cli']
    bounded = [ctx.config.get('python', sys.executable), 'tools/local_release/run_sentry_upload.py',
               '--timeout', '600', '--', cli]
    for mapping_id, path in mappings.items():
        ctx.command([*bounded, 'upload-proguard', '--require-one', '--uuid', mapping_id, str(path)])
    if not ndk_ids:
        raise ReleaseError('Missing native ELF symbol IDs for Android')
    # CLI 2.58.6 --require-all checks only files returned by the upload,
    # which excludes already processed files during a retry.
    args = [*bounded, 'debug-files', 'upload', '--type', 'elf', '--wait-for', '480']
    for debug_id in sorted(ndk_ids):
        args.extend(['--id', debug_id])
    ctx.command([*args, str(root / 'apk/ndk'), str(root / 'aab/ndk')])
    return receipts


def verify_registry(ctx, receipts):
    expected = {}
    for receipt in receipts.values():
        expected[receipt['r8_uuid']] = 'proguard'
        expected.update({image['debug_id']: 'elf' for image in receipt['images'].values()})
    endpoint = 'https://sentry.io/api/0/projects/ai11-link/playas-flutter/files/dsyms/'
    headers = {'Authorization': 'Bearer ' + ctx.env['SENTRY_AUTH_TOKEN']}
    for debug_id, kind in expected.items():
        request = Request(endpoint + '?' + urlencode({'debug_id': debug_id}), headers=headers)
        with urlopen(request, timeout=20) as response:
            files = json.load(response)
        if not any(item.get('debugId') == debug_id and item.get('symbolType') == kind for item in files):
            raise ReleaseError(f'Sentry registry is missing {kind} debug ID {debug_id}')
