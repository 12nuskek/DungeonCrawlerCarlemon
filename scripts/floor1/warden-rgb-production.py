"""Warden-only preservation wiring. Separate reviewed authority is mandatory."""
from pathlib import Path
import copy, hashlib, json, os, stat, subprocess, time, types
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT/relative)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
s = module('warden_production_scope', 'scripts/floor1/rgb-warden-preservation-scope.py')
b, e, require = s.bindings, s.engine, s.require
BASE = 'faa22cb13587d3204e3c39fd596fa0b30a9c098a'
PREP_SHA = '42a774091b4a1926b0bed17cefe83846dce57591c8aef0ce3795d84bcb1d5983'
PREP_HANDOFF_SHA = 'd4e58aa62bbb645dabce94777bf3452364f0a3e8cced1d055bfaaa8d40fa2e82'
PREP_SUITE_SHA = '3213f0cf01def696222b5765f557ba5c5ce1672b1b4f6af8771d1255c4c51211'
OFFLINE = s.SCRATCH/'warden-rgb-production-wiring-offline-r1-20261011'
PRODUCTION = OFFLINE/'production-proposal-private.json'
ADMISSION = OFFLINE/'production-admission-private.json'
AUDIT = OFFLINE/'actual-protection-readback-private.json'
OUT, AUTHORITY, CAP = s.PROPOSED_OUTPUT, s.AUTHORITY, s.CAP
FILES = ('scripts/floor1/warden-rgb-production.py', 'scripts/preserve-warden-rgb-r1.py',
         'scripts/test-warden-rgb-production-offline.py',
         'docs/floor1/warden-rgb-production-r1-contract.md',
         'docs/floor1/warden-rgb-preservation-r1-contract.md')
CLAIM = 'preservation-exclusive-claim-private.json'
STOP = 'preservation-STOP-private.json'
STOP_BYTES, STOP_FILES = 8192, 2
ROOTS = (s.VISUAL, s.PREPARATION, s.OFFLINE, OFFLINE, OUT)
CODEC_KEYS = ('format','compress_command','decoder_pass1','decoder_pass2','gzip_version',
    'gzip_executable_SHA256','python_executable_SHA256','zlib_version',
    'zlib_module_origin','tool_dependencies_SHA256')

def encoded(value): return (json.dumps(value,sort_keys=True)+'\n').encode()
def read(path): e.identity(Path(path)); return json.loads(Path(path).read_text())
def check_entry(path, entry):
    path=Path(path); require(e.identity(path)==entry['identity'] and path.stat().st_nlink==1,
                            'protected identity/link changed: '+str(path))
    require(e.digest(path)==entry['SHA256'] and e.identity(path)==entry['identity'],
            'protected bytes changed: '+str(path))

def check_historical_record(row):
    require(set(row)=={'path','identity','SHA256'}, 'complete historical record')
    p=Path(row['path']); before=b.retention.identity(p)
    require(before==row['identity'] and b.retention.sha(p)==row['SHA256'] and
            b.retention.identity(p)==before, 'historical protected file changed: '+str(p))

def referenced_protection(contract):
    refs=contract['historical_protection_refs']
    for path,entry in refs.items(): check_entry(path,entry)
    inventory=b.retention.PREP/'protected-inventory-private.jsonl'
    require(str(inventory) in refs and refs[str(inventory)]['SHA256']==
            '175ce1506bae8d9dfb3e954fbe64f412bf929e8425d91bd92c5ad4fdae226620',
            'exact referenced historical inventory')
    # Verify every recorded actual file, not merely this inventory's pointer.
    seen=set()
    with inventory.open() as file:
        for line in file:
            row=json.loads(line); require(row['path'] not in seen, 'duplicate historical operand')
            seen.add(row['path']); check_historical_record(row)
    require(len(seen)==37000, 'complete 37000-entry actual protected scope')
    b.retention.verify_representation()  # Existing archive/proof relationships; no codec replay.
    for path,entry in refs.items(): check_entry(path,entry)
    return len(seen)

def metadata_usage(extra_bytes=0,extra_files=0,failure=False):
    streams={str(OUT/row[k]) for row in s.definitions()
             for k in ('compressed_relative_path','frame_hashes_relative_path')}
    paths=[p for root in ROOTS if root.exists() for p in (root,*root.rglob('*'))]
    if AUTHORITY.exists(): paths.append(AUTHORITY)
    require(all(not p.is_symlink() for p in paths), 'aggregate namespace has symlink')
    files=[p for p in paths if p.is_file() and str(p) not in streams]
    logical=sum(p.stat().st_size for p in files)
    allocated=sum(p.stat().st_blocks*512 for p in paths if p.is_dir() or str(p) not in streams)
    require(len(files)+extra_files<=s.METADATA_FILES-(0 if failure else STOP_FILES) and
            logical+extra_bytes<=s.METADATA_CAP-(0 if failure else STOP_BYTES),
            'aggregate visual/preparation/test/execution/failure metadata exceeded')
    require(allocated<=s.METADATA_CAP+64*s.BLOCK+6*s.BLOCK,'aggregate metadata allocated bound')
    return dict(files=len(files),logical_bytes=logical,allocated_bytes=allocated)

def accepted_inputs():
    p=s.PREPARATION/'proposal-contract-private.json'; h=s.PREPARATION/'final-review-handoff-private.json'
    old_suite=s.OFFLINE/'scope-suite-private.json'
    require(e.digest(p)==PREP_SHA and e.digest(h)==PREP_HANDOFF_SHA and
            e.digest(old_suite)==PREP_SUITE_SHA and e.digest(s.HANDOFF)==s.HANDOFF_SHA,
            'exact accepted Warden proposal/handoff/admission/runtime seals')
    proposal,handoff,checked=read(p),read(h),read(old_suite)
    for path,entry in handoff['private_artifacts'].items(): check_entry(path,entry)
    require(handoff['PASS'] and checked['PASS'] and handoff['tested_commit']==
            handoff['published_commit']==checked['source_commit']==proposal['proposal_source_commit']==BASE and
            checked['case_count']==100 and checked['real_unlinks']==checked['compressors']==0,
            'accepted preparation only')
    require(set(checked['source_files_SHA256'])==set(s.FILES) and
            all(proposal['source_files_SHA256'][p]==pin for p,pin in checked['source_files_SHA256'].items()),
            'four direct preparation files are separate from inherited closure')
    for rel,pin in checked['source_files_SHA256'].items():
        require(hashlib.sha256(b.git_bytes('show',BASE+':'+rel)).hexdigest()==pin,
                'historical preparation blob changed')
    inherited={p:pin for p,pin in proposal['source_files_SHA256'].items() if p not in s.FILES}
    require(len(inherited)==2668, 'complete inherited preparation closure')
    for rel,pin in inherited.items(): require(e.digest(ROOT/rel)==pin,'inherited source changed: '+rel)
    require(proposal['chunk_count']==13 and proposal['frames']==24207 and
            proposal['original_bytes']==2788646400 and proposal['storage']==s.storage_cap(proposal['chunks']) and
            proposal['storage']['all_inclusive_cap_bytes']==CAP and
            proposal['actual_runtime_handoff_SHA256']==s.HANDOFF_SHA,
            'exact Warden13 inventory/cap/runtime handoff')
    s.validate_scope(proposal['chunks'],proposal['protected_entries'],proposal['previously_replaced_paths'])
    return proposal

def build_proposal(preparation):
    head=b.git('rev-parse','HEAD'); require(not b.git('status','--porcelain'),'clean production source')
    require(b.git('merge-base',BASE,head)==BASE and
            set(b.git('diff','--name-only',BASE,head).splitlines())==set(FILES), 'focused five-file production delta')
    sources=dict(preparation['source_files_SHA256'])
    for rel in set(s.FILES)|set(FILES): sources[rel]=e.digest(ROOT/rel)
    env=b.environment(Path(b.read(b.CONFIG)['tool_root']))
    return dict(schema='Warden13-production-proposal/v1',source_commit=head,source_base=BASE,
        preparation_proposal_SHA256=PREP_SHA,preparation_handoff_SHA256=PREP_HANDOFF_SHA,
        preparation_admission_SHA256=PREP_SUITE_SHA,actual_runtime_handoff_SHA256=s.HANDOFF_SHA,
        direct_preparation_files=list(s.FILES),inherited_source_files=[p for p in preparation['source_files_SHA256'] if p not in s.FILES],
        direct_production_files=list(FILES),source_files_SHA256=sources,
        direct_production_files_SHA256={p:sources[p] for p in FILES},
        environment=env,environment_SHA256=hashlib.sha256(encoded(env)).hexdigest(),
        codec={k:preparation[k] for k in CODEC_KEYS},output_root=str(OUT),authority_path=str(AUTHORITY),
        chunk_count=13,frames=24207,raw_bytes=2788646400,cap_bytes=CAP,
        metadata_roots=[str(p) for p in ROOTS],metadata_cap_bytes=s.METADATA_CAP,
        metadata_file_limit=64,STOP_reserved_bytes=STOP_BYTES,STOP_reserved_files=STOP_FILES,
        controller_limit=1,verifier_children=2,controller_wall_seconds=7200,child_wall_seconds=1800,
        execution_permitted=False,runtime='CLOSED',first_failure_terminal=True,retry=False)

def provider_check(prod):
    env=b.environment(Path(b.read(b.CONFIG)['tool_root']))
    require(env==prod['environment'] and hashlib.sha256(encoded(env)).hexdigest()==prod['environment_SHA256'],
            'exact sealed provider environment')
    codec=prod['codec']
    for path,pin in codec['tool_dependencies_SHA256'].items(): require(e.digest(Path(path))==pin,'codec provider changed')
    deps=b.merge_exact(b.linked(e.GZIP,env),b.linked(Path(b.provider('python3')),env),
        {str(e.GZIP):e.digest(e.GZIP),b.provider('python3'):e.digest(Path(b.provider('python3')))})
    require(deps==codec['tool_dependencies_SHA256'] and e.zlib.ZLIB_RUNTIME_VERSION==codec['zlib_version'] and
            s.accepted.accepted.zlib_provider(e.zlib,Path(b.provider('python3')))[1]==codec['zlib_module_origin'] and
            subprocess.check_output([str(e.GZIP),'--version'],env=env,text=True,timeout=10).splitlines()[0]==codec['gzip_version'],
            'fixed accepted gzip/Python/zlib/linkage')

def authority_template(prod,proposal_hash,admission_hash):
    return dict(status='APPROVED_ONE_WARDEN13_LOCAL_PRESERVATION',source_commit=prod['source_commit'],
        production_proposal_SHA256=proposal_hash,production_admission_SHA256=admission_hash,
        preparation_proposal_SHA256=PREP_SHA,output_root=str(OUT),cap_bytes=CAP,chunk_count=13,
        frames=24207,raw_bytes=2788646400,controller_limit=1,verifier_children=2,
        preservation_only=True,runtime_authority=False,parent_review_verified=True,retry=False)

def validate_production(prod,preparation):
    expected=set(preparation['source_files_SHA256'])|set(FILES)
    require(set(prod['source_files_SHA256'])==expected and len(expected)==2676 and
            set(prod['direct_production_files_SHA256'])==set(FILES) and
            prod['direct_preparation_files']==list(s.FILES) and prod['direct_production_files']==list(FILES) and
            set(prod['inherited_source_files'])==set(preparation['source_files_SHA256'])-set(s.FILES),
            'exact direct/inherited/complete source sets')
    require(all(prod['source_files_SHA256'][p]==pin for p,pin in preparation['source_files_SHA256'].items()
                if p not in FILES) and all(prod['source_files_SHA256'][p]==pin for p,pin in prod['direct_production_files_SHA256'].items()),
            'immutable inherited source and admitted direct overlaps')
    require(prod['schema']=='Warden13-production-proposal/v1' and prod['source_base']==BASE and
            prod['first_failure_terminal'] is True and
            prod['codec']=={k:preparation[k] for k in CODEC_KEYS} and
            (prod['chunk_count'],prod['frames'],prod['raw_bytes'],prod['cap_bytes'])==(13,24207,2788646400,CAP) and
            prod['preparation_proposal_SHA256']==PREP_SHA and prod['preparation_handoff_SHA256']==PREP_HANDOFF_SHA and
            prod['preparation_admission_SHA256']==PREP_SUITE_SHA and prod['actual_runtime_handoff_SHA256']==s.HANDOFF_SHA and
            prod['output_root']==str(OUT) and prod['authority_path']==str(AUTHORITY) and
            prod['metadata_roots']==[str(p) for p in ROOTS] and prod['metadata_cap_bytes']==s.METADATA_CAP and
            prod['metadata_file_limit']==64 and prod['STOP_reserved_bytes']==STOP_BYTES and
            prod['STOP_reserved_files']==STOP_FILES and prod['controller_limit']==1 and prod['verifier_children']==2 and
            prod['controller_wall_seconds']==7200 and prod['child_wall_seconds']==1800 and
            prod['execution_permitted'] is False and prod['runtime']=='CLOSED' and prod['retry'] is False,
            'immutable production scope/providers/paths/bounds/permission')

# Reuse only the accepted generic validation, durable synchronization/removal
# barrier and exact inode/fsync primitives. Historical launchers/workers/default
# accounting and their hardcoded 17-count receipts are never called.
c=module('warden_durable_barrier','scripts/floor1/howler-rgb-preservation-controller.py')
PRIMITIVES=c.LocalIO
c.OUT,c.CAP,c.PROPOSAL_SHA,c.FILES=OUT,CAP,PREP_SHA,FILES
c.scope=types.SimpleNamespace(pair_check=s.pair_check,validate_scope=s.validate_scope,
    gzip_bound=s.gzip_bound,METADATA_CAP=s.METADATA_CAP,METADATA_FILES=64,BLOCK=s.BLOCK,AUDIT_RESERVE=s.AUDIT_RESERVE)
inherited_paths=c.synchronized_paths
def synchronized_paths(mapping):
    return inherited_paths(mapping)+[OUT/CLAIM,PRODUCTION,ADMISSION,AUTHORITY,AUDIT]
c.synchronized_paths=synchronized_paths

def validate_contract(contract,preparation):
    prod=contract['production_proposal']; validate_production(prod,preparation)
    require(contract['approved_proposal_SHA256']==PREP_SHA and
            contract['approved_production_proposal_SHA256']==hashlib.sha256(encoded(prod)).hexdigest() and
            contract['preservation_source_commit']==prod['source_commit'] and
            contract['source_files_SHA256']==prod['source_files_SHA256'] and
            contract['status']=='FROZEN_LOCAL_PRESERVATION_ONLY' and
            contract['preservation_execution_permitted'] is True and contract['preservation_only'] is True,
            'exact frozen production source/proposal permission binding')
    mutable={'source_files_SHA256','status','preservation_execution_permitted','chunks'}
    require(all(contract[k]==v for k,v in preparation.items() if k not in mutable),
            'complete unchanged accepted preparation scope/history/providers')
    s.validate_scope(contract['chunks'],contract['protected_entries'],contract['previously_replaced_paths'])
    for row,original in zip(contract['chunks'],preparation['chunks']):
        require(set(row)==set(original)|{'frame_hashes_SHA256'} and all(row[k]==v for k,v in original.items()),
                'frozen original/ledger row relationship')
c.validate_contract=validate_contract

def validate_claim(claim,prod,ph,ah,authority_hash,pid):
    expected=dict(pid=pid,source_commit=prod['source_commit'],production_proposal_SHA256=ph,
        admission_SHA256=ah,authority_SHA256=authority_hash,limit=1,cap_bytes=CAP,
        actual_available_bytes=claim.get('actual_available_bytes'),terminal_on_failure=True)
    require(claim==expected and type(pid) is int and pid>0 and
            type(claim['actual_available_bytes']) is int and claim['actual_available_bytes']>=CAP,
            'exact exclusive controller claim/source/capacity relationships')

def admission(io,action):
    require(action in ('preserve','verify-zlib','verify-gzip'),'only scoped production actions')
    prod,checked=io.load(PRODUCTION),io.load(ADMISSION); preparation=io.preparation_proposal()
    validate_production(prod,preparation)
    ph,ah=io.digest(PRODUCTION),io.digest(ADMISSION)
    audit=io.load(AUDIT)
    require(checked['actual_protection_readback_SHA256']==io.digest(AUDIT) and
            audit['PASS'] is True and audit['source_commit']==prod['source_commit'] and
            (audit['historical_files'],audit['new_protected_entries'],audit['raw_chunks'],audit['raw_frames'],audit['raw_bytes'])==
            (37000,514,13,24207,2788646400) and audit['actual_codec_passes']==audit['real_unlinks']==0,
            'complete actual protection audit/admission/source relationship')
    require(checked['PASS'] is True and checked['source_commit']==prod['source_commit'] and
            checked['production_proposal_SHA256']==ph and checked['execution_permitted'] is False and
            checked['source_files_SHA256']==prod['source_files_SHA256'] and
            checked['direct_production_files_SHA256']==prod['direct_production_files_SHA256'] and
            checked['actual_historical_files_verified']==37000 and checked['real_unlinks']==checked['real_codecs']==0,
            'exact production offline admission/closure/protection relationships')
    require(io.load(AUTHORITY)==authority_template(prod,ph,ah),'CLOSED: separate exact one-use preservation authority required')
    io.permission_check(); io.source_check_proposal(prod); io.provider_check(prod)
    require(not io.exists(OUT/STOP) and not io.exists(OUT/'preservation-result-private.json'),'terminal result/STOP cannot resume')
    if action=='preserve': require(not io.exists(OUT),'one fresh output/exclusive controller claim')
    else: require(io.exists(OUT/CLAIM),'actual controller claim required before verifier')
    io.metadata_check(); require(io.available()>=CAP,'fresh full 2941345792-byte preservation capacity')
    return preparation,prod,ph,ah

class AggregateBudget(e.Budget):
    def __init__(self,io): super().__init__(OUT,cap=CAP,reserve=s.AUDIT_RESERVE); self.io=io
    def check(self,extra=0):
        self.io.metadata_check(); u=e.usage(OUT)
        external=self.io.external_usage()
        require(max(u.values())+max(external.values())+s.AUDIT_RESERVE+extra<=CAP,'full aggregate explicit cap exceeded')
        return u

class LocalIO:
    def __init__(self): self.owned=False; self.contract=None; self.removed=[]; self.ticket=None
    load=staticmethod(read); digest=staticmethod(e.digest); identity=staticmethod(e.identity)
    exists=staticmethod(lambda p:os.path.lexists(p))
    preparation_proposal=staticmethod(accepted_inputs)
    provider_check=staticmethod(provider_check)
    metadata_check=staticmethod(metadata_usage)
    def permission_check(self):
        for path in (PRODUCTION,ADMISSION,AUTHORITY):
            row=e.identity(path)
            require(row['uid']==os.geteuid() and row['mode']==0o600 and path.stat().st_nlink==1,
                    'private owned single-link proposal/admission/authority')
        if OUT.exists(): require(stat.S_IMODE(OUT.stat().st_mode)==0o700,'private output mode700')
    def available(self):
        v=os.statvfs(s.SCRATCH); require(v.f_frsize==4096 and not v.f_flag&os.ST_RDONLY,'same writable block4096 workspace')
        return v.f_bavail*v.f_frsize
    def source_check_proposal(self,prod):
        require(b.git('rev-parse','HEAD')==prod['source_commit'] and not b.git('status','--porcelain') and
                b.git('ls-remote','--heads','origin','task/floor1-c01-warden-continuation-offline')==
                prod['source_commit']+'\trefs/heads/task/floor1-c01-warden-continuation-offline', 'exact clean published source')
        require(dict(os.environ)==prod['environment'],'exact process provider environment; no inherited overrides')
        for rel,pin in prod['source_files_SHA256'].items(): require(e.digest(ROOT/rel)==pin,'production source changed')
    def external_usage(self):
        paths=[p for root in ROOTS[:-1] if root.exists() for p in (root,*root.rglob('*'))]
        if AUTHORITY.exists(): paths.append(AUTHORITY)
        return dict(logical_bytes=sum(p.stat().st_size for p in paths if p.is_file()),
                    allocated_bytes=sum(p.stat().st_blocks*512 for p in paths))
    def attach(self,contract):
        self.contract=contract; self.preparation=self.external_usage(); self.budget=AggregateBudget(self)
    def usage(self): self.preparation=self.external_usage(); return self.budget.check()
    def read(self,name): return read(OUT/name)
    def source_check(self,contract):
        prod=contract['production_proposal']; self.source_check_proposal(prod); provider_check(prod)
        require(self.digest(PRODUCTION)==contract['approved_production_proposal_SHA256'] and
                self.digest(ADMISSION)==contract['controller_admission_SHA256'] and
                self.digest(AUTHORITY)==contract['execution_authority_SHA256'] and not self.exists(OUT/STOP),
                'immutable authority/admission/production/terminal state')
        require(self.load(AUTHORITY)==authority_template(prod,self.digest(PRODUCTION),self.digest(ADMISSION)), 'unchanged authority')
        require(self.load(ADMISSION)['actual_protection_readback_SHA256']==self.digest(AUDIT), 'unchanged actual protection audit')
        claim=self.read(CLAIM)
        validate_claim(claim,prod,self.digest(PRODUCTION),self.digest(ADMISSION),self.digest(AUTHORITY),claim['pid'])
    def protected_check(self,contract):
        for path,entry in contract['protected_entries'].items(): check_entry(path,entry)
        for row in contract['recordings']: e.index_check(Path(row['index_path']),row['frames'])
        referenced_protection(contract)
        require(all(not os.path.lexists(p) for p in contract['previously_replaced_paths']), 'historical replaced operands remain absent')
    check_raw=staticmethod(s.check_entry)
    sync_file=PRIMITIVES.sync_file
    sync_dir=PRIMITIVES.sync_dir
    def json(self,name,value,failure=False):
        data=encoded(value); metadata_usage(len(data),1,failure)
        require(len(data)<=4*1024**2,'bounded production receipt')
        if failure: require(len(data)<=STOP_BYTES,'reserved bounded terminal failure evidence')
        path=OUT/name; require(path.parent==OUT,'receipt path boundary')
        with path.open('xb') as file:
            os.fchmod(file.fileno(),0o600); file.write(data); file.flush(); os.fsync(file.fileno())
        self.sync_dir(OUT); metadata_usage(failure=failure)
    def claim(self,value):
        OUT.mkdir(mode=0o700); self.owned=True
        (OUT/'Warden-continuation-PASS').mkdir(mode=0o700)
        self.json(CLAIM,value); self.sync_dir(OUT.parent)
    def ledger(self,row):
        self.check_raw(row); hashes=bytearray(); whole=hashlib.sha256()
        with Path(row['raw_path']).open('rb') as file:
            for _ in range(row['frames']):
                frame=e.read_exact(file,s.FRAME); require(len(frame)==s.FRAME,'complete ledger frame')
                whole.update(frame); hashes.extend(hashlib.sha256(frame).digest())
            require(not file.read(1) and whole.hexdigest()==row['raw_SHA256'],'original exact chunk hash/EOF')
        self.check_raw(row); self.budget.write(OUT/row['frame_hashes_relative_path'],hashes)
        return hashlib.sha256(hashes).hexdigest()
    def compress(self,row): e.compress_once(Path(row['raw_path']),OUT/row['compressed_relative_path'],self.budget)
    def verify_chunk(self,row,action):
        return e.verify_chunk(row,OUT,e.zlib_blocks if action=='verify-zlib' else e.gzip_blocks)
    def unlink_raw(self,row):
        require(self.ticket is not None and self.ticket.consumed and self.ticket.io is self,'barrier-controlled unlink only')
        require(row['raw_path'] in {x['raw_path'] for x in s.definitions()},'only thirteen originals')
        return PRIMITIVES.unlink_raw(self,row)
    def run_verifier(self,action,prod):
        require(self.available()>=CAP,'fresh cap immediately before verifier creation')
        path=OUT/(action+'.log'); metadata_usage(65536,2)
        with path.open('xb') as log:
            os.fchmod(log.fileno(),0o600)
            process=subprocess.Popen([b.provider('python3'),'-B',str(ROOT/'scripts/preserve-warden-rgb-r1.py'),action],
                cwd=ROOT,env=prod['environment'],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT)
            try:
                self.json(action+'-started-private.json',dict(pid=process.pid,controller_PID=os.getpid(),action=action,
                    source_commit=prod['source_commit'],contract_SHA256=self.digest(OUT/c.CONTRACT_NAME)))
                process.stdin.write(b'GO\n'); process.stdin.close()
                deadline=time.monotonic()+1800
                while process.poll() is None:
                    require(time.monotonic()<deadline and path.stat().st_size<=65536,'verifier bounded wall/log')
                    self.usage()
                    try: process.wait(timeout=1)
                    except subprocess.TimeoutExpired: pass
                require(process.returncode==0,'fresh verifier failed; terminal/no retry')
            finally:
                if process.poll() is None: process.kill(); process.wait()
            log.flush(); os.fsync(log.fileno())
        require(path.stat().st_size<=65536,'bounded verifier log'); self.usage()
    pid=staticmethod(os.getpid); ppid=staticmethod(os.getppid)

def worker(io,action,preparation,prod):
    number=0 if action=='verify-zlib' else 1
    contract=io.read(c.CONTRACT_NAME); mapping=io.read(c.MAPPING_NAME); c.validate_contract(contract,preparation)
    io.attach(contract); io.source_check(contract); c.validate_mapping(contract,mapping,io.digest(OUT/c.CONTRACT_NAME))
    claim=io.read(CLAIM); operation=io.read('operation-start-private.json'); started=io.read(action+'-started-private.json')
    validate_claim(claim,prod,io.digest(PRODUCTION),io.digest(ADMISSION),io.digest(AUTHORITY),io.ppid())
    require(operation['pid']==io.ppid()==claim['pid'] and operation['source_commit']==prod['source_commit'] and
            operation['contract_SHA256']==io.digest(OUT/c.CONTRACT_NAME) and
            started==dict(pid=io.pid(),controller_PID=io.ppid(),action=action,source_commit=prod['source_commit'],
                          contract_SHA256=io.digest(OUT/c.CONTRACT_NAME)) and
            not io.exists(OUT/c.RECEIPT_NAMES[number]), 'one actual fresh exact verifier child')
    io.owned=True; io.protected_check(contract)
    results=[]
    for row in mapping['chunks']: io.check_raw(row); results.append(io.verify_chunk(row,action)); io.usage()
    io.protected_check(contract)
    receipt=dict(PASS=True,verification=c.LABELS[number],pid=io.pid(),controller_PID=io.ppid(),
        source_commit=prod['source_commit'],fresh_verifier_process=True,no_second_full_decoded_copy=True,
        contract_SHA256=io.digest(OUT/c.CONTRACT_NAME),mapping_SHA256=io.digest(OUT/c.MAPPING_NAME),
        chunks=results,chunk_count=13,frames=24207,decoded_bytes=2788646400,originals_retained=True)
    s.accepted.receipt_check(receipt,c.LABELS[number],io.digest(OUT/c.CONTRACT_NAME),io.digest(OUT/c.MAPPING_NAME),mapping['chunks'])
    io.json(c.RECEIPT_NAMES[number],receipt)

def preserve(io,preparation,prod,ph,ah):
    io.protected_check(preparation)
    for row in preparation['chunks']: io.check_raw(row)
    fresh=io.available(); require(fresh>=CAP,'fresh full cap immediately before exclusive claim')
    io.claim(dict(pid=io.pid(),source_commit=prod['source_commit'],production_proposal_SHA256=ph,
        admission_SHA256=ah,authority_SHA256=io.digest(AUTHORITY),limit=1,cap_bytes=CAP,
        actual_available_bytes=fresh,terminal_on_failure=True))
    contract=copy.deepcopy(preparation)
    contract.update(approved_proposal_SHA256=PREP_SHA,approved_production_proposal_SHA256=ph,
        production_proposal=prod,preservation_only=True,preservation_source_commit=prod['source_commit'],
        source_files_SHA256=prod['source_files_SHA256'],status='FROZEN_LOCAL_PRESERVATION_ONLY',
        preservation_execution_permitted=True,controller_admission_SHA256=ah,execution_authority_SHA256=io.digest(AUTHORITY))
    io.attach(contract)
    for row in contract['chunks']: row['frame_hashes_SHA256']=io.ledger(row)
    c.validate_contract(contract,preparation); io.json(c.CONTRACT_NAME,contract); io.source_check(contract)
    fresh=io.available(); require(fresh>=CAP,'fresh cap before fixed compression operation')
    io.json('operation-start-private.json',dict(pid=io.pid(),source_commit=prod['source_commit'],
        contract_SHA256=io.digest(OUT/c.CONTRACT_NAME),preservation_only=True,available_workspace_bytes_before_operation=fresh))
    mapping=dict(contract_SHA256=io.digest(OUT/c.CONTRACT_NAME),proposal_SHA256=PREP_SHA,cap_bytes=CAP,output_root=str(OUT),chunks=[])
    for original in contract['chunks']:
        row=dict(original); io.check_raw(row); io.compress(row); io.check_raw(row)
        row.update(compressed_identity=io.identity(OUT/row['compressed_relative_path']),compressed_SHA256=io.digest(OUT/row['compressed_relative_path']))
        mapping['chunks'].append(row); io.usage()
    c.validate_mapping(contract,mapping,io.digest(OUT/c.CONTRACT_NAME)); io.json(c.MAPPING_NAME,mapping)
    for action in ('verify-zlib','verify-gzip'): io.run_verifier(action,prod)
    one,two=(io.read( name) for name in c.RECEIPT_NAMES)
    ticket=c.synchronize_barrier(io,contract,preparation,mapping,one,two); io.ticket=ticket
    accounting=c.replace_originals(io,ticket,contract,preparation,mapping,one,two)
    after=io.available(); delta=c.measured_space_savings(fresh,after)
    io.json('preservation-result-private.json',dict(PASS=True,source_commit=prod['source_commit'],
        production_proposal_SHA256=ph,contract_SHA256=io.digest(OUT/c.CONTRACT_NAME),mapping_SHA256=io.digest(OUT/c.MAPPING_NAME),
        verifier_receipt_SHA256=[io.digest(OUT/n) for n in c.RECEIPT_NAMES],verifier_PIDs=[one['pid'],two['pid']],
        replaced_files=13,replaced_paths=io.removed,raw_bytes=2788646400,frames=24207,cap_bytes=CAP,
        accounting=accounting,measured_available_bytes_increase=delta,runtime='CLOSED',runtime_capacity_admitted=False))

def dispatch(action,io=None):
    io=LocalIO() if io is None else io
    try:
        preparation,prod,ph,ah=admission(io,action)
        if action=='preserve': preserve(io,preparation,prod,ph,ah)
        else: worker(io,action,preparation,prod)
    except Exception as error:
        if io.owned and not io.exists(OUT/STOP):
            message=type(error).__name__+': '+str(error)
            io.json(STOP,dict(PASS=False,action=action,error=message[:1500],error_SHA256=hashlib.sha256(message.encode()).hexdigest(),
                retained_original_paths=[r['raw_path'] for r in s.definitions() if io.raw_exists(r)],
                first_failure_terminal=True,retry=False,partial_outputs_retained=True,runtime='CLOSED'),failure=True)
        raise
LocalIO.raw_exists=staticmethod(lambda row:os.path.lexists(row['raw_path']))
for name in ('LocalIO','freeze','execute','verify_worker','run_verifier','admission','accepted_inputs','record_stop'):
    setattr(c,name,s.closed)
