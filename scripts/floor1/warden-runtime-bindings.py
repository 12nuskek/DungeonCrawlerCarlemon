"""Exact accepted scaffold/dependency inventories. Reading grants no runtime authority."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
SCRATCH=Path('/workspace/scratch')
ACCEPTED=SCRATCH/'c01-warden-continuation-finalization-offline-r6-20261011'
CONFIG=SCRATCH/'c01-warden-finalization-offline-inputs-r6-20261011.json'
HANDOFF=SCRATCH/'c01-warden-finalization-offline-final-handoff-private-r6-20261011.json'
CONFIG_SHA='852d58aac1e3f013f2f4f54fd09192be1344826c2bf256c6de000569409a05f8'
RECEIPT_SHA='02cd5b36296852cfb244ef9c4894f560e8345c5fa42876787ee6f864adf1f5bd'
HANDOFF_SHA='816caec7e8889b75833222b85e9dadb58d033f4f5b4a876b335cf31981ea683a'
TESTED='ffc023294348afadbf5e70658b37a57333889254'
PROOF=SCRATCH/'c01-warden-native-dialogue-state-proof-r1-20261011/proof-receipt-private.json'
PROOF_SHA='f82bc04d5852b5a6d81795e2a9974ba8cdd106cfb19f0f0b49bf72ec4f045f73'
GAME_SOURCE='4a92a9de70848b9d7275f9f255bb0d2f53232ab8'
ENGINE_TREE='0fedd142f43f136ceee189c54101b095fc88f495'
MAIN='2574e5751767a6f32859bbe8852e0acd0722cf8d'
LOCAL_MAIN='65bc4073d140b9d58bf1b83bd33235e28c972b23'
ROM_SHA='79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246'
ELF_SHA='7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d'
WIRING=('scripts/floor1/warden-runtime-supervisor.py','scripts/floor1/warden-runtime-bindings.py',
        'scripts/floor1/warden-runtime-retention.py','scripts/floor1/warden-runtime-validator-closure.py',
        'scripts/run-f1-c01-warden-r1.py','scripts/test-warden-runtime-wiring-offline.py',
        'scripts/contracts/f1-c01-warden-supervisor-r1.json','docs/floor1/c01-warden-supervisor-r1-contract.md',
        'AGENTS.md','docs/backlog.md','docs/progress.md','docs/floor1/backlog.md','docs/floor1/accepted-plan.md')

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

retention=module('warden_retention',ROOT/'scripts/floor1/warden-runtime-retention.py')
require,sha,read=retention.require,retention.sha,retention.read

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def environment(tool):
    env=dict(os.environ,LD_LIBRARY_PATH=str(tool/'usr/lib/x86_64-linux-gnu'),PATH=str(Path(sys.executable).resolve().parent)+os.pathsep+os.defpath,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
    for key in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','LD_PRELOAD'):env.pop(key,None)
    return env

def merge_exact(*manifests):
    result={}
    for manifest in manifests:
        for path,pin in manifest.items():
            require(path not in result or result[path]==pin,'conflicting exact dependency overlap: '+path)
            result[path]=pin
    return result

def verify_manifest(actual,expected):require(actual==expected,'exact dependency keys/hashes; no missing, extras or changed entries')

def reviewed():
    require(sha(CONFIG)==CONFIG_SHA and sha(HANDOFF)==HANDOFF_SHA and sha(ACCEPTED/'offline-receipt-private.json')==RECEIPT_SHA and sha(PROOF)==PROOF_SHA,'accepted actual offline receipt/proof/config seals')
    config,h,r,p=read(CONFIG),read(HANDOFF),read(ACCEPTED/'offline-receipt-private.json'),read(PROOF)
    require(h['PASS'] and r['PASS'] and h['tested_commit']==h['published_commit']==r['source_commit']==TESTED and r['observer_never_invoked'] is True and not r['runtime_authority'] and r['runtime_claims']==r['emulator_processes']==0,'accepted exact offline scaffold')
    require(config['files']==r['input_pins'] and config['protected_history']==r['protected_history_SHA256'] and len(config['files'])==842 and len(config['protected_history'])==129 and len(r['source_inventory'])==2623,'exact sealed scaffold inventories, not mismatched receipt sets')
    for name,row in h['artifacts'].items():require(sha(ACCEPTED/name)==row['SHA256'],'accepted compiled/inert/proof artifact: '+name)
    for path,pin in config['files'].items():require(sha(path)==pin,'unchanged accepted input: '+path)
    for path,pin in config['protected_history'].items():require(sha(path)==pin,'unchanged accepted prior receipt: '+path)
    for rel,pin in r['source_inventory'].items():require(sha(ROOT/rel)==pin,'unchanged accepted scaffold source: '+rel)
    require(p['PASS'] and p['emulators']==0 and p['runtime_admission'] is False and p['ROM_SHA256']==ROM_SHA and p['ELF_SHA256']==ELF_SHA,'accepted native proof identity and limited offline scope')
    for path,pin in p['input_pins'].items():require(sha(path)==pin,'native source/ELF proof input: '+path)
    for path,pin in p['protected_history'].items():require(sha(path)==pin,'native proof prior history: '+path)
    require(git('rev-parse','refs/heads/main')==LOCAL_MAIN and git('rev-parse','refs/remotes/origin/main')==MAIN and git('rev-parse','HEAD:engine')==ENGINE_TREE and h['identities']['game_build']==GAME_SOURCE and h['identities']['ROM_SHA256']==ROM_SHA and h['identities']['ELF_SHA256']==ELF_SHA,'unchanged local/published main/game source/tree/build')
    require(r['budgets']['continuation']['total']==134360 and r['budgets']['cold']['total']==2044 and r['storage']['reservation_bytes']==17694519296 and r['generated_Save_hooks_release_two_Yes_completion'],'unchanged full route/reservation/native Save assertions')
    return config,r

def sources(config,r):
    project={str(Path(p).relative_to(ROOT)):pin for p,pin in config['files'].items() if Path(p).is_relative_to(ROOT)}
    historic=read(retention.PREP/'proposal-private.json')['source_files_SHA256']
    result=merge_exact(r['source_inventory'],project,historic,{p:sha(ROOT/p) for p in WIRING})
    for rel,pin in result.items():require(sha(ROOT/rel)==pin,'complete exact source closure: '+rel)
    return result

def linked(binary,env):
    text=subprocess.check_output(['ldd',str(binary)],env=env,text=True,timeout=10)
    require('not found' not in text and 'not a dynamic executable' not in text,'complete native linkage')
    return {str(Path(word).resolve()):sha(Path(word).resolve()) for word in text.split() if word.startswith('/')}

def tools(config,observer,closure):
    tool=Path(config['tool_root']);env=environment(tool)
    result={p:pin for p,pin in config['files'].items() if not Path(p).is_relative_to(ROOT)}
    result=merge_exact(result,closure['files'],linked(observer,env),{str(Path(sys.executable).resolve()):sha(Path(sys.executable).resolve())})
    for name in ('cc','git','ldd'):
        binary=Path(shutil.which(name,path=env['PATH'])).resolve();result[str(binary)]=sha(binary)
        if name!='ldd':result=merge_exact(result,linked(binary,env))
        else:
            require(binary.read_bytes().startswith(b'#!/bin/bash\n'),'exact ldd script interpreter')
            shell=Path('/bin/bash').resolve();result=merge_exact(result,{str(shell):sha(shell)},linked(shell,env))
    for name in ('cc1','as','ld'):
        binary=Path(subprocess.check_output(['cc','-print-prog-name='+name],env=env,text=True).strip())
        if not binary.is_absolute():binary=Path(shutil.which(str(binary),path=env['PATH']))
        binary=binary.resolve();result[str(binary)]=sha(binary);result=merge_exact(result,linked(binary,env))
    # Derive the actual compile-header graph rather than assuming the older
    # accepted header inventory covers this recovered compiler's system headers.
    deps=subprocess.check_output(['cc','-std=gnu11','-I'+str(tool/'usr/include'),'-M',str(observer.parent/'observer.c')],cwd=ROOT,env=env,text=True,timeout=30)
    require(len(deps)<1024**2 and ': ' in deps,'bounded actual compiler dependency graph')
    headers={Path(p).resolve() for p in shlex.split(deps.split(': ',1)[1].replace('\\\n',' '))}
    require(observer.parent/'observer.c' in headers and any(p.suffix=='.h' for p in headers),'actual observer/header operands')
    result=merge_exact(result,{str(p):sha(p) for p in headers})
    for path,pin in result.items():require(sha(path)==pin,'exact actual tooling closure')
    return result

def candidate_source():
    old=(ACCEPTED/'observer.c').read_text()
    require(hashlib.sha256(old.encode()).hexdigest()=='6a5bdfc6763e983aea115016e27f0c0317358a651c04121704f1a3c21d2cbbc8','exact tested closed observer source')
    gate='    return 101; /* CLOSED: offline-only; no core, ROM, Save, reset or frames. */\n'
    require(old.count(gate)==1,'exact old unconditional entry refusal')
    candidate=old.replace(gate,'',1)
    at=old.index(gate)
    require(candidate[:at]+gate+candidate[at:]==old,'only the declared unconditional refusal is removed')
    require(candidate.count('->runFrame(')==old.count('->runFrame(') and candidate.count('core->reset(')==old.count('core->reset('),'all accepted cadence and runtime assertions unchanged')
    return candidate
