"""Read-only adoption of completed archive preservation; never extract or remove."""
from pathlib import Path
import hashlib,json,os,stat

ROOT=Path(__file__).resolve().parents[2]
SCRATCH=Path('/workspace/scratch')
VISUAL=SCRATCH/'new-input-visual-pair-20261010'
PREP=SCRATCH/'v01-frame-archive-proposal-r1-20261011'
OUTPUT=SCRATCH/'v01-frame-archive-replacement-r1-20261011'
HANDOFF=SCRATCH/'v01-frame-archive-offline-r1-20261011/identity-adoption-preflight-r1-20261011/execution-final-handoff-private.json'
HANDOFF_SHA='460ed8edce5f033fcd4b10d7f0878d93d504500eedfa64b93d56278a0544f946'
PROPOSAL_SHA='4d92865f5eba94a74b8f8acb0d9d5bb24e34aa53f881976f6fe69fc5e2fdc9c1'
ARCHIVE_SHA='f43bdc3b80c55a3b566c1f4058e2ece2844ec6c051164c7605ab73c2843dbcd3'
COUNT=31254

def require(value,reason):
    if not value:raise AssertionError(reason)

def sha(path):
    path=Path(path);before=path.lstat()
    require(stat.S_ISREG(before.st_mode) and not path.is_symlink(),'regular immutable input')
    h=hashlib.sha256()
    with path.open('rb') as file:
        for data in iter(lambda:file.read(1024**2),b''):h.update(data)
    stable=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns,s.st_nlink)
    require(stable(path.lstat())==stable(before),'input metadata changed during hashing')
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_text())

def identity(path):
    s=Path(path).lstat();require(stat.S_ISREG(s.st_mode),'regular retained identity')
    return dict(device=str(s.st_dev),inode=str(s.st_ino),mode=str(stat.S_IMODE(s.st_mode)),uid=str(s.st_uid),mtime_ns=str(s.st_mtime_ns),bytes=s.st_size,allocated_bytes=s.st_blocks*512,nlink=s.st_nlink)

def verify_representation():
    require(sha(HANDOFF)==HANDOFF_SHA and sha(PREP/'proposal-private.json')==PROPOSAL_SHA,'accepted completed preservation seals')
    handoff,proposal=read(HANDOFF),read(PREP/'proposal-private.json')
    require(handoff['PASS'] and handoff['tested_execution_commit']=='3fa36fb0f18e3fb8db4fe6a647992d4764bd6543' and handoff['actual_complete_verifier_processes']==2 and handoff['exact_redundant_frame_copies_replaced']==COUNT,'completed exact local preservation')
    for path,pin in handoff['private_artifacts_SHA256'].items():require(sha(path)==pin,'preserved operation artifact: '+path)
    for rel,pin in proposal['source_files_SHA256'].items():require(sha(ROOT/rel)==pin,'unchanged historical preservation source bytes')
    rows=[json.loads(line) for line in (PREP/'frame-inventory-private.jsonl').read_text().splitlines()]
    names=[f'{mode}/battle-{i:05}.ppm' for mode in ('baseline','candidate') for i in range(15627)]
    require([r['member'] for r in rows]==names and len(rows)==COUNT,'exact authorized representation members')
    for row in rows:
        require(row['raw_path']==str(VISUAL/row['member']) and row['bytes']==115215 and not os.path.lexists(row['raw_path']),'only mapped replaced raw operands are expected absent')
    require(sha(VISUAL/'new-input-pair-private-evidence.tar.gz')==ARCHIVE_SHA and identity(VISUAL/'new-input-pair-private-evidence.tar.gz')==handoff['archive_identity_after'],'retained archive exact bytes and actual identity')
    proofs=[]
    for decoder in ('zlib','gzip'):
        r=read(OUTPUT/f'verification-{decoder}-private.json')
        require(r['PASS'] and r['fresh_process'] is True and r['target_count']==COUNT and r['decoded_frame_bytes']==3600929610 and r['archive_member_count']==32166 and r['archive_member_chain_SHA256']==proposal['archive_member_chain_SHA256'] and r['exact_archive_original_frame_hash_EOF'] is True,'completed full archive/original proof')
        require(sha(OUTPUT/f'verification-{decoder}-private.jsonl')==r['ledger_SHA256']==handoff['both_complete_ledger_SHA256'],'complete immutable ordered proof ledger')
        proofs.append(r['pid'])
    require(proofs==handoff['actual_verifier_PIDs'] and len(set(proofs))==2,'two actual distinct historical verifier identities')
    stop=SCRATCH/'v01-frame-archive-offline-r1-20261011/replacement-admission-r1-20261011/preflight-STOP-private.json'
    require(sha(stop)==handoff['prior_pre_authority_STOP_SHA256'],'earlier terminal failure preserved separately')
    return dict(handoff_SHA256=HANDOFF_SHA,proposal_SHA256=PROPOSAL_SHA,archive_SHA256=ARCHIVE_SHA,
                frame_inventory_SHA256=proposal['inventory_SHA256'],protected_inventory_SHA256=proposal['protected_SHA256'],
                target_count=COUNT,representation='existing exact local archive and frozen member mapping',
                raw_paths_expected_absent=True,original_inode_restoration=False,independent_backup_verified=False)

def verify_protected():
    representation=verify_representation()
    rows=[json.loads(line) for line in (PREP/'protected-inventory-private.jsonl').read_text().splitlines()]
    require(len(rows)==37000,'complete preserved unique evidence scope')
    for row in rows:
        require(identity(row['path'])==row['identity'] and sha(row['path'])==row['SHA256'] and identity(row['path'])==row['identity'],'protected actual identity/hash: '+row['path'])
    expected={r['path'] for r in rows if Path(r['path']).is_relative_to(VISUAL)}
    actual={str(p) for p in VISUAL.rglob('*') if p.is_file() or p.is_symlink()}
    require(actual==expected,'remaining visual namespace is exactly the protected non-target inventory')
    return representation
