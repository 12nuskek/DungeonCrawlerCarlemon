"""Synthetic offline contract tests; NOT evidence of native CPU authority."""
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'cases.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "v01-battle-snapshot-contract.h"
static void put32(unsigned char *p,unsigned w){for(unsigned i=0;i<4;i++)p[i]=w>>(8*i);}
static void fixture(unsigned char *p){
 memset(p,0,600);put32(p,0x12345678);put32(p+4,0x23456789);
 unsigned sum=0,key=bv_snapshot_word(p)^bv_snapshot_word(p+4);
 for(unsigned i=32;i<80;i+=4){unsigned word=i*65537;sum+=(word&65535)+(word>>16);put32(p+i,word^key);}
 p[28]=sum;p[29]=sum>>8;
}
int main(void){
 unsigned char encrypted[600],plain[600],partial[600],changed[600],other[4]={1,2,3,4},badOther[4]={1,2,3,5};
 fixture(encrypted);memcpy(plain,encrypted,600);unsigned key=bv_snapshot_word(plain)^bv_snapshot_word(plain+4);
 for(unsigned i=32;i<80;i+=4)put32(plain+i,bv_snapshot_word(plain+i)^key);
 memcpy(partial,encrypted,600);put32(partial+32,bv_snapshot_word(partial+32)^key);
 assert(bv_snapshot_party_valid(encrypted));assert(!bv_snapshot_party_valid(plain));assert(!bv_snapshot_party_valid(partial));
 struct BvSnapshotGuard g={0};
 assert(!bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,encrypted,encrypted,other,other,4,1));
 assert(!bv_snapshot_pair(&g,BV_SNAPSHOT_TRANSIENT,BV_SNAPSHOT_VALID,NULL,encrypted,other,other,4,0));
 assert(!bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_TRANSIENT,encrypted,NULL,other,other,4,0));
 assert(g.valid==1&&g.deferred==2&&g.pending&&g.frames==3);
 assert(!bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,encrypted,encrypted,other,other,4,1));
 assert(g.valid==2&&g.reentries==1&&!g.pending&&g.frames==4);
 // Persistent checksum-preserving mutation, including after a deferred read.
 memcpy(changed,encrypted,600);changed[84]=1;
 assert(!bv_snapshot_pair(&g,BV_SNAPSHOT_TRANSIENT,BV_SNAPSHOT_VALID,NULL,encrypted,other,other,4,0));
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,changed,encrypted,other,other,4,0)==103&&g.pending);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,plain,encrypted,other,other,4,0)==116);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,partial,encrypted,other,other,4,0)==116);
 memcpy(changed,encrypted,600);changed[33]^=1;assert(!bv_snapshot_party_valid(changed));
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,changed,encrypted,other,other,4,0)==116);
 assert(bv_snapshot_pair(&g,(enum BvSnapshotAuthority)3,BV_SNAPSHOT_VALID,encrypted,encrypted,other,other,4,0)==115);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_UNKNOWN,BV_SNAPSHOT_VALID,plain,encrypted,other,other,4,0)==115);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_TRANSIENT,BV_SNAPSHOT_VALID,NULL,encrypted,badOther,other,4,0)==103);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_TRANSIENT,BV_SNAPSHOT_VALID,NULL,encrypted,other,other,4,1)==115);
 assert(bv_snapshot_pair(&g,BV_SNAPSHOT_VALID,BV_SNAPSHOT_VALID,NULL,encrypted,other,other,4,0)==116);
 puts("PASS synthetic encrypted/plain/partial buffers, unread proven-transient pointers, symmetric deferral, exact reentry and persistent mutation, invalid checksum outside transient, missing CPU authority, exact other/control bytes and mandatory complete checkpoints; zero emulator frames; runtime CPU classifier BLOCKED");
}
''')
    with (out/'offline-contract.log').open('w') as f:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1'),str(out/'cases.c'),'-o',str(out/'cases')],stdout=f,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'cases')],cwd=out,stdout=f,stderr=subprocess.STDOUT,check=True)
    result={'result':'PASS synthetic offline contract only','runtime_serialization_authority':'BLOCKED; no classifier, no integration, no deferral activated','emulator_frames':0}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
