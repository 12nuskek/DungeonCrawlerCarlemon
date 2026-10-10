"""Extend unchanged r3 inert transaction checks with actual two-foe reader tests."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(observer,fixture_header):
    spec=importlib.util.spec_from_file_location('conserve_native_inert',ROOT/'scripts/floor1/medicine-transaction-inert.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);s=old.generate(observer,fixture_header)
    def once(a,b):
        nonlocal s
        assert s.count(a)==1,(a[:90],s.count(a));s=s.replace(a,b)
    once('unsigned c,cm,d,dm,g,n,s,b;', 'unsigned c,cm,d,dm,g,h,n,s,b;')
    once('fscanf(f,"%u %u %u %u %u %u %u %u",&c,&cm,&d,&dm,&g,&n,&s,&b)==8',
         'fscanf(f,"%u %u %u %u %u %u %u %u %u",&c,&cm,&d,&dm,&g,&h,&n,&s,&b)==9')
    once('gc_choice(c,cm,d,dm,g,n,s,b)', 'gc_choice(c,cm,d,dm,g,h,n,s,b)')
    fixture=(ROOT/'scripts/floor1/conserve-medicine-integration.h').read_text()
    once('int main(int argc,char**argv){',fixture+'\nint main(int argc,char**argv){\n if(argc==2&&!strcmp(argv[1],"--foes")){conserveIntegration();return 0;}')
    return s
