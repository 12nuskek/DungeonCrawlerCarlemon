#!/usr/bin/env python3
"""Bounded offline text/script/command proof; never changes runtime admission."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,re,resource,signal,struct,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def definition(source,anchor):
    match=re.search(re.escape(anchor)+r'[^;{]*\{',source);assert match,anchor
    start=match.start();i=match.end();depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[start:i]
def proof(config,out):
    assert __debug__ and not out.exists();out.mkdir()
    receipt=dict(PASS=False,scope='OFFLINE dialogue proof only',emulator_processes=0,runtime_admission=False)
    try:
        def timeout(signum,frame):raise TimeoutError('dialogue proof exceeded240seconds')
        signal.signal(signal.SIGALRM,timeout);signal.alarm(240)
        resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        assert head==config['source_commit'] and not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
        for section in ('files','protected_history'):
            for p,h in config[section].items():assert sha(p)==h,(section,p)
        prior=json.loads(Path(config['accepted_offline_receipt']).read_text());assert prior['PASS']
        observer=Path(config['observer_source']).read_text()
        assert sha(config['observer_source'])==prior['observer_source_SHA256']
        route=prior['route']['continuation'];calls=[line.split()[1:] for line in route.splitlines() if line.startswith('pages ')]
        labels=[c[1] for c in calls]
        assert labels==['DCC_Live_Boss_Text_Won','DCC_F1D1Warden_StairsText','DCC_Boss_Text_StairsCancel','DCC_F1D1Warden_StairsText','DCC_F1D1Checkpoint_ReviewText']
        assert all(',' not in label for label in labels) and 'pilot fortify 30000\n' in route
        parser=module('dialogue_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py')
        boundary=module('dialogue_bytes',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
        elf=Path(config['ELF']);rows=parser.elf_symbols(elf)
        for rel in ('src/text.c','src/main.c','src/menu.c','src/field_message_box.c','src/scrcmd.c','src/script_menu.c','src/overworld.c','src/task.c','include/text.h','include/global.h','asm/macros/event.inc','asm/macros/map.inc','data/script_cmd_table.inc','data/specials.inc','charmap.txt'):
            assert (ROOT/'engine'/rel).read_bytes()==(elf.parent/rel).read_bytes(),('exact compiled native source',rel)
        def row(name):
            hits=[r for r in rows if r['name']==name and r['index']];assert len(hits)==1,name;return hits[0]
        def address(name):return row(name)['value']
        sources={}
        files=['data/scripts/dcc_live_navigation.inc','data/maps/DCC_F1D1Warden/scripts.inc','data/maps/DCC_Boss/scripts.inc','data/maps/DCC_F1D1Checkpoint/scripts.inc','data/scripts/std_msgbox.inc']
        for rel in files:
            text=(ROOT/'engine'/rel).read_text()
            assert (ROOT/'engine'/rel).read_bytes()==(elf.parent/rel).read_bytes(),'exact compiled source'
            matches=list(re.finditer(r'^(\w+)::?\s*$',text,re.M))
            for n,m in enumerate(matches):sources[m[1]]=(rel,text[m.end():matches[n+1].start() if n+1<len(matches) else len(text)])
        chars={m[1]:bytes.fromhex(m[2]) for m in re.finditer(r"^'([^']+)'\s*=\s*([0-9A-F]{2}(?: [0-9A-F]{2})*)",(ROOT/'engine/charmap.txt').read_text(),re.M)}
        def text_bytes(name):
            raw=''.join(re.findall(r'\.string\s+"([^\"]*)"',sources[name][1]));assert raw
            result=b'';i=0
            while i<len(raw):
                token=raw[i:i+2] if raw[i]=='\\' else raw[i];result+=chars[token];i+=len(token)
            assert result[-1]==255 and 255 not in result[:-1];return result
        text_proofs={}
        # Verify all text targets in the compiled branch graph, not just counts.
        nodes=['DCC_Live_Boss_Encounter','DCC_Live_Boss_Prepared','DCC_Live_Boss_Result','DCC_Live_Boss_Won','DCC_Live_Boss_Already','DCC_Live_Boss_Locked','DCC_F1D1Warden_Stairs','DCC_Boss_StairsLocked','DCC_Boss_StairsCancel','DCC_F1D1Checkpoint_Review','Std_MsgboxDefault','Std_MsgboxYesNo']
        text_names=set(labels)
        for node in nodes:
            text_names.update(re.findall(r'\b(?:DCC_\w+_Text_\w+|DCC_F1D1\w+Text)\b',sources[node][1]))
        for name in sorted(text_names):
            data=text_bytes(name);assert boundary.rom_bytes(elf,address(name),len(data))==data,name
            text_proofs[name]=dict(address=address(name),source=sources[name][0],bytes=data.hex(),SHA256=hashlib.sha256(data).hexdigest(),length=len(data),paragraphs=data.count(251),scrolls=data.count(250),extended_controls=data.count(252),placeholders=data.count(253))
        assert [text_proofs[n]['paragraphs'] for n in labels]==[0,0,0,0,1]
        assert all(text_proofs[n]['scrolls']==text_proofs[n]['extended_controls']==text_proofs[n]['placeholders']==0 for n in labels)
        table=(ROOT/'engine/data/script_cmd_table.inc').read_text()
        ops={n:(int(v,16),fn) for n,fn,v in re.findall(r'script_cmd_table_entry\s+(SCR_OP_\w+)\s+(\w+)\s+@ (0x[0-9a-f]+)',table)}
        used=set()
        def op(name):used.add(name);return bytes([ops['SCR_OP_'+name][0]])
        constants={}
        for rel in ('flags.h','opponents.h','vars.h'):
            constants.update({n:int(v,0) for n,v in re.findall(r'^#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|[0-9]+)\b',(ROOT/'engine/include/constants'/rel).read_text(),re.M)})
        constants.update(NO=0,YES=1)
        def value(expr):return sum(int(x.strip(),0) if x.strip().isdigit() or x.strip().startswith('0x') else constants[x.strip()] for x in expr.split('+'))
        specials=re.findall(r'^\s*def_special\s+(\w+)',(ROOT/'engine/data/specials.inc').read_text(),re.M)
        graph={}
        for name in nodes:
            data=b'';commands=[];edges=[]
            for line in sources[name][1].splitlines():
                line=line.strip()
                if not line or line.startswith('@'):continue
                cmd,*rest=line.split(None,1);args=[a.strip() for a in rest[0].split(',')] if rest else []
                commands.append(line)
                if cmd in ('end','return','lock','lockall','faceplayer','release','releaseall','waitstate','waitmessage','waitbuttonpress'):data+=op(cmd.upper())
                elif cmd in ('goto_if_set','goto_if_unset'):
                    data+=op('CHECKFLAG')+struct.pack('<H',value(args[0]))+op('GOTO_IF')+bytes([int(cmd=='goto_if_set')])+struct.pack('<I',address(args[1]));edges.append(args[1])
                elif cmd=='goto_if_eq':data+=op('COMPARE_VAR_TO_VALUE')+struct.pack('<HH',value(args[0]),value(args[1]))+op('GOTO_IF')+b'\x01'+struct.pack('<I',address(args[2]));edges.append(args[2])
                elif cmd=='msgbox':data+=op('LOAD_WORD')+b'\0'+struct.pack('<I',address(args[0]))+op('CALL_STD')+bytes([4 if args[1]=='MSGBOX_DEFAULT' else 5])
                elif cmd=='setflag':data+=op('SETFLAG')+struct.pack('<H',value(args[0]))
                elif cmd=='special':
                    sid=specials.index(args[0]);data+=op('SPECIAL')+struct.pack('<H',sid)
                    target=struct.unpack('<I',boundary.rom_bytes(elf,address('gSpecials')+sid*4,4))[0];assert target==address(args[0])
                elif cmd=='warp':assert args==['MAP_DCC_F1D1CHECKPOINT','4','4'];data+=op('WARP')+bytes([35,4,255])+struct.pack('<hh',4,4)
                elif cmd=='trainerbattle_double':data+=op('TRAINERBATTLE')+b'\x06'+struct.pack('<HH',value(args[0]),0)+b''.join(struct.pack('<I',address(a)) for a in args[1:]);edges.append(args[-1])
                elif cmd=='message':assert args==['NULL'];data+=op('MESSAGE')+bytes(4)
                elif cmd=='yesnobox':assert args==['20','8'];data+=op('YESNOBOX')+bytes([20,8])
                else:raise AssertionError(('unresolved compiled script command',name,line))
            assert boundary.rom_bytes(elf,address(name),len(data))==data,('compiled script mismatch',name)
            graph[name]=dict(address=address(name),source=sources[name][0],commands=commands,edges=edges,compiled_bytes=data.hex(),SHA256=hashlib.sha256(data).hexdigest())
        for kind,n in ((4,'Std_MsgboxDefault'),(5,'Std_MsgboxYesNo')):assert struct.unpack('<I',boundary.rom_bytes(elf,address('gStdScripts')+kind*4,4))[0]==address(n)
        for name in used:
            opcode,fn=ops['SCR_OP_'+name];assert struct.unpack('<I',boundary.rom_bytes(elf,address('gScriptCmdTable')+opcode*4,4))[0]==address(fn)
        names=['AgbMain','ReadKeys','CB2_Overworld','OverworldBasic','RunTasks','ScriptContext_RunScript','ShowFieldMessage','AddTextPrinterForMessage','AddTextPrinter','Task_DrawFieldMessage','RunTextPrintersAndIsPrinter0Active','RunTextPrinters','IsTextPrinterActive','RenderText','TextPrinterWaitWithDownArrow','TextPrinterWait','TextPrinterWaitAutoMode','ScrCmd_waitmessage','IsFieldMessageBoxHidden','ScrCmd_waitbuttonpress','WaitForAorBPress','ScrCmd_yesnobox','ScriptMenu_YesNo','Task_HandleYesNoInput','ScriptContext_Enable']
        functions={}
        for name in names:
            symbol=row(name);assert symbol['type']==2 and symbol['size'];a=symbol['value']&~1;data=boundary.rom_bytes(elf,a,symbol['size'])
            targets=[boundary.thumb_bl(a+i,data[i:i+4]) for i in range(0,len(data)-3,2)]
            functions[name]=dict(address=a,size=len(data),SHA256=hashlib.sha256(data).hexdigest(),direct_calls=[n for n in names if (address(n)&~1) in targets])
        tool_env=dict(os.environ,LD_LIBRARY_PATH=str(Path(config['tool_root'])/'usr/lib/x86_64-linux-gnu'))
        with (out/'native-disassembly.txt').open('w') as log:
            for name in names:subprocess.run([config['objdump'],'-d','--disassemble='+name,str(elf)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,env=tool_env)
        # Store literal native source used by fixtures. Hardware/fonts/task
        # scheduling are deliberately mocked, never asserted as native timing.
        header=(ROOT/'engine/include/text.h').read_text();text=(ROOT/'engine/src/text.c').read_text();main=(ROOT/'engine/src/main.c').read_text()
        types=definition(header,'struct TextPrinterSubStruct\n')+';\n'+definition(header,'struct TextPrinterTemplate\n')+';\n'
        types+='typedef void (*TextPrinterCallback)(struct TextPrinterTemplate *printerTemplate, u16 renderCmd);\n'+definition(header,'struct TextPrinter\n')+';\n'
        (out/'native-types.inc').write_text(types)
        native='\n'.join(definition(text,a) for a in ('bool8 TextPrinterWaitAutoMode(','bool16 TextPrinterWaitWithDownArrow(','bool16 TextPrinterWait(','void RunTextPrinters('))
        # Intent annotation only for the unchanged native PRINT->UPDATE fallthrough.
        fallthrough='CopyWindowToVram(sTextPrinters[i].printerTemplate.windowId, COPYWIN_GFX);'
        assert native.count(fallthrough)==1;native=native.replace(fallthrough,fallthrough+' /* fall through */',1)
        (out/'native-printer.inc').write_text(native)
        scrcmd=(ROOT/'engine/src/scrcmd.c').read_text();menu=(ROOT/'engine/src/script_menu.c').read_text()
        assert '#define tRight          data[2]' in menu
        completion=definition(scrcmd,'static bool8 WaitForAorBPress(')+'\n'+definition(menu,'static void Task_HandleYesNoInput(')
        (out/'native-completion.inc').write_text(completion)
        (out/'native-task-ready.inc').write_text(definition(observer,'static unsigned co_task_state('))
        keys=['gMain.newKeysRaw = keyInput & ~gMain.heldKeysRaw;','gMain.newKeys = gMain.newKeysRaw;','gMain.heldKeysRaw = keyInput;']
        assert all(main.count(k)==1 for k in keys);(out/'native-key-edge.inc').write_text('\n'.join(keys)+'\n')
        start=observer.index('        if (!strncmp(line,"pages ",6)) {');end=observer.index('\n        if (!strncmp(line,"wait-task ',start)
        command=observer[start:end];assert 'attempt<32' in command and 'frame<400' in command and command.count('co_run(')==2
        assert observer.count('co_capture_frame(p,w,h,after);')==1
        assert observer.index('c->runFrame(c);co.frames++')<observer.index('co_capture_frame(p,w,h,after);')<observer.index('if(before||after)')
        (out/'pages-command.inc').write_text(command)
        data='';lengths=[]
        for i,name in enumerate(labels):
            b=bytes.fromhex(text_proofs[name]['bytes']);lengths.append(len(b));data+=f'static const unsigned char text_{i}[]={{'+','.join(map(str,b))+'};\n'
        data+='static const unsigned char*texts[5]={'+','.join('text_'+str(i) for i in range(5))+'};\n'
        data+='static unsigned lengths[5]={'+','.join(map(str,lengths))+'};\n'
        data+='static const char*labels[5]={'+','.join(json.dumps(n) for n in labels)+'};\n';(out/'compiled-text.inc').write_text(data)
        (out/'fixture.sym').write_text('\n'.join(f'{0x1000+0x400*i:08x} V {n}' for i,n in enumerate(labels))+'\n')
        # Duplicate prompt label has identical bytes; either table occurrence
        # remains the exact same text operand, with no address-selection search.
        (out/'fixture.c').write_bytes((ROOT/'scripts/floor1/warden-dialogue-proof-fixture.c').read_bytes())
        tool=Path(config['tool_root'])
        with (out/'compile.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(tool/'usr/include'),str(out/'fixture.c'),'-o',str(out/'fixture')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        with (out/'fixture.log').open('w') as log:subprocess.run([str(out/'fixture'),str(out/'fixture.sym')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30)
        assert 'cases=41' in (out/'fixture.log').read_text()
        # End-to-end command ceiling, including one final failed command.
        # Success requires the final inactive inspection inside the32-attempt
        # guard, so at most31 pulse/release cycles precede that inspection.
        success=31*401;failure=32*401;five=max(5*success,4*success+failure)
        assert (success,failure,five)==(12431,12832,62556)
        components=prior['budgets']['continuation']['components'];assert components['pages']==5*32*401
        proposed_frames=prior['budgets']['continuation']['total']-components['pages']+five
        assert proposed_frames==132756
        ledger=copy.deepcopy(prior['storage']);process=ledger['processes']['continuation'];process['frames']=proposed_frames
        chunks,remainder=divmod(proposed_frames,2000)
        for f in process['files']:
            if f['name']=='full_RGB_chunks':f['count']=chunks
            elif f['name']=='last_RGB_chunk':f.update(count=int(bool(remainder)),per_file_bytes=remainder*115200)
            elif f['name']=='frame_index':f['per_file_bytes']=proposed_frames*16
            elif f['name']=='complete_field_trace':f['per_file_bytes']=proposed_frames*3340
            elif f['name']=='complete_battle_trace':f['per_file_bytes']=proposed_frames*1040
            f['allocated_bytes']=f['count']*((f['per_file_bytes']+4095)//4096)*4096
        process['bytes']=sum(f['allocated_bytes'] for f in process['files']);process['logical_bytes']=sum(f['count']*f['per_file_bytes'] for f in process['files'])
        ledger['reservation_bytes']=sum(p['bytes'] for p in ledger['processes'].values())+ledger['headroom_bytes']
        assert ledger['headroom_bytes']==256*1024**2 and ledger['processes']['cold']==prior['storage']['processes']['cold']
        for section in ('files','protected_history'):
            for p,h in config[section].items():assert sha(p)==h,(section,p)
        total=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());assert total<64*1024**2
        receipt.update(PASS=True,source_commit=head,ELF_SHA256=sha(elf),ROM_SHA256=sha(config['ROM']),observer_source_SHA256=sha(config['observer_source']),route_SHA256=hashlib.sha256(route.encode()).hexdigest(),text_proofs=text_proofs,compiled_script_graph=graph,native_functions=functions,
                       native_reachability='Resolved call: boss flag47 already set ->Already. Stairs: flag47 set ->YesNo; result0 ->Cancel, result1 ->checkpoint warp. Missing boss flag ->Locked and a mismatched-text STOP. Checkpoint Review ->Default. Both standard scripts/dispatcher bytes checked; prepared/locked/trainer/result alternatives retained in full graph.',
                       unresolved_native_tighter_bound='gStringVar4 equality plus active/state2/3 does not bind currentChar, callback, owning Task_DrawFieldMessage, disable flag or per-host-frame printer dispatch. RunTextPrinters can skip rendering when disabled. Inert inhibited cases show this admission gap, not native route reachability or gameplay timing. No paragraph-count-only/native timing bound claimed.',
                       guard_proof=dict(single_success=success,single_failure=failure,five_success=5*success,five_first_failure=five,first_failure_terminal=True,all_32_attempts_retained=True,fixture_cases=41,full_synthetic_frame_coverage=True,terminal_RGB_frame_included=True,timeout_page_captures=32,last_page_capture_frame=12431,timeout_frame=12832,terminal_context_capture='Existing pages exhaustion returns41 without co_stop; complete frame recording remains. Future supervisor terminal context/capture remains a runtime gate.16 fixed/terminal PPM slots retained.'),
                       proposed_only=dict(whole_route_frames=proposed_frames,cold_frames=2044,battle_frames=30000,storage=ledger,activated=False,derivative_capture_limits_unchanged=True),active_reservation_bytes=17694519296,active_route_frames=134360,input_pins=config['files'],protected_history=config['protected_history'],actual_output_bytes_before_receipt=total,fixture_log=(out/'fixture.log').read_text(),retention='Private verified local only; no backup/upload',runtime_next='Independent review; supervisor/authority/full-capacity gates unchanged')
        write(out/'proof-receipt-private.json',receipt);signal.alarm(0)
        print(json.dumps(dict(PASS=True,source_commit=head,proposed_frames=proposed_frames,proposed_reservation_bytes=ledger['reservation_bytes'],active_reservation_bytes=17694519296,emulators=0)))
    except BaseException as e:
        receipt.update(first_failure=type(e).__name__+': '+str(e),traceback=traceback.format_exc());write(out/'STOP-proof-private.json',receipt);raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();proof(json.loads(args.inputs.read_text()),args.out.resolve())
