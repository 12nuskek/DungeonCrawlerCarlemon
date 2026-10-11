"""Source-bound, import-only Warden dependency derivation; never runs an entry point."""
from pathlib import Path
import ast,hashlib,importlib,importlib.util,json,os,stat,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
ENTRY_FILES=('scripts/run-f1-c01-warden-r1.py','scripts/floor1/warden-runtime-supervisor.py','scripts/floor1/warden-continuation-state.py')
EXTRACTED_FILES={'scripts/floor1/native-friendship.py':('target','level_ups'),'scripts/floor1/guard-first-state.py':('encode','level_stats')}
_probe=None
def require(value,reason):
    if not value:raise AssertionError(reason)
def sha(path):
    path=Path(path);before=path.lstat();require(stat.S_ISREG(before.st_mode),'regular validator dependency required: '+str(path))
    h=hashlib.sha256(path.read_bytes()).hexdigest();after=path.lstat()
    stable=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns)
    require(stable(before)==stable(after),'validator dependency changed during derivation')
    return h
def verify_manifest(actual,expected):
    require(actual==expected,'missing, added or changed genuine validator dependency')
def linked_paths(binary,text):
    require('not found' not in text,'missing genuine native dependency: '+str(binary))
    require('statically linked' not in text and 'not a dynamic executable' not in text,'unexpected native linkage: '+str(binary))
    paths={Path(word).resolve() for word in text.split() if word.startswith('/')}
    require(paths,'empty native linkage: '+str(binary));return paths
def probe():
    # The exact entry files are loaded with non-__main__ names. The spy records
    # native state adapters that use spec loaders without sys.modules entries.
    loaded=set();original=importlib.util.spec_from_file_location
    def tracked(name,location,*args,**kwargs):
        p=Path(location).resolve();require(p.is_relative_to(ROOT/'scripts'),'unexpected local validator source')
        loaded.add(p);return original(name,p,*args,**kwargs)
    importlib.util.spec_from_file_location=tracked
    try:
        for i,name in enumerate(ENTRY_FILES):
            spec=tracked('warden_import_only_'+str(i),ROOT/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    finally:importlib.util.spec_from_file_location=original
    sources={p:ast.parse(p.read_text()) for p in loaded}
    # Existing adapters execute only these extracted definitions, rather than
    # importing obsolete historical module top-level source assertions.
    for name,functions in EXTRACTED_FILES.items():
        p=ROOT/name;tree=ast.parse(p.read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in functions]
        require({n.name for n in selected}==set(functions),'extracted validator definitions changed')
        sources[p]=ast.Module(body=selected,type_ignores=[])
    imports=[]
    for p,tree in sorted(sources.items()):
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                for alias in n.names:importlib.import_module(alias.name)
            elif isinstance(n,ast.ImportFrom) and n.module!='__future__':
                require(not n.level,'unreviewed relative project import')
                parent=importlib.import_module(n.module)
                for alias in n.names:
                    require(alias.name!='*','unreviewed wildcard project import')
                    if not hasattr(parent,alias.name):importlib.import_module(n.module+'.'+alias.name)
            elif isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='__import__':
                require(n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str),'unresolved dynamic project import')
                importlib.import_module(n.args[0].value)
            if isinstance(n,(ast.Import,ast.ImportFrom)):imports.append(dict(source=str(p.relative_to(ROOT)),line=n.lineno,statement=ast.unparse(n)))
    # Exercise the exact late P6/RGB decoder path using in-memory synthetic bytes.
    # This is import discovery, never an observer/gameplay capture or state test.
    import io
    from PIL import Image,PpmImagePlugin
    require(Image.OPEN['PPM'][0] is PpmImagePlugin.PpmImageFile,'exact PPM registration')
    with Image.open(io.BytesIO(b'P6\n240 160\n255\n'+bytes(115200)),formats=['PPM']) as image:
        require(image.mode=='RGB' and len(image.convert('RGB').tobytes())==115200,'native P6 decoder discovery')
    import sysconfig,site
    sysconfig.get_path('stdlib') # Resolve the platform's actual sysconfig data.
    modules={};paths={Path(sys.executable).resolve()}
    for name,m in sorted(sys.modules.items()):
        spec=getattr(m,'__spec__',None);origin=getattr(spec,'origin',None)
        if origin in ('built-in','frozen') or origin is None:modules[name]=origin;continue
        p=Path(origin).resolve();require(p.is_file(),'missing loaded Python operand: '+str(p));paths.add(p);modules[name]=str(p)
        cache=getattr(m,'__cached__',None)
        if cache and Path(cache).is_file():paths.add(Path(cache).resolve())
    for p in sources:
        paths.add(p)
        cache=Path(importlib.util.cache_from_source(str(p)))
        if cache.is_file():paths.add(cache.resolve())
    # Site startup executes these files before normal imports; retain their pins.
    for directory in site.getsitepackages():paths.update(p.resolve() for p in Path(directory).glob('*.pth'))
    config=Path(sys.prefix)/'pyvenv.cfg'
    if config.is_file():paths.add(config.resolve())
    mapped=set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        parts=line.split()
        if len(parts)>=6 and parts[5].startswith('/') and '.so' in Path(parts[5]).name:
            require(not line.endswith(' (deleted)'),'deleted mapped validator dependency');mapped.add(Path(parts[5]).resolve())
    paths.update(mapped)
    print(json.dumps(dict(schema='warden-source-import-closure/v1',entry_files=list(ENTRY_FILES),project_sources={str(p.relative_to(ROOT)):sha(p) for p in sources},extracted_definitions=EXTRACTED_FILES,project_import_statements=imports,modules=modules,paths=sorted(map(str,paths)),native_extensions=sorted({str(Path(origin)) for origin in modules.values() if origin and str(origin).endswith('.so')}),mapped_libraries=sorted(map(str,mapped)),Tk_imported=any(n=='_tkinter' or n=='tkinter' or n.startswith('tkinter.') for n in modules),entry_points_executed=0,emulators=0,synthetic_decoder_discovery=True),sort_keys=True))
def derive(environment):
    global _probe
    if _probe is None:
        p=subprocess.run([str(Path(sys.executable).resolve()),'-B',str(Path(__file__).resolve()),'--probe'],env=environment,cwd=ROOT,text=True,capture_output=True,timeout=30)
        require(p.returncode==0 and not p.stderr,'source import derivation failed: '+p.stderr[-2000:])
        require(len(p.stdout)<8*1024**2,'source import derivation output bound');_probe=json.loads(p.stdout)
        require(_probe['entry_points_executed']==_probe['emulators']==0,'import-only derivation required')
    record=dict(_probe);paths={Path(p) for p in record['paths']}
    for rel,pin in record['project_sources'].items():require(sha(ROOT/rel)==pin,'derived executable source changed')
    native={Path(sys.executable).resolve(),Path('/bin/sh').resolve(),Path('/bin/bash').resolve()}
    for command in ('git','ldd'):
        import shutil
        p=shutil.which(command,path=environment['PATH']);require(p,'missing validator command: '+command);paths.add(Path(p).resolve())
        if command=='git':native.add(Path(p).resolve())
    native.update(Path(p) for p in record['native_extensions']);paths.update(native);links={}
    for p in sorted(native):
        text=subprocess.check_output(['ldd',str(p)],env=environment,text=True,timeout=10)
        linked=linked_paths(p,text);paths.update(linked);links[str(p)]=sorted(map(str,linked))
    record.update(native_link_closure=links,files={str(p):sha(p) for p in sorted(paths)})
    return record
if __name__=='__main__':
    require(sys.argv[1:]==['--probe'],'only inert import discovery is supported');probe()
