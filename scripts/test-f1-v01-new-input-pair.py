"""One new-input baseline and conditional candidate; immutable original/copies and first STOP."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, resource, shutil, struct, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path('/workspace/scratch/new-input-visual-pair-20261010')
BASE='c6d647a815ffce44a2419a2cf83b6c2c094359f0'
CANDIDATE='9c83611e8e9b61d55388c18496c361d3362e462e'
SEED=Path('/workspace/scratch/ordinary-recovery-r6-20261010/runtime-prepare-03/patrol.sav')
SAVE_SHA='53f62dc2e283d89236d5572f47c3e7449c0bc1c06de738b1427fc9664ae67eb6'
MAIN_BUILD=Path('/workspace/scratch/ordinary-recovery-r4-20261010/build')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
ROUTE_SHA='afbd80b02d9d5acb9f63669f967fac3edc8eb00a2d2352e778f4114acb51bc27'
FILE_CAP=2*1024**3

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(FILE_CAP,FILE_CAP))
def inputs():
    assert sha(SEED)==SAVE_SHA and not SEED.is_symlink()
    assert sha(ROOT/'scripts/contracts/f1-v01-battle.route')==ROUTE_SHA
    assert len((ROOT/'scripts/contracts/f1-v01-battle.route').read_text().splitlines())==48
    assert sha(TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5')=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    assert not git('status','--porcelain'),'Commit reviewed source before preparation/execution'
def prepared(case):return OUTPUT/case

def prepare():
    inputs(); assert not (OUTPUT/'freeze.json').exists() and not (OUTPUT/'STOP.json').exists()
    old=module('new_pair_helpers',ROOT/'scripts/test-f1-v01-battle.py')
    state=module('new_pair_main_save',MAIN_BUILD/'source/scripts/floor1/guard-first-state.py')
    binding=module('new_pair_storage',ROOT/'scripts/floor1/v01-retained-reference.py')
    code,_=module('new_pair_host',ROOT/'scripts/floor1/v01-battle-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='1647352d92b3fa6f0135cf80f4c48df1c2a8a3818b711fd94651390a6334977f'
    budget=binding.storage_bound(code,13488067)
    # Preserve every original capacity and combined capture/log allowance. Bound
    # the new stream/copy by a hard kernel limit rather than historical density.
    block=budget['filesystem_block_bytes'];rounded=lambda n:(n+block-1)//block*block
    budget['required_available_bytes']+=rounded(FILE_CAP)-rounded(budget['reference_copy'])
    budget['reference_copy']=FILE_CAP
    pair_budget=2*budget['required_available_bytes']+3*FILE_CAP
    stat=os.statvfs(OUTPUT);available=stat.f_bavail*stat.f_frsize
    assert available>=pair_budget,'Combined pair/reference/captures/two clips/archive storage unavailable'
    cases={}
    for case,build,game in [('baseline',MAIN_BUILD,BASE),('candidate',OUTPUT/'candidate-build',CANDIDATE)]:
        out=prepared(case);assert out.is_dir() and not (out/'identity.json').exists()
        native=json.loads((out/'result.json').read_text());assert native['PASS'] and native['active_game_source']==game
        assert native['host_source_SHA256']==hashlib.sha256(code.encode()).hexdigest()
        engine=build/'source/engine'; assert (build/'tested-commit.txt').read_text().strip()==game
        decoded=state.seed_snapshot(SEED,out/'expected')
        assert decoded['count']==2 and decoded['map']==[35,3] and decoded['position']==[8,7] and decoded['friendship_counter']==47
        (out/'expected-counter.bin').write_bytes(struct.pack('<H',decoded['friendship_counter']))
        rows=json.loads((ROOT/'scripts/contracts/f1-v01-battle-assets.json').read_text());assert len(rows)==17
        poses=b''.join(old.packed(ROOT/r['source']) for r in rows)+old.packed(ROOT/'engine/graphics/dcc/warden/front.png');assert len(poses)==18*2048
        (out/'visual-poses.bin').write_bytes(poses);(out/'visual-mode.bin').write_bytes(bytes([case=='candidate']))
        palette=[]
        for ch in ['carl','donut','warden']:
            for line in (ROOT/'engine/graphics/dcc'/ch/'normal.pal').read_text().splitlines()[3:]:
                r,g,b=map(int,line.split());palette.append((r>>3)|((g>>3)<<5)|((b>>3)<<10))
        assert len(palette)==48;(out/'visual-palettes.bin').write_bytes(struct.pack('<48H',*palette))
        shutil.copyfile(ROOT/'scripts/contracts/f1-v01-battle.route',out/'input.route')
        files={f.name:sha(f) for f in out.iterdir() if f.is_file()}
        identity=dict(case=case,preparation_source=git('rev-parse','HEAD'),build_source=game,engine_tree=git('rev-parse',game+':engine'),ROM_SHA256=sha(engine/'pokeemerald.gba'),ELF_SHA256=sha(engine/'pokeemerald.elf'),input_Save_SHA256=SAVE_SHA,route_SHA256=ROUTE_SHA,files_SHA256=files,storage_bound=budget,native_binding=native,execution_limit=1,battle_bound=30000,visual_bound=36000,hard_process_file_limit_bytes=FILE_CAP)
        assert identity['ROM_SHA256']==('ae1e9d36a94ed2eaa9d8fc79d790a2dc47173b932551891d889c657e12ca8461' if case=='baseline' else json.loads((build/'result.json').read_text())['actual_outputs']['pokeemerald.gba'])
        write(out/'identity.json',identity);cases[case]=sha(out/'identity.json')
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    tool_records=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009')
    tooling={n:sha(tool_records/n) for n in ['agbcc-identity.json','libmgba-identity.json','readiness.json']}
    write(OUTPUT/'freeze.json',dict(contract='NEW INPUT visual pair, not historical oracle/legacy acceptance',preparation_source=git('rev-parse','HEAD'),cases=cases,dependencies_SHA256=dependencies,tool_records_SHA256=tooling,original_Save= str(SEED),original_Save_SHA256=SAVE_SHA,policy='fortify',output=str(OUTPUT),pair_storage_required_bytes=pair_budget,available_at_freeze_bytes=available,first_failure_terminal=True,historical_executions=[6,4],ordinary_recovery_processes=5,new_execution_limits=[1,1],private_retention='Local only; no verified independent backup; no Library attempt'))
    print('PASS new-input pair frozen; zero emulator invocations')

def execute(case):
    inputs();assert not (OUTPUT/'STOP.json').exists(),'First actual failure is terminal'
    freeze=json.loads((OUTPUT/'freeze.json').read_text());out=prepared(case)
    assert sha(out/'identity.json')==freeze['cases'][case]
    for name,digest in freeze['dependencies_SHA256'].items():assert sha(ROOT/name)==digest,name
    identity=json.loads((out/'identity.json').read_text())
    for name,digest in identity['files_SHA256'].items():assert sha(out/name)==digest,name
    build=MAIN_BUILD if case=='baseline' else OUTPUT/'candidate-build';engine=build/'source/engine'
    assert sha(engine/'pokeemerald.gba')==identity['ROM_SHA256'] and sha(engine/'pokeemerald.elf')==identity['ELF_SHA256']
    if case=='candidate':
        before=prepared('baseline');summary=json.loads((before/'summary.json').read_text());assert summary['PASS']
        verifier=module('new_pair_reference',ROOT/'scripts/floor1/v01-new-input-reference.py')
        reference=before/'native-boundary-trace.bin';assert verifier.scan(reference)==summary['complete_reference'] and sha(reference)==summary['reference_SHA256']
        target=out/'expected-native-boundary-trace.bin';assert not target.exists();shutil.copyfile(reference,target);assert sha(target)==sha(reference)
    binding=module('new_execution_storage',ROOT/'scripts/floor1/v01-retained-reference.py');binding.preflight(identity['storage_bound'],out)
    save=out/'ordinary.sav';assert not save.exists();shutil.copyfile(SEED,save);assert sha(save)==SAVE_SHA
    claim=dict(identity,execution_source=git('rev-parse','HEAD'),freeze_SHA256=sha(OUTPUT/'freeze.json'))
    if case=='candidate':claim['new_reference_SHA256']=sha(out/'expected-native-boundary-trace.bin')
    with (out/'execution-claim.json').open('x') as f:json.dump(claim,f,indent=2)
    with (out/'input.route').open() as inp,(out/'replay.log').open('x') as log,(out/'errors.log').open('x') as err:
        run=subprocess.run([str(out/'observer-compile-only'),str(engine/'pokeemerald.gba'),str(save),str(out/'game.sym')],cwd=out,stdin=inp,stdout=log,stderr=err,preexec_fn=limits)
    log=(out/'replay.log').read_text();footer=re.search(r'result=(\d+) assertions=(\d+)\n$',log)
    summary=dict(case=case,execution_source=claim['execution_source'],native_exit=run.returncode,errors_bytes=(out/'errors.log').stat().st_size,assertions=int(footer[2]) if footer else None,original_Save_SHA256=sha(SEED),copy_Save_SHA256=sha(save),visual=re.findall(r'BV_FINISH .*',log),peaks=re.findall(r'BV_PEAK .*',log),warning=re.findall(r'BV_WARNING .*',log),battles=re.findall(r'WARDEN .*',log),vitals=re.findall(r'VITALS .*',log),pilot=re.findall(r'pilot completed .*',log),native_readiness=re.findall(r'BV_READY .*',log),pose_events=len(re.findall(r'BV_POSE .*',log)),ordinary_controls_SHA256=hashlib.sha256('\n'.join(re.findall(r'pilot frame=.*',log)).encode()).hexdigest(),replay_SHA256=sha(out/'replay.log'),PASS=False)
    try:
        assert run.returncode==0 and summary['errors_bytes']==0 and footer and int(footer[1])==0
        assert len(summary['visual'])==len(summary['peaks'])==1 and summary['native_readiness']
        assert summary['original_Save_SHA256']==summary['copy_Save_SHA256']==SAVE_SHA
        parser=module('complete_new_reference',ROOT/'scripts/floor1/v01-new-input-reference.py')
        reference=out/('native-boundary-trace.bin' if case=='baseline' else 'expected-native-boundary-trace.bin')
        summary['complete_reference']=parser.scan(reference);summary['reference_SHA256']=sha(reference)
        fmt=module('storage_format',ROOT/'scripts/floor1/v01-timeline-storage-format.py')
        with (out/'native-timeline-summary-private.bin').open('rb') as f:records=list(fmt.summaries(f))
        assert records and records[-1][0][4]&1 and not records[-1][0][3]
        summary['timeline_summary_count']=len(records)
        if case=='candidate':
            before=json.loads((prepared('baseline')/'summary.json').read_text())
            for field in ['peaks','battles','vitals','pilot','ordinary_controls_SHA256','complete_reference','reference_SHA256']:assert summary[field]==before[field],field
        summary['PASS']=True
    except Exception as error:
        summary['validation_failure']=str(error)
        write(OUTPUT/'STOP.json',dict(case=case,summary=summary,first_failure_terminal=True))
    write(out/'summary.json',summary);print(json.dumps(summary))
    if not summary['PASS']:raise SystemExit('STOP first actual failure; no further execution')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','execute']);p.add_argument('--case',choices=['baseline','candidate']);args=p.parse_args()
    if args.action=='prepare':prepare()
    else:assert args.case;execute(args.case)
