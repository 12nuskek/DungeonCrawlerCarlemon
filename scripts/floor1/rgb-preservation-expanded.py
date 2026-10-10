"""Enumerated expansion of the tested gzip preservation engine; no game imports."""
from pathlib import Path
import importlib.util,json,os,subprocess
ROOT=Path(__file__).resolve().parents[2]
OLD_SOURCE='e5073a511b62041f4356932c7fcc3c355cc3ff76'
OLD_RECEIPTS='dee9076184cedebc72aedc0ae01ac79bd4de0a57'
OUT=Path('/workspace/scratch/floor1-rgb-expanded-preservation-r1-20261010')
PRIOR=Path('/workspace/scratch/c01-rgb-preservation-r1-20261010')
SCRATCH=Path('/workspace/scratch')
spec=importlib.util.spec_from_file_location('unchanged_rgb_engine',ROOT/'scripts/floor1/rgb-preservation.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OLD_FILES=('scripts/floor1/rgb-preservation.py','scripts/preserve-c01-rgb-r1.py','scripts/verify-c01-rgb-r1.py','scripts/test-rgb-preservation-offline.py','docs/floor1/c01-rgb-preservation-r1-contract.md')
NEW_FILES=('scripts/floor1/rgb-preservation-expanded.py','scripts/preserve-floor1-rgb-expanded-r1.py','scripts/test-rgb-preservation-expanded-offline.py','docs/floor1/rgb-expanded-preservation-r1-contract.md')
# label, root, stage, original frames, chunks, retained manifest or summary
PLANS=(('opening1-STOP82','c01-uninterrupted-unprepared-r1-20261010','opening',1538,1,'local-retention-manifest.json'),
       ('opening4-STOP101','c01-guard-choice-opening4-r3-20261010','opening',27144,14,'private-retention-manifest.json'),
       ('opening5-PASS','c01-conserve-medicine-opening5-r1-20261010','opening',34117,18,'private-retention-manifest.json'),
       ('cold1-STOP96','c01-conserve-medicine-opening5-r1-20261010','cold',2044,2,'private-retention-manifest.json'),
       ('cold2-PASS','c01-cold2-continue-r1-20261010','cold',2044,2,'private-retention-manifest.json'),
       ('ordinary-fresh','ordinary-recovery-r5-20261010/prepare-01','fresh',4910,1,'summary.json'),
       ('ordinary-seed-STOP40','ordinary-recovery-r5-20261010/prepare-01','seed',760,1,'summary.json'),
       ('ordinary-setup','ordinary-recovery-r6-20261010/runtime-prepare-03','setup',1644,1,'summary.json'),
       ('ordinary-patrol','ordinary-recovery-r6-20261010/runtime-prepare-03','patrol',7770,1,'summary.json'),
       ('ordinary-cold','ordinary-recovery-r6-20261010/runtime-prepare-03','cold',511,1,'summary.json'))
FRAMES=82482;BYTES=9501926400;CHUNKS=43
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def definitions():
    rows=[]
    for label,base,stage,count,n,manifest in PLANS:
        single=base.startswith('ordinary-');start=1
        for i in range(n):
            frames=count if single else min(2000,count-start+1)
            name='motion.rgb' if single else f'motion-{i:03}.rgb'
            rows.append(dict(recording=label,chunk=i,first_frame=start,last_frame=start+frames-1,frames=frames,
                raw_path=str(SCRATCH/base/stage/name),compressed_relative_path=f'{label}/{name}.gz',
                frame_hashes_relative_path=f'{label}/{name}.frame-sha256.bin'))
            start+=frames
        m.require(start==count+1,'source recording definition')
    m.require(len(rows)==CHUNKS and sum(r['frames'] for r in rows)==FRAMES,'source inventory totals')
    return rows
def validate_layout(rows):
    expected=definitions();m.require(len(rows)==len(expected),'complete43-file layout required')
    for row,want in zip(rows,expected):
        m.require(all(row[k]==v for k,v in want.items()),'missing/reordered/unapproved recording/path/range')
        m.require(row['raw_identity']['bytes']==row['frames']*m.FRAME,'original byte/dimension count')
def receipt_check(r,label,ch,mh,rows):
    m.require(r['PASS'] is True and r['verification']==label and r['chunk_count']==CHUNKS and r['frames']==FRAMES and r['decoded_bytes']==BYTES and r['originals_retained'] is True,'incomplete expanded verification')
    m.require(r['contract_SHA256']==ch and r['mapping_SHA256']==mh,'receipt identity binding')
    keys=('recording','chunk','frames','raw_SHA256','compressed_SHA256')
    m.require([[x[k] for k in keys] for x in r['chunks']]==[[x[k] for k in keys] for x in rows],'receipt chunk mapping')
    m.require(all(x['exact_frame_bytes'] is True and x['exact_EOF'] is True for x in r['chunks']),'incomplete exact bytes/EOF')
old_protected=m.protected_check;old_identity=m.check_identity
def protected_check(c):
    # All non-target files are still checked by the unchanged engine. Monolithic
    # recovery streams have implicit sample order, not a fabricated native index.
    old_protected(dict(c,recordings=[r for r in c['recordings'] if r['index_path']]))
def check_identity(row):
    old_identity(row);m.require(Path(row['raw_path']).stat().st_nlink==1,'original raw file gained hardlinks')
m.OUT=OUT;m.validate_layout=validate_layout;m.receipt_check=receipt_check
m.protected_check=protected_check;m.check_identity=check_identity
def prior_admission():
    contract=json.loads((PRIOR/'preservation-contract.json').read_text());tests=json.loads((PRIOR/'offline-tests.json').read_text())
    m.require(contract['source_commit']==OLD_SOURCE and tests['PASS'] and tests['case_count']==36,'prior tested admission')
    for rel in OLD_FILES:
        old=subprocess.check_output(['git','show',OLD_SOURCE+':'+rel],cwd=ROOT)
        m.require(m.digest(ROOT/rel)==m.hashlib.sha256(old).hexdigest()==contract['source_files_SHA256'][rel],'historical tooling changed')
    m.code_check(contract)
    m.require(m.zlib.ZLIB_RUNTIME_VERSION==contract['zlib_version'] and subprocess.check_output([str(m.GZIP),'--version'],text=True).splitlines()[0]==contract['gzip_version'],'tested codec/runtime versions changed')
    result=json.loads((PRIOR/'preservation-result-private.json').read_text())
    m.require(result['PASS'] and result['replaced_file_count']==31,'prior completed STOP90/104 preservation')
    return dict(tested_source=OLD_SOURCE,evidence_source=OLD_RECEIPTS,tests_SHA256=m.digest(PRIOR/'offline-tests.json'),
        contract_SHA256=m.digest(PRIOR/'preservation-contract.json'),completed_result_SHA256=m.digest(PRIOR/'preservation-result-private.json'),prior_tests_repeated=False,prior_recordings_repeated=False)
def expected_hash(plan,raw):
    label,base,stage,count,n,name=plan;manifest=SCRATCH/base/name;data=json.loads(manifest.read_text())
    if base.startswith('ordinary-'):
        record=next(x for x in data if x['stage']==stage)['captures']['motion']
        m.require(record['samples']==count,'ordinary retained sample count');return record['raw_SHA256']
    rows=data['entries'];key=str(raw) if str(raw) in rows else str(raw.relative_to(SCRATCH/base))
    m.require(key in rows and rows[key]['bytes']==raw.stat().st_size,'historical raw inventory identity')
    return rows[key]['SHA256']
def protected_paths(targets):
    roots={SCRATCH/p[1] for p in PLANS}|{PRIOR}
    files={p for root in roots for p in root.rglob('*') if p.is_file()}
    files|={p for p in SCRATCH.rglob('*.rgb') if not p.is_relative_to(OUT)}
    return sorted(files-{Path(p) for p in targets})
def ensure_source(c):
    m.code_check(c)
    for p,h in c['tool_dependencies_SHA256'].items():m.require(m.digest(Path(p))==h,'preservation decoder dependency changed')
    m.require(git('rev-parse','HEAD')==c['source_commit'] and not git('status','--porcelain'),'exact frozen clean source required')
def verify(c,mapping,decoder,label):
    ensure_source(c)
    result=m.verify_all(c,mapping,decoder,label,base=OUT)
    result.update(pid=os.getpid(),preservation_only=True)
    return result
