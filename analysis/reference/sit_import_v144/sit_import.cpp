#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
#define _WIN32_IE 0x0600
#include <windows.h>
#include <commctrl.h>
#include <commdlg.h>
#include <shellapi.h>
#include <cstdio>
#ifndef LVS_EX_DOUBLEBUFFER
#define LVS_EX_DOUBLEBUFFER 0x10000
#endif
#include <memory>
#include "logger.h"
#include "native_data.h"
static HINSTANCE instance;
static std::wstring wide(const std::string&s,UINT cp=CP_UTF8){int n=MultiByteToWideChar(cp,0,s.data(),int(s.size()),0,0);std::wstring w(n,L' ');if(n)MultiByteToWideChar(cp,0,s.data(),int(s.size()),&w[0],n);return w;}
static std::string utf8(const std::wstring&w){int n=WideCharToMultiByte(CP_UTF8,0,w.data(),int(w.size()),0,0,0,0);std::string s(n,' ');if(n)WideCharToMultiByte(CP_UTF8,0,w.data(),int(w.size()),&s[0],n,0,0);return s;}
static std::wstring caption(HWND h){int n=GetWindowTextLengthW(h);std::wstring s(n+1,L' ');GetWindowTextW(h,&s[0],n+1);s.resize(n);return s;}
static HWND control(HWND p,const wchar_t*cls,const wchar_t*txt,DWORD style,int x,int y,int w,int h,int id){HWND c=CreateWindowExW(0,cls,txt,WS_CHILD|WS_VISIBLE|style,x,y,w,h,p,(HMENU)(INT_PTR)id,instance,0);SendMessageW(c,WM_SETFONT,(WPARAM)GetStockObject(DEFAULT_GUI_FONT),TRUE);return c;}
static std::wstring fieldLabel(const std::string&f){
 if(f.compare(0,3,"M1_")==0||f.compare(0,3,"M2_")==0)return wide(f.substr(0,3))+fieldLabel(f.substr(3));
 if(f=="Delta_seconds")return L"Time difference (seconds)";
 if(f=="C")return L"C - Conductivity (mS/cm)";if(f=="T")return L"T - Temperature (\u00b0C, Celsius)";if(f=="T_degF")return L"T_degF - Temperature (\u00b0F, Fahrenheit)";if(f=="P")return L"P - Pressure (dbar)";
 if(f=="OF")return L"OF - Fluorescence (\u00b5g/L)";if(f=="OT")return L"OT - Turbidity (FTU)";
 if(f=="S"||f=="S_from_C"||f=="Salinity_SIT")return wide(f)+L" - Salinity";
 if(f=="Par")return L"Par - PAR";if(f=="Par_umol_m2_s")return L"PAR (\u00b5mol photons/m\u00b2/s)";
 if(f=="Depth_m")return L"Real depth (m)";
 if(f=="OX")return L"OX - SAIV205 (%)";if(f=="OxR")return L"OxR - RINKO (%)";
 if(f=="OxR_mg_L")return L"OxR (mg/L)";if(f=="OxR_mL_L")return L"OxR (mL/L)";
 if(f=="OX_mg_L")return L"OX (mg/L)";if(f=="OX_mL_L")return L"OX (mL/L)";
 if(f=="Sound_velocity_SIT_m_s")return L"Sound velocity (m/s)";
 if(f=="Density_anomaly_SIT_kg_m3")return L"Density -1000 (kg/m3)";return wide(f);
}
static void error(HWND h,const std::string&s){MessageBoxW(h,wide(s).c_str(),L"SAIV IT - Import",MB_OK|MB_ICONERROR);}
static double formula(int f,double a,double b,double c){typedef double (__stdcall *Fn)(double,double,double);BYTE* base=(BYTE*)GetModuleHandleW(0);if(f==3){typedef double (__stdcall *Fn2)(double,double);return ((Fn2)(base+0x10cb5c))(a,b);}static const size_t offsets[]={0x10a5b8,0x10a8f0,0x10c330};return ((Fn)(base+offsets[f]))(a,b,c);}
static std::string readFile(const std::wstring&path,bool probe=false){HANDLE h=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot read selected file");LARGE_INTEGER size;if(!GetFileSizeEx(h,&size)||(!probe&&size.QuadPart>20*1024*1024)||size.QuadPart<0){CloseHandle(h);throw std::runtime_error("Import supports files up to 20 MB");}std::string s(size_t(probe?std::min<LONGLONG>(65536,size.QuadPart):size.QuadPart),' ');DWORD got=0;BOOL ok=ReadFile(h,s.empty()?0:&s[0],DWORD(s.size()),&got,0);CloseHandle(h);if(!ok||got!=s.size())throw std::runtime_error("Could not read the complete file");return s;}
#include "wizard.inc"
#include "presets_ui.inc"
#include "merge_ui.inc"
struct View {sit::Data data;std::wstring path;HWND list=0,combo=0,plot=0;int channel=0;bool allowNative=true;std::wstring cell;};
static void save(HWND h,View&v){wchar_t name[32768];std::wstring suggestion=v.path;size_t dot=suggestion.find_last_of(L'.');if(dot!=std::wstring::npos)suggestion.resize(dot);suggestion+=L"_SIT.txt";lstrcpynW(name,suggestion.c_str(),32768);OPENFILENAMEW of={};of.lStructSize=sizeof(of);of.hwndOwner=h;of.lpstrFilter=L"SIT text data (*.txt)\0*.txt\0All files\0*.*\0\0";of.lpstrFile=name;of.nMaxFile=32768;of.lpstrDefExt=L"txt";of.lpstrTitle=L"Export all fields to a new file";of.Flags=OFN_PATHMUSTEXIST|OFN_NOCHANGEDIR;
 if(!GetSaveFileNameW(&of))return;std::string out=sit::output(v.data);HANDLE f=CreateFileW(name,GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot create output. Choose a new filename; existing files are never overwritten.");DWORD n=0;BOOL ok=WriteFile(f,out.data(),DWORD(out.size()),&n,0);BOOL flush=FlushFileBuffers(f);CloseHandle(f);if(!ok||n!=out.size()||!flush){DeleteFileW(name);throw std::runtime_error("Export failed; incomplete output removed");}MessageBoxW(h,L"All fields and metadata were exported.",L"SAIV IT",MB_OK);}
static bool importConverted(HWND owner,const sit::Data&data);
static LRESULT CALLBACK plotProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){if(msg!=WM_PAINT)return DefWindowProcW(h,msg,wp,lp);PAINTSTRUCT ps;HDC dc=BeginPaint(h,&ps);RECT rc;GetClientRect(h,&rc);FillRect(dc,&rc,(HBRUSH)GetStockObject(WHITE_BRUSH));View*v=(View*)GetWindowLongPtrW(GetParent(h),GWLP_USERDATA);
 if(v&&!v->data.rows.empty()&&v->channel>=0){auto&d=v->data;int da=sit::index(d,"DATE"),ti=sit::index(d,"TIME"),col=v->channel;double ymin=1e300,ymax=-1e300,xmin=1e300,xmax=-1e300;std::vector<std::pair<double,double> >pts;
  for(auto&r:d.rows){if(r[col].empty()){pts.push_back({0,NAN});continue;}double x=sitnative::timestamp(r[da],r[ti]),y=sit::number(r[col]);pts.push_back({x,y});xmin=std::min(xmin,x);xmax=std::max(xmax,x);ymin=std::min(ymin,y);ymax=std::max(ymax,y);}
  if(ymin<=ymax){std::wstring title=fieldLabel(d.fields[col])+L"    "+wide(sit::fmt(ymin))+L" .. "+wide(sit::fmt(ymax));TextOutW(dc,10,5,title.c_str(),int(title.size()));int left=22,top=31,width=rc.right-44,height=rc.bottom-61;Rectangle(dc,left,top,left+width,top+height);HPEN pen=CreatePen(PS_SOLID,1,RGB(0,95,150));HGDIOBJ old=SelectObject(dc,pen);bool first=true;for(auto&p:pts){if(!std::isfinite(p.second)){first=true;continue;}int x=left+int((p.first-xmin)/(xmax>xmin?xmax-xmin:1)*width);int y=top+height-int((p.second-ymin)/(ymax>ymin?ymax-ymin:1)*height);if(first)MoveToEx(dc,x,y,0);else LineTo(dc,x,y);Ellipse(dc,x-2,y-2,x+2,y+2);first=false;}SelectObject(dc,old);DeleteObject(pen);std::wstring a=wide(d.rows.front()[da]+" "+d.rows.front()[ti]),b=wide(d.rows.back()[da]+" "+d.rows.back()[ti]);TextOutW(dc,left,rc.bottom-22,a.c_str(),int(a.size()));SIZE bs;GetTextExtentPoint32W(dc,b.c_str(),int(b.size()),&bs);TextOutW(dc,rc.right-22-bs.cx,rc.bottom-22,b.c_str(),int(b.size()));}}
 EndPaint(h,&ps);return 0;}
static void layout(HWND h,View&v){RECT r;GetClientRect(h,&r);int ph=std::max(120,int((r.bottom-90)/3));MoveWindow(v.list,12,48,r.right-24,r.bottom-ph-72,TRUE);MoveWindow(v.plot,12,r.bottom-ph-12,r.right-24,ph,TRUE);}
static LRESULT CALLBACK viewProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){View*v=(View*)GetWindowLongPtrW(h,GWLP_USERDATA);if(msg==WM_NCCREATE){v=(View*)((CREATESTRUCTW*)lp)->lpCreateParams;SetWindowLongPtrW(h,GWLP_USERDATA,(LONG_PTR)v);}if(!v)return DefWindowProcW(h,msg,wp,lp);
 try{switch(msg){case WM_CREATE:{control(h,L"BUTTON",L"Export all fields...",WS_TABSTOP,12,10,135,28,201);int shift=v->allowNative?145:0;if(v->allowNative)control(h,L"BUTTON",L"Import to SD2...",WS_TABSTOP,157,10,135,28,205);control(h,L"STATIC",L"Graph:",0,165+shift,15,48,22,202);v->combo=control(h,L"COMBOBOX",L"",WS_TABSTOP|CBS_DROPDOWNLIST|WS_VSCROLL,216+shift,10,265,220,203);std::wstring count=wide(std::to_string(v->data.rows.size()))+L" measurements"+(v->data.estimatedTime?L" - header-derived times":L" - original row times");control(h,L"STATIC",count.c_str(),0,500+shift,15,440-shift,22,204);
 v->list=control(h,WC_LISTVIEWW,L"",LVS_REPORT|LVS_OWNERDATA|LVS_SHOWSELALWAYS|WS_BORDER|WS_TABSTOP,12,48,920,310,210);SendMessageW(v->list,LVM_SETEXTENDEDLISTVIEWSTYLE,0,LVS_EX_FULLROWSELECT|LVS_EX_GRIDLINES|LVS_EX_DOUBLEBUFFER);SendMessageW(v->list,CCM_SETUNICODEFORMAT,TRUE,0);
 for(size_t i=0;i<v->data.fields.size();++i){std::wstring s=fieldLabel(v->data.fields[i]);LVCOLUMNW c={};c.mask=LVCF_TEXT|LVCF_WIDTH|LVCF_SUBITEM;c.pszText=&s[0];c.cx=std::max(95,std::min(215,int(s.size())*7+16));c.iSubItem=int(i);SendMessageW(v->list,LVM_INSERTCOLUMNW,i,(LPARAM)&c);if(!sitnative::dateField(v->data.fields[i])&&!sitnative::timeField(v->data.fields[i])&&!sitnative::separator(v->data.fields[i])){LRESULT n=SendMessageW(v->combo,CB_ADDSTRING,0,(LPARAM)s.c_str());SendMessageW(v->combo,CB_SETITEMDATA,n,i);}}
 SendMessageW(v->list,LVM_SETITEMCOUNT,v->data.rows.size(),LVSICF_NOSCROLL);int selected=0;int preferred=sit::index(v->data,"T");if(preferred<0)preferred=sit::index(v->data,"T_degF");if(preferred<0)preferred=sit::index(v->data,"Par");for(int j=0;j<SendMessageW(v->combo,CB_GETCOUNT,0,0);++j)if(SendMessageW(v->combo,CB_GETITEMDATA,j,0)==preferred)selected=j;SendMessageW(v->combo,CB_SETCURSEL,selected,0);v->channel=int(SendMessageW(v->combo,CB_GETITEMDATA,selected,0));v->plot=control(h,L"SITImportPlot",L"",WS_BORDER,12,374,920,170,211);layout(h,*v);return 0;}
 case WM_SIZE:if(v->list)layout(h,*v);return 0;
 case WM_GETMINMAXINFO:((MINMAXINFO*)lp)->ptMinTrackSize={760,480};return 0;
 case WM_NOTIFY:{NMHDR*nm=(NMHDR*)lp;if(nm->code==LVN_GETDISPINFOW){NMLVDISPINFOW*di=(NMLVDISPINFOW*)lp;auto&i=di->item;if((i.mask&LVIF_TEXT)&&i.iItem>=0&&size_t(i.iItem)<v->data.rows.size()&&i.iSubItem>=0&&size_t(i.iSubItem)<v->data.fields.size()){v->cell=wide(v->data.rows[i.iItem][i.iSubItem]);i.pszText=&v->cell[0];}return 0;}break;}
 case WM_COMMAND:if(LOWORD(wp)==205){if(importConverted(h,v->data))DestroyWindow(h);return 0;}if(LOWORD(wp)==201){save(h,*v);return 0;}if(LOWORD(wp)==203&&HIWORD(wp)==CBN_SELCHANGE){int c=int(SendMessageW(v->combo,CB_GETCURSEL,0,0));v->channel=int(SendMessageW(v->combo,CB_GETITEMDATA,c,0));InvalidateRect(v->plot,0,TRUE);return 0;}break;
 case WM_CLOSE:DestroyWindow(h);return 0;
 case WM_NCDESTROY:SetWindowLongPtrW(h,GWLP_USERDATA,0);delete v;break;
 }}catch(const std::exception&e){error(h,e.what());return 0;}return DefWindowProcW(h,msg,wp,lp);}
static void registerClasses(){static bool registered=false;if(registered)return;INITCOMMONCONTROLSEX ic={sizeof(ic),ICC_LISTVIEW_CLASSES};InitCommonControlsEx(&ic);WNDCLASSW wc={};wc.hInstance=instance;wc.hIcon=LoadIconW(GetModuleHandleW(0),L"MAINICON");wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=(HBRUSH)(COLOR_BTNFACE+1);wc.lpfnWndProc=wizardProc;wc.lpszClassName=L"SITImportChoices";RegisterClassW(&wc);wc.lpfnWndProc=viewProc;wc.lpszClassName=L"SITImportData";RegisterClassW(&wc);wc.lpfnWndProc=plotProc;wc.lpszClassName=L"SITImportPlot";RegisterClassW(&wc);registered=true;}
#include "native_ui.inc"
extern "C" __declspec(dllexport) int __stdcall SitImport(HWND owner,const char*filename){
 try{std::wstring path=wide(filename,CP_ACP);std::unique_ptr<View>v(new View);v->path=path;v->data.source=utf8(path);if(!sit::parse(readFile(path),v->data)){error(owner,"Use File > Import CSV/TXT for legacy instrument files.");return 1;}registerClasses();std::string signature=sitpreset::signature(v->data);sitpreset::Record previous;sit::Choices choice;bool reused=false;
 if(loadPreset(v->data,previous)){int answer=offerPreset(owner,v->data,previous);if(answer==IDCANCEL)return 1;if(answer==IDYES){choice=sitpreset::reuse(previous,v->data);reused=true;}}
 sit::Choices saved=choice;if(!choose(owner,v->data,choice,reused?&saved:0))return 1;sit::calculate(v->data,choice,formula);
 if(!savePreset(signature,v->data.source,choice))MessageBoxW(owner,L"Conversion succeeded, but these choices could not be saved for next time.",L"SAIV IT - Convert",MB_OK|MB_ICONINFORMATION);if(sit::canSal(v->data)&&sit::complete(v->data,"T")&&sit::complete(v->data,"P"))v->data.metadata.push_back("# CTD calculations use the original SIT executable routines; raw CTD fields are retained");std::wstring title=L"SAIV IT - Logger data - "+path.substr(path.find_last_of(L"\\/")+1);RECT r;GetWindowRect(owner,&r);View*raw=v.release();HWND h=CreateWindowExW(0,L"SITImportData",title.c_str(),WS_OVERLAPPEDWINDOW,r.left+24,r.top+24,1000,650,owner,0,instance,raw);if(!h)throw std::runtime_error("Cannot create logger data window");EnableWindow(owner,FALSE);ShowWindow(h,SW_SHOW);UpdateWindow(h);MSG message;while(IsWindow(h)&&GetMessageW(&message,0,0,0)>0){if(!IsDialogMessageW(h,&message)){TranslateMessage(&message);DispatchMessageW(&message);}}EnableWindow(owner,TRUE);SetActiveWindow(owner);return 1;
 }catch(const std::exception&e){error(owner,e.what());return 1;}catch(...){error(owner,"Import failed. Original file was not changed.");return 1;}}
BOOL WINAPI DllMain(HINSTANCE h,DWORD reason,LPVOID){if(reason==DLL_PROCESS_ATTACH){instance=h;DisableThreadLibraryCalls(h);}return TRUE;}
