"""Extract committed inputs only. Engine caches are forbidden source authorities."""
import subprocess
from pathlib import Path

def snapshot(repository, revision, destination, engine_cache=None, extra_paths=()):
    if engine_cache:
        raise ValueError('DCC_G01_CACHE is unsupported: do not copy an engine tree. Use DCC_CACHE for the separately pinned toolchain only.')
    destination=Path(destination)
    assert not destination.exists(), 'Fresh snapshot directory required'
    destination.mkdir(parents=True)
    paths=['engine','scripts/contracts/f1-g01-opening.json','scripts/floor1/opening-graybox.py','scripts/setup-foundation.sh']
    # Additional diagnostic tooling must also come from this exact Git archive.
    # Never accept absolute paths, traversal, generated products or cache trees.
    for path in extra_paths:
        assert path.startswith(('scripts/contracts/', 'scripts/floor1/'))
        assert '..' not in Path(path).parts and not Path(path).is_absolute()
        assert path.endswith(('.py', '.json'))
        if path not in paths: paths.append(path)
    archive=subprocess.Popen(['git','archive',revision,*paths],cwd=repository,stdout=subprocess.PIPE)
    try:
        subprocess.run(['tar','-x','-C',str(destination)],stdin=archive.stdout,check=True)
    finally:
        archive.stdout.close()
    if archive.wait():raise RuntimeError('Committed archive extraction failed')
    (destination/'.dcc-diagnostic-snapshot').write_text(revision+'\n')
