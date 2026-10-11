#!/usr/bin/env python3
"""One fresh bounded inert cold-only suite. Never invokes an observer or runtime stage."""
from pathlib import Path
import ast, contextlib, copy, hashlib, importlib.util, json, os, resource, signal, struct, time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cold_offline', ROOT/'scripts/floor1/warden-cold-only-supervisor-r1.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
CAP, FILE_CAP, SECONDS = 64*1024**2, 8*1024**2, 300

def write(name, value):
    data = (json.dumps(value, sort_keys=True)+'\n').encode()
    usage = sum(x.stat().st_blocks*512 for x in w.OFFLINE.rglob('*') if x.is_file())
    w.require(len(data) <= FILE_CAP and usage+len(data)+2*1024**2 < CAP, 'bounded offline evidence with STOP reserve')
    w.old.write(w.OFFLINE/name, value)

class ModelIO:
    """Only Python objects and read-only earned state; no native or runtime writes."""
    def __init__(self, proposal, before):
        self.proposal = copy.deepcopy(proposal)
        self.current = copy.deepcopy(proposal)
        self.receipt = dict(PASS=True, source_commit=proposal['source_commit'], proposal=self.proposal,
            proposal_SHA256=w.old.digest(self.proposal), positive_first=True, execution_permitted=False)
        self.receipt_sha = 'e'*64
        self.approval = w.authority_template(self.receipt, self.receipt_sha)
        self.present, self.events = set(), []
        self.expected, self.state = copy.deepcopy(before), copy.deepcopy(before)
        self.free, self.exit_seconds, self.exit_code = w.old.RESERVATION, 10.0, 0
        self.created_process, self.result, self.failure = None, None, None
        self.authority_missing = False
        self.footer = 'PASS full native Warden continuation cold\nCONTINUOUS frames=2044 valid=1 deferred=2043 attempts=0 per-encounter=0,0,0,0\nresult=0 assertions=1\n'
        self.save = w.SAVE
        self.change_result = None
        self.fail_start_record = False
    def authority(self):
        w.require(not self.authority_missing, 'CLOSED: model authority absent')
        return self.receipt
    def locked(self): return contextlib.nullcontext()
    def admit(self, receipt):
        w.validate_gate(self.proposal, self.current, self.approval, receipt, self.receipt_sha, self.present)
        self.events.append('admission')
        return dict(source_commit=receipt['source_commit'])
    def inputs(self, frozen):
        self.present.add(w.MODE)
        self.events.append('earned-Save/state-copy')
    def claim(self, frozen):
        w.require('exclusive-claim.json' not in self.present, 'model second claim')
        self.present.add('exclusive-claim.json')
        self.events.append('exclusive-claim')
    def launch(self, receipt, frozen, clock):
        self.events.append('fresh-full-capacity')
        w.old.capacity(self.free)
        def factory(*args, **kwargs):
            self.events.append('one-native-creation')
            self.created_process = SimpleNamespace(pid=999999, poll=lambda:0, wait=lambda: self.exit_code)
            return self.created_process
        with patch.object(w.timing.time, 'monotonic', return_value=1000.0):
            process = w.timing.create_process(['SYNTHETIC-NO-OBSERVER'], lifecycle_clock=clock, process_factory=factory)
        if self.fail_start_record: raise OSError('SYNTHETIC start-record failure after creation')
        return process
    def wait(self, process, clock):
        with patch.object(w.timing.time, 'monotonic', return_value=1000.0+self.exit_seconds):
            code = w.timing.wait_process(process, clock)
        self.events.append('native-exit')
        return code
    def native_result(self, receipt, process):
        footer = w.parse_footer(self.footer)
        w.require(w.sha(self.save) == w.SAVE_SHA, 'unchanged model Save checksum')
        w.old.state.cold_equivalence(self.expected, self.state, self.save)
        files = {name:'a'*64 for name in w.NATIVE_FILES}
        files['game.sav'], files['expected-final-state.bin'] = w.SAVE_SHA, w.STATE_SHA
        result = dict(footer=footer, captures=dict(frames=2044, index_SHA256='a'*64,
            motion_SHA256={'motion-000.rgb':'a'*64, 'motion-001.rgb':'a'*64},
            captures_SHA256={'cold.ppm':'a'*64}), files=files,
            full_14_sector_live_disk_verified=True, unchanged_Save=True)
        if self.change_result: self.change_result(result)
        self.events.append('full-fourteen-sector/state/capture-result')
        return result
    def persist(self, result):
        w.require(self.result is None, 'one modeled result only')
        self.result = copy.deepcopy(result)
        self.present.add('verdict-private.json')
        self.events.append('complete-result')
    def stop(self, process):
        if process is not None: self.events.append('stop/reap-owned-process')
    def terminal(self, error, process, clock):
        if self.failure is None and 'verdict-private.json' not in self.present:
            self.failure = dict(error=type(error).__name__+': '+str(error), first_failure_terminal=True,
                                retry=False, actual_processes=int(process is not None))
            self.present.add('STOP.json')

def main():
    started = time.monotonic()
    w.require(not any(os.path.lexists(path) for path in (w.OFFLINE,w.OUT,w.AUTHORITY)), 'fresh named offline suite; runtime absent')
    head = w.b.git('rev-parse','HEAD')
    review = w.read(w.REVIEW)
    w.require(review['PASS'] and review['source_commit'] == head and
        review['source_files'] == {rel:w.sha(ROOT/rel) for rel in w.FILES}, 'grouped source/interface/schema audit before suite')
    w.OFFLINE.mkdir(mode=0o700)
    w.old.sync(w.OFFLINE.parent)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('one bounded cold-only offline suite')))
    signal.alarm(SECONDS)
    resource.setrlimit(resource.RLIMIT_FSIZE,(FILE_CAP,FILE_CAP))
    proposal = w.build_proposal()
    write('proposal-private.json', proposal)
    before = w.old.state.snapshot(w.STATE)
    w.old.state.cold_equivalence(before,before,w.SAVE)
    cases, negatives = [], []
    positive = ModelIO(proposal,before)
    result = w.execute(positive)
    w.require(positive.events == ['admission','earned-Save/state-copy','exclusive-claim','fresh-full-capacity',
        'one-native-creation','native-exit','full-fourteen-sector/state/capture-result','complete-result'] and
        positive.result == result and positive.failure is None, 'complete positive modeled cold lifecycle first')
    write('positive-modeled-cold-lifecycle-private.json',dict(PASS=True,model_only=True,
        source_commit=head,proposal_SHA256=w.old.digest(proposal),events=positive.events,result=result,
        actual_authorities=0,actual_freezes=0,actual_claims=0,actual_emulators=0,actual_Save_actions=0,
        complete_before_mutation_negatives=True))
    cases.append('complete positive modeled one-use Continue-only lifecycle before all negatives')
    def reject(name, action):
        try: action()
        except (AssertionError,RuntimeError,OSError,ValueError) as error:
            negatives.append(dict(case=name,error=type(error).__name__+': '+str(error)))
        else: raise AssertionError('accepted invalid cold-only fixture: '+name)
    def mutate(name, change):
        io = ModelIO(proposal,before)
        change(io)
        reject(name,lambda:w.execute(io))
        w.require(io.result is None, 'negative produced accepted cold result')
        if io.failure:
            saved = copy.deepcopy(io.failure)
            reject(name+' terminal second attempt', lambda:w.execute(io))
            w.require(io.failure == saved and io.events.count('one-native-creation') <= 1,
                      'immutable first failure; no second modeled process')
    for name in w.IO_METHODS:
        mutate('missing/noncallable interface '+name, lambda io,name=name:setattr(io,name,None))
    mutate('missing new authority',lambda io:setattr(io,'authority_missing',True))
    for key,bad in (('status','APPROVED_ONE_WARDEN_AND_CONDITIONAL_INDEPENDENT_COLD'),('source_commit','stale'),
        ('claims',2),('encounters',1),('frames',2045),('wall_seconds',601),('parent_review_verified',False),
        ('input_Save_SHA256','changed'),('output_root',str(w.old.OUT)),('offline_receipt_SHA256','changed')):
        mutate('wrong/consumed authority '+key,lambda io,key=key,bad=bad:io.approval.__setitem__(key,bad))
    mutate('authority extra consumed flag',lambda io:io.approval.__setitem__('consumed',True))
    mutate('authority bool cannot replace claim count',lambda io:io.approval.__setitem__('claims',True))
    mutate('authority integer cannot replace approval bool',lambda io:io.approval.__setitem__('parent_review_verified',1))
    for key,bad in (('source_commit','stale'),('source_files',{}),('provider_files',{}),('provider_environment',{}),
                   ('input_Save_SHA256','changed'),('input_state_SHA256','changed'),('lineage',{}),
                   ('representation',{}),('route_SHA256','changed'),('observer_artifacts',{})):
        mutate('stale changed admission '+key,lambda io,key=key,bad=bad:io.current.__setitem__(key,bad))
    mutate('old STOP tampering',lambda io:io.current['lineage'].__setitem__(str(w.old.OUT/'STOP.json'),'changed'))
    mutate('missing compressed evidence mapping',lambda io:io.current['representation'].__setitem__('mapping_SHA256','missing'))
    for marker in ('STOP.json','PREPARATION-STOP.json','exclusive-claim.json',w.MODE,'verdict-private.json'):
        mutate('consumed lifecycle '+marker,lambda io,marker=marker:io.present.add(marker))
    mutate('capacity one byte short',lambda io:setattr(io,'free',w.old.RESERVATION-1))
    mutate('late exit without running poll',lambda io:setattr(io,'exit_seconds',600.001))
    mutate('native exit failure',lambda io:setattr(io,'exit_code',96))
    mutate('start record failure owns created process',lambda io:setattr(io,'fail_start_record',True))
    w.require(positive.result == result, 'original positive result immutable')
    saved_result = copy.deepcopy(positive.result)
    reject('second launch after success',lambda:w.execute(positive))
    w.require(positive.result == saved_result and positive.events.count('one-native-creation') == 1,
              'one process only; no consumed-authority reuse')
    good = ModelIO(proposal,before).footer
    for label,bad in (('encounter',good.replace('attempts=0','attempts=1')),
                     ('battle frame',good.replace('per-encounter=0,0,0,0','per-encounter=0,0,0,1')),
                     ('short route',good.replace('frames=2044','frames=2043').replace('deferred=2043','deferred=2042')),
                     ('long route',good.replace('frames=2044','frames=2045').replace('deferred=2043','deferred=2044')),
                     ('missing helper',good.replace('PASS full native Warden continuation cold\n','')),
                     ('incomplete result',good.replace('result=0 assertions=1\n','')),
                     ('extra EOF',good+'extra\n')):
        mutate('native footer '+label,lambda io,bad=bad:setattr(io,'footer',bad))
    for key in ('party','saved','flags','vars'):
        def change(io,key=key):
            data=bytearray(io.state[key]);data[0]^=1;io.state[key]=bytes(data)
        mutate('full state mismatch '+key,change)
    for key in ('count','saved_count','counter','section','facing'):
        mutate('full state mismatch '+key,lambda io,key=key:io.state.__setitem__(key,io.state[key]+1))
    for flag in (2193,2194):
        def change(io,flag=flag):
            data=bytearray(io.state['flags']);data[flag//8]^=1<<(flag%8);io.state['flags']=bytes(data)
        mutate('exact native TV flag '+str(flag),change)
    def poison(io):
        data=bytearray(io.state['vars']);struct.pack_into('<H',data,0x56,2);io.state['vars']=bytes(data)
    mutate('exact poison counter',poison)
    mutate('canonical resources',lambda io:io.state.__setitem__('logical',b'SYNTHETIC changed canonical resources'))
    for key in ('full_14_sector_live_disk_verified','unchanged_Save'):
        mutate('native complete result '+key,lambda io,key=key:setattr(io,'change_result',lambda result:result.__setitem__(key,False)))
    mutate('missing native file',lambda io:setattr(io,'change_result',lambda result:result['files'].pop('current-state.bin')))
    mutate('missing motion chunk',lambda io:setattr(io,'change_result',lambda result:result['captures']['motion_SHA256'].pop('motion-001.rgb')))
    mutate('capture/file hash mismatch',lambda io:setattr(io,'change_result',lambda result:result['captures']['captures_SHA256'].__setitem__('cold.ppm','changed')))
    # Exact future native PID/claim/capacity bindings, modeled without files or a PID.
    frozen=dict(source_commit=head)
    clock=dict(creation_monotonic=1000.0,termination_monotonic=1010.0)
    pins=dict(freeze='a'*64,binding='b'*64,claim='c'*64,capacity='d'*64)
    records=dict(binding=w.input_binding(proposal),claim=dict(source_commit=head,mode=w.MODE,
        freeze_SHA256=pins['freeze'],input_binding_SHA256=pins['binding'],route_SHA256=w.ROUTE_SHA,limit=1,terminal_on_failure=True),
        capacity=dict(fresh_available_bytes=w.old.RESERVATION,required_bytes=w.old.RESERVATION,source_commit=head,
            mode=w.MODE,measured_time_ns=1,measured_immediately_before_creation=True,prepared_credit=False),
        started=dict(pid=999999,mode=w.MODE,source_commit=head,exclusive_claim_SHA256=pins['claim'],
            capacity_record_SHA256=pins['capacity'],creation_monotonic=1000.0,wall_limit_seconds=600),hashes=pins)
    w.validate_launch_records(records,frozen,positive.receipt,999999,clock)
    cases.append('exact modeled native PID/claim/fresh capacity/input linkage')
    for row,key,bad in (('binding','earned_source','wrong'),('claim','limit',2),('claim','route_SHA256','wrong'),
        ('capacity','fresh_available_bytes',w.old.RESERVATION-1),('capacity','prepared_credit',True),
        ('capacity','measured_immediately_before_creation',False),('started','pid',999998),
        ('started','creation_monotonic',999.0),('started','capacity_record_SHA256','wrong')):
        altered=copy.deepcopy(records);altered[row][key]=bad
        reject('launch evidence '+row+' '+key,lambda altered=altered:w.validate_launch_records(altered,frozen,positive.receipt,999999,clock))
    # Each sector is independently refused by the unchanged real decoder. These
    # labelled copies are test operands, never an earned Save or game output.
    original = w.SAVE.read_bytes()
    latest=max(struct.unpack_from('<I',original,i*4096+0xffc)[0] for i in range(28)
               if struct.unpack_from('<I',original,i*4096+0xff8)[0]==0x08012025)
    sectors={}
    for i in range(28):
        sid,_,signature,count=struct.unpack_from('<HHII',original,i*4096+0xff4)
        if signature==0x08012025 and count==latest and sid<14:sectors[sid]=i
    w.require(set(sectors)==set(range(14)), 'actual fourteen-sector fixture origin')
    for sid,i in sorted(sectors.items()):
        data=bytearray(original);data[i*4096]^=1
        path=w.OFFLINE/('SYNTHETIC-invalid-sector-%02d.sav'%sid)
        with path.open('xb') as file:os.fchmod(file.fileno(),0o600);file.write(data)
        reject('unchanged real validator rejects sector '+str(sid),lambda path=path:w.old.state.disk_equivalence(path,before,([35,4],[8,6])))
        if sid==0:mutate('Save checksum changed',lambda io,path=path:setattr(io,'save',path))
    clock={'creation_monotonic':1000.0};process=SimpleNamespace(poll=lambda:None,wait=lambda:0)
    with patch.object(w.timing.time,'monotonic',return_value=1600.001):
        reject('running timeout',lambda:w.timing.wait_process(process,clock))
    clock={'creation_monotonic':1000.0};polls=iter((None,0));process=SimpleNamespace(poll=lambda:next(polls),wait=lambda:0)
    with patch.object(w.timing.time,'monotonic',side_effect=(1599.999,1600.001)),patch.object(w.timing,'check_root_usage'),patch.object(w.timing.time,'sleep'):
        reject('late exit between polls',lambda:w.timing.wait_process(process,clock))
    # Real fixed-allocation capacity record only in the labelled offline root;
    # the supplied factory is inert and can never launch a native executable.
    events=[]
    def factory(*args,**kwargs):events.append('inert-create');return object()
    with patch.object(w.timing,'OUT',w.OFFLINE),patch.object(w.timing.shutil,'disk_usage',return_value=SimpleNamespace(free=w.old.RESERVATION)):
        w.timing.capacity_before_creation(w.OFFLINE/'SYNTHETIC-capacity-record.json',w.MODE,head,factory,['SYNTHETIC-NO-NATIVE'])
    w.require(events==['inert-create'] and w.read(w.OFFLINE/'SYNTHETIC-capacity-record.json')['fresh_available_bytes']==w.old.RESERVATION,
              'full fresh recorded capacity immediately before inert creation')
    with patch.object(w.timing,'OUT',w.OFFLINE),patch.object(w.timing.shutil,'disk_usage',return_value=SimpleNamespace(free=w.old.RESERVATION-1)):
        reject('real record one byte short cannot create',lambda:w.timing.capacity_before_creation(w.OFFLINE/'SYNTHETIC-short-capacity.json',w.MODE,head,factory,['SYNTHETIC-NO-NATIVE']))
    w.require(events==['inert-create'], 'no creation after capacity refusal')
    reject('missing actual runtime authority',w.LocalIO().authority)
    cases.extend(('real earned Save full state/disk/TV semantics','all fourteen checksum sector negatives',
                  'reviewed creation-through-exit clock including late exit','fixed-allocation fresh capacity before inert factory',
                  'separate authority absent; zero actual runtime outputs'))
    w.require(not w.OUT.exists() and not w.AUTHORITY.exists() and w.sha(w.SAVE)==w.SAVE_SHA and
        w.sha(w.old.OUT/'STOP.json')==w.OLD_STOP_SHA, 'old Save/STOP unchanged; no runtime authority/freeze/claim')
    w.require(w.build_proposal()==proposal, 'actual current inputs/representation/helper closure unchanged after inert suite')
    receipt=dict(PASS=True,source_commit=head,proposal=proposal,proposal_SHA256=w.old.digest(proposal),
        positive_first=True,positive_receipt_SHA256=w.sha(w.OFFLINE/'positive-modeled-cold-lifecycle-private.json'),
        execution_permitted=False,cases=cases,case_count=len(cases),negative_receipts=negatives,
        negative_count=len(negatives),source_review_SHA256=w.sha(w.REVIEW),elapsed_seconds=time.monotonic()-started,
        bounds=dict(internal_seconds=SECONDS,outer_seconds=360,file_bytes=FILE_CAP,total_bytes=CAP),
        actual_runtime_authorities=0,actual_freezes=0,actual_claims=0,actual_emulators=0,actual_Save_actions=0,
        actual_cold_processes=0,actual_game_builds=0,actual_observer_builds=0,actual_codec_runs=0,
        compiler_identity='unchanged pinned recovered binaries; no original historical binary identity claim',
        fresh_capacity_measurement=os.statvfs(w.b.SCRATCH).f_bavail*os.statvfs(w.b.SCRATCH).f_frsize,
        future_capacity_admitted=False,runtime='CLOSED',retry=False)
    write('offline-admission-private.json',receipt)
    write('proposed-contract-private.json',dict(status='OFFLINE_PROPOSED_REVIEW_ONLY',execution_permitted=False,
        contract=proposal['contract'],proposal_SHA256=receipt['proposal_SHA256'],receipt_SHA256=w.sha(w.OFFLINE/'offline-admission-private.json')))
    signal.alarm(0)
    print('PASS one cold-only inert suite:',len(cases),'positive checks;',len(negatives),'expected negatives; runtime=0')
    print('source',head,'proposal',w.sha(w.OFFLINE/'proposal-private.json'),'receipt',w.sha(w.OFFLINE/'offline-admission-private.json'))

if __name__=='__main__':
    try:main()
    except BaseException as error:
        signal.alarm(0)
        if w.OFFLINE.is_dir() and not (w.OFFLINE/'STOP-offline-private.json').exists():
            write('STOP-offline-private.json',dict(PASS=False,error=type(error).__name__+': '+str(error),first_failure_terminal=True,
                retry=False,actual_runtime_authorities=0,actual_freezes=0,actual_claims=0,actual_emulators=0,actual_cold_processes=0))
        raise
