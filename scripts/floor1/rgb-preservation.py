"""Local, bounded byte preservation. No emulator or gameplay imports."""
from pathlib import Path
import hashlib,json,os,shutil,stat,struct,subprocess,sys,zlib

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01-rgb-preservation-r1-20261010')
FRAME=240*160*3
CAP=3758096384
EXTERNAL_RESERVE=128*1024**2
RESERVATION=10000408128
GZIP=Path('/usr/bin/gzip')
RECORDINGS=(('STOP90',Path('/workspace/scratch/c01-uninterrupted-unprepared-r2-20261010'),31258,16,'local-retention-manifest.json'),
            ('STOP104',Path('/workspace/scratch/c01-guard-choice-r1-20261010'),28707,15,'private-retention-manifest.json'))

def require(ok,why):
    if not ok:raise RuntimeError(why)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def identity(p):
    p=Path(p);s=p.lstat()
    require(stat.S_ISREG(s.st_mode) and p.resolve()==p,'regular exact path required: '+str(p))
    return dict(device=s.st_dev,inode=s.st_ino,bytes=s.st_size,allocated_bytes=s.st_blocks*512,
                mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,mtime_ns=s.st_mtime_ns)
def usage(root):
    logical=allocated=0
    for p in [root,*root.rglob('*')]:
        s=p.lstat();require(not stat.S_ISLNK(s.st_mode),'no output symlinks')
        allocated+=s.st_blocks*512
        if p.is_file():logical+=s.st_size
    return dict(logical_bytes=logical,allocated_bytes=allocated)
class Budget:
    def __init__(self,root,cap=CAP,reserve=EXTERNAL_RESERVE):self.root,self.cap,self.reserve=root,cap,reserve
    def check(self,extra=0):
        u=usage(self.root);require(max(u.values())+self.reserve+extra<=self.cap,'all-inclusive replacement/audit cap exceeded')
        return u
    def write(self,p,b):
        require(p.resolve().is_relative_to(self.root),'output outside preservation root')
        self.check(len(b)+4096)
        with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        self.check()
    def json(self,p,obj):self.write(p,(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode())

def read_exact(f,n):
    out=bytearray()
    while len(out)<n:
        b=f.read(n-len(out))
        if not b:break
        out.extend(b)
    return bytes(out)
def index_check(p,count):
    require(p.stat().st_size==count*16,'index byte count')
    with p.open('rb') as f:
        for i in range(1,count+1):require(struct.unpack('<4I',read_exact(f,16))[0]==i,'frame index order')
        require(not f.read(1),'index EOF')
def validate_layout(rows):
    require(len(rows)==31,'31 replacement chunks required')
    n=0
    for label,base,count,chunks,_ in RECORDINGS:
        start=1
        for i in range(chunks):
            row=rows[n];n+=1;frames=min(2000,count-start+1)
            require(row['recording']==label and row['chunk']==i and row['first_frame']==start and row['frames']==frames,'missing/reordered chunk or frame range')
            require(row['raw_path']==str(base/'opening'/f'motion-{i:03}.rgb'),'unapproved raw path')
            require(row['raw_identity']['bytes']==frames*FRAME,'frame dimensions/byte count')
            require(row['compressed_relative_path']==f'{label}/motion-{i:03}.rgb.gz','replacement path/boundary')
            start+=frames
        require(start==count+1,'recording frame count')
    require(sum(r['frames'] for r in rows)==59965,'full frame count')
def check_identity(row):require(identity(Path(row['raw_path']))==row['raw_identity'],'original identity changed: '+row['raw_path'])
def zlib_blocks(p):
    dc=zlib.decompressobj(31)
    with p.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):
            while b:
                out=dc.decompress(b,65536);b=dc.unconsumed_tail
                require(not dc.unused_data,'compressed trailing bytes/member')
                if out:yield out
        require(dc.eof and not dc.unused_data and not dc.unconsumed_tail,'truncated gzip / exact EOF')
def gzip_blocks(p):
    proc=subprocess.Popen([str(GZIP),'-dc','--',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for b in iter(lambda:proc.stdout.read(65536),b''):yield b
        error=proc.stderr.read(4097);code=proc.wait()
        require(code==0 and not error,'gzip decoder failure: '+error[:4096].decode(errors='replace'))
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
        proc.stdout.close();proc.stderr.close()
def frame_blocks(blocks,count):
    pending=bytearray();n=0
    for b in blocks:
        pending.extend(b)
        while len(pending)>=FRAME:
            require(n<count,'extra decoded frame/EOF');frame=bytes(pending[:FRAME]);del pending[:FRAME];n+=1;yield frame
    require(n==count and not pending,'decoded frame count/dimensions/EOF')
def verify_chunk(row,base,decoder):
    check_identity(row);compressed=base/row['compressed_relative_path'];hashes=base/row['frame_hashes_relative_path']
    require(digest(compressed)==row['compressed_SHA256'],'compressed file hash mismatch')
    require(digest(hashes)==row['frame_hashes_SHA256'] and hashes.stat().st_size==32*row['frames'],'per-frame ledger identity')
    h=hashlib.sha256();n=0
    with Path(row['raw_path']).open('rb') as raw,hashes.open('rb') as ledger:
        for frame in frame_blocks(decoder(compressed),row['frames']):
            require(frame==read_exact(raw,FRAME),'decoded original frame bytes mismatch')
            require(hashlib.sha256(frame).digest()==read_exact(ledger,32),'per-frame hash mismatch')
            h.update(frame);n+=1
        require(not raw.read(1) and not ledger.read(1),'original/ledger exact EOF')
    require(h.hexdigest()==row['raw_SHA256'] and n==row['frames'],'original chunk hash/count')
    check_identity(row);require(digest(compressed)==row['compressed_SHA256'],'compressed file changed during decode')
    return dict(recording=row['recording'],chunk=row['chunk'],frames=n,raw_SHA256=h.hexdigest(),compressed_SHA256=row['compressed_SHA256'],exact_frame_bytes=True,exact_EOF=True)
def protected_check(contract):
    for name,row in contract['protected_entries'].items():
        p=Path(name);require(identity(p)==row['identity'] and digest(p)==row['SHA256'],'protected evidence changed: '+name)
    for row in contract['recordings']:
        p=Path(row['index_path']);index_check(p,row['frames']);require(digest(p)==row['index_SHA256'],'index changed')
def code_check(contract):
    for p,h in contract['source_files_SHA256'].items():require(digest(ROOT/p)==h,'preservation source changed')
    require(digest(GZIP)==contract['gzip_executable_SHA256'] and digest(Path(sys.executable))==contract['python_executable_SHA256'],'codec/decoder executable changed')
def verify_all(contract,mapping,decoder,label,base=OUT):
    code_check(contract);validate_layout(mapping['chunks']);protected_check(contract)
    require(mapping['contract_SHA256']==digest(base/'preservation-contract.json'),'mapping/contract binding')
    results=[]
    for row in mapping['chunks']:
        result=verify_chunk(row,base,decoder);results.append(result);Budget(base).check()
        print(f'{label} {row["recording"]} chunk={row["chunk"]} frames={row["frames"]} exact=1',flush=True)
    protected_check(contract)
    return dict(PASS=True,verification=label,decoder='Python zlib gzip stream' if decoder is zlib_blocks else 'GNU gzip -dc separate process',
                contract_SHA256=digest(base/'preservation-contract.json'),mapping_SHA256=digest(base/'representation-mapping-private.json'),
                chunks=results,chunk_count=len(results),frames=sum(r['frames'] for r in results),decoded_bytes=sum(r['frames']*FRAME for r in results),originals_retained=True,
                no_second_full_decoded_copy=True,frame_buffer_bound_bytes=FRAME+65536,frame_comparison_buffer_bound_bytes=4*FRAME+2*65536,gameplay_processes=0,runtime_claims=0)
def compress_once(raw,dest,budget):
    budget.check(4096)
    proc=subprocess.Popen([str(GZIP),'-6','-n','-c','--',str(raw)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        with dest.open('xb') as f:
            for b in iter(lambda:proc.stdout.read(65536),b''):
                budget.check(len(b)+4096);f.write(b)
            f.flush();os.fsync(f.fileno())
        error=proc.stderr.read(4097);code=proc.wait()
        require(code==0 and not error,'gzip compressor failure: '+error[:4096].decode(errors='replace'))
        budget.check()
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
        proc.stdout.close();proc.stderr.close()
def receipt_check(receipt,label,contract_hash,mapping_hash,rows):
    require(receipt['PASS'] and receipt['verification']==label and receipt['chunk_count']==31 and receipt['frames']==59965 and receipt['decoded_bytes']==6907968000,'incomplete verification: '+label)
    require(receipt['contract_SHA256']==contract_hash and receipt['mapping_SHA256']==mapping_hash,'receipt identity binding')
    require([(r['recording'],r['chunk'],r['frames'],r['raw_SHA256'],r['compressed_SHA256']) for r in receipt['chunks']]==[(r['recording'],r['chunk'],r['frames'],r['raw_SHA256'],r['compressed_SHA256']) for r in rows],'receipt chunk mapping')
    require(all(r['exact_frame_bytes'] and r['exact_EOF'] for r in receipt['chunks']),'incomplete exact bytes/EOF')
def removal_barrier(contract,mapping,one,two,base=OUT):
    validate_layout(mapping['chunks']);code_check(contract);protected_check(contract)
    for receipt,label in ((one,'pass1-zlib'),(two,'pass2-independent-gzip')):
        receipt_check(receipt,label,digest(base/'preservation-contract.json'),digest(base/'representation-mapping-private.json'),mapping['chunks'])
    for row in mapping['chunks']:
        check_identity(row);require(digest(base/row['compressed_relative_path'])==row['compressed_SHA256'],'replacement changed before removal')
    u=Budget(base).check();logical=sum(r['raw_identity']['bytes'] for r in mapping['chunks']);allocated=sum(r['raw_identity']['allocated_bytes'] for r in mapping['chunks'])
    net=logical-u['logical_bytes']-EXTERNAL_RESERVE
    require(net>=contract['minimum_net_savings_bytes'] and shutil.disk_usage(base).free+allocated>=RESERVATION,'insufficient measured all-inclusive savings/capacity')
    return dict(raw_logical_bytes=logical,raw_allocated_bytes=allocated,output_usage_before_removal=u,external_audit_reserve_bytes=EXTERNAL_RESERVE,conservative_net_savings_bytes=net,projected_available_bytes=shutil.disk_usage(base).free+allocated)
