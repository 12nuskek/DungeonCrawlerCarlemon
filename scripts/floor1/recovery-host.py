"""Reconstruct the published read-only host; never execute an exclusive old runner."""
import ast
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED_HOST = 'c7c5ca5d68ece7ce8aaebf2cfcad002368da0ce4'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def replace_once(code, old, new):
    assert code.count(old) == 1, ('host anchor', old[:80], code.count(old))
    return code.replace(old, new)


def generate(git):
    walking = module('recovery_walking', ROOT / 'scripts/floor1/walking-harness.py')
    observer = module('recovery_observer', ROOT / 'scripts/floor1/live-save-observer.py')
    code = observer.instrument(walking.instrument(git('show', PUBLISHED_HOST + ':scripts/playtest.c') + '\n'))
    code = code.replace('!number(values[0],15,&tx)', '!number(values[0],255,&tx)')
    code = code.replace('!number(values[1],11,&ty)', '!number(values[1],255,&ty)')
    reconstructed_base = hashlib.sha256(code.encode()).hexdigest()
    assert reconstructed_base == '897d1d698ea33aee7d7bcf6cd77475dc1a8b6ae562c92376103fdef6ef7c5e1c'
    begin = code.index('        if (!strcmp(line,"snapshot\\n")) {')
    end = code.index('        if (!strncmp(line,"measure start ",14)) {', begin)
    code = code[:begin] + code[end:]
    # Reuse only the committed host transformations, not CLI, claims, saves or runs.
    source = git('show', PUBLISHED_HOST + ':scripts/test-f1-g01e-current-patrol.py')
    tree = ast.parse(source)
    start = source.index("code = replace_once(code, 'int main(int argc, char **argv)'")
    finish = source.index("assert not any(x in code", start)
    namespace = dict(code=code, ROOT=ROOT, replace_once=replace_once)
    for node in tree.body:
        segment = ast.get_source_segment(source, node)
        if isinstance(node, ast.Assign) and segment and start <= source.index(segment) < finish:
            assert all(isinstance(t, ast.Name) and t.id in ['code', 'point', 'anchor'] for t in node.targets)
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<published-host-transform>', 'exec'), namespace)
    code = namespace['code']
    assert not any(x in code for x in ['snapshot', 'STATE {', 'encryption_key', 'busWrite'])
    # Field item controls are separate from the unchanged published battle policy.
    code = replace_once(code, 'selectedItem=0;', 'selectedItem=0, fieldContext=0;')
    code = replace_once(code, '        if (!strcmp(symbol,"gTasks")) tasks=addr;',
        '        if (!strcmp(symbol,"Task_ItemContext_MultipleRows")) fieldContext=addr;\n        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    point = '        if (!strcmp(line,"quit\\n")) break;'
    code = replace_once(code, point, point + r'''
        if (!strncmp(line,"wait-task ",10)) {
            char task[32];unsigned limit,elapsed=0,callback=0;
            if (sscanf(line,"wait-task %31s %u %c",task,&limit,&extra)!=2 || !limit || limit>3600) {result=46;break;}
            if (!strcmp(task,"bag")) callback=bagInput;
            if (!strcmp(task,"field-context")) callback=fieldContext;
            if (!strcmp(task,"party")) callback=partyInput;
            if (!strcmp(task,"healed")) callback=restoredText;
            if (!callback) {result=46;break;}
            core->setKeys(core,0);
            while (elapsed<limit && !menu_ready(core,tasks,fade,callback)) {core->runFrame(core);elapsed++;total++;}
            if (!menu_ready(core,tasks,fade,callback)) {result=46;fprintf(stderr,"Required field menu not ready: %s",line);break;}
            checks++;printf("PASS task ready %s frames=%u\n",task,elapsed);continue;
        }
        if (!strcmp(line,"return-field\n")) {
            unsigned elapsed=0;
            while (elapsed<3600 && (core->busRead8(core,fieldLock) || core->busRead8(core,scriptStatus)!=2
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u))) {
                if (core->busRead8(core,mainstate+0x439)&2) {result=46;break;}
                core->setKeys(core,elapsed%12==0?2:0);core->runFrame(core);elapsed++;total++;
            }
            core->setKeys(core,0);
            if (result || elapsed==3600) {result=46;fprintf(stderr,"Field menu return exceeded bound\n");break;}
            checks++;printf("PASS field menu return frames=%u\n",elapsed);continue;
        }
        if (!strncmp(line,"levels ",7)) {
            unsigned c,d;
            if (sscanf(line,"levels %u %u %c",&c,&d,&extra)!=2 || core->busRead8(core,party+0x54)!=c || core->busRead8(core,party+100+0x54)!=d) {result=46;fprintf(stderr,"Reconstructed levels diverged\n");break;}
            checks++;printf("PASS %s",line);continue;
        }
''')
    assert not any(x in code for x in ['snapshot', 'STATE {', 'encryption_key', 'busWrite'])
    return code, reconstructed_base
