"""Exact r2 policy/keys plus one passive source-bound transaction validator."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01-medicine-transaction-offline-r3-20261010')
NAMES=['boot','note','supply','guide-initial','trial','scrap','guide-posttrial','guard','guide-guard','save']
KINDS=['BOOT','NOTE','SUPPLY','GUIDE','TRIAL','SCRAP','GUIDE','GUARD','GUIDE','SAVE']
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def generate(git):
 old=module('tx_r2_host',ROOT/'scripts/floor1/guard-choice-r2-host.py');code,base=old.generate(git)
 def once(a,b):
  nonlocal code
  assert code.count(a)==1,a[:100];code=code.replace(a,b)
 bindings=(OUT/'transaction-bindings.h').read_text();transaction=(ROOT/'scripts/floor1/medicine-transaction.h').read_text()
 once('static unsigned gc_lifecycle(struct mCore*c,unsigned cb,const unsigned*positions) {',bindings+'\n'+transaction+'\nstatic unsigned gc_lifecycle(struct mCore*c,unsigned cb,const unsigned*positions) {\n    unsigned transaction=gt_transition(c,cb,positions);if(transaction!=GT_NONE)return transaction;')
 once('gc.healingCount=c->busRead8(c,co.a.turn-16);gc.heals=0;', 'gt_reset(c);gc.healingCount=c->busRead8(c,co.a.turn-16);gc.heals=0;')
 once('gc.healed=now;gc_dump(&now,"healed");gc.stage=5;', 'gc.healed=now;unsigned transaction=gt_activate(c);if(transaction)return transaction;gc_dump(&now,"healed");gc.stage=5;')
 start=code.index('static unsigned gc_read(struct mCore*c,struct CoSnapshot*s) {');end=code.index('\n}',start)+2;reader=code[start:end]
 a=reader.index('    for(unsigned i=0;i<6;i++) {');b=reader.index('    const unsigned skipped[]',a)
 progressive=reader[:a]+'    if(memcmp(s->party,expected,600))return 106;\n'+reader[b:]
 progressive=progressive.replace('static unsigned gc_read(struct mCore*c,struct CoSnapshot*s)', 'static unsigned gt_read_progressive(struct mCore*c,struct CoSnapshot*s,const unsigned char*expected)')
 code=code[:end]+'\n'+progressive+code[end:]
 once('    co.core=core;co.pending=!co.cold;', '    if((gc.a.partyMain&~1u)!=GT_PARTY||(gc.a.restored&~1u)!=GT_RESTORED||(gc.a.printWait&~1u)!=GT_PRINTWAIT||(gc.a.closeText&~1u)!=GT_CLOSETEXT||(gc.a.closeFade&~1u)!=GT_CLOSEFADE)return 4;\n    co.core=core;co.pending=!co.cold;')
 assert code.count('->runFrame(')==1 and code.count('core->reset(')==1
 assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
 return code,base
