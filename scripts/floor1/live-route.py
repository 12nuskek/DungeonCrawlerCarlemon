"""Normal-controller paths through the frozen live opening contract."""
class Route:
    def __init__(self,spec,geometry,key,pos,facing,flags,opened=False):self.maps=spec["maps"];self.ids=spec["production_identity_proposal"]["maps"];self.g=geometry;self.opened=opened;self.key=key;self.pos=tuple(pos);self.face={1:128,2:64,3:32,4:16}[facing];self.flags=flags;self.lines=[]
    def step(self,n,key=0,label='-'):self.lines.append(f'step {n} {key} {label}')
    def expect(self):self.lines.append(f'expect 35 {self.ids[self.key]["map_num"]} {self.pos[0]} {self.pos[1]} {self.flags}')
    def follow(self,end):
        m=self.maps[self.key];end=tuple(end)
        if end==self.pos and any(tuple(w['at'])==end for w in m['warps']):
            legal=self.g.cells(m,self.opened)-{tuple(w['at']) for w in m['warps']};x,y=end;self.follow(next(n for n in [(x,y+1),(x+1,y),(x,y-1),(x-1,y)] if n in legal))
        path=self.g.path(m,self.opened,self.pos,end);buttons=[{(0,-1):64,(1,0):16,(0,1):128,(-1,0):32}[(b[0]-a[0],b[1]-a[1])] for a,b in zip(path,path[1:])];i=0
        while i<len(buttons):
            j=i+1
            while j<len(buttons) and buttons[j]==buttons[i]:j+=1
            self.step(16*(j-i)+(4 if buttons[i]!=self.face else 0),buttons[i]);self.face=buttons[i];self.pos=path[j];self.step(40);i=j
            if i<len(buttons):self.expect()
        warp=next((w for w in m['warps'] if tuple(w['at'])==end),None)
        if warp:
            self.step(300);self.key=next(k for k,v in self.maps.items() if v['map_num']==warp['dest']);self.pos=tuple(self.maps[self.key]['warps'][warp['dest_warp']]['at'])
        self.expect()
    def anchor(self,n):self.follow(self.maps[self.key]['anchors'][n])
    def talk(self,button,label):
        self.step(1,button);self.face=button;self.step(40);self.step(1,1);self.step(400,0,label+'.ppm');self.lines+=['dialog 3600','ready'];self.step(40);self.expect()
    def save(self):
        for n,key in [(1,8),(120,0),(1,128),(20,0),(1,128),(20,0),(1,1),(160,0),(1,1),(180,0),(1,1),(600,0),(1,1),(600,0)]:self.step(n,key)
        self.step(40,0,'saved.ppm');self.lines+=['ready','snapshot'];self.expect()
