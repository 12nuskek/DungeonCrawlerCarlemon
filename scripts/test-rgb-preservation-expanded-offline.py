#!/usr/bin/env python3
"""New scope/layout/receipt tests; never repeat the completed codec admission."""
from pathlib import Path
import copy,importlib.machinery,importlib.util,json,tempfile,types,sys
p=Path(__file__).resolve().parent/'floor1/rgb-preservation-expanded.py'
s=importlib.util.spec_from_file_location('expanded_scope_test',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.m
def main():
    m.require(not a.git('status','--porcelain'),'clean committed scope source')
    out=a.ADMISSION
    m.require(not out.exists(),'exclusive new scope admission')
    prior=a.prior_admission();cases=[]
    python=Path(sys.executable).resolve()
    def module(origin,loader,file=None,name='zlib'):
        return types.SimpleNamespace(__spec__=types.SimpleNamespace(name=name,origin=origin,loader=loader),**({} if file is None else dict(__file__=file)))
    machinery=importlib.machinery
    builtin=module('built-in',machinery.BuiltinImporter)
    assert a.zlib_provider(builtin,python)==(python,'built-in');cases.append('built-in-zlib-provider-without-file')
    # Inert path/loader fixtures only: no extension binary is loaded or executed.
    with tempfile.TemporaryDirectory(prefix='zlib-provider-offline-') as directory:
        path=Path(directory)/('zlib'+machinery.EXTENSION_SUFFIXES[0]);path.touch()
        other=path.with_name('other'+machinery.EXTENSION_SUFFIXES[0]);other.touch()
        loader=machinery.ExtensionFileLoader('zlib',str(path))
        extension=module(str(path),loader,str(path))
        assert a.zlib_provider(extension,python)==(path.resolve(),str(path));cases.append('extension-provider-matching-paths-and-loader')
        alias=path.with_name('alias'+machinery.EXTENSION_SUFFIXES[0]);alias.symlink_to(path.name)
        extension=module(str(alias),machinery.ExtensionFileLoader('zlib',str(alias)),str(path))
        assert a.zlib_provider(extension,python)==(path.resolve(),str(alias));cases.append('extension-provider-matching-resolved-aliases')
        bads=(('missing-spec',types.SimpleNamespace()),
            ('built-in-with-file',module('built-in',machinery.BuiltinImporter,str(path))),
            ('missing-extension-file',module('/absent/zlib.so',machinery.ExtensionFileLoader('zlib','/absent/zlib.so'),'/absent/zlib.so')),
            ('unknown-frozen-origin-existing-file',module('frozen',loader,str(path))),
            ('mismatched-origin-file',module(str(other),loader,str(path))),
            ('wrong-extension-loader',module(str(path),machinery.SourceFileLoader('zlib',str(path)),str(path))),
            ('mismatched-loader-path',module(str(path),machinery.ExtensionFileLoader('zlib',str(other)),str(path))),
            ('wrong-built-in-loader',module('built-in',loader)),
            ('wrong-extension-name',module(str(path),machinery.ExtensionFileLoader('other',str(path)),str(path))),
            ('wrong-module-name',module(str(path),loader,str(path),name='other')),
            ('unsupported-extension-suffix',module(str(m.GZIP),machinery.ExtensionFileLoader('zlib',str(m.GZIP)),str(m.GZIP))))
        for label,bad in bads:
            try:a.zlib_provider(bad,python)
            except RuntimeError:cases.append('provider-identity-negative-'+label)
            else:raise AssertionError('unverifiable zlib provider accepted: '+label)
    origin,pins=a.decoder_dependencies();assert origin==m.zlib.__spec__.origin and pins[str(python)]==m.digest(python);cases.append('actual-runtime-provider-and-linked-dependency-pins')
    rows=[dict(r,raw_identity=dict(bytes=r['frames']*m.FRAME),raw_SHA256='raw-'+str(i),compressed_SHA256='gzip-'+str(i)) for i,r in enumerate(a.definitions())]
    a.validate_layout(rows);cases.append('complete42-file82482-frame-layout')
    bads=[rows[:-1],list(reversed(rows)),[rows[1],rows[0],*rows[2:]]]
    for key,value in (('raw_path','/tmp/unapproved.rgb'),('compressed_relative_path','../outside.gz'),('first_frame',0),('last_frame',0),('frames',0),('recording','unapproved')):
        bad=copy.deepcopy(rows);bad[0][key]=value;bads.append(bad)
    bad=copy.deepcopy(rows);bad[0]['raw_identity']['bytes']-=1;bads.append(bad)
    for i,bad in enumerate(bads):
        try:a.validate_layout(bad)
        except RuntimeError:cases.append('scope-negative-'+str(i))
        else:raise AssertionError('scope expansion accepted')
    chunks=[dict(r,exact_frame_bytes=True,exact_EOF=True) for r in rows]
    good=dict(PASS=True,verification='pass1-zlib',chunk_count=a.CHUNKS,frames=a.FRAMES,decoded_bytes=a.BYTES,originals_retained=True,contract_SHA256='contract',mapping_SHA256='mapping',chunks=chunks)
    a.receipt_check(good,'pass1-zlib','contract','mapping',rows);cases.append('complete-new-scope-removal-receipt')
    bads=[dict(good,**{k:v}) for k,v in (('PASS',False),('verification','pass2-independent-gzip'),('chunk_count',41),('frames',82481),('decoded_bytes',a.BYTES-1),('originals_retained',False),('contract_SHA256','other'),('mapping_SHA256','other'))]
    for key,value in (('exact_frame_bytes',False),('exact_EOF',False),('raw_SHA256','other'),('compressed_SHA256','other'),('frames',0)):
        bad=copy.deepcopy(good);bad['chunks'][0][key]=value;bads.append(bad)
    bads.extend((dict(good,chunks=chunks[:-1]),dict(good,chunks=list(reversed(chunks)))))
    for i,bad in enumerate(bads):
        try:a.receipt_check(bad,'pass1-zlib','contract','mapping',rows)
        except RuntimeError:cases.append('receipt-negative-'+str(i))
        else:raise AssertionError('incomplete receipt accepted')
    pins={rel:m.digest(a.ROOT/rel) for rel in (*a.OLD_FILES,*a.NEW_FILES)}
    m.require(m.CAP==3758096384 and m.EXTERNAL_RESERVE==134217728 and m.RESERVATION==10000408128,'unchanged all-inclusive capacity definitions')
    m.require(a.BYTES-m.CAP>m.RESERVATION-m.shutil.disk_usage(a.SCRATCH).free,'whole cap and original retention fit worst-case future capacity')
    m.require(not a.git('status','--porcelain'),'source unchanged during adapter checks')
    out.write_text(json.dumps(dict(PASS=True,source_commit=a.git('rev-parse','HEAD'),prior_admission=prior,cases=cases,case_count=len(cases),source_files_SHA256=pins,codec_tests_repeated=False,recordings_compressed=0,gameplay_processes=0,runtime_claims=0),indent=2)+'\n')
    print('PASS expanded scope '+str(len(cases))+' cases; prior36 codec/EOF/cap tests and STOP90/104 preservation reused unchanged')
if __name__=='__main__':main()
