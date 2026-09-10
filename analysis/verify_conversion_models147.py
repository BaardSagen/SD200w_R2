"""Build integration tests using separately recovered/verified native equations."""
from pathlib import Path
import ast,subprocess,json,hashlib
R=Path(__file__).resolve().parent.parent
W=R/'analysis/models147';W.mkdir(exist_ok=True)
def expr(n):
 if isinstance(n,ast.Constant):return repr(float(n.value))
 if isinstance(n,ast.Name):return n.id
 if isinstance(n,ast.UnaryOp):return '(-'+expr(n.operand)+')'
 if isinstance(n,ast.BinOp):
  if isinstance(n.op,ast.Pow):return 'std::pow('+expr(n.left)+','+expr(n.right)+')'
  return '('+expr(n.left)+{ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(n.op)]+expr(n.right)+')'
 if isinstance(n,ast.Compare):return '('+expr(n.left)+'<'+expr(n.comparators[0])+')'
 if isinstance(n,ast.IfExp):return '('+expr(n.test)+'?'+expr(n.body)+':'+expr(n.orelse)+')'
 if isinstance(n,ast.Call):
  name=n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id
  if name=='radians':return '('+expr(n.args[0])+'*3.14159265358979323846/180)'
  return ('std::' if name in ['abs','sqrt','sin','exp'] else '')+name+'('+','.join(map(expr,n.args))+')'
 raise ValueError(ast.dump(n))
out=['#include <cmath>','namespace reference {']
for f in ast.parse((R/'analysis/recovered_formulas.py').read_text(encoding='utf-8-sig')).body:
 if not isinstance(f,ast.FunctionDef):continue
 out.append('inline double '+f.name+'('+','.join('double '+x.arg for x in f.args.args)+'){')
 seen=set()
 for n in f.body:
  if isinstance(n,ast.Assign):
   name=n.targets[0].id;out.append(('' if name in seen else 'double ')+name+'='+expr(n.value)+';');seen.add(name)
  elif isinstance(n,ast.AugAssign):out.append(n.target.id+'+='+expr(n.value)+';')
  elif isinstance(n,ast.Return):out.append('return '+expr(n.value)+';')
  elif isinstance(n,ast.If):out.append('if('+expr(n.test)+')return '+expr(n.body[0].value)+';')
  else:raise ValueError(ast.dump(n))
 out.append('}')
out.append('}')
(W/'reference.h').write_text('\n'.join(out))
gsw=R/'sit_import/vendor/gsw'
objects=[]
for name in ['gsw_oceanographic_toolbox','gsw_saar']:
 obj=W/(name+'.o');src=gsw/(name+'.c')
 if not obj.exists() or obj.stat().st_mtime<src.stat().st_mtime:subprocess.run(['g++','-O2','-c',str(src),'-o',str(obj)],check=True)
 objects.append(str(obj))
exe=W/'verify.exe'
subprocess.run(['g++','-std=c++11','-O2','-static-libgcc','-static-libstdc++',str(R/'analysis/test_conversion_models147.cpp'),*objects,'-o',str(exe)],check=True)
result=subprocess.run([str(exe)],cwd=R,text=True,capture_output=True)
print(result.stdout);print(result.stderr);result.check_returncode()
(W/'validation.json').write_text(json.dumps({'result':result.stdout,'test_source_sha256':hashlib.sha256((R/'analysis/test_conversion_models147.cpp').read_bytes()).hexdigest()},indent=2))
