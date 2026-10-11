#!/usr/bin/env python3
"""One separately admitted Warden-only operation; imports grant no permission."""
from pathlib import Path
import argparse, importlib.util, os, resource, signal, sys
path=Path(__file__).resolve().parent/'floor1/warden-rgb-production.py'
spec=importlib.util.spec_from_file_location('warden_production_cli',path)
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('preserve','verify-zlib','verify-gzip'))
    action=parser.parse_args().action
    os.umask(0o077)
    if action!='preserve':
        resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
        # The parent first durably records this child's real PID; only then does
        # it release this pipe. No started-file race or freely launched worker.
        signal.alarm(30)
        p.require(sys.stdin.buffer.readline(4)==b'GO\n','controller handshake required')
    else:
        bound=p.s.gzip_bound(2000*p.s.FRAME)
        resource.setrlimit(resource.RLIMIT_FSIZE,(bound,bound))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('bounded preservation process')))
    signal.alarm(7200 if action=='preserve' else 1800)
    p.dispatch(action)
if __name__=='__main__': main()
