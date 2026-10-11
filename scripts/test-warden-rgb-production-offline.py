#!/usr/bin/env python3
"""One newly named bounded production-entrypoint suite; every operation is inert."""
from pathlib import Path
import copy, hashlib, importlib.util, json, os, resource, signal, time

spec=importlib.util.spec_from_file_location('warden_wiring_test',Path(__file__).resolve().parent/'floor1/warden-rgb-production.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

def write(name,value):
    data=p.encoded(value); p.metadata_usage(len(data),1)
    with (p.OFFLINE/name).open('xb') as file:
        os.fchmod(file.fileno(),0o600); file.write(data); file.flush(); os.fsync(file.fileno())

class InertIO:
    """Only dictionaries/lists and small explicitly labelled protection fixtures."""
    def __init__(self,preparation,prod,checked,fixtures):
        self.prep=copy.deepcopy(preparation); self.prod=copy.deepcopy(prod)
        self.files={str(p.PRODUCTION):p.encoded(prod),str(p.ADMISSION):p.encoded(checked)}
        self.files[str(p.AUDIT)]=p.AUDIT.read_bytes()
        self.files[str(p.AUTHORITY)]=p.encoded(p.authority_template(prod,self.digest(p.PRODUCTION),self.digest(p.ADMISSION)))
        self.directories=set(); self.identities={}; self.owned=False; self.removed=[]; self.ticket=None
        self.actor=100; self.parent=99; self.free=5*1024**3; self.contract=None
        self.flags=set(); self.corrupt_second={}; self.corrupt_result=None; self.corrupt_mapping=False
        self.fixtures=fixtures; self.sync_files=[]; self.sync_dirs=[]; self.fail_sync_at=None; self.fail_dir_at=None
    def load(self,path): return json.loads(self.files[str(path)])
    def read(self,name): return self.load(p.OUT/name)
    def digest(self,path): return hashlib.sha256(self.files[str(path)]).hexdigest()
    def identity(self,path): return self.identities[str(path)]
    def exists(self,path): return str(path) in self.files or str(path) in self.directories
    def preparation_proposal(self): return copy.deepcopy(self.prep)
    def permission_check(self): p.require('permission' not in self.flags,'inert wrong permissions')
    def source_check_proposal(self,prod):
        p.require('source' not in self.flags and prod['source_commit']==self.prod['source_commit'], 'inert changed source')
    def provider_check(self,prod):
        p.require('provider' not in self.flags and prod['codec']==self.prod['codec'], 'inert changed provider/environment')
    def metadata_check(self):
        p.metadata_usage(extra_files=64 if 'metadata' in self.flags else 0)
    def available(self):
        if 'capacity' in self.flags: return p.CAP-1
        if self.removed:
            return self.free+sum(r['raw_identity']['allocated_bytes'] for r in self.prep['chunks'])-8*1024**2
        return self.free
    def pid(self): return self.actor
    def ppid(self): return self.parent
    def raw_exists(self,row): return row['raw_path'] not in self.removed
    def claim(self,value):
        self.directories.update((str(p.OUT),str(p.OUT/'Warden-continuation-PASS')))
        self.owned=True; self.json(p.CLAIM,value)
    def attach(self,contract):
        self.contract=contract; u=p.metadata_usage()
        self.preparation=dict(logical_bytes=u['logical_bytes'],allocated_bytes=u['allocated_bytes'])
    def source_check(self,contract):
        self.source_check_proposal(contract['production_proposal']); self.provider_check(contract['production_proposal'])
        p.require(not self.exists(p.OUT/p.STOP),'inert terminal source gate')
        p.require(self.load(p.AUTHORITY)==p.authority_template(self.prod,self.digest(p.PRODUCTION),self.digest(p.ADMISSION)),
                  'inert authority changed')
        p.validate_claim(self.read(p.CLAIM),self.prod,self.digest(p.PRODUCTION),self.digest(p.ADMISSION),self.digest(p.AUTHORITY),100)
    def protected_check(self,contract):
        if 'reference' in self.flags: p.check_entry(*self.fixtures['reference-altered'])
        if 'protected-file' in self.flags: p.check_historical_record(self.fixtures['file-altered'])
        p.require('protection' not in self.flags,'inert protected file changed')
    def check_raw(self,row): p.require('raw' not in self.flags and self.raw_exists(row),'inert changed/missing raw')
    def ledger(self,row):
        data=b'L'*(32*row['frames']); path=str(p.OUT/row['frame_hashes_relative_path'])
        self.files[path]=data; self.identities[path]=dict(bytes=len(data))
        return hashlib.sha256(data).hexdigest()
    def compress(self,row):
        p.require('compress-failure' not in self.flags,'inert first compression failure')
        data=b'INERT-NOT-GZIP-'+str(row['chunk']).encode(); path=str(p.OUT/row['compressed_relative_path'])
        self.files[path]=data
        self.identities[path]=dict(device=27,inode=1000+row['chunk'],bytes=len(data),allocated_bytes=4096,mode=0o600,uid=1000,mtime_ns=1)
    def usage(self):
        if 'no-savings' in self.flags: return dict(logical_bytes=p.s.RAW_BYTES,allocated_bytes=p.s.RAW_BYTES)
        if 'output-cap' in self.flags: return dict(logical_bytes=p.CAP,allocated_bytes=p.CAP)
        output=[data for path,data in self.files.items() if path.startswith(str(p.OUT)+'/')]
        return dict(logical_bytes=sum(len(data) for data in output),allocated_bytes=sum(p.s.round_block(len(data)) for data in output))
    def json(self,name,value,failure=False):
        path=str(p.OUT/name); p.require(path not in self.files,'exclusive inert persisted receipt')
        if failure: p.require(len(p.encoded(value))<=p.STOP_BYTES,'bounded inert STOP')
        else: self.metadata_check()
        self.files[path]=p.encoded(value)
        if name==p.c.MAPPING_NAME and self.corrupt_mapping:
            wrong=copy.deepcopy(value); wrong['chunks'].pop(); self.files[path]=p.encoded(wrong)
        if name=='synchronization-complete-private.json':
            self.sync_file(Path(path)); self.sync_dir(p.OUT)
    def verify_chunk(self,row,action):
        return dict(recording=row['recording'],chunk=row['chunk'],frames=row['frames'],raw_SHA256=row['raw_SHA256'],
            compressed_SHA256=row['compressed_SHA256'],exact_frame_bytes=True,exact_EOF='EOF' not in self.flags)
    def run_verifier(self,action,prod):
        child=101 if action=='verify-zlib' or 'same-child' in self.flags else 102
        self.json(action+'-started-private.json',dict(pid=child,controller_PID=100,action=action,
            source_commit=prod['source_commit'],contract_SHA256=self.digest(p.OUT/p.c.CONTRACT_NAME)))
        self.files[str(p.OUT/(action+'.log'))]=b'INERT CHILD ONLY\n'
        old_actor,old_parent=self.actor,self.parent; self.actor,self.parent=child,100
        try: p.dispatch(action,self)
        finally: self.actor,self.parent=old_actor,old_parent
        if action=='verify-gzip':
            name=p.c.RECEIPT_NAMES[1]; receipt=self.read(name); receipt.update(self.corrupt_second)
            if self.corrupt_result: self.corrupt_result(receipt)
            self.files[str(p.OUT/name)]=p.encoded(receipt)
    def sync_file(self,path):
        p.require(not self.removed,'sync before every virtual removal')
        self.sync_files.append(str(path)); self.digest(path)
        if len(self.sync_files)==self.fail_sync_at: raise OSError('inert fsync failure')
    def sync_dir(self,path):
        self.sync_dirs.append(str(path))
        if len(self.sync_dirs)==self.fail_dir_at: raise OSError('inert directory fsync failure')
    def unlink_raw(self,row):
        p.require(self.ticket is not None and self.ticket.consumed,'one-use barrier before virtual unlink')
        self.check_raw(row); self.removed.append(row['raw_path'])

def main():
    p.require(not p.OFFLINE.exists() and not p.OUT.exists() and not p.AUTHORITY.exists(),'new bounded suite; actual execution absent')
    p.OFFLINE.mkdir(mode=0o700)
    preparation=p.accepted_inputs(); prod=p.build_proposal(preparation); p.validate_production(prod,preparation)
    p.provider_check(prod)
    # Actual evidence checks run once, independently of all in-memory scenarios.
    started=time.monotonic(); actual=p.LocalIO(); actual.protected_check(preparation)
    for row in preparation['chunks']: p.s.check_entry(row)
    for path,pin in preparation['actual_provider_files_SHA256'].items():
        p.require(p.e.digest(Path(path))==pin,'actual Warden tooling manifest')
    write('actual-protection-readback-private.json',dict(PASS=True,source_commit=prod['source_commit'],
        historical_files=37000,new_protected_entries=514,raw_chunks=13,raw_frames=24207,raw_bytes=2788646400,
        seconds=time.monotonic()-started,actual_codec_passes=0,real_unlinks=0))
    write('production-proposal-private.json',prod)
    checked=dict(PASS=True,source_commit=prod['source_commit'],production_proposal_SHA256=p.e.digest(p.PRODUCTION),
        source_files_SHA256=prod['source_files_SHA256'],direct_production_files_SHA256=prod['direct_production_files_SHA256'],
        actual_historical_files_verified=37000,real_unlinks=0,real_codecs=0,execution_permitted=False,
        actual_protection_readback_SHA256=p.e.digest(p.AUDIT))
    fixtures={}
    for name,content in (('reference-altered',b'ref'),('file-altered',b'keep'),('file-unchanged',b'keep')):
        path=p.OFFLINE/(name+'.fixture')
        with path.open('xb') as file: os.fchmod(file.fileno(),0o600); file.write(content)
        entry=dict(identity=p.e.identity(path),SHA256=p.e.digest(path))
        row=dict(path=str(path),identity=p.b.retention.identity(path),SHA256=p.e.digest(path))
        if name.endswith('altered'):
            with path.open('wb') as file: file.write(b'changed')
        fixtures[name]=(path,entry) if name.startswith('reference') else row
    p.check_historical_record(fixtures['file-unchanged'])
    cases=[]; negatives=[]
    def reject(name,mutate=None,action='preserve'):
        io=InertIO(preparation,prod,checked,fixtures)
        if mutate: mutate(io)
        try: p.dispatch(action,io)
        except (RuntimeError,OSError,KeyError,ValueError) as error:
            p.require(not io.removed,'negative performed premature virtual unlink')
            if io.owned:
                stop=io.read(p.STOP); p.require(stop['first_failure_terminal'] and stop['retry'] is False and
                    len(stop['retained_original_paths'])==13,'complete retained first-failure evidence')
                old=io.digest(p.OUT/p.STOP)
                try: p.dispatch('preserve',io)
                except (RuntimeError,OSError,KeyError,ValueError): pass
                else: raise AssertionError('terminal operation resumed')
                p.require(io.digest(p.OUT/p.STOP)==old,'immutable first failure')
            cases.append(name); negatives.append(dict(case=name,error=type(error).__name__+': '+str(error),
                claimed=io.owned,remaining_originals=13,virtual_unlinks=0))
        else: raise AssertionError('negative accepted: '+name)
    def edit(io,path,mutation):
        value=io.load(path); mutation(value); io.files[str(path)]=p.encoded(value)
    reject('authority-absent',lambda io:io.files.pop(str(p.AUTHORITY)))
    reject('authority-wrong-scope',lambda io:edit(io,p.AUTHORITY,lambda x:x.update(chunk_count=17)))
    reject('audit-count',lambda io:edit(io,p.AUDIT,lambda x:x.update(historical_files=36999)))
    reject('audit-relationship',lambda io:edit(io,p.ADMISSION,lambda x:x.update(actual_protection_readback_SHA256='wrong')))
    for key,value in (('chunk_count',17),('frames',28700),('raw_bytes',3306240000),('cap_bytes',3459215360),
                      ('output_root','/tmp/wrong'),('preparation_proposal_SHA256','wrong'),('actual_runtime_handoff_SHA256','wrong')):
        reject('production-'+key,lambda io,key=key,value=value:edit(io,p.PRODUCTION,lambda x:x.update({key:value})))
    reject('missing-inherited-closure',lambda io:edit(io,p.PRODUCTION,lambda x:x['source_files_SHA256'].pop(x['inherited_source_files'][0])))
    reject('unlike-four-file-admission',lambda io:edit(io,p.ADMISSION,lambda x:x.update(source_files_SHA256={k:preparation['source_files_SHA256'][k] for k in p.s.FILES})))
    reject('wrong-direct-production-set',lambda io:edit(io,p.PRODUCTION,lambda x:x['direct_production_files_SHA256'].pop(p.FILES[0])))
    reject('codec-settings',lambda io:edit(io,p.PRODUCTION,lambda x:x['codec']['compress_command'].append('-9')))
    reject('altered-provider-pin',lambda io:edit(io,p.PRODUCTION,lambda x:x['codec'].update(gzip_executable_SHA256='wrong')))
    for flag in ('provider','permission','source','capacity','metadata','reference','protected-file','protection','raw',
                 'compress-failure','same-child','EOF','no-savings','output-cap'):
        reject(flag,lambda io,flag=flag:io.flags.add(flag))
    reject('incomplete-mapping',lambda io:setattr(io,'corrupt_mapping',True))
    for key,value in (('PASS',False),('chunk_count',12),('frames',24206),('decoded_bytes',2788646399),
        ('originals_retained',False),('contract_SHA256','wrong'),('mapping_SHA256','wrong'),('pid',0),
        ('pid',100),('controller_PID',999),('source_commit','wrong'),('fresh_verifier_process',False),
        ('no_second_full_decoded_copy',False)):
        reject('second-proof-'+key,lambda io,key=key,value=value:io.corrupt_second.update({key:value}))
    reject('partial-byte-proof',lambda io:setattr(io,'corrupt_result',lambda x:x['chunks'][0].update(exact_frame_bytes=False)))
    reject('proof-order',lambda io:setattr(io,'corrupt_result',lambda x:x['chunks'].reverse()))
    # Fault every inherited+new synchronized proof boundary, including completion.
    sync_bound=9+2*13+5+1
    for at in range(1,sync_bound+1): reject('fsync-'+str(at),lambda io,at=at:setattr(io,'fail_sync_at',at))
    for at in range(1,7): reject('directory-fsync-'+str(at),lambda io,at=at:setattr(io,'fail_dir_at',at))
    reject('worker-without-claim',action='verify-zlib')
    io=InertIO(preparation,prod,checked,fixtures); p.dispatch('preserve',io)
    result=io.read('preservation-result-private.json')
    p.require(result['replaced_files']==13 and result['frames']==24207 and result['raw_bytes']==2788646400 and
        result['cap_bytes']==p.CAP and result['verifier_PIDs']==[101,102] and
        io.removed==[r['raw_path'] for r in preparation['chunks']], 'complete positive real-entrypoint inert lifecycle')
    cases.append('positive-gated-inert-controller-and-two-workers-13-only')
    try: p.c.replace_originals(io,io.ticket,io.contract,preparation,io.read(p.c.MAPPING_NAME),io.read(p.c.RECEIPT_NAMES[0]),io.read(p.c.RECEIPT_NAMES[1]))
    except RuntimeError: cases.append('one-use-removal-ticket')
    else: raise AssertionError('one-use ticket replay accepted')
    p.require(not p.OUT.exists() and not p.AUTHORITY.exists(),'no actual preservation output/authority')
    checked.update(case_count=len(cases),negative_count=len(negatives),cases=cases,negative_receipts=negatives,
        sync_file_boundaries_faulted=sync_bound,sync_directory_boundaries_faulted=6,actual_new_controller_processes=0,actual_new_verifier_processes=0,
        real_compressions=0,actual_claims=0,actual_freezes=0,gameplay_processes=0,
        actual_protection_readback_SHA256=p.e.digest(p.OFFLINE/'actual-protection-readback-private.json'),
        metadata=p.metadata_usage(),first_failure_terminal=True,retry=False,wall_bound_seconds=300,
        scoped_V01_pair_PR114_technical_accepted=True,broader_human_legacy_C01_gates_open=True)
    write('production-admission-private.json',checked)
    p.require(not p.b.git('status','--porcelain'),'tested committed source unchanged')
    print('PASS',len(cases),'new production-entrypoint cases;',len(negatives),'negatives; actual protected37000+514; codecs/unlinks=0')

if __name__=='__main__':
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('300-second bounded offline wiring suite')))
    signal.alarm(300)
    try: main()
    except Exception as error:
        if p.OFFLINE.exists():
            data=p.encoded(dict(PASS=False,error=type(error).__name__+': '+str(error),retry=False,partial_outputs_retained=True))
            p.metadata_usage(len(data),1,failure=True)
            with (p.OFFLINE/'offline-wiring-STOP-private.json').open('xb') as file:
                os.fchmod(file.fileno(),0o600); file.write(data); file.flush(); os.fsync(file.fileno())
        raise
