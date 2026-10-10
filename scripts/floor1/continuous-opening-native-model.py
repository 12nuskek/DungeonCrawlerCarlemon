"""Current source-bound comparison adapter; historical model pins stay untouched."""
from pathlib import Path
import ast,hashlib,importlib.util,re,subprocess,types
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fields=module('co_current_fields',ROOT/'scripts/floor1/party-fields.py')
resources=module('co_current_resources',ROOT/'scripts/floor1/prepared-save-validation.py')
current=(ROOT/'engine/src/pokemon.c').read_bytes();assert hashlib.sha256(current).hexdigest()=='b7ff983d5b356d017e1e8e150d27183226df6a51f2dc0a480191f06c0e9628c0'
old=subprocess.check_output(['git','show','e5032830315e162d65dbe66cf698153333b60618:engine/src/pokemon.c'],cwd=ROOT)
assert hashlib.sha256(old).hexdigest()=='df008d2d381b70f30998e476ed1f7183871580ea037d0fc5832bea11beb9c064'
def block(text,anchor):
 text=text.decode();start=text.index(anchor);op=text.index('{',start);depth=1;i=op+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i]
for anchor in ('static const s8 sFriendshipEventModifiers[][3] =','void AdjustFriendship(struct Pokemon *mon, u8 event)'):
 assert block(old,anchor)==block(current,anchor),'exact reviewed native friendship table/function'
friendship=types.SimpleNamespace(MODIFIERS={'GROW_LEVEL':(5,3,2),'WALKING':(1,1,1)})
source=(ROOT/'scripts/floor1/native-friendship.py').read_text();tree=ast.parse(source)
ns={'MODIFIERS':friendship.MODIFIERS}
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed-native-friendship-definitions>','exec'),ns)
friendship.target=ns['target'];friendship.level_ups=ns['level_ups']
source=(ROOT/'scripts/floor1/guard-first-state.py').read_text();tree=ast.parse(source);ns={'fields':fields,'struct':__import__('struct')}
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ('encode','level_stats'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed-native-encoding-stat-definitions>','exec'),ns)
encode=ns['encode'];level_stats=ns['level_stats']
