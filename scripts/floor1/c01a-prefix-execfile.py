"""Read-only admission of the retained own-compiled observer; never launch it."""
from pathlib import Path
import hashlib, os, stat

def verify_executable(path, expected):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), 'observer must be a regular non-symlink file'
    if 'device' in expected:
        assert (before.st_dev, before.st_ino) == (expected['device'], expected['inode']), 'frozen observer identity mismatch'
    assert before.st_uid == expected['owner_uid'] == os.geteuid(), 'observer owner mismatch'
    assert stat.S_IMODE(before.st_mode) == expected['mode'] == 0o700, 'observer mode must be0700'
    assert os.access(path, os.X_OK), 'observer executable access denied'
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        assert (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino), 'observer identity changed'
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
        after = os.fstat(stream.fileno())
    current = path.lstat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_uid, s.st_mode, s.st_size, s.st_mtime_ns)
    assert fields(before) == fields(opened) == fields(after) == fields(current), 'observer changed during check'
    assert digest.hexdigest() == expected['SHA256'], 'observer byte hash mismatch'
    return {'SHA256': digest.hexdigest(), 'mode': '0700', 'owner_uid': before.st_uid,
            'regular_non_symlink': True, 'executable_access': True,
            'device': before.st_dev, 'inode': before.st_ino}
