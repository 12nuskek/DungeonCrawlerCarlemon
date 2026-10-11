#!/usr/bin/env python3
"""One bounded offline state/ownership audit. No runtime or timing assumption."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,re,resource,signal,struct,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def proof(config,out):
    assert __debug__ and not out.exists();out.mkdir()
    receipt=dict(PASS=False,scope='OFFLINE native state reachability audit and real outer failure closure',emulators=0,runtime_admission=False)
    try:
        def timeout(signum,frame):raise TimeoutError('native state proof exceeded240seconds')
        signal.signal(signal.SIGALRM,timeout);signal.alarm(240)
        resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        assert head==config['source_commit'] and not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
        for section in ('files','protected_history'):
            for p,h in config[section].items():assert sha(p)==h,(section,p)
        old=json.loads(Path(config['dialogue_proof']).read_text());assert old['PASS']
        prior=json.loads(Path(config['accepted_offline_receipt']).read_text());assert prior['PASS']
        observer=Path(config['observer_source']).read_text();assert sha(config['observer_source'])==old['observer_source_SHA256']
        helpers=module('native_state_helpers',ROOT/'scripts/floor1/warden-dialogue-proof.py')
        symbols=module('native_state_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py')
        boundary=module('native_state_bytes',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
        elf=Path(config['ELF']);rom=Path(config['ROM']).read_bytes();rows=symbols.elf_symbols(elf)
        assert sha(elf)==old['ELF_SHA256'] and sha(config['ROM'])==old['ROM_SHA256']
        def row(name):
            found=[r for r in rows if r['name']==name and r['index']];assert len(found)==1,name;return found[0]
        def addr(name):return row(name)['value']
        def exact_bytes(a,n):
            b=boundary.rom_bytes(elf,a,n);assert rom[a-0x08000000:a-0x08000000+n]==b;return b
        relatives=['src/text.c','src/string_util.c','src/menu.c','src/field_message_box.c','src/scrcmd.c','src/script.c','src/script_menu.c','src/overworld.c','src/main.c','src/task.c','include/text.h','include/script.h','include/constants/characters.h','include/constants/battle.h']
        compiled_sources={}
        for rel in relatives:
            p=ROOT/'engine'/rel;q=elf.parent/rel;assert p.read_bytes()==q.read_bytes(),('compiled source',rel);compiled_sources[rel]=sha(p)
        names=list(old['native_functions'])+['StringExpandPlaceholders','AddTextPrinterParameterized2','ExpandStringAndStartDrawFieldMessage','RenderFont','FontFunc_Normal','TextPrinterInitDownArrowCounters','HideFieldMessageBox','StopFieldMessage','SetDefaultFontsPointer','SetFontsPointer','RunScriptCommand','CallCallbacks','UpdateLinkAndCallCallbacks','WaitForVBlank','SetMainCallback2','SetupNativeScript','DestroyTask']
        bindings={}
        for name in names:
            r=row(name);assert r['type']==2 and r['size'];a=r['value']&~1;b=exact_bytes(a,r['size'])
            if name in old['native_functions']:assert hashlib.sha256(b).hexdigest()==old['native_functions'][name]['SHA256']
            bindings[name]=dict(address=a,size=len(b),SHA256=hashlib.sha256(b).hexdigest(),bytes=b.hex())
        env=dict(os.environ,LD_LIBRARY_PATH=str(Path(config['tool_root'])/'usr/lib/x86_64-linux-gnu'))
        with (out/'native-disassembly.txt').open('w') as log:
            for name in names:subprocess.run([config['objdump'],'-d','--disassemble='+name,str(elf)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,env=env)
        # Exact tested machine-code tables and constructor publication ordering.
        a=addr('AddTextPrinter')&~1
        assert exact_bytes(a+0x22,4)==bytes.fromhex('c1760277') # temp active=1, state=0
        assert exact_bytes(a+0x84,12)==bytes.fromhex('1cc81cc18cc88cc194c894c1')
        assert struct.unpack('<II',exact_bytes(a+0x94,8))==(addr('sTempTextPrinter'),addr('sTextPrinters'))
        r=addr('RenderText')&~1
        state_table=struct.unpack('<7I',exact_bytes(r+0x20,28))
        char_table=struct.unpack('<8I',exact_bytes(r+0xe4,32))
        assert char_table[2:4]==(r+0x398,r+0x394) # FA scroll=3; FB clear=2
        assert exact_bytes(r+0x394,8)==bytes.fromhex('022000e003203077')
        assert row('sTempTextPrinter')['size']==36 and row('sTextPrinters')['size']==32*36
        normal_font=struct.unpack('<I',exact_bytes(addr('sFontInfos')+12,4))[0];assert normal_font==addr('FontFunc_Normal')
        machine=dict(temp_active_state_writes=a+0x22,publication_instructions=[a+0x86,a+0x8a,a+0x8e],publication_byte_ranges=[[0,12],[12,24],[24,36]],pointer_offset=0,callback_offset=16,active_offset=27,state_offset=28,constructor_size=36,state_table=list(state_table),char_F8_FF_table=list(char_table),clear_scroll_store=r+0x39a,normal_font_pointer=normal_font)
        route=prior['route']['continuation'];lines=route.splitlines();calls=[l.split()[1:] for l in lines if l.startswith('pages ')]
        labels=[c[1] for c in calls];assert labels==['DCC_Live_Boss_Text_Won','DCC_F1D1Warden_StairsText','DCC_Boss_Text_StairsCancel','DCC_F1D1Warden_StairsText','DCC_F1D1Checkpoint_ReviewText']
        text_proofs={};data=''
        for i,label in enumerate(labels):
            p=old['text_proofs'][label];b=bytes.fromhex(p['bytes']);assert exact_bytes(p['address'],len(b))==b
            assert b[-1]==255 and 255 not in b[:-1] and all(c not in b for c in (250,252,253))
            if i<4:assert 251 not in b
            else:assert b.count(251)==1
            text_proofs[label]=p;data+=f'static const unsigned char text_{i}[]={{'+','.join(map(str,b))+'};\n'
        data+='static const unsigned char*texts[5]={'+','.join('text_'+str(i) for i in range(5))+'};\n'
        data+='static unsigned lengths[5]={'+','.join(str(old['text_proofs'][n]['length']) for n in labels)+'};\n'
        data+='static const char*labels[5]={'+','.join(json.dumps(n) for n in labels)+'};\n';(out/'compiled-text.inc').write_text(data)
        (out/'fixture.sym').write_text('\n'.join(f'{0x1000+0x400*i:08x} V {n}' for i,n in enumerate(labels))+'\n')
        for name,p in old['compiled_script_graph'].items():assert exact_bytes(p['address'],len(bytes.fromhex(p['compiled_bytes'])))==bytes.fromhex(p['compiled_bytes'])
        text=(ROOT/'engine/src/text.c').read_text();header=(ROOT/'engine/include/text.h').read_text()
        def native(anchor):return helpers.definition(text,anchor)
        enums='\n'.join(re.findall(r'enum\n\{[^}]*\};',header)[:3]);assert 'RENDER_STATE_PAUSE' in enums
        types=enums+'\n'+helpers.definition(header,'struct TextPrinterSubStruct\n')+';\n'+helpers.definition(header,'struct TextPrinterTemplate\n')+';\n'
        types+='typedef void (*TextPrinterCallback)(struct TextPrinterTemplate *printerTemplate, u16 renderCmd);\n'+helpers.definition(header,'struct TextPrinter\n')+';\n'+helpers.definition(header,'struct FontInfo\n')+';\n'
        (out/'native-types.inc').write_text(types);(out/'characters.inc').write_bytes((ROOT/'engine/include/constants/characters.h').read_bytes())
        anchors=['static u16 FontFunc_Normal(','void TextPrinterInitDownArrowCounters(','bool8 TextPrinterWaitAutoMode(','bool16 TextPrinterWaitWithDownArrow(','bool16 TextPrinterWait(','static u16 RenderText(','static u32 RenderFont(','bool16 AddTextPrinter(','void RunTextPrinters(','bool16 IsTextPrinterActive(']
        rendered='\n'.join(native(n) for n in anchors)
        fallthrough='CopyWindowToVram(sTextPrinters[i].printerTemplate.windowId, COPYWIN_GFX);';assert rendered.count(fallthrough)==1
        rendered=rendered.replace(fallthrough,fallthrough+' /* fall through */',1);(out/'native-render.inc').write_text(rendered)
        (out/'host-types.inc').write_text('\n'.join(helpers.definition(observer,n)+';' for n in ('struct CoSnapshot ','struct CoAddresses ','struct CoGuard ')))
        host='\n'.join(helpers.definition(observer,n) for n in ('static int capture(','static void co_dump(','static void co_stop('));(out/'host-stop.inc').write_text(host)
        start=observer.index('        if (!strncmp(line,"pages ",6)) {');end=observer.index('\n        if (!strncmp(line,"wait-task ',start)
        pages=observer[start:end];assert 'attempt<32' in pages and 'frame<400' in pages
        (out/'pages-command.inc').write_text(pages)
        closure='    if(result)co_stop(result,pixels,width,height);'
        assert observer.count(closure)==1 and observer.index(closure)>end
        assert '\n    }\n\n'+closure in observer
        assert closure in (ROOT/'scripts/floor1/continuous-opening-host.py').read_text()
        (out/'outer-closure.inc').write_text(closure+'\n')
        assert observer.index('co_capture_frame(p,w,h,after);')>observer.index('c->runFrame(c);co.frames++')
        (out/'fixture.c').write_bytes((ROOT/'scripts/floor1/warden-native-dialogue-state-fixture.c').read_bytes())
        with (out/'compile.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(Path(config['tool_root'])/'usr/include'),str(out/'fixture.c'),'-o',str(out/'fixture')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        with (out/'fixture.log').open('w') as log:subprocess.run([str(out/'fixture'),str((out/'fixture.sym').resolve())],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        log=(out/'fixture.log').read_text();match=re.search(r'PASS native-state local_cases=(\d+) outer_closure_cases=17 checkpoint_failure=12832 final_frame_included=1 emulators=0',log);assert match
        assert 'PARTIAL_COPY snapshots=24 mixed_owner_pauses=4;' in log
        # Conservative result: the local transition invariant is conditional.
        # No unspecified old owner, callback or frame cut is declared unreachable.
        call_proofs=[]
        for prefix,label in calls[:4]:
            position=lines.index('pages '+prefix+' '+label);assert lines[position-1]=='step 400 0 -' and lines[position-2]=='step 1 1 -'
            call_proofs.append(dict(prefix=prefix,label=label,preceding_route=lines[max(0,position-6):position],local_invariant='Completed successful NORMAL constructor with exact expanded buffer, NULL callback and preserved ownership starts HANDLE_CHAR. Exact bytes contain no FA/FB/FC/FD. Owned HANDLE_CHAR cannot transition to CLEAR/SCROLL_START, independently of delay/key/speed.',complete_native_boundary_invariant=False,accepted_active_state_2_or_3='UNRESOLVED, not proven reachable or impossible on this route',generic_failure_allowance=12832,generic_success_allowance=12431,zero_frames_proven=False,unresolved=['gStringVar4 equality does not bind currentChar or callback; ExpandStringAndStartDrawFieldMessage writes buffer before constructor; ShowFieldMessage can return false; AddTextPrinter can return false if gFonts is NULL.','Compiled copy publishes cursor then callback in separate instructions while old active/state remain. Old inactive excludes accepted pause at instruction cuts; that old-inactive ownership precondition is not established by the host readiness checks. STM word-intermediate cuts are not assumed host-observable or atomic.','Preceding phase/dialog/ready checks bind field callbacks/lock/script status, not script PC/native waiter, field-message task or printer cursor. waitmessage is a native barrier only if the exact script reached it and completion is established; elapsed step counts do not prove that without timing.','Completed native message constructor supplies NULL callback. Prior owner callback/frame interruption and other buffer/task writers are not globally excluded by the frozen admission. No route-state speed or hardware scheduling assumption closes these obligations.']))
        base=prior['budgets']['continuation']['total'];pages_budget=prior['budgets']['continuation']['components']['pages'];assert (base,pages_budget)==(134360,64160)
        other=base-pages_budget;checkpoint=32*401;generic=other+4*31*401+checkpoint;conditional=other+checkpoint
        assert (other,checkpoint,generic,conditional)==(70200,12832,132756,83032)
        ledger=copy.deepcopy(prior['storage']);process=ledger['processes']['continuation'];process['frames']=conditional
        chunks,remainder=divmod(conditional,2000)
        for f in process['files']:
            if f['name']=='full_RGB_chunks':f['count']=chunks
            elif f['name']=='last_RGB_chunk':f.update(count=int(bool(remainder)),per_file_bytes=remainder*115200)
            elif f['name']=='frame_index':f['per_file_bytes']=conditional*16
            elif f['name']=='complete_field_trace':f['per_file_bytes']=conditional*3340
            elif f['name']=='complete_battle_trace':f['per_file_bytes']=conditional*1040
            f['allocated_bytes']=f['count']*((f['per_file_bytes']+4095)//4096)*4096
        process['bytes']=sum(f['allocated_bytes'] for f in process['files']);process['logical_bytes']=sum(f['count']*f['per_file_bytes'] for f in process['files'])
        ledger['reservation_bytes']=sum(p['bytes'] for p in ledger['processes'].values())+ledger['headroom_bytes'];assert ledger['reservation_bytes']==11555897344
        for section in ('files','protected_history'):
            for p,h in config[section].items():assert sha(p)==h,(section,p)
        total=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());assert total<64*1024**2
        receipt.update(PASS=True,source_commit=head,ROM_SHA256=sha(config['ROM']),ELF_SHA256=sha(elf),observer_source_SHA256=sha(config['observer_source']),route_SHA256=hashlib.sha256(route.encode()).hexdigest(),compiled_sources=compiled_sources,compiled_bindings=bindings,compiled_machine_state_binding=machine,text_proofs=text_proofs,call_proofs=call_proofs,local_fixture_cases=int(match[1]),partial_copy_snapshots=24,mixed_owner_pause_countermodels=4,outer_closure_fixture_cases=17,fixture_log=log,
                       corrected_terminal_conclusion='Supersedes only the mistaken isolated-fixture assertion that pages timeout lacks terminal context/capture. Retained observer exits pages loop with result41 and exact outer closure invokes real co_stop; native CPU-context writer, PPM writer and snapshot writer exercised with synthetic inputs. Final synthetic frame12832/index/RGB matches terminal PPM; page31 remains at12431. Production capture unchanged.',
                       scope_limit='Complete audit with explicit unresolved global boundary obligations. Conditional completed-constructor/owned-cursor invariant is verified; no zero-frame native route-call proof, no rendering speed claim, no fabricated runtime reachability.',
                       active_unchanged=dict(route_frames=134360,reservation_bytes=17694519296,cold_frames=2044,battle_frames=30000,helper_attempts=32),
                       arithmetic=dict(other_route_frames=other,all_other_components_unchanged=prior['budgets']['continuation']['components'],per_generic_call_success=12431,per_generic_call_failure=12832,first_failure_by_call=[i*12431+12832 for i in range(5)],four_unresolved_calls=4,checkpoint_full_failure=checkpoint,checkpoint_final_frame_included=True,conservative_total=base,generic_first_failure_total=generic,conditional_zero_four_total=conditional,conditional_antecedent_established=False,conditional_ledger=ledger,activated=False),input_pins=config['files'],protected_history=config['protected_history'],actual_output_bytes_before_receipt=total,retention='Hash-verified private local only; independent backup unverified',next='Independent private review of unresolved ownership/frame-cut obligations. No runtime contract or capacity admission.')
        write(out/'proof-receipt-private.json',receipt);signal.alarm(0)
        print(json.dumps(dict(PASS=True,source_commit=head,local_cases=int(match[1]),closure_cases=17,zero_frame_calls_proven=0,active_route_frames=134360,active_reservation_bytes=17694519296,emulators=0)))
    except BaseException as e:
        receipt.update(first_failure=type(e).__name__+': '+str(e),traceback=traceback.format_exc());write(out/'STOP-proof-private.json',receipt);raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();proof(json.loads(a.inputs.read_text()),a.out.resolve())
