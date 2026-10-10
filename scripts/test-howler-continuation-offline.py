#!/usr/bin/env python3
"""Complete separately named offline aggregate. Never initialize an emulator."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,itertools,json,os,shutil,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='65bc4073d140b9d58bf1b83bd33235e28c972b23'
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reject(fn):
    try:fn()
    except AssertionError:return
    raise AssertionError('offline invalid fixture accepted')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',required=True,type=Path);args=parser.parse_args()
    d=args.artifacts;d.mkdir() # Exclusive OFFLINE directory, never a runtime claim.
    runner=module('howler_common',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
    host=module('howler_host',ROOT/'scripts/floor1/howler-continuation-host.py')
    route=module('howler_route',ROOT/'scripts/floor1/howler-continuation-route.py')
    state=module('howler_state',ROOT/'scripts/floor1/howler-continuation-state.py')
    audit=module('howler_audit',ROOT/'scripts/floor1/howler-continuation-audit.py')
    extra=module('howler_pack',ROOT/'scripts/floor1/guard-choice-offline.py')
    source_status=git('status','--porcelain');tested=git('rev-parse','HEAD')
    assert git('merge-base',BASE,tested)==BASE
    operands={p:sha(p) for p in (state.IMMUTABLE/'game.sav',state.IMMUTABLE/'phase-09-state.bin')}
    original,_=state.old.original(state.IMMUTABLE/'game.sav',state.IMMUTABLE/'phase-09-state.bin')
    shutil.copyfile(state.IMMUTABLE/'game.sav',d/'howler-input-verified-copy.sav')
    assert sha(d/'howler-input-verified-copy.sav')==state.old.SAVE_SHA
    derived=state.old.expected(original) # Synthetic offline expectation, no game RAM writes.
    code,inherited=host.generate(git);plans=route.routes()
    assert code.count('->runFrame(')==code.count('core->reset(')==1
    assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    assert 'co.attempts!=0' in code and 'phaseSeq!=4||co.attempts!=1' in code
    assert 'if(co.newSeen)co_stop(88' in code
    assert 'cm!=36&&cm!=38' in code and 'dm!=28&&dm!=30' in code
    assert 'money!=initial+360' in code and 'gc.uses>=1' in code
    assert 'species[]={66,370,52,288}' in code and 'if(s->savedCount!=2)return 81' in code
    assert [x[10:] for x in plans['howler-continuation'].splitlines() if x.startswith('phase end ')]==host.NAMES
    assert plans['howler-continuation'].count('pilot donut-heal 36000')==1
    assert plans['howler-continuation'].count('co overwrite-ready')==1
    assert not any(x in plans['howler-continuation'] for x in ('phase begin trial','phase begin guard','phase begin boss','phase begin stairs','newgame'))
    for name,text in plans.items():assert text==(ROOT/f'scripts/contracts/f1-c01-{name}.route').read_text()
    final_budget=route.budget(plans['howler-continuation']);assert final_budget['total']==70625
    assert final_budget['total']<=72000
    text=(ROOT/'engine/data/text/save.inc').read_text().split('gText_AlreadySavedFile::')[1].split('gText_SavingDontTurnOff::')[0]
    assert '\\n' in text and '\\p' not in text and 'Is it okay to overwrite it?' in text
    save=(ROOT/'engine/src/start_menu.c').read_text()
    for token in ('ShowSaveMessage(gText_AlreadySavedFile, SaveConfirmOverwriteCallback);','sSaveDialogCallback = SaveOverwriteInputCallback;','sSaveDialogCallback = SaveSavingMessageCallback;','TrySavingData(SAVE_NORMAL)'):
        assert token in save
    source_audit=audit.audit();rewards=extra.source_rewards();assert rewards['howler']==dict(XP=121,EV=[1,0,0,1,0,0],money=360)
    (d/'observer.c').write_text(code)
    command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(runner.TOOL/'usr/include')]
    link=['-L'+str(runner.TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba']
    subprocess.run(command+[str(d/'observer.c'),*link,'-o',str(d/'observer')],check=True)
    # Production CLI negatives finish before find/init/load/reset. No valid-mode
    # invocation occurs, and no ROM operand is provided to a core.
    production_negatives=0
    for argv in ([],['absent.rom','absent.sav','absent.sym','opening'],['absent.rom','absent.sav','absent.sym','cold'],['--execute']):
        p=subprocess.run([str(d/'observer'),*argv],cwd=d,env=runner.ENV,capture_output=True)
        assert p.returncode==2 and b'mGBA ' not in p.stdout;production_negatives+=1
    (d/'inert-observer.c').write_text(code.replace('int main(int argc','int continuous_host_main(int argc'))
    proof=module('howler_tx_proof',ROOT/'scripts/floor1/medicine-transaction-proof.py')
    actual=json.loads((proof.OUT/'transaction-proof-private.json').read_text());assert actual['PASS'] and actual['ELF_SHA256']==runner.ELF_SHA
    arrays=''
    for name,key in (('txMemcpyOpcodes','copy_instruction_bytes'),('txUpdateOpcodes','update_instruction_bytes'),('txFreeOpcodes','free_instruction_bytes'),('txFreeInternalOpcodes','freeInternal_instruction_bytes')):
        raw=bytes.fromhex(actual[key]);arrays+='static const unsigned '+name+'[]={'+','.join(hex(v) for v in struct.unpack('<'+'H'*(len(raw)//2),raw))+'};\n'
    arrays+='static const unsigned txNativeParty='+hex(actual['objects']['party']['address'])+'u;\n'
    (d/'fixtures.h').write_text(arrays+(ROOT/'scripts/floor1/medicine-transaction-fixtures.h').read_text()+'\n'+(ROOT/'scripts/floor1/medicine-transaction-update-fixtures.h').read_text())
    adapter=module('howler_inert',ROOT/'scripts/floor1/howler-continuation-inert.py')
    (d/'inert.c').write_text(adapter.generate(d/'inert-observer.c',d/'fixtures.h'))
    subprocess.run(command+['-fsanitize=undefined',str(d/'inert.c'),*link,'-o',str(d/'inert')],check=True)
    def sync(s):
        s=dict(s);s['owned']=state.prior.resources.canonical(s['logical'],struct.pack('<I',s['context']))
        p=d/'synthetic-offline-state.bin';p.write_bytes(extra.pack(s));return state.snapshot(p)
    fixture=sync(dict(derived,context=0));(d/'fixture.bin').write_bytes(extra.pack(fixture))
    for option in ('--foes','--medicine'):
        with (d/(option[2:]+'.log')).open('w') as log:
            subprocess.run([str(d/'inert'),option],cwd=d,env=runner.ENV,stdout=log,stderr=subprocess.STDOUT,check=True)
        print((d/(option[2:]+'.log')).read_text()[-1800:],end='')
    vectors=list(itertools.product(range(39),(36,38),range(31),(28,30),(0,1),(0,1),(0,1),(0,1,8),(0,40)))
    (d/'choices.txt').write_text(''.join(' '.join(map(str,v))+'\n' for v in vectors))
    native=list(map(int,subprocess.check_output([str(d/'inert'),'--choices',str(d/'choices.txt')],env=runner.ENV,text=True).splitlines()))
    assert native==[audit.choice(*v) for v in vectors]
    counts={'complete_stationary_handoffs':0,'physical_walk_steps':0,'phase_negative_cases':0,'cold_byte_negatives':0,'disk_sector_negatives':0}
    def native_transition(a,b,kind,allow=False):
        (d/'before.bin').write_bytes(extra.pack(a));(d/'after.bin').write_bytes(extra.pack(b))
        p=subprocess.run([str(d/'inert'),'--transition',str(d/'before.bin'),str(d/'after.bin'),str(kind)],cwd=d,env=runner.ENV,capture_output=True)
        if not allow:assert p.returncode==0,(kind,p.stdout,p.stderr)
        return p.returncode
    def mutate_member(s,i,fn):
        raw=s['party'][100*i:100*(i+1)];c=bytearray(state.fields.decode(raw)['canonical']);fn(c)
        p=bytearray(s['party']);p[100*i:100*(i+1)]=state.prior.encode(c,raw);s['party']=bytes(p)
    def walk(s,mapnum,pos,facing):
        t=copy.deepcopy(s);t['counter']+=1;t['map']=[35,mapnum];t['position']=pos;t['facing']=facing
        sections=json.loads((ROOT/'engine/src/data/region_map/region_map_sections.json').read_text())['map_sections'];model=json.loads((ROOT/f'engine/data/maps/DCC_F1D1{("Field" if mapnum==0 else "Quiet")}/map.json').read_text())
        t['section']=next(i for i,x in enumerate(sections) if x['id']==model['region_map_section'])
        variables=bytearray(t['vars']);struct.pack_into('<H',variables,0x54,t['counter']);struct.pack_into('<H',variables,0x56,(struct.unpack_from('<H',variables,0x56)[0]+1)%4)
        if s['map']!=t['map']:struct.pack_into('<H',variables,2,0)
        t['vars']=bytes(variables);t=sync(t);native_transition(s,t,1)
        if mapnum==0 and struct.unpack_from('<H',t['vars'],2)[0]==0:
            v=bytearray(t['vars']);struct.pack_into('<H',v,2,1);u=sync(dict(t,vars=bytes(v)));native_transition(t,u,1);t=u
        counts['physical_walk_steps']+=1;return t
    state.continue_equivalence(fixture,d/'howler-input-verified-copy.sav')
    s=fixture
    for pos,mapnum,facing in [([4,4],1,2),([37,26],0,2)]+[([x,26],0,4) for x in range(38,52)]+[([51,27],0,1)]:s=walk(s,mapnum,pos,facing)
    assert s['counter']==95
    phase_pairs=[];before=s;after=copy.deepcopy(before)
    for i in range(2):
        def earned(c):
            reward=rewards['howler'];xp=struct.unpack_from('<I',c,36)[0]+reward['XP'];struct.pack_into('<I',c,36,xp)
            for j,v in enumerate(reward['EV']):c[56+j]+=v
            level=c[84]+1;c[41]=state.friendship.level_ups(c[41],levels=1,met_location=c[69],section=after['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=0,pokerus=c[68]);c[84]=level
            stats=state.prior.level_stats(c,level);struct.pack_into('<7H',c,86,stats[0]-3,*stats);c[52:54]=bytes((2,40) if i==0 else (0,37))
        mutate_member(after,i,earned)
    flags=bytearray(after['flags']);flags[2137//8]|=1<<(2137%8);after['flags']=bytes(flags)
    logical=bytearray(after['logical']);struct.pack_into('<I',logical,0,4000);after['logical']=bytes(logical)
    variables=bytearray(after['vars']);struct.pack_into('<H',variables,0x56,0);after['vars']=bytes(variables);after=sync(after)
    state.validate('howler',before,after);native_transition(before,after,9);phase_pairs.append(('howler',before,after,9));s=after
    # Independently exercise the same source-native medicine/Thumb/IRQ closure
    # after source-derived growth to38/30, while retaining the original saved
    # party, trainer flag and unrewarded money. Synthetic offline state only.
    grown=sync(dict(before,party=after['party']))
    (d/'fixture.bin').write_bytes(extra.pack(grown))
    with (d/'medicine-grown.log').open('w') as log:
        subprocess.run([str(d/'inert'),'--medicine'],cwd=d,env=runner.ENV,stdout=log,stderr=subprocess.STDOUT,check=True)
    (d/'fixture.bin').write_bytes(extra.pack(fixture))
    # Immediate repeat: full state exact, including once-only XP/money/flags.
    state.validate('howler-repeat',s,s);native_transition(s,s,1);phase_pairs.append(('howler-repeat',s,s,1))
    for pos,mapnum,facing in [([51,26],0,2)]+[([x,26],0,3) for x in range(50,37,-1)]+[([4,3],1,3),([4,4],1,1),([4,5],1,1)]:s=walk(s,mapnum,pos,facing)
    assert s['counter']==112 and counts['physical_walk_steps']==34
    before=s;after=copy.deepcopy(s)
    for i in range(2):
        def healed(c):c[52:56]=bytes((8 if i==0 else 2,40,0,0));struct.pack_into('<I',c,80,0);c[86:88]=c[88:90]
        mutate_member(after,i,healed)
    after=sync(after);state.validate('guide-howler',before,after);native_transition(before,after,4);phase_pairs.append(('guide-howler',before,after,4));s=after
    before=s;after=sync(dict(s,saved=s['party'],saved_count=2));state.validate('save',before,after);native_transition(before,after,12);phase_pairs.append(('save',before,after,12));s=after
    for name,a,b,kind in phase_pairs:
        counts['complete_stationary_handoffs']+=1
        # Byte-complete stable/repeat/guide/Save checks. Combat HP and PP are
        # actual variable fields: alter protected regions plus checksum/header,
        # flags/rewards/native growth; no claim that allowed combat HP is fixed.
        offsets=range(3324) if name!='howler' else itertools.chain(range(200,3324),range(0,28),range(100,128))
        for off in offsets:
            raw=bytearray(extra.pack(b));raw[off]^=1;p=d/'negative.bin';p.write_bytes(raw)
            reject(lambda:state.validate(name,a,state.snapshot(p)))
            counts['phase_negative_cases']+=1
        assert b['saved']==(b['party'] if name=='save' else a['saved'])
        print('PASS source-derived complete phase/byte fixtures '+name,flush=True)
    # A Potion path derives the exact native removal, including Bag compaction
    # and the preferred slot. UI/transaction stages above use production C.
    a=phase_pairs[0][1];b=phase_pairs[0][2];logical=state.medicine.remove(state.medicine.compact(a['logical']),position=0)
    logical=bytearray(logical);struct.pack_into('<I',logical,0,4000);medicated=sync(dict(b,logical=bytes(logical)))
    state.validate('howler',a,medicated,(0,));reject(lambda:state.validate('howler',a,medicated,()))
    # Synthetic native-format fourteen-sector positive/negative fixture. This
    # file is explicitly NOT a gameplay Save or new runtime identity.
    raw=bytearray((d/'howler-input-verified-copy.sav').read_bytes());selected={};latest=max(struct.unpack_from('<I',raw,i*4096+0xffc)[0] for i in range(28) if struct.unpack_from('<I',raw,i*4096+0xff8)[0]==0x08012025)
    for i in range(28):
        sid,_,sig,count=struct.unpack_from('<HHII',raw,i*4096+0xff4)
        if sig==0x08012025 and count==latest and sid<14:selected[sid]=i
    sb=bytearray(b''.join(raw[selected[j+1]*4096:selected[j+1]*4096+min(3968,0x3d88-j*3968)] for j in range(4)))
    sb[0:4]=struct.pack('<hh',4,5);sb[4:6]=bytes((35,1));struct.pack_into('<I',sb,0x234,2);sb[0x238:0x490]=s['party'];sb[0x1270:0x139c]=s['flags'];sb[0x139c:0x159c]=s['vars']
    key=raw[selected[0]*4096+0xac:selected[0]*4096+0xb0];sb[0x490:0x988]=state.prior.resources.canonical(s['logical'],key)
    for j in range(4):
        n=min(3968,len(sb)-j*3968);raw[selected[j+1]*4096:selected[j+1]*4096+n]=sb[j*3968:j*3968+n]
    # Native save-sector checksum sizes, independently consumed by saved_party.
    sizes=[0xf2c]+[min(3968,0x3d88-i*3968) for i in range(4)]+[min(3968,0x83d0-i*3968) for i in range(9)]
    for sid,i in selected.items():
        values=struct.unpack('<'+'I'*(sizes[sid]//4),raw[i*4096:i*4096+sizes[sid]]);total=sum(values)&0xffffffff
        struct.pack_into('<H',raw,i*4096+0xff6,((total&65535)+(total>>16))&65535)
    fake=d/'SYNTHETIC-OFFLINE-NOT-GAMEPLAY-SAVE.sav';fake.write_bytes(raw);state.disk_equivalence(fake,s);state.cold_equivalence(s,s,fake)
    for sid,i in selected.items():
        bad=bytearray(raw);bad[i*4096]^=1;(d/'bad-sector.sav').write_bytes(bad);reject(lambda:state.disk_equivalence(d/'bad-sector.sav',s));counts['disk_sector_negatives']+=1
    for off in range(3324):
        bad=bytearray(extra.pack(s));bad[off]^=1;(d/'negative.bin').write_bytes(bad)
        reject(lambda:state.cold_equivalence(s,state.snapshot(d/'negative.bin'),fake));counts['cold_byte_negatives']+=1
    for key in ('flags','party','saved','logical','vars'):
        bad=bytearray(s[key]);bad[0]^=1;reject(lambda:state.same(s,dict(s,**{key:bytes(bad)})))
    binding=runner.binding_table(code,d);assert binding['SaveOverwriteInputCallback']['function_identity']=='L:start_menu.o:SaveOverwriteInputCallback'
    assert binding['gDifferentSaveFile']['size']==1
    abi=runner.abi(d);game=runner.verify_game()
    tool_pins=json.loads(Path('/workspace/scratch/c01a-journal-admission-r3-20261010/freeze.json').read_text())['tool_files']
    for p,h in tool_pins.items():assert runner.sha(p)==h
    checker=module('howler_exec_gate',ROOT/'scripts/floor1/c01a-prefix-execfile.py');os.chmod(d/'observer',0o700);st=(d/'observer').stat()
    identity=dict(SHA256=sha(d/'observer'),owner_uid=st.st_uid,mode=0o700,device=st.st_dev,inode=st.st_ino);checker.verify_executable(d/'observer',identity)
    for k,v in [('SHA256','0'*64),('owner_uid',st.st_uid+1),('mode',0o755),('inode',st.st_ino+1)]:reject(lambda:checker.verify_executable(d/'observer',dict(identity,**{k:v})))
    (d/'observer-symlink').symlink_to(d/'observer');reject(lambda:checker.verify_executable(d/'observer-symlink',identity))
    assert all(sha(p)==h for p,h in operands.items())
    admission=module('howler_hash_admission',ROOT/'scripts/floor1/howler-continuation-admission.py')
    dependency_paths=sorted({str(p) for p in (ROOT/'scripts/floor1').glob('howler-continuation-*')}|{str(ROOT/'scripts/test-howler-continuation-offline.py'),str(ROOT/'docs/floor1/c01-howler-continuation-offline-contract.md')}|{str(ROOT/f'scripts/contracts/f1-c01-{name}.route') for name in plans})
    dependency_pins={p:admission.digest(p) for p in dependency_paths};admission.verify(dependency_pins,dependency_paths)
    for missing in dependency_paths:reject(lambda:admission.verify({p:h for p,h in dependency_pins.items() if p!=missing},dependency_paths))
    fake_dependency=d/'hash-gate-fixture.bin';fake_dependency.write_bytes(b'offline-only-source');pins={str(fake_dependency):admission.digest(fake_dependency)}
    fake_dependency.write_bytes(b'changed-source');reject(lambda:admission.verify(pins,[fake_dependency]))
    (d/'hash-gate-symlink').symlink_to(fake_dependency);reject(lambda:admission.digest(d/'hash-gate-symlink'))
    for action in ('prepare','freeze','claim','execute','Save','cold'):
        try:admission.runtime_action(action)
        except RuntimeError as e:assert 'CLOSED' in str(e)
        else:raise AssertionError('runtime action admitted')
    used=sum(p.stat().st_size for p in d.rglob('*') if p.is_file() and not p.is_symlink());assert used<=256*1024**2
    storage=runner.storage();reservation=runner.reservation();free=shutil.disk_usage(d).free
    captures={name:[x.split()[3] for x in text.splitlines() if x.startswith('step ') and x.split()[3]!='-'] for name,text in plans.items()}
    receipt=dict(PASS=True,offline_only=True,runtime_review='CLOSED',gameplay_processes=0,base_commit=BASE,tested_source_commit=tested,source_status_at_start=source_status,
        generated_C_SHA256=sha(d/'observer.c'),observer_SHA256=sha(d/'observer'),inherited_generated_source_SHA256=inherited,
        Guard_Save_SHA256=state.old.SAVE_SHA,original_operands_unchanged=True,verified_copy_SHA256=sha(d/'howler-input-verified-copy.sav'),
        native_ABI=abi,binding_count=len(binding),build_verification=game,tool_pin_count=len(tool_pins),source_audit=source_audit,
        policy_vectors=len(vectors),stateful_flow=counts,native_foes_and_Save_log_SHA256=sha(d/'foes.log'),native_transaction_log_SHA256=sha(d/'medicine.log'),native_grown_transaction_log_SHA256=sha(d/'medicine-grown.log'),native_single_stock_medicine_cases=8,
        production_preinit_negatives=production_negatives,executable_hash_gate_negatives=5,dependency_hash_gate_negatives=len(dependency_paths)+2,dependency_pins=dependency_pins,runtime_actions_rejected=6,whole_route_budget=final_budget,capture_ledger=captures,
        storage=storage,reservation_bytes=reservation,available_bytes=free,runtime_storage_admitted=free>=reservation,shortfall_bytes=max(0,reservation-free),
        offline_output_bytes=used,independent_private_backup='unapproved/unverified',
        artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and not p.is_symlink()})
    (d/'offline-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps({k:receipt[k] for k in ('PASS','tested_source_commit','stateful_flow','policy_vectors','reservation_bytes','available_bytes','runtime_storage_admitted')},sort_keys=True))
if __name__=='__main__':main()
