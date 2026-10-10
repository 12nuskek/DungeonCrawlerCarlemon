"""Exact pinned archive representation checks; never normalize actual input."""
from pathlib import Path
import hashlib
import os
import subprocess


def expected_archive_bytes(blob, attributes):
    assert attributes.get('export-subst', 'unspecified') == 'unspecified', 'Unexpected export substitution'
    eol = attributes.get('eol', 'unspecified')
    if eol == 'crlf':
        assert attributes.get('text') == 'set', 'CRLF requires explicit pinned text attribute'
        assert b'\r\n' not in blob, 'Pinned CRLF text must have canonical LF blob'
        return blob.replace(b'\n', b'\r\n')
    assert eol in ('lf', 'unspecified'), 'Unsupported pinned EOL attribute'
    return blob


def verify_inventory(expected, actual):
    assert set(expected) == set(actual), ('tracked inventory', sorted(set(expected)-set(actual)), sorted(set(actual)-set(expected)))
    for path, (blob, attributes) in expected.items():
        assert actual[path] == expected_archive_bytes(blob, attributes), ('exact pinned archive bytes', path)


def verify(repo, commit, source, hydration):
    env = dict(os.environ, GIT_ATTR_NOSYSTEM='1')
    def git(*args, **kwargs):
        return subprocess.check_output(['git', '-c', 'core.attributesFile=/dev/null', *args], cwd=repo, env=env, **kwargs)
    info = Path(git('rev-parse', '--git-path', 'info/attributes', text=True).strip())
    if not info.is_absolute(): info = repo/info
    assert not info.exists() or not info.read_bytes(), 'Unpinned info attributes'
    tree = git('ls-tree', '-r', '-z', commit)
    rows = {}
    for line in tree.split(b'\0'):
        if not line: continue
        header, path = line.split(b'\t'); mode, kind, oid = header.split()
        name=path.decode()
        # Verify every archived runtime helper as well as engine, with immutable attrs.
        if name.startswith(('engine/', 'scripts/')) or name == '.gitattributes':
            assert kind == b'blob'
            rows[name] = oid.decode()
    attrdata=git('check-attr', '--source='+commit, '-z', '--stdin', 'text', 'eol', 'export-subst', input=b'\0'.join(p.encode() for p in rows)+b'\0')
    parts=attrdata.split(b'\0'); assert parts[-1]==b'';attrs={p:{} for p in rows}
    for i in range(0,len(parts)-1,3):
        path, key, value=parts[i:i+3];attrs[path.decode()][key.decode()]=value.decode()
    data=git('cat-file','--batch',input=''.join(oid+'\n' for oid in rows.values()).encode())
    cursor=0;expected={};actual={};manifest={}
    for path,oid in rows.items():
        end=data.index(b'\n',cursor);header=data[cursor:end].split();size=int(header[2]);blob=data[end+1:end+1+size];cursor=end+size+2
        assert header[0].decode()==oid and header[1]==b'blob'
        expected[path]=(blob,attrs[path]);actual[path]=(source/path).read_bytes()
        manifest[path]=dict(git_blob=oid,attributes=attrs[path],archive_SHA256=hashlib.sha256(actual[path]).hexdigest())
    assert cursor==len(data)
    verify_inventory(expected,actual)
    for path,record in hydration.items():
        assert 'engine/'+path not in rows, 'Hydration must not override tracked source'
        assert hashlib.sha256((source/'engine'/path).read_bytes()).hexdigest()==record['SHA256']
    return manifest
