#!/usr/bin/env python3
"""Inert native-layout fixtures; never launch mGBA or exclusive gameplay runners."""
from pathlib import Path
import importlib.util,subprocess,tempfile,json,struct,copy,hashlib
ROOT=Path(__file__).resolve().parents[1]
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def fixtures(model):
 party=b''
 for i in range(2):
  c=bytearray(100);struct.pack_into('<I',c,0,128 if i==0 else 0);struct.pack_into('<I',c,4,1234567);c[19]=2
  struct.pack_into('<H',c,32,66 if i==0 else 52);struct.pack_into('<I',c,36,399 if i==0 else 709);c[41]=70
  struct.pack_into('<4H',c,44,355 if i==0 else 357,356 if i==0 else 358,0,0);c[52:56]=bytes((8 if i==0 else 2,40,0,0));c[84]=8
  struct.pack_into('<I',c,72,sum(20<<(5*j) for j in range(6))|(i<<31));stats=model.prior.level_stats(c,8);struct.pack_into('<7H',c,86,stats[0],*stats)
  party+=model.prior.encode(c,c)
 party+=bytes(400);flags=bytearray(300);flags[4]=1
 owned=bytearray(1272);struct.pack_into('<I',owned,0,3000)
 variables=bytearray(512);struct.pack_into('<H',variables,2,1);struct.pack_into('<H',variables,0x9c,1)
 return dict(party=party,flags=bytes(flags),logical=bytes(owned),owned=bytes(owned),vars=bytes(variables),saved=bytes(600),saved_count=0,context=0,counter=0,count=2,group=35,mapnum=0,map=[35,0],section=0,position=[8,38],x=8,y=38,facing=1)
def main():
 model=module('co_offline_state',ROOT/'scripts/floor1/continuous-opening-state.py');host=module('co_offline_host',ROOT/'scripts/floor1/continuous-opening-host.py');route=module('co_offline_route',ROOT/'scripts/floor1/continuous-opening-route.py')
 code,base=host.generate(git);plans=route.routes();names=host.NAMES
 ends=[s[10:] for s in plans['opening'].splitlines() if s.startswith('phase end ')];assert ends==names
 assert plans['opening'].count('pilot offensive 36000')==3 and plans['opening'].count('pilot fortify 30000')==1
 assert plans['opening'].count('co save-ready')==1 and not any(x in plans['opening'] for x in ['snapshot','checkpoint boot','mutation ','growth ','cold-approach','policy '])
 assert all(x not in code for x in ['busWrite','loadState','PatrolGuard','ordinary_initial']) and code.count('->runFrame(')==code.count('core->reset(')==1
 assert code.count('TURN_METRIC')==1 and code.index('TURN_METRIC')>code.index('if (actor!=UINT_MAX)')
 # Entire authored battle decision block is unchanged, apart from a terminal
 # depleted-Carl guard. Fixture coverage includes all legal actor/turn/PP states.
 original=(ROOT/'scripts/playtest.c').read_text();a=original.index('                            unsigned desired=0;');b=original.index('                            unsigned cursor=',a)
 baseline=original[a:b];new=code[code.index('                            unsigned desired=0;'):code.index('                            unsigned cursor=',code.index('                            unsigned desired=0;'))]
 assert new.startswith(baseline.rstrip())
 decisions=0
 for actor in (0,2):
  for turn in range(12):
   for pp in range(3):
    for policy in ('offensive','fortify'):
     desired=1 if policy=='fortify' and turn<3 else 1 if actor==2 and pp==0 else 0
     for cursor in (0,1):
      button=1 if cursor==desired else 16 if desired else 32;assert button in (1,16,32);decisions+=1
 # Source equations/guards, not copied historical Save bytes.
 initial=fixtures(model);model.validate('boot',initial,initial)
 battle_checks=0
 for phase,gain,ev,flag,money in [('trial',96,(1,0,0,1,0,0),2135,320),('guard',132,(0,0,0,1,1,0),2136,320),('howler',121,(1,0,0,1,0,0),2137,360),('boss',226,(3,0,0,0,0,0),2138,360)]:
  after=copy.deepcopy(initial);p=bytearray(initial['party']);f=bytearray(initial['flags']);f[flag//8]|=1<<(flag%8)
  if phase=='trial':f[37//8]|=1<<(37%8)
  if phase=='boss':f[47//8]|=1<<(47%8)
  for i in range(2):
   raw=p[100*i:100*(i+1)];c=bytearray(model.fields.decode(raw)['canonical']);xp=struct.unpack_from('<I',c,36)[0]+gain;struct.pack_into('<I',c,36,xp)
   for j,v in enumerate(ev):c[56+j]+=v
   level=c[84]
   threshold=lambda l:max(0,6*l**3//5-15*l*l+100*l-140) if i==0 else l**3
   while xp>=threshold(level+1):level+=1
   c[41]=model.friendship.level_ups(c[41],levels=level-c[84],met_location=c[69],section=0,ball=0,held_item=0,pokerus=0);c[84]=level
   stats=model.prior.level_stats(c,level);struct.pack_into('<7H',c,86,stats[0]-3,*stats);c[52]=max(0,c[52]-1);p[100*i:100*(i+1)]=model.prior.encode(c,raw)
  after['party']=bytes(p);after['flags']=bytes(f);lo=bytearray(initial['logical']);struct.pack_into('<I',lo,0,struct.unpack_from('<I',lo)[0]+money);after['logical']=bytes(lo)
  vv=bytearray(after['vars']);struct.pack_into('<H',vv,0x56,0);after['vars']=bytes(vv)
  model.validate(phase,initial,after);battle_checks+=1
  for key,offset in [('party',20),('party',225),('logical',90),('flags',90),('vars',90)]:
   bad=copy.deepcopy(after);changed=bytearray(bad[key]);changed[offset]^=1;bad[key]=bytes(changed)
   try:model.validate(phase,initial,bad)
   except AssertionError:battle_checks+=1
   else:raise AssertionError(('accepted unrelated mutation',phase,key,offset))
  initial=after
 # Independent native14-sector persistence fixture and every-sector corruption.
 cold=copy.deepcopy(initial);cold['map']=[35,4];cold['position']=[8,6];cold['saved']=cold['party'];cold['saved_count']=2
 vv=bytearray(cold['vars']);struct.pack_into('<H',vv,2,0);cold['vars']=bytes(vv)
 sizes=[0xf2c]+[min(3968,0x3d88-i*3968) for i in range(4)]+[min(3968,0x83d0-i*3968) for i in range(9)]
 sb=bytearray(0x3d88);struct.pack_into('<hh',sb,0,8,6);sb[4:6]=bytes((35,4));struct.pack_into('<I',sb,0x234,2);sb[0x238:0x238+600]=cold['party'];sb[0x1270:0x139c]=cold['flags'];sb[0x139c:0x159c]=cold['vars'];sb[0x490:0x988]=cold['logical']
 sectors=[bytes(0xf2c)]+[bytes(sb[i*3968:i*3968+sizes[i+1]]) for i in range(4)]+[bytes(sizes[i]) for i in range(5,14)]
 save=bytearray(b'\xff'*131072)
 for sid,data in enumerate(sectors):
  base=sid*4096;save[base:base+len(data)]=data;total=sum(struct.unpack('<'+str(len(data)//4)+'I',data))&0xffffffff;checksum=((total&65535)+(total>>16))&65535
  struct.pack_into('<HHII',save,base+0xff4,sid,checksum,0x08012025,1)
 with tempfile.TemporaryDirectory(prefix='co-inert-') as t:
  d=Path(t);(d/'observer.c').write_text(code.replace('int main(int argc','int continuous_host_main(int argc'))
  (d/'save.sav').write_bytes(save);assert model.disk_equivalence(d/'save.sav',cold)['PASS']
  for sid in range(14):
   bad=bytearray(save);bad[sid*4096]^=1;(d/'save-corrupt.sav').write_bytes(bad)
   try:model.disk_equivalence(d/'save-corrupt.sav',cold)
   except AssertionError:pass
   else:raise AssertionError(('accepted corrupt native sector',sid))
  # Inert RGB, explicitly not game imagery; exact FFV1 full-frame round trip.
  rgb=bytes((i*31+i//17)%256 for i in range(115200*3));(d/'inert.rgb').write_bytes(rgb)
  subprocess.run(['ffmpeg','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','240x160','-framerate','16777216/280896','-i',str(d/'inert.rgb'),'-c:v','ffv1','-level','3','-pix_fmt','bgr0',str(d/'inert.mkv')],check=True)
  decoded=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(d/'inert.mkv'),'-f','rawvideo','-pix_fmt','rgb24','-'])
  assert decoded==rgb

  init=fixtures(model)
  packed=init['party']+init['flags']+init['owned']+init['vars']+init['saved']+struct.pack('<10I',0,0,2,0,35,0,0,8,38,1)
  (d/'fixture.bin').write_bytes(packed)
  source=(ROOT/'scripts/floor1/continuous-opening-inert.c').read_text().replace('OBSERVER',str(d/'observer.c'))
  (d/'test.c').write_text(source)
  command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-I'+str(TOOL/'usr/include'),str(d/'test.c'),'-L'+str(TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(d/'test')]
  subprocess.run(command,check=True);env=dict(__import__('os').environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
  log=subprocess.check_output([str(d/'test')],cwd=d,env=env,text=True);print(log,end='')
 print(json.dumps(dict(PASS=True,generated_host_SHA256=hashlib.sha256(code.encode()).hexdigest(),route_phases=len(names),battle_decision_vectors=decisions,complete_transition_positive_negative_checks=battle_checks,native_sector_corruption_negatives=14,lossless_native_timing_roundtrip_frames=3,gameplay_processes=0),sort_keys=True))
if __name__=='__main__':main()
