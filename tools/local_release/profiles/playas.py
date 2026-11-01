"""Playas: one Windows builder for Android APK/AAB and Web ZIP."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

from ..core import ReleaseError, atomic_json, digest, git, read_json
from .ai11 import pack, verify_zip, tools

QUALITY = ['dependencies', 'analyze', 'tests', 'coverage', 'coverage-threshold', 'legacy',
           'boundaries', 'test-layout', 'changelog', 'workflow-parity', 'tool-tests',
           'costaflow-setup', 'costaflow-tests', 'costaflow-inventory']
BUILD = ['apk', 'verify-apk', 'aab', 'verify-aab', 'web', 'web-zip', 'verify-web']


def metadata(repo, sha, profile):
    match = re.search(r'^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$', git(repo, 'show', sha + ':pubspec.yaml'), re.M)
    if not match:
        raise ReleaseError('Cannot parse committed Playas version')
    version, build = match[1], int(match[2])
    notes = re.search(r'(^## \[' + re.escape(version) + r'\].*?)(?=\n## |\Z)',
                      git(repo, 'show', sha + ':CHANGELOG.md'), re.M | re.S)
    if not notes:
        raise ReleaseError('Missing Playas changelog section')
    names = [f'playas-{version}+{build}.apk', f'playas-{version}+{build}.aab', f'playas-web-{version}+{build}.zip']
    tags = [t for t in git(repo, 'tag', '--points-at', sha).splitlines() if t.startswith('v')]
    return dict(version=version, build=build, tag=tags[0] if tags else f'auto-v{version}-b{build}-{sha[:8]}',
        generated_output_paths=['coverage/lcov.info'],
        generated_source_overlays={'android/gradle.properties':hashlib.sha256(gradle_properties(repo,sha).encode()).hexdigest()},
        artifacts=names, release_notes=notes[1].strip().removesuffix('---').strip(),
        release_prerelease=not bool(tags), release_make_latest='true' if tags else 'false',
        required_steps={'windows': ['preflight', *QUALITY, 'integration-android', 'integration-web', *BUILD]},
        artifact_specs={n: {'host': 'windows', 'gates': [g]} for n,g in zip(names,['verify-apk','verify-aab','verify-web'])},
        architectures={'android':['armeabi-v7a','arm64-v8a','x86_64'],'web':['javascript']},
        step_dependencies={'verify-apk':['apk'],'verify-aab':['aab'],'web-zip':['web'],'verify-web':['web-zip']})


def gradle_properties(repo,sha):
    source=git(repo,'show',sha+':android/gradle.properties').rstrip()+'\n'
    for key,comment in [('android.builtInKotlin','builtInKotlin'),('android.newDsl','newDsl')]:
        if not re.search(r'^'+re.escape(key)+r'=',source,re.M):
            source+='# This '+comment+' flag was added automatically by Flutter migrator\n'+key+'=false\n'
    return source


def compile_defines(config):
    values = read_json(Path(config['defines_file']))
    required = ['IP2LOCATION_API_KEY', 'GEOCODING_API_KEY']
    if any(not isinstance(values.get(k), str) or not values[k].strip() for k in required):
        raise ReleaseError('Playas requires both client API defines')
    return {k:values[k] for k in required}


def input_metadata(config):
    certificate = config.get('expected_signing_certificate_sha256','').lower().replace(':','')
    maps = config.get('environment',{}).get('GOOGLE_MAPS_ANDROID_API_KEY','')
    if not re.fullmatch('[a-f0-9]{64}',certificate) or not maps.strip():
        raise ReleaseError('Pin the existing release certificate and configure Android Maps key')
    return dict(compile_defines_sha256=hashlib.sha256(json.dumps(compile_defines(config),sort_keys=True).encode()).hexdigest(),
        signing_certificate_sha256=certificate, signing_keystore_sha256=digest(Path(config['signing_store_file'])),
        maps_key_sha256=hashlib.sha256(maps.encode()).hexdigest(),
        firebase_config_sha256=digest(Path(config['firebase_config_file'])) if config.get('firebase_config_file') else None)


def configure(ctx):
    for k,v in input_metadata(ctx.config).items():
        if ctx.job.get(k) != v: raise ReleaseError('Prepared Playas input changed: '+k)
    ctx.result['compile_defines_sha256']=ctx.job['compile_defines_sha256']
    for name in ['SIGNING_KEY_ALIAS','SIGNING_KEY_PASSWORD','SIGNING_STORE_PASSWORD']:
        if not ctx.env.get(name): raise ReleaseError('Missing signing variable: '+name)
    ctx.env['JAVA_HOME']=ctx.config['java_home']
    ctx.env['ANDROID_HOME']=ctx.config['android_sdk']
    ctx.env['PATH']=os_path(ctx)
    ctx.env['AI11_LOCAL_RELEASE_ENGINE']=str(Path(__file__).resolve().parents[1])
    ctx.refresh_redaction([*compile_defines(ctx.config).values(),ctx.env['GOOGLE_MAPS_ANDROID_API_KEY'],ctx.env['SIGNING_KEY_ALIAS']])
    atomic_json(ctx.workspace/'env/dart_defines.release.ci.json',compile_defines(ctx.config))
    def escaped(v): return str(v).replace('\\','\\\\').replace('\n','\\n').replace('\r','\\r')
    values={'storeFile':Path(ctx.config['signing_store_file']).as_posix(),'keyAlias':ctx.env['SIGNING_KEY_ALIAS'],
            'keyPassword':ctx.env['SIGNING_KEY_PASSWORD'],'storePassword':ctx.env['SIGNING_STORE_PASSWORD']}
    (ctx.workspace/'android/key.properties').write_text(''.join(k+'='+escaped(v)+'\n' for k,v in values.items()),encoding='utf-8')
    (ctx.workspace/'android/local.properties').write_text('sdk.dir='+Path(ctx.config['android_sdk']).as_posix()+'\nflutter.sdk='+Path(ctx.config['flutter_sdk']).as_posix()+'\n',encoding='utf-8')
    if ctx.config.get('firebase_config_file'): shutil.copy2(ctx.config['firebase_config_file'],ctx.workspace/'android/app/google-services.json')
    if not (ctx.workspace/'android/app/google-services.json').is_file(): raise ReleaseError('Missing Firebase Android config')


def os_path(ctx):
    import os
    return os.pathsep.join([str(Path(ctx.config['java_home'])/'bin'),str(Path(ctx.config['flutter_sdk'])/'bin'),ctx.env.get('PATH','')])


def preflight(ctx):
    configure(ctx)
    flutter=json.loads(ctx.command(['flutter','--version','--machine']))
    if flutter['frameworkVersion']!=ctx.job['profile']['flutter']: raise ReleaseError('Flutter differs from pinned profile')
    java=ctx.command(['java','-version'])
    if not re.search(r'version "17[.\"]',java): raise ReleaseError('Playas requires Java17')
    if sys.version_info[:2]!=(3,12): raise ReleaseError('CostaFlow requires pinned Python3.12')
    ctx.command(['flutter','doctor','-v'])
    atomic_json(ctx.directory/'results/windows-environment.json',dict(sha=ctx.job['sha'],flutter=flutter,java=java,platforms=['android','web']))


def coverage(ctx):
    source=ctx.workspace/'coverage/lcov.info'; hit=total=0; active=False
    for line in source.read_text().splitlines():
        if line.startswith('SF:'): active='/lib/' in '/'+line[3:].replace('\\','/') or line[3:].startswith('lib/')
        if active and line.startswith('DA:'):
            total+=1; hit+=int(line.split(',')[1])>0
    if not total or hit/total<.70: raise ReleaseError(f'Coverage {hit}/{total} below70%')
    shutil.copy2(source,ctx.directory/'results/windows-lcov.info')
    atomic_json(ctx.directory/'results/coverage.json',dict(hit=hit,total=total,percent=100*hit/total,threshold=70))


def verify_apk(ctx,path):
    aapt,signer=tools(ctx); badging=ctx.command([aapt,'dump','badging',path])
    expected="package: name='click.playas' versionCode='"+str(ctx.job['build'])+"' versionName='"+ctx.job['version']+"'"
    if expected not in badging or not all("'"+abi+"'" in badging for abi in ctx.job['architectures']['android']): raise ReleaseError('APK identity/version/ABIs mismatch')
    signed=ctx.command([signer,'verify','--verbose','--print-certs',path])
    cert=re.search(r'Signer #1 certificate SHA-256 digest: ([a-fA-F0-9]+)',signed)
    if not cert or cert[1].lower()!=ctx.job['signing_certificate_sha256']: raise ReleaseError('APK signing certificate mismatch')
    atomic_json(ctx.directory/'results/android-signing.json',dict(package='click.playas',version=ctx.job['version'],build=ctx.job['build'],sha=ctx.job['sha'],certificate_sha256=cert[1].lower(),apk_sha256=digest(path)))


def protobuf(data):
    """Read the wire types used by AAPT2 Resources.proto, rejecting truncation."""
    pos=0; result={}
    def varint():
        nonlocal pos
        value=0
        for shift in range(0,70,7):
            if pos>=len(data): raise ReleaseError('Truncated protobuf')
            byte=data[pos];pos+=1;value|=(byte&127)<<shift
            if byte<128:return value
        raise ReleaseError('Invalid protobuf varint')
    while pos<len(data):
        tag=varint();field,wire=tag>>3,tag&7
        if not field:raise ReleaseError('Invalid protobuf field')
        if wire==0:value=varint()
        elif wire in (1,2,5):
            length=varint() if wire==2 else (8 if wire==1 else 4)
            if pos+length>len(data):raise ReleaseError('Truncated protobuf value')
            value=data[pos:pos+length];pos+=length
        else:raise ReleaseError('Unsupported protobuf wire type')
        result.setdefault(field,[]).append(value)
    return result


def manifest_attributes(data):
    # https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/tools/aapt2/Resources.proto
    node=protobuf(data);element=protobuf(node[1][0]);attrs={}
    if element[3][0]!=b'manifest':raise ReleaseError('AAB root is not manifest')
    for encoded in element.get(4,[]):
        attr=protobuf(encoded);name=attr[2][0].decode()
        if 3 in attr:value=attr[3][0].decode()
        elif 6 in attr:
            item=protobuf(attr[6][0])
            if 7 in item:
                primitive=protobuf(item[7][0]);value=str(primitive.get(6,primitive.get(7,[None]))[0])
            else:continue
        else:continue
        attrs[name]=value
    return attrs


def verify_aab(ctx,path):
    verify_zip(path,['BundleConfig.pb','base/manifest/AndroidManifest.xml','base/dex/classes.dex'])
    with zipfile.ZipFile(path) as z:
        if not all(any(n.startswith('base/lib/'+abi+'/') for n in z.namelist()) for abi in ctx.job['architectures']['android']): raise ReleaseError('AAB omits ABI')
        attrs = manifest_attributes(z.read('base/manifest/AndroidManifest.xml'))
        expected = {'package':'click.playas','versionName':ctx.job['version'],'versionCode':str(ctx.job['build'])}
        if any(attrs.get(k)!=v for k,v in expected.items()): raise ReleaseError('AAB identity/version/build mismatch')
    verification=ctx.command(['jarsigner','-verify',path])
    if 'jar verified.' not in verification: raise ReleaseError('AAB JAR signature invalid')
    cert=ctx.command(['keytool','-printcert','-jarfile',path])
    pin=re.search(r'SHA256:\s*([A-Fa-f0-9:]+)',cert)
    if not pin or pin[1].lower().replace(':','')!=ctx.job['signing_certificate_sha256']: raise ReleaseError('AAB certificate mismatch')
    atomic_json(ctx.directory/'results/aab-signing.json',dict(aab_sha256=digest(path),certificate_sha256=ctx.job['signing_certificate_sha256']))


def verify_web(ctx,path):
    verify_zip(path,['index.html','main.dart.js','flutter_bootstrap.js','version.json'])
    with zipfile.ZipFile(path) as z:
        version=json.loads(z.read('version.json'))
        if (version.get('version'),str(version.get('build_number')))!=(ctx.job['version'],str(ctx.job['build'])): raise ReleaseError('Web version/build mismatch')


def integration(ctx,platform):
    from ..prerequisites import android_device,chrome_driver
    target='integration_test/pla297_release_smoke_test.dart'
    generated=ctx.workspace/target
    if generated.exists(): raise ReleaseError('Generated integration entrypoint already exists; preserve it for inspection')
    tests=sorted((ctx.workspace/'integration_test').glob('*_test.dart'))
    if not tests: raise ReleaseError('No Playas integration tests')
    text='\n'.join("import '"+p.name+"' as test"+str(i)+';' for i,p in enumerate(tests))+'\nvoid main() {\n'+''.join('test'+str(i)+'.main();\n' for i in range(len(tests)))+'}\n'
    generated.write_text(text,encoding='utf-8')
    try:
        if platform=='android':
            with android_device(ctx):
                ctx.command(['flutter','test','--no-pub',target,'-d',ctx.config['android_device'],'--reporter=expanded'],cwd=ctx.workspace)
        else:
            with chrome_driver(ctx):
                ctx.command(['flutter','drive','--no-pub','--release','--driver=tools/local_release/driver.dart','--target='+target,'-d','web-server','--browser-name=chrome','--headless','--driver-port='+str(ctx.config['chromedriver_port']),'--web-port='+str(ctx.config['web_port']),'--web-browser-flag=--incognito','--web-browser-flag=--user-data-dir='+str(ctx.root/'w/chrome-Playas-PLA297-01a19838')],cwd=ctx.workspace)
        atomic_json(ctx.directory/('results/integration-'+platform+'.json'),{'sha':ctx.job['sha'],'tests':[p.relative_to(ctx.workspace).as_posix() for p in tests],'platform':platform,'status':'passed'})
    finally:
        generated.unlink(missing_ok=True)


def run(ctx):
    if ctx.host!='windows': raise ReleaseError('Playas uses one Windows builder')
    try:
        ctx.stage('preflight',lambda:preflight(ctx),always=True)
        bash=ctx.config['bash']; python=ctx.config['python']
        commands={'dependencies':['flutter','pub','get'],'analyze':['dart','analyze'],
            'tests':['flutter','test','--no-pub','--reporter=expanded'],
            'coverage':['flutter','test','--no-pub','--coverage','--reporter=expanded'],
            'legacy':[bash,'tools/ci/check_no_new_legacy_imports.sh'],
            'boundaries':[bash,'tools/ci/check_import_boundaries.sh'],
            'test-layout':[bash,'tools/ci/check_test_layout.sh'],
            'changelog':[bash,'tools/ci/check_changelog_version.sh'],
            'workflow-parity':[python,'tools/local_release/inventory.py','--check'],
            'tool-tests':[python,'-m','unittest','discover','-s','tools/local_release/tests','-v']}
        for name,argv in commands.items():
            ctx.stage(name,lambda argv=argv:ctx.command(argv,cwd=ctx.workspace))
        ctx.stage('coverage-threshold',lambda:coverage(ctx),['results/windows-lcov.info','results/coverage.json'])
        venv=ctx.workspace/'.venv-costaflow'; py=venv/'Scripts/python.exe'
        def setup():
            if not py.exists(): ctx.command([python,'-m','venv',venv],cwd=ctx.workspace)
            ctx.command([py,'-m','pip','install','./tools/costaflow[dev]'],cwd=ctx.workspace)
        ctx.stage('costaflow-setup',setup)
        if not py.exists(): setup()
        ctx.stage('costaflow-tests',lambda:ctx.command([py,'-m','pytest','tools/costaflow/tests','-q'],cwd=ctx.workspace))
        ctx.stage('costaflow-inventory',lambda:ctx.command([py,'-m','costaflow','inventory','--output',ctx.directory/'results/costaflow'],cwd=ctx.workspace),['results/costaflow/coverage.json','results/costaflow/coverage.html'])
        for platform in ['android','web']: ctx.stage('integration-'+platform,lambda platform=platform:integration(ctx,platform))
        apk,aab,web=[ctx.output/n for n in ctx.job['artifacts']]
        # The normal build pub phase regenerates release-only plugin registration after integration_test.
        flags=['--release','--dart-define-from-file=env/dart_defines.release.ci.json']
        for name,command,source,dest in [('apk','apk','build/app/outputs/flutter-apk/app-release.apk',apk),('aab','appbundle','build/app/outputs/bundle/release/app-release.aab',aab)]:
            def build(command=command,source=source,dest=dest):
                ctx.command(['flutter','build',command,*flags],cwd=ctx.workspace);shutil.copy2(ctx.workspace/source,dest)
            ctx.stage(name,build,['packages/'+dest.name])
            verifier=verify_apk if name=='apk' else verify_aab
            ctx.stage('verify-'+name,lambda verifier=verifier,dest=dest:verifier(ctx,dest))
        ctx.stage('web',lambda:ctx.command(['flutter','build','web',*flags,'--no-wasm-dry-run','--no-tree-shake-icons'],cwd=ctx.workspace))
        ctx.stage('web-zip',lambda:pack(ctx.workspace/'build/web',web),['packages/'+web.name])
        ctx.stage('verify-web',lambda:verify_web(ctx,web))
    finally:
        for rel in ['android/key.properties','env/dart_defines.release.ci.json']:(ctx.workspace/rel).unlink(missing_ok=True)
