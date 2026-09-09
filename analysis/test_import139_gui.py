"""Validate the delivered single EXE, native point arrays and file reopening."""
from native139_gui_support import *
import struct,csv,io,subprocess,pefile,math
checks=0;reports=[]
def read(a,nbytes=4):
 buf=c.create_string_buffer(nbytes);assert k.ReadProcessMemory(pi.process,a,buf,nbytes,None);return buf.raw
def d(a):return int.from_bytes(read(a),'little')
def source_table(path):
 lines=path.read_text(encoding='utf-8-sig').splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('FIELDS:'));return list(csv.DictReader([lines[i][7:].strip()]+lines[i+1:],delimiter=';'))
def close_views():
 for h,t,cl in windows():
  if cl in ['SITImportData','TdlgMchart']:u.PostMessageW(h,0x10,0,0)
 time.sleep(.2)
def select_range():
 end=time.monotonic()+8
 while time.monotonic()<end:
  found=[h for h,t,cl in windows() if cl=='TSelectDlg']
  if found:
   h=found[0]
   for ch,txt,typ,id in children(h):
    if typ=='TCheckBox' and 'Mask measurements' in txt:u.SendMessageW(ch,0xf1,0,0)
   btn=next(ch for ch,txt,typ,id in children(h) if typ in ('TButton','TBitBtn') and txt.replace('&','').lower()=='ok');u.PostMessageW(btn,0xf5,0,0);time.sleep(.4);return
  time.sleep(.1)
 raise AssertionError(windows())
def menu(term):return next(i for t,i in menus(u.GetMenu(main)) if term in t)
def open_file(path):
 u.PostMessageW(main,0x111,menu('&Open...'),0);dlg=waitfor('#32770');settext(next(h for h,t,cl,i in children(dlg) if cl=='Edit'),path);click(dlg,1);select_range()
def toolbar(name):
 button=objects[name];parent=d(button+0x24);hwnd=d(parent+0x14c);x=d(button+0x30)+d(button+0x38)//2;y=d(button+0x34)+d(button+0x3c)//2;u.PostMessageW(hwnd,0x201,1,x|(y<<16));u.PostMessageW(hwnd,0x202,0,x|(y<<16));return waitfor('TdlgMchart')
def get_points(series):
 count=d(d(series+0x8c)+0x4c);return [struct.unpack('<'+str(count)+'d',read(d(d(series+off)+0x48),8*count)) for off in (0x8c,0x94)]
def verify_graph(rows,slot_fields):
 global checks
 graph=d(d(base+0x1b2268));start=__import__('datetime').datetime.fromisoformat(rows[0]['DATE']+'T'+rows[0]['TIME']);times=[(__import__('datetime').datetime.fromisoformat(r['DATE']+'T'+r['TIME'])-start).total_seconds() for r in rows]
 offsets=[0x330,0x334,0x33c,0x338,0x340,0x344,0x354,0x370,0x374,0x3d8]
 for off,field in zip(offsets,slot_fields):
  xs,ys=get_points(d(graph+off));assert len(xs)==len(rows),(field,len(xs),len(rows))
  for i,r in enumerate(rows):assert abs(xs[i]-times[i])<1e-6,(field,i,xs[i],times[i]);assert abs(ys[i]-float(r[field]))<1e-10,(field,i,ys[i],r[field]);checks+=2
 return times[-1]
def export_list(expected):
 global checks
 view=waitfor('SITImportData');assert u.SendMessageW(u.GetDlgItem(view,210),0x1004,0,0)==len(expected)
 path=out/('fields_'+str(time.time_ns())+'.txt');click(view,201);dlg=waitfor('#32770','Export all fields');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),path);click(dlg,1);click(waitfor('#32770','SAIV IT'),1)
 actual=source_table(path);assert len(actual)==len(expected)
 for a,b in zip(actual,expected):
  for field,value in b.items():assert a[field]==value,(field,a[field],value);checks+=1
 u.PostMessageW(view,0x10,0,0);return actual
try:
 main=waitfor('TForm1');time.sleep(.6);peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8);form=d(base+0x1c8964)
 fields=d(d(form)-56);count=int.from_bytes(read(fields,2),'little');ptr=fields+6;objects={}
 for i in range(count):offset=d(ptr);nchar=read(ptr+6,1)[0];name=read(ptr+7,nchar).decode();objects[name]=d(form+offset);ptr+=7+nchar
 for filename in ['2026_09_03_20-28-52_C.txt','2026_09_07_19-34-42_C.txt','2026_09_03_20-28-52_C_merged-3.txt']:
  source=ROOT/'analysis/reference/import137_inputs'/filename;rows=source_table(source);close_views();u.PostMessageW(main,0x111,menu('Import CSV/TXT'),0);dlg=waitfor('#32770','Import CSV/TXT');settext(next(h for h,t,cl,i in children(dlg) if cl=='Edit'),source);click(dlg,1)
  save=waitfor('#32770','Save native dataset');target=out/(source.stem+'_'+str(time.time_ns())+'.SD2');settext(next(h for h,t,cl,i in children(save) if cl=='Edit'),target);click(save,1);select_range();actual=export_list(rows)
  sf=target.with_suffix('.SF2').read_bytes();assert sf.split(b'\n',1)[1]==source.read_bytes();assert d(d(base+0x1b16c0))==len(rows)
  preferred=[f for f in rows[0] if f not in ['COUNT','DATE','TIME'] and not f.endswith(('_DATE','_TIME','_COUNT','_separator','_Delta_seconds'))][:10]
  graph=toolbar('sbtnMgraph');time.sleep(.3);duration=verify_graph(rows,preferred)
  # Every source numeric field remains selectable, including merge counts/delta.
  panel=next(h for h,t,cl,id in children(graph) if cl=='SITNativeChannels');combo=u.GetDlgItem(panel,700);count=u.SendMessageW(combo,0x146,0,0);assert count>=len(preferred)+1
  extra='M1_COUNT' if 'M1_COUNT' in rows[0] else 'COUNT';label=c.create_unicode_buffer(extra);ix=u.SendMessageW(combo,0x158,-1,c.addressof(label));assert ix>=0,extra;u.SendMessageW(combo,0x14e,ix,0);u.PostMessageW(panel,0x111,700|(1<<16),combo);time.sleep(.2);verify_graph(rows,[extra]+preferred[1:])
  close_views();u.PostMessageW(main,0x111,menu('Close file'),0);time.sleep(.2);open_file(target);u.PostMessageW(main,0x111,menu('&List'),0);time.sleep(.2)
  # File > Export > List may be first; use the toolbar to request the imported list.
  for h,t,cl in windows():
   if cl=='#32770':u.PostMessageW(h,0x111,2,0)
  button=objects['sbtnList'];parent=d(button+0x24);xy=(d(button+0x30)+13)|((d(button+0x34)+13)<<16);u.PostMessageW(d(parent+0x14c),0x201,1,xy);u.PostMessageW(d(parent+0x14c),0x202,0,xy);export_list(rows)
  graph=toolbar('sbtnGrTime');time.sleep(.2);assert text(graph).startswith('Graph - ');pref='T' if 'T' in rows[0] else 'Par';verify_graph(rows,[pref]);close_views()
  if 'T' in rows[0]:
   u.PostMessageW(main,0x111,menu('Salinity / Temperature'),0);graph=waitfor('TdlgMchart');time.sleep(.2);verify_graph(actual,['S_from_C','T']);close_views()
   u.PostMessageW(main,0x111,menu('Sound &velocity'),0);graph=waitfor('TdlgMchart');time.sleep(.2);verify_graph(actual,['Sound_velocity_SIT_m_s','Density_anomaly_SIT_kg_m3']);close_views()
  reports.append(dict(source=filename,rows=len(rows),duration=duration,target=str(target),reopened=True));print('PASS',filename,len(rows),'rows, native graph/multigraph/field switching/list and reopening',flush=True)
 (out/'native139_gui_validation.json').write_text(json.dumps(dict(checks=checks,files=reports),indent=2));print('PASS',checks,'native plotted coordinates and list values')
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
