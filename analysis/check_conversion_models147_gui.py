"""Actual shipped EXE, own process/registry, no instrument commands."""
from models147_gui_support import *
import math
from capture_window import capture as window_capture
def capture(h,path):window_capture(h,path,2)
report={}
def checkbox(h,id,on=True):u.SendMessageW(u.GetDlgItem(h,id),0xf1,int(on),0)
def guide(h,title):
 click(h,133);g=waitfor('SITQuickGuide');assert text(u.GetDlgItem(g,402))==title;assert not u.IsWindowEnabled(h);click(g,1);assert u.IsWindowEnabled(h)
def toolbar_list():
 peb=c.c_size_t();assert n.NtQueryInformationProcess(pi.process,26,c.byref(peb),c.sizeof(peb),None)==0;base=d(peb.value+8);form=d(base+0x1c8964)
 fields=d(d(form)-56);count=int.from_bytes(read(fields,2),'little');ptr=fields+6;objects={}
 for i in range(count):
  offset=d(ptr);length=read(ptr+6,1)[0];name=read(ptr+7,length).decode();objects[name]=d(form+offset);ptr+=7+length
 button=objects['sbtnList'];parent=d(button+0x24);xy=(d(button+0x30)+13)|((d(button+0x34)+13)<<16);u.PostMessageW(d(parent+0x14c),0x201,1,xy);u.PostMessageW(d(parent+0x14c),0x202,0,xy)
def finish_fields(wiz,models=True):
 seen=[]
 for step in range(30):
  title=text(u.GetDlgItem(wiz,101));seen.append(title)
  if title.startswith('Review'):
   if models:select(wiz,131,1)
   capture(wiz,out/'conditions.png');click(wiz,1);break
  field=title.split(': ',1)[1].split(' -',1)[0]
  if field=='C':
   assert u.SendMessageW(u.GetDlgItem(wiz,102),0x146,0,0)==4
   if models:select(wiz,102,3);checkbox(wiz,132,True)
   guide(wiz,'Conductivity and salinity');assert u.SendMessageW(u.GetDlgItem(wiz,102),0x147,0,0)==(3 if models else 0)
   capture(wiz,out/'conductivity.png')
  elif field=='S':
   if models:select(wiz,102,1)
  elif field=='T':
   if models:select(wiz,131,1)
   guide(wiz,'Temperature')
  elif field=='P':
   assert u.SendMessageW(u.GetDlgItem(wiz,102),0x146,0,0)==6
   if models:select(wiz,102,4)
   guide(wiz,'Depth: modes and fjords');capture(wiz,out/'depth.png')
  elif field in ['OX','OxR']:
   assert u.SendMessageW(u.GetDlgItem(wiz,102),0x146,0,0)==7
   if models:select(wiz,102,6);select(wiz,134,1)
   guide(wiz,'Oxygen: saturation and units');capture(wiz,out/'oxygen.png')
  elif field=='Derived seawater properties':
   assert u.SendMessageW(u.GetDlgItem(wiz,102),0x146,0,0)==6
   assert u.SendMessageW(u.GetDlgItem(wiz,135),0x146,0,0)==4
   if models:select(wiz,102,2);select(wiz,135,3)
   guide(wiz,'Sound velocity');click(wiz,143);g=waitfor('SITQuickGuide');assert text(u.GetDlgItem(g,402))=='Density and Sigma T';click(g,1)
   capture(wiz,out/'water.png')
  click(wiz,1)
 return seen
try:
 main=prepare()
 a=out/'model_source.txt';a.write_text('FIELDS: COUNT;S;C;T;P;OX;OxR;Par;OF;OT;DATE;TIME\n1;32.539;33.71963249253746;7.773;16.72;3.47;100;2.5;5.67;1.08;2026-09-01;12:00:00\n')
 openfile(main,a);wiz=waitfor('SITImportChoices');report['pages']=finish_fields(wiz)
 view=waitfor('SITImportData');capture(view,out/'result.png');first=export(view,'all_models');rows=table(first);assert len(rows)==1
 for col in ['SA_TEOS10_g_kg','CT_TEOS10_degC','Density_TEOS10_kg_m3','Sigma0_TEOS10_kg_m3','Sound_velocity_TEOS10_m_s','Depth_m','OX_mg_L','OX_mL_L','OX_umol_L','OX_umol_kg','S_from_C']:assert col in rows[0],col
 assert 'temperature input=ITS-90' in first.read_text(encoding='utf-8-sig')
 assert rows[0]['S']=='32.539' and rows[0]['C']=='33.71963249253746'
 assert abs(float(rows[0]['OX_umol_L'])-float(rows[0]['OX_mg_L'])*1000/31.998)<1e-10
 report['export']=str(first);report['values']=rows[0]
 # Original native callback values through the actual Next workflow.
 openfile(main,a);click(waitfor('#32770','Previous conversion'),7);wiz=waitfor('SITImportChoices');finish_fields(wiz,False);baseline=table(export(waitfor('SITImportData'),'native'))[0]
 assert abs(float(baseline['Density_anomaly_SIT_kg_m3'])-25.451007880937)<1e-8
 assert abs(float(baseline['Sound_velocity_SIT_m_s'])-1478.8273740930208)<1e-8
 # Restore modern selection before verifying stored model choices.
 openfile(main,a);click(waitfor('#32770','Previous conversion'),7);finish_fields(waitfor('SITImportChoices'));export(waitfor('SITImportData'),'modern_again')
 # Saved model choices go to conditions; Back reveals the retained models.
 openfile(main,a);click(waitfor('#32770','Previous conversion'),6);wiz=waitfor('SITImportChoices');assert text(u.GetDlgItem(wiz,101)).startswith('Review');click(wiz,3);assert u.SendMessageW(u.GetDlgItem(wiz,102),0x147,0,0)==2;assert u.SendMessageW(u.GetDlgItem(wiz,135),0x147,0,0)==3;click(wiz,1);click(wiz,1);second=export(waitfor('SITImportData'),'reuse');assert table(second)==rows;report['preset_models_retained']=True
 # Legacy STD input is accepted by Convert, keeps optical fields and source SP.
 openfile(main,ROOT/'data/26090606_18.11.51.txt');wiz=waitfor('SITImportChoices');finish_fields(wiz)
 legacy=export(waitfor('SITImportData'),'legacy');lr=table(legacy);assert len(lr)==43;assert all('C' not in row for row in lr);assert lr[0]['S']=='00.036';assert 'Legacy Convert: row timestamps reconstructed' in legacy.read_text(encoding='utf-8-sig');report['legacy_43_rows']=True
 # Surface-only worst-case conditions page: missing T/SP/AP plus GSW and GPS.
 surface=out/'surface.txt';surface.write_text('FIELDS: COUNT;OxR;DATE;TIME\n1;100;2026-09-01;12:00:00\n')
 openfile(main,surface);wiz=waitfor('SITImportChoices');select(wiz,102,6);select(wiz,134,1);click(wiz,1)
 assert u.GetDlgItem(wiz,110) and u.GetDlgItem(wiz,111)
 settext(u.GetDlgItem(wiz,110),'10');settext(u.GetDlgItem(wiz,111),'35');select(wiz,131,1);select(wiz,144,1);checkbox(wiz,121);u.PostMessageW(wiz,0x111,121,0);time.sleep(.1);settext(u.GetDlgItem(wiz,122),'45, -30');capture(wiz,out/'surface_conditions.png')
 click(wiz,3);click(wiz,1);assert text(u.GetDlgItem(wiz,110))=='10' and text(u.GetDlgItem(wiz,111))=='35';click(wiz,1)
 surface_export=export(waitfor('SITImportData'),'surface');assert 'missing P treated as zero sea pressure' in surface_export.read_text(encoding='utf-8-sig');report['surface_support_back_and_atlas']=True
 # Convert -> native SD2 -> reopened extra fields must retain model values.
 openfile(main,a);click(waitfor('#32770','Previous conversion'),6);click(waitfor('SITImportChoices'),1);view=waitfor('SITImportData')
 native=out/('modern_native_'+str(time.time_ns())+'.SD2');click(view,205);dlg=waitfor('#32770','Save native dataset');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),native);click(dlg,1)
 def accept_range():
  sel=waitfor('TSelectDlg')
  for ch,txt,typ,id in children(sel):
   if typ=='TCheckBox' and 'Mask measurements' in txt:u.SendMessageW(ch,0xf1,0,0)
  btn=next(ch for ch,txt,typ,id in children(sel) if typ in ('TButton','TBitBtn') and txt.replace('&','').lower()=='ok');u.PostMessageW(btn,0xf5,0,0);time.sleep(.5)
 accept_range();imported=export(waitfor('SITImportData','Imported fields'),'native_imported');assert table(imported)==rows
 core=struct.unpack_from('<5d',native.read_bytes(),64);assert abs(core[0]-float(rows[0]['S_from_C']))<1e-10;assert abs(core[4]-float(rows[0]['Sound_velocity_TEOS10_m_s']))<1e-10
 close_command=next(id for label,id in menus(u.GetMenu(main)) if label.replace('&','').startswith('Close file'));click(main,close_command);command=next(id for label,id in menus(u.GetMenu(main)) if label.replace('&','').startswith('Open'));click(main,command);dlg=waitfor('#32770');settext(next(h for h,t,cl,id in children(dlg) if cl=='Edit'),native);click(dlg,1);accept_range();toolbar_list();reopened=export(waitfor('SITImportData','Imported fields'),'reopened');assert table(reopened)==rows
 report['native_import_and_reopen_preserve_model_columns']=True
 report['shipped_exe_sha256']=__import__('hashlib').sha256((ROOT/'SAIV_Instrument_Terminal_v1.4.7_Sept2026.exe').read_bytes()).hexdigest()
 report['single_exe_non_admin']=True;report['instrument_commands_sent']=False
 (out/'gui_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:
 k.TerminateProcess(pi.process,0);k.WaitForSingleObject(pi.process,5000);k.CloseHandle(pi.process);finish(bundle);u.CloseDesktop(desk)
 try:winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER,registry,winreg.KEY_WOW64_32KEY)
 except FileNotFoundError:pass
