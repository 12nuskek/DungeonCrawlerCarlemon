"""Read retained ELFs/records and count source-bound printer operations offline.

No emulator, game build, replay, timing acceptance or synthetic recovered trace.
Full symbols/disassembly/records remain private under --output.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,struct,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/workspace/scratch/c01a-action-hints-r4-20261010/baseline')
CAND=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010/candidate')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def function(source,name):
    match=re.search(r'^[^\n;]*\b'+re.escape(name)+r'\([^;\n]*\)\n\{',source,re.M);assert match,name
    end=source.index('\n}',match.start())+2;return source[match.start():end]
def summaries(path):
    data=path.read_bytes();assert data[:8]==b'BVTS0003' and (len(data)-32)%184==0
    chain=bytes(32);rows=[];digests=[]
    for i,start in enumerate(range(32,len(data),184)):
        b=data[start:start+184];w=struct.unpack('<22I',b[:88]);assert w[0]==i and b[88:120]==chain
        chain=hashlib.sha256(chain+b[:88]+b[120:152]).digest();assert b[152:]==chain
        rows.append(w);digests.append(b[120:152].hex())
    return rows,digests
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    sym=module('timing_symbols',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
    freeze=json.loads((CAND.parent/'freeze.json').read_text())
    # Verify all actually frozen tool bytes, not just versions or historical pins.
    for p,h in freeze['tool_files'].items():assert sha(p)==h,p
    versions={'gcc':subprocess.check_output(['gcc','-dumpfullversion'],text=True).strip()}
    toolroot=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009')
    agbcc=json.loads((toolroot/'agbcc-identity.json').read_text());mgba=json.loads((toolroot/'libmgba-identity.json').read_text())
    assert agbcc['source_commit']=='da598c1d918402c42c0c0d7128ba14567f3175e9' and not agbcc['original_tool_identity_claimed']
    assert sha(mgba['path'])==mgba['SHA256']=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    versions.update(agbcc_source=agbcc['source_commit'],libmGBA='0.10.5',libmGBA_SHA256=mgba['SHA256'],recovered_compiler_binaries_are_not_historical=True)
    env=dict(os.environ,LD_LIBRARY_PATH='/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root/usr/lib/x86_64-linux-gnu')
    objdump='/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root/usr/bin/arm-none-eabi-objdump'
    manifest=json.loads((toolroot/'tool-root-manifest.json').read_text())
    objpin=[r for r in manifest if r['path']=='usr/bin/arm-none-eabi-objdump'];assert len(objpin)==1 and sha(objdump)==objpin[0]['SHA256']
    packages=json.loads((toolroot/'reused-packages.json').read_text());binutils=[p for p in packages if p['Package']=='binutils-arm-none-eabi'];assert len(binutils)==1
    assert '2.44-3+23+b1' in binutils[0]['source'] and sha(binutils[0]['source'])==binutils[0]['SHA256']
    versions.update(ARM_binutils_package='2.44-3+23+b1',objdump_SHA256=objpin[0]['SHA256'],binutils_package_SHA256=binutils[0]['SHA256'])
    versions['objdump']=subprocess.check_output([objdump,'--version'],env=env,text=True).splitlines()[0]
    names=['BattleMainCB1','BattleMainCB2','HandleInputChooseAction','HandleTurnActionSelectionState','PlayerBufferRunCommand','PlayerHandleChooseMove',
      'InitMoveSelectionsVarsAndStrings','MoveSelectionDisplayMoveNames','MoveSelectionCreateCursorAt','MoveSelectionDisplayPPString','MoveSelectionDisplayPPNumber',
      'MoveSelectionDisplayMoveType','HandleChooseMoveAfterDma3','HandleInputChooseMove','BattlePutTextOnWindow','AddTextPrinter','RenderFont','RenderText',
      'FontFunc_Narrow','FontFunc_Normal','DecompressGlyph_Narrow','DecompressGlyph_Normal','CopyGlyphToWindow','CopyWindowToVram','LoadBgTiles','LoadBgVram',
      'CopyBgTilemapBufferToVram','RequestDma3Copy','ProcessDma3Requests','CheckForSpaceForDma3Request','IsDma3ManagerBusyWithBgCopy','VBlankIntr',
      'OpponentBufferRunCommand','OpponentHandleChooseAction','OpponentHandleChooseMove','OpponentBufferExecCompleted','AI_TrySwitchOrUseItem','GetMonData2','GetBoxMonData2','GetSubstruct','__umodsi3']
    builds={};raw={};allfunc={};sources={}
    for case,p in [('baseline',BASE),('candidate',CAND)]:
        ident=json.loads((p/'identity.json').read_text());elf=Path(ident['ROM']).with_suffix('.elf');engine=elf.parent
        assert sha(elf)==ident['ELF_SHA256'] and sha(ident['ROM'])==ident['ROM_SHA256']
        assert subprocess.check_output(['git','rev-parse',ident['source']+':engine'],cwd=ROOT,text=True).strip()==ident['engine_tree']
        rows=sym.symbols.elf_symbols(elf);fs=sym.symbols.functions(rows);allfunc[case]=fs;raw[case]=rows;sources[case]=engine
        selected={}
        for name in names:
            scope='L:battle_controller_player.o:' if name in ['HandleInputChooseAction','HandleInputChooseMove'] else None
            if name in ['GetMonData2','GetBoxMonData2']:scope='G:'
            found=[r for r in fs if any(a==(scope+name) if scope else a.endswith(':'+name) for a in r['aliases'])];assert len(found)==1,name
            f=found[0];b=sym.rom_bytes(elf,f['address'],f['size'])
            calls=[]
            for offset in range(0,len(b)-3,2):
                target=sym.thumb_bl(f['address']+offset,b[offset:offset+4])
                if target is not None:
                    hit=[t for t in fs if t['address']==target]
                    calls.append({'offset':offset,'target':hit[0]['identity'] if len(hit)==1 else hex(target)})
            selected[name]={'identity':f['identity'],'address':f['address'],'size':f['size'],'bytes_SHA256':hashlib.sha256(b).hexdigest(),'direct_BL':calls}
            dis=subprocess.check_output([objdump,'-d',f'--start-address={f["address"]}',f'--stop-address={f["address"]+f["size"]}',str(elf)],env=env,text=True)
            (out/(case+'-'+name+'.txt')).write_text(dis)
        sf={}
        for filename in ['battle_controller_player.c','battle_controller_opponent.c','battle_main.c','battle_message.c','battle_bg.c','text.c','window.c','bg.c','dma3_manager.c','main.c','pokemon.c','battle_ai_switch_items.c']:
            path=engine/'src'/filename;data=path.read_bytes();gitdata=subprocess.check_output(['git','show',ident['source']+':engine/src/'+filename],cwd=ROOT)
            assert data.replace(b'\r\n',b'\n')==gitdata.replace(b'\r\n',b'\n'),filename
            sf[filename]=sha(path)
        builds[case]={k:ident[k] for k in ['source','engine_tree','ROM_SHA256','ELF_SHA256']};builds[case]['compiled_paths']=selected;builds[case]['source_files_SHA256']=sf
    def locate(case,rawpc,cpsr):
        pc=rawpc-(2 if cpsr&32 else 4)
        fs=[f for f in allfunc[case] if f['address']<=pc<f['address']+f['size']]
        return {'raw_PC':rawpc,'instruction_PC':pc,'CPSR':cpsr,'identity':fs[0]['identity'] if len(fs)==1 else 'no unique ELF STT_FUNC (e.g. BIOS IRQ/vector)','offset':pc-fs[0]['address'] if len(fs)==1 else None}
    bs,bd=summaries(BASE/'native-timeline-summary-private.bin');cs,cd=summaries(CAND/'native-timeline-summary-private.bin')
    assert len(bs)==9096 and len(cs)==5217 and cs[-1][3]==124
    # Passive detail hashes include build-specific native addresses/CPU paths.
    # These hashes are diagnostics, never the strict normalized state oracle.
    assert bs[5213]==cs[5213] and bs[5214][:20]==cs[5214][:20]
    joined=[]
    for visual in [3169,3170,3171]:
        index=visual+2044
        joined.append({'visual':visual,'baseline_summary_first22':bs[index],'candidate_summary_first22':cs[index],
          'baseline_location':locate('baseline',bs[index][20],bs[index][21]),'candidate_location':locate('candidate',cs[index][20],cs[index][21]),
          'complete_frame_record_digest_equal':bd[index]==cd[index]})
    detail={};selected_detail={}
    for case,p in [('baseline',BASE),('candidate',CAND)]:
        data=(p/'native-timeline-private.bin').read_bytes();assert data[:8]==b'BVTD0003' and (len(data)-32)%184==0
        words=[struct.unpack('<46I',data[i:i+184]) for i in range(32,len(data),184)]
        detail[case]={'SHA256':sha(p/'native-timeline-private.bin'),'visual_range':[min(w[40] for w in words),max(w[40] for w in words)],'records':len(words)}
        selected_detail[case]=[w for w in words if 3169<=w[40]<=3171]
    assert not selected_detail['baseline'] and len(selected_detail['candidate'])==101
    write(out/'candidate-window-detail-private.json',selected_detail['candidate'])
    tail=[w for w in selected_detail['candidate'] if w[0] in [6,8]]
    context=[{'event':w[0],'visual':w[40],'input':w[39],'location':locate('candidate',w[3],w[5]),
      'read_iteration':w[35],'dispatch_iteration':w[36],'CB1_iteration':w[37],'CB2_iteration':w[38],
      'video_counter':w[15],'IE':w[16],'IF':w[17],'IME':w[18],'main_intr_flags':w[19],'BIOS_intr_flags':w[20],
      'pending_IRQ':w[27],'event_root_id':w[24],'copy_buffer_count':w[31],'copy_buffer_armed':w[32],'copy_buffer_bytes':w[33]} for w in tail]
    # Parse original strict native B/F/E bytes; no candidate actual B trace exists.
    trace=(BASE/'native-boundary-trace.bin').read_bytes();pos=0;last=None;boundary=None;count=0
    while pos<len(trace):
        h=trace[pos:pos+29];assert len(h)==29;kind=h[0];ord,video,epoch,n,frame,keys=struct.unpack('<Q5I',h[1:]);pos+=29
        if kind==66:
            snap=trace[pos:pos+2560];assert len(snap)==2560;pos+=2560;count+=1
            if ord==3149:boundary={'ordinal':ord,'video':video,'input_epoch':epoch,'frame_count':n,'emulator_frame':frame,'keys':keys,'snapshot_SHA256':hashlib.sha256(snap).hexdigest()}
        assert kind in [66,70,69]
    assert count==6883 and boundary and boundary['input_epoch']==5214
    assert sha(BASE/'native-boundary-trace.bin')==sha(CAND/'expected-native-boundary-trace.bin')
    a=(CAND/'ui-stop-actual-private.bin').read_bytes();e=(CAND/'ui-stop-expected-private.bin').read_bytes()
    assert [i for i,(x,y) in enumerate(zip(a,e)) if x!=y]==[2533,2534,2535,2536,2560]
    assert (struct.unpack_from('<I',a,2560)[0],struct.unpack_from('<I',e,2560)[0])==(9,11)
    # Source-bound encoded printer/count fixture; model character rendering only.
    fixture=[]
    cm={c:int(h,16) for c,h in re.findall(r"^'([^']*)'\s*=\s*([0-9A-Fa-f]+)",(sources['candidate']/'charmap.txt').read_text(),re.M)}
    moves=[int(re.search(r'#define '+n+r'\s+(\d+)',(sources['candidate']/'include/constants/moves.h').read_text())[1]) for n in ['MOVE_DCC_STRIKE','MOVE_DCC_BRACE','MOVE_DCC_SPARK','MOVE_DCC_WEAKEN']]
    def symbol_bytes(case,name):
        r=[r for r in raw[case] if r['name']==name];assert len(r)==1,name
        return sym.rom_bytes(Path(json.loads(((BASE if case=='baseline' else CAND)/'identity.json').read_text())['ROM']).with_suffix('.elf'),r[0]['value'],r[0]['size'])
    message=(sources['candidate']/'src/battle_message.c').read_text()
    for name,text in [('gText_MoveInterfacePP','PP '),('gText_MoveInterfaceType','TYPE/'),('gText_MoveInterfaceUses','USES'),('gText_DccStrikeHint','ONE FOE'),('gText_DccBraceHint','SELF DEF+'),('gText_DccSparkHint','BOTH FOES'),('gText_DccWeakenHint','ALL FOES ATK-')]:
        actual=symbol_bytes('candidate',name);assert actual==bytes([cm[c] for c in text]+[255]),name
    textsrc=(sources['candidate']/'src/text.c').read_text();windowsrc=(sources['candidate']/'src/window.c').read_text()
    # Assert the branches that the counting model represents verbatim in source.
    assert 'subStruct->fontId = *textPrinter->printerTemplate.currentChar;' in function(textsrc,'RenderText')
    assert 'DecompressGlyph_Narrow(currChar, textPrinter->japanese);' in function(textsrc,'RenderText')
    assert 'CopyGlyphToWindow(textPrinter);' in function(textsrc,'RenderText')
    for case in ['baseline','candidate']:
        controller=(sources[case]/'src/battle_controller_player.c').read_text();generated=[]
        for name in ['MoveSelectionDisplayPPString','MoveSelectionDisplayMoveType']:
            generated.append(function(controller,name))
        if case=='candidate':generated.insert(0,function(controller,'MoveSelectionGetHint'))
        constants='\n'.join(f'#define {name} {num}' for name,num in zip(['MOVE_DCC_STRIKE','MOVE_DCC_BRACE','MOVE_DCC_SPARK','MOVE_DCC_WEAKEN'],moves))
        arrays=[]
        for name in ['gText_MoveInterfacePP','gText_MoveInterfaceType']+(['gText_MoveInterfaceUses','gText_DccStrikeHint','gText_DccBraceHint','gText_DccSparkHint','gText_DccWeakenHint'] if case=='candidate' else []):
            arrays.append('static const u8 '+name+'[]={'+','.join(map(str,symbol_bytes(case,name)))+'};')
        bm=symbol_bytes(case,'gBattleMoves');types=symbol_bytes(case,'gTypeNames')
        # BattleMove ABI compiled: 12 bytes, type at byte2; type names 7 bytes.
        assert all(bm[12*m+2]<18 for m in moves)
        types_decl='static const u8 gTypeNames[][7]={'+','.join('{'+','.join(map(str,types[i:i+7]))+'}' for i in range(0,len(types),7))+'};'
        move_decl='static struct {u8 type;} gBattleMoves[65536]={' + ','.join(f'[{m}]={{ {bm[12*m+2]} }}' for m in moves)+'};'
        pre=r'''
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
typedef uint8_t u8;typedef uint16_t u16;typedef int bool16;
#define FALSE 0
#define TRUE 1
#define FONT_NORMAL 1
#define FONT_NARROW 7
#define EXT_CTRL_CODE_BEGIN 252
#define EXT_CTRL_CODE_FONT 6
#define B_WIN_PP 0
#define B_WIN_MOVE_TYPE 1
#define COPYWIN_GFX 2
#define COPYWIN_FULL 3
#define COPYWIN_MAP 1
#define TEXT_SKIP_DRAW 255
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define RENDER_STATE_HANDLE_CHAR 0
#define RENDER_FINISH 1
struct ChooseMoveStruct {u16 moves[4];};
static u8 gBattleBufferA[1][32],gActiveBattler,gMoveSelectionCursor[1],gDisplayedStringBattle[256];
static u8 *StringCopy(u8 *d,const u8 *s){while(*s!=255)*d++=*s++;*d=255;return d;}
struct TextPrinterTemplate{const u8 *currentChar;u8 windowId,fontId,fgColor,bgColor,shadowColor;};
typedef void (*TextPrinterCallback)(void);
struct TextPrinter{struct TextPrinterTemplate printerTemplate;TextPrinterCallback callback;u8 active,state,textSpeed,delayCounter,scrollDistance,subStructFields[7],minLetterSpacing,japanese;};
static int fonts;static int *gFonts=&fonts;static struct TextPrinter sTempTextPrinter,sTextPrinters[2];static u8 gDisableTextPrinters;
struct Window{struct{u8 bg,width,height;u16 baseBlock;}window;void *tileData;};static struct Window gWindows[2]={{{0,4,2,0},0},{{0,8,2,0},0}};
static unsigned glyph[2][10],controls[2],calls[2],gfx[2],maps[2],bytes[2],lookups[2];
static void GenerateFontHalfRowLookupTable(u8 a,u8 b,u8 c){(void)a;(void)b;(void)c;lookups[sTempTextPrinter.printerTemplate.windowId]++;}
/* Source-bound counting model, not RenderText execution or ARM timing. */
static u16 RenderFont(struct TextPrinter *p){unsigned win=p->printerTemplate.windowId;u8 c=*p->printerTemplate.currentChar++;
 if(c==255)return RENDER_FINISH;
 if(c==252){assert(*p->printerTemplate.currentChar++==6);p->subStructFields[0]=*p->printerTemplate.currentChar++;controls[win]++;return 2;}
 if(!p->subStructFields[1]){p->subStructFields[0]=p->printerTemplate.fontId;p->subStructFields[1]=1;}
 glyph[win][p->subStructFields[0]]++;return 0;}
static void LoadBgTiles(u8 bg,const void *data,u16 size,u16 block){(void)bg;(void)data;(void)block;unsigned win=sTempTextPrinter.printerTemplate.windowId;gfx[win]++;bytes[win]+=size;}
static void CopyBgTilemapBufferToVram(u8 bg){(void)bg;maps[sTempTextPrinter.printerTemplate.windowId]++;}
'''
        middle=function(windowsrc,'CopyWindowToVram')+'\n'+function(textsrc,'AddTextPrinter')
        stub=r'''
static void BattlePutTextOnWindow(const u8 *s,u8 window){struct TextPrinterTemplate t={s,window,FONT_NARROW,13,14,15};calls[window]++;AddTextPrinter(&t,0,0);CopyWindowToVram(window,COPYWIN_FULL);}
'''
        mainc='int main(void){unsigned moves[4]={'+','.join(map(str,moves))+'};for(unsigned i=0;i<4;i++){memset(glyph,0,sizeof glyph);memset(controls,0,sizeof controls);memset(calls,0,sizeof calls);memset(gfx,0,sizeof gfx);memset(maps,0,sizeof maps);memset(bytes,0,sizeof bytes);((struct ChooseMoveStruct *)&gBattleBufferA[0][4])->moves[0]=moves[i];MoveSelectionDisplayPPString();MoveSelectionDisplayMoveType();for(unsigned w=0;w<2;w++)printf("%u %u %u %u %u %u %u %u %u\\n",i,w,calls[w],glyph[w][7],glyph[w][1],controls[w],gfx[w],maps[w],bytes[w]);}return 0;}'
        cpath=out/(case+'-printer-count.c');cpath.write_text(pre+constants+'\n'+'\n'.join(arrays)+'\n'+types_decl+'\n'+move_decl+'\n'+middle+'\n'+stub+'\n'+'\n'.join(generated)+'\n'+mainc)
        binary=out/(case+'-printer-count');subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(cpath),'-o',str(binary)],check=True)
        lines=subprocess.check_output([str(binary)],text=True).splitlines();assert len(lines)==8
        for line in lines:
            move,win,call,narrow,normal,control,gfxn,mapn,bytesn=map(int,line.split());assert call==1 and gfxn==2 and mapn==1 and bytesn==(512 if win==0 else 1024)
            expected=(3,0,0) if case=='baseline' and win==0 else (5,6,1) if case=='baseline' else (4,0,0) if win==0 else ([7,9,9,13][move],0,0)
            assert (narrow,normal,control)==expected
            fixture.append({'case':case,'move_index':move,'window':win,'printing_calls':call,'narrow_glyphs':narrow,'normal_glyphs':normal,'font_controls':control,'GFX_submissions':gfxn,'MAP_submissions':mapn,'GFX_bytes':bytesn,'MAP_bytes_if_BG0_visible_normal_screen2':4096})
    report={'PASS':True,'scope':'Retained source/ELF/timeline audit and host-native source-bound operation-count fixture; no game rebuild, emulator or recovered timing',
      'checkpoint':'92d6f40fde2b7b5f9944d286a42ad2a6e897af4b','base':freeze['base'],'builds':builds,'tool_versions':versions,'frozen_tool_file_count':len(freeze['tool_files']),
      'original_observer_source_SHA256':freeze['observer_source_SHA256'],'original_observer_binary_SHA256':freeze['observer_binary_SHA256'],
      'last_equal_native_boundary':boundary,'join':joined,'detail_availability':detail,'candidate_frame_context':context,'printer_operation_fixture':fixture,
      'candidate_actual_native_B_trace_absent':True,'copied_expected_trace_is_not_actual':True,'passive_frame_hashes_are_not_normalized_state_comparisons':True,
      'opponent_execution_bit1_difference':True,'cursor_refresh_input_branches_not_run':True,'increased_print_or_DMA_submission_count_not_supported':True,
      'not_observed':['baseline detailed interval/iteration/stack','gActiveBattler or controller command byte at STOP','candidate stack/caller chain above GetSubstruct','sDma3Requests/lock/cursor/busy mask/VCOUNT at mismatch','unflushed candidate edge buffer'],
      'recommended_game_remedy':None,'next':'Review minimal passive diagnostic proposal before any separately frozen bounded gameplay claim; keep original strict streams and STOP124'}
    for p,h in freeze['original_r4_artifacts_SHA256'].items():assert sha(BASE.parent/p)==h,p
    assert sha(freeze['Save_path'])==sha(BASE/'game.sav')==sha(CAND/'game.sav')==freeze['Save_SHA256']
    write(out/'offline-timing-proof.json',report)
    print('PASS: both retained ELFs and all frozen tools/source paths verified; boundary3149 joined;16 printer counts; no game remedy established')
if __name__=='__main__':main()
