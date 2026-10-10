static void conserveSetup(unsigned g,unsigned s,unsigned ch,unsigned dh,unsigned stock){
 setup();gcf=(struct GcFoeAddresses){0xc0,0xc4,0xc8};memory[gcf.count]=4;
 const unsigned species[]={66,308,52,288};
 for(unsigned i=0;i<4;i++){memory[gcf.positions+i]=i;put16(co.a.mons+88*i,species[i]);}
 put16(co.a.mons+40,ch);put16(co.a.mons+44,33);put16(co.a.mons+2*88+40,dh);put16(co.a.mons+2*88+44,28);
 put16(co.a.mons+88+40,g?3:0);put16(co.a.mons+88+44,29);put16(co.a.mons+3*88+40,s?18:0);put16(co.a.mons+3*88+44,24);
 gc.a.indexes=0x2c00;put16(gc.a.indexes,0);put16(gc.a.indexes+4,1);
 memory[co.a.mons+36]=4;memory[co.a.mons+37]=40;
 memset(gc.owned,0,1272);if(stock){put16(0x300,13);put16(0x302,stock);memcpy(gc.owned+0xd0,memory+0x300,4);}
}
static void conserveIntegration(void){
 unsigned checks=0;
 for(unsigned g=0;g<2;g++)for(unsigned s=0;s<2;s++)for(unsigned absence=0;absence<2;absence++){
  conserveSetup(g,s,22,18,2);memory[gcf.absent]=absence?(!g?2:0)|(!s?8:0):0;
  unsigned a=9,b=9;assert(gc_decision(&mock,&a,&b)==0&&a==g&&b==s);checks++;closeFiles();
 }
 const unsigned vectors[][6]={{1,1,21,18,2,1},{1,1,22,18,2,0},{1,0,15,12,1,1},{1,0,16,12,0,0},
  {0,1,12,18,2,1},{0,1,13,18,0,0},{1,1,22,12,2,2},{0,1,13,12,1,2},
  {1,1,21,12,2,100},{1,1,21,18,0,101},{1,1,1,18,2,102},{0,0,1,1,0,0},
  {1,1,0,18,2,90},{0,0,0,1,0,90}};
 for(unsigned i=0;i<sizeof vectors/sizeof *vectors;i++){
  const unsigned*v=vectors[i];conserveSetup(v[0],v[1],v[2],v[3],v[4]);unsigned g=9,s=9;
  assert(gc_decision(&mock,&g,&s)==v[5]);checks++;closeFiles();
 }
 for(unsigned i=0;i<11;i++){
  conserveSetup(1,1,22,18,2);
  if(i==0)memory[gcf.count]=3;
  if(i==1)memory[gcf.positions+1]=3;
  if(i==2)put16(co.a.mons+88,288);
  if(i==3)put16(gc.a.indexes+4,0);
  if(i==4)put16(co.a.mons+88+40,30);
  if(i==5)put16(co.a.mons+3*88+40,25);
  if(i==6)put16(co.a.mons+88+44,30);
  if(i==7)put16(co.a.mons+3*88+44,25);
  if(i==8)memory[gcf.absent]=2;
  if(i==9)memory[gcf.absent]=8;
  if(i==10)memory[gcf.absent]=1;
  unsigned g=9,s=9;assert(gc_decision(&mock,&g,&s)==103);checks++;closeFiles();
 }
 assert(checks==33);printf("PASS two-foe native decision integration checks=%u all4presence combinations and native identity/HP/absent guards\n",checks);
}
