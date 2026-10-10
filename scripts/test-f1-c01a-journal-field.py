"""One separately counted conditional field probe; terminal first failure."""
from pathlib import Path
import importlib.util,json,os,resource,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-journal-field-r1-20261010')
BATTLE=Path('/workspace/scratch/c01a-journal-admission-r3-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sha=module('fieldRunHash',ROOT/'scripts/floor1/c01a-complete-artifacts.py').sha
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def run():
    assert not (OUT/'STOP.json').exists() and not (BATTLE/'STOP.json').exists()
    freeze=json.loads((OUT/'freeze.json').read_text());case=OUT/'field-probe'
    assert sha(BATTLE/'battle-PASS.json')==freeze['battle_PASS_SHA256']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==freeze['helper_commit']
    for n,h in freeze['dependencies'].items():assert sha(ROOT/n)==h,n
    for n,h in freeze['tool_files'].items():assert sha(n)==h,n
    for n,h in freeze['files_SHA256'].items():assert sha(case/n)==h,n
    assert sha(freeze['ROM'])==freeze['ROM_SHA256'] and sha(Path(freeze['ROM']).with_suffix('.elf'))==freeze['ELF_SHA256']
    assert sha(freeze['Save_path'])==sha(case/'game.sav')==freeze['Save_SHA256']
    module('fieldRunExec',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',freeze['observer_admission'])
    assert sha(OUT/'observer.c')==freeze['observer_source_SHA256']
    claim=dict(freeze['claim'],execution_commit=head,freeze_SHA256=sha(OUT/'freeze.json'),UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),no_retry=True)
    with (case/'exclusive-claim.json').open('x') as f:json.dump(claim,f,indent=2);f.write('\n')
    def limit():resource.setrlimit(resource.RLIMIT_FSIZE,(freeze['storage']['file_hard_max'],freeze['storage']['file_hard_max']))
    try:
        env=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
        with (case/'input.route').open('rb') as route,(case/'runtime.log').open('xb') as log:
            process=subprocess.Popen([str(OUT/'observer'),freeze['ROM'],str(case/'game.sav'),str(case/'game.sym')],cwd=case,env=env,stdin=route,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limit)
            write(case/'process-started.json',{'pid':process.pid,'overall_actual_process':9,'field_attempt':1,'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            size=0
            while chunk:=process.stdout.read(65536):
                size+=len(chunk)
                if size>freeze['storage']['logs_max_bytes']:process.kill();process.wait();raise RuntimeError('Field log cap')
                log.write(chunk)
            exitcode=process.wait()
        assert exitcode==0,exitcode
        assert sha(case/'game.sav')==sha(freeze['Save_path'])==freeze['Save_SHA256']
        assert (case/'field-start-state.bin').read_bytes()==(case/'field-end-state.bin').read_bytes()
        packet=(case/'field-end-state.bin').read_bytes()
        decoder=module('fieldNativePartyDecode',ROOT/'scripts/floor1/party-fields.py')
        decoded=[decoder.decode(packet[100*i:100*i+100]) for i in range(6)]
        assert all(p['checksum_valid'] and p['reencoding_exact'] for p in decoded)
        duo=[p['fields'] for p in decoded[:2]]
        assert [p['level'] for p in duo]==[11,10] and [p['experience'] for p in duo]==[748,1058]
        assert [p['hp_maxhp_attack_defense_speed_spatk_spdef'][0] for p in duo]==[38,30]
        assert [p['status'] for p in duo]==[0,0] and [p['PP'][:2] for p in duo]==[[8,40],[2,40]]
        write(case/'decoded-party-private.json',{'all_six_checksums_valid':True,'decoded_fields':[p['fields'] for p in decoded]})
        log=(case/'runtime.log').read_text();lines=log.splitlines();assert lines[-1].startswith('result=0 assertions=')
        assert lines.count('PASS JF native-yesno-ready')==4 and lines.count('PASS JF native-start-ready cursor=4')==4
        assert lines.count('PASS JF native-answer=1')==2 and lines.count('PASS JF native-answer=0')==2
        assert lines.count('PASS ready')==5
        frames=sorted(case.glob('field-[0-9]*.ppm'));assert 0<len(frames)<=18000 and [p.name for p in frames]==[f'field-{i:05d}.ppm' for i in range(len(frames))]
        pages={label:sorted(case.glob(label+'-*.ppm')) for label in ('yes-objective','no-objective','b-objective','repeat-objective','yes-notes','repeat-notes')}
        assert len(pages['yes-notes'])==len(pages['repeat-notes'])==4
        assert len(pages['yes-objective'])==len(pages['no-objective'])==len(pages['b-objective'])==len(pages['repeat-objective'])
        for p in frames+[p for items in pages.values() for p in items]:assert p.read_bytes().startswith(b'P6\n240 160\n255\n') and p.stat().st_size==115215
        result=dict(PASS=True,exit=exitcode,actual_emulator_process=9,field_attempt=1,consumed_claim=10,source=freeze['source'],helper_commit=head,ROM_SHA256=freeze['ROM_SHA256'],ELF_SHA256=freeze['ELF_SHA256'],Save_unchanged=True,full_private_state_packet_unchanged=True,packet_bytes=(case/'field-start-state.bin').stat().st_size,packet_regions=freeze['packet_regions'],visual_frames=len(frames),native_pages={k:[p.name for p in v] for k,v in pages.items()},native_controls_returned_after_each=True,Yes_No_B_reopen_reread_passed=True,no_battle_or_Save_command=True,first_failure_stop=True,assertions=int(lines[-1].split('assertions=')[1]),runtime_log_SHA256=sha(case/'runtime.log'),capture_SHA256={p.name:sha(p) for p in case.glob('*.ppm')})
        write(OUT/'field-PASS.json',result);print('PASS one field-only Journal probe: Yes/No/B/reopen/pages/native closure; full state/Save unchanged')
    except Exception as e:
        write(OUT/'STOP.json',{'phase':'Conditional field-only Journal probe','failure':repr(e),'no_retry':True,'first_failure_stop':True,'consumed_claim':10});raise
if __name__=='__main__':run()
