"""Separately named inert adapter; no emulator creation or historical runner call."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(observer,fixture):
    spec=importlib.util.spec_from_file_location('howler_tx',ROOT/'scripts/floor1/conserve-medicine-inert.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);code=old.generate(observer,fixture)
    def once(a,b):
        nonlocal code
        assert code.count(a)==1,(a[:100],code.count(a));code=code.replace(a,b)
    a=code.index('static void conserveSetup(');b=code.index('int main(int argc,char**argv){',a)
    code=code[:a]+(ROOT/'scripts/floor1/howler-continuation-integration.h').read_text()+'\n'+code[b:]
    once('conserveIntegration();','howlerIntegration();howlerSaveIntegration();')
    once('static void setup(void){','static void installSnapshot(const struct CoSnapshot*s);\nstatic void setup(void){')
    once(' co.trace=tmpfile();', ' installSnapshot(&co.last);\n co.trace=tmpfile();')
    # Only historical medicine fixture setup is adapted; the new terminal test
    # deliberately retains a real forbidden Guard-kind case.
    code=code.replace('setup();memset(&gc,0,sizeof gc);co.kind=CO_GUARD;',
                      'setup();memset(&gc,0,sizeof gc);co.kind=CO_HOWLER;')
    once('howlerIntegration();howlerSaveIntegration();', 'howlerIntegration();howlerSaveIntegration();howlerTerminalIntegration();')
    once('quantity<=2;quantity++','quantity<=1;quantity++')
    once('medicineUse(swapped,recipient,quantity);closeFiles();',
         'medicineUse(swapped,recipient,quantity);gc.stage=1;assert(gc_observe(&mock,mockPixels,240,160)==104);gc.stage=0;closeFiles();')
    once('twoSuccessive();puts("PASS medicine native UI/animation/WAIT lifecycle mocks: 8 cases + 2 successive uses, all stages observed");',
         '(void)twoSuccessive;puts("PASS Howler medicine native UI/animation/WAIT lifecycle: 4 single-stock cases; duplicate/exhausted use forbidden");')
    return code
