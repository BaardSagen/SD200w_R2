#include "merge.h"
#include <shlobj.h>
struct MergeCandidate {std::wstring path;uint64_t hash=0;size_t rows=0,hits=0;long long maxDelta=0;std::wstring first,last;};
struct MergeJob {
 HWND hwnd=0;std::wstring masterPath,folder;long long tol=0;volatile LONG cancel=0;
 sit::Data master;uint64_t masterHash=0;std::vector<MergeCandidate> candidates;
 std::wstring issues;size_t scanned=0,unmatched=0;std::string failure;
};
struct MergeWindow {HWND list=0;HANDLE thread=0;std::unique_ptr<MergeJob> job;bool closing=false,valid=false;std::wstring cell;};
static std::wstring leaf(const std::wstring&p){return p.substr(p.find_last_of(L"\\/")+1);}
static std::wstring fullPath(const std::wstring&p){wchar_t b[32768];DWORD n=GetFullPathNameW(p.c_str(),32768,b,0);if(!n||n>=32768)throw std::runtime_error("Invalid path");return b;}
static std::wstring timeText(long long t){auto d=sit::unstamp(t/1000000);std::string s=d.first+" "+d.second;if(t%1000000){char f[16];std::sprintf(f,".%06d",int(t%1000000));s+=f;while(s.back()=='0')s.pop_back();}return wide(s);}
static DWORD WINAPI mergeScanThread(LPVOID arg){MergeJob&j=*(MergeJob*)arg;
 try{
  std::string bytes=readFile(j.masterPath);j.masterHash=sitmerge::fingerprint(bytes);j.master=sitmerge::parse(bytes,utf8(j.masterPath));auto mt=sitmerge::times(j.master);
  WIN32_FIND_DATAW fd;HANDLE find=FindFirstFileW((j.folder+L"\\*").c_str(),&fd);if(find==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot scan folder or folder is empty");
  try{do{
   if(InterlockedCompareExchange(&j.cancel,0,0))break;if(fd.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)continue;
   std::wstring name=fd.cFileName;size_t dot=name.find_last_of(L'.');if(dot==std::wstring::npos)continue;std::wstring ext=name.substr(dot);for(wchar_t&c:ext)c=towlower(c);if(ext!=L".txt"&&ext!=L".csv")continue;
   std::wstring path=fullPath(j.folder+L"\\"+name);if(lstrcmpiW(path.c_str(),j.masterPath.c_str())==0)continue;++j.scanned;
   try{std::string content=readFile(path);sit::Data data=sitmerge::parse(content,utf8(path));auto times=sitmerge::times(data);auto m=sitmerge::match(mt,times,j.tol);
    if(m.count){MergeCandidate c;c.path=path;c.hash=sitmerge::fingerprint(content);c.rows=data.rows.size();c.hits=m.count;c.maxDelta=m.maxDelta;c.first=timeText(times.sorted.front().first);c.last=timeText(times.sorted.back().first);j.candidates.push_back(c);}else ++j.unmatched;
   }catch(const std::exception&e){j.issues+=name+L": "+wide(e.what())+L"\r\n";}
   if(j.scanned%10==0)PostMessageW(j.hwnd,WM_APP+32,j.scanned,0);
  }while(FindNextFileW(find,&fd));}catch(...){FindClose(find);throw;}FindClose(find);
  std::sort(j.candidates.begin(),j.candidates.end(),[](const MergeCandidate&a,const MergeCandidate&b){return a.path<b.path;});
 }catch(const std::exception&e){j.failure=e.what();}catch(...){j.failure="Folder scan failed";}
 PostMessageW(j.hwnd,WM_APP+31,0,0);return 0;
}
static void mergeBusy(HWND h,bool busy){for(int id:{301,302,303,304,305,306,307,308,310})EnableWindow(GetDlgItem(h,id),!busy);EnableWindow(GetDlgItem(h,309),!busy);SetWindowTextW(GetDlgItem(h,IDCANCEL),busy?L"Cancel scan":L"Close");}
static int mergeSelected(MergeWindow&w){int count=0;for(int i=0;i<ListView_GetItemCount(w.list);++i)if(ListView_GetCheckState(w.list,i))++count;return count;}
static bool mergePick(HWND h,std::wstring&path,bool save){wchar_t name[32768]={};lstrcpynW(name,path.c_str(),32768);OPENFILENAMEW o={};o.lStructSize=sizeof(o);o.hwndOwner=h;o.lpstrFilter=L"CSV/TXT files (*.csv;*.txt)\0*.csv;*.txt\0\0";o.lpstrFile=name;o.nMaxFile=32768;o.lpstrDefExt=L"txt";o.lpstrTitle=save?L"Save merged data to a new file":L"Choose master file";o.Flags=OFN_NOCHANGEDIR|OFN_PATHMUSTEXIST|(save?0:OFN_FILEMUSTEXIST);if(!(save?GetSaveFileNameW(&o):GetOpenFileNameW(&o)))return false;path=name;return true;}
static void mergeSave(HWND h,MergeWindow&w){
 if(!w.valid||!w.job)throw std::runtime_error("Scan files first");int count=mergeSelected(w);if(count<1||count>2)throw std::runtime_error("Select one or two files to merge with the master");MergeJob&j=*w.job;
 if(sitmerge::fingerprint(readFile(j.masterPath))!=j.masterHash)throw std::runtime_error("Master file changed. Scan again before merging.");
 std::vector<sit::Data> files;for(size_t i=0;i<j.candidates.size();++i)if(ListView_GetCheckState(w.list,int(i))){auto&c=j.candidates[i];std::string bytes=readFile(c.path);if(sitmerge::fingerprint(bytes)!=c.hash)throw std::runtime_error("A selected file changed. Scan again before merging.");files.push_back(sitmerge::parse(bytes,utf8(c.path)));}
 auto merged=sitmerge::merge(j.master,files,j.tol,checked(GetDlgItem(h,307)),checked(GetDlgItem(h,308)));std::wstring path=j.masterPath;size_t dot=path.find_last_of(L'.');if(dot!=std::wstring::npos)path.resize(dot);path+=L"_merged.txt";if(!mergePick(h,path,true))return;
 std::string out=sitmerge::output(merged);HANDLE f=CreateFileW(path.c_str(),GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Choose a new output filename. Existing files are never overwritten.");DWORD n=0;BOOL ok=WriteFile(f,out.data(),DWORD(out.size()),&n,0);BOOL flush=FlushFileBuffers(f);CloseHandle(f);if(!ok||n!=out.size()||!flush){DeleteFileW(path.c_str());throw std::runtime_error("Write failed; incomplete output was removed");}
 std::wstring text=L"Merged file saved:\r\n"+path+L"\r\n\r\n"+wide(std::to_string(merged.rows.size()))+L" master rows retained. Unmatched additional cells are empty.";MessageBoxW(h,text.c_str(),L"SAIV IT - Merge",MB_OK|MB_ICONINFORMATION);
}
static LRESULT CALLBACK mergeProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){
 MergeWindow*w=(MergeWindow*)GetWindowLongPtrW(h,GWLP_USERDATA);if(msg==WM_NCCREATE){w=(MergeWindow*)((CREATESTRUCTW*)lp)->lpCreateParams;SetWindowLongPtrW(h,GWLP_USERDATA,(LONG_PTR)w);}if(!w)return DefWindowProcW(h,msg,wp,lp);
 try{switch(msg){
 case WM_CREATE:{
  control(h,L"STATIC",L"Master file (keeps its rows and timestamps):",0,16,14,730,20,320);
  control(h,L"EDIT",L"",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,16,38,660,25,301);control(h,L"BUTTON",L"Browse...",WS_TABSTOP,688,38,100,25,302);
  control(h,L"STATIC",L"Folder containing additional CSV/TXT files:",0,16,74,730,20,321);
  control(h,L"EDIT",L"",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,16,98,660,25,303);control(h,L"BUTTON",L"Browse...",WS_TABSTOP,688,98,100,25,304);
  control(h,L"STATIC",L"Time tolerance (0.0 - 10.0 seconds):",0,16,140,245,24,322);control(h,L"EDIT",L"0.0",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,264,136,74,25,305);
  control(h,L"BUTTON",L"Scan folder",WS_TABSTOP,350,134,115,28,306);
  control(h,L"BUTTON",L"Add '-' separator column between files",BS_AUTOCHECKBOX|WS_TABSTOP,16,174,760,24,307);
  control(h,L"BUTTON",L"Include date/time from merged files",BS_AUTOCHECKBOX|WS_TABSTOP,480,136,308,25,308);SendMessageW(GetDlgItem(h,308),BM_SETCHECK,BST_CHECKED,0);
  control(h,L"STATIC",L"Select up to two matching files. Nearest time wins; a source row may be reused.",0,16,207,772,22,323);
  w->list=control(h,WC_LISTVIEWW,L"",LVS_REPORT|WS_BORDER|WS_TABSTOP|LVS_SHOWSELALWAYS,16,234,772,220,310);SendMessageW(w->list,CCM_SETUNICODEFORMAT,TRUE,0);ListView_SetExtendedListViewStyle(w->list,LVS_EX_CHECKBOXES|LVS_EX_FULLROWSELECT|LVS_EX_GRIDLINES|LVS_EX_DOUBLEBUFFER);
  int widths[]={232,150,150,92,65,78};const wchar_t*names[]={L"File",L"First measurement",L"Last measurement",L"Master matches",L"File rows",L"Max |dt| (s)"};for(int i=0;i<6;++i){LVCOLUMNW c={};c.mask=LVCF_TEXT|LVCF_WIDTH;c.pszText=(wchar_t*)names[i];c.cx=widths[i];SendMessageW(w->list,LVM_INSERTCOLUMNW,i,(LPARAM)&c);}
  control(h,L"STATIC",L"Choose a master file and folder, then scan. Times are used as recorded (no time-zone conversion).",0,16,464,772,40,311);
  control(h,L"EDIT",L"",ES_MULTILINE|ES_READONLY|WS_VSCROLL|WS_BORDER,16,509,772,70,312);
  control(h,L"BUTTON",L"Merge files",WS_TABSTOP|BS_DEFPUSHBUTTON,562,590,114,30,309);EnableWindow(GetDlgItem(h,309),FALSE);control(h,L"BUTTON",L"Close",WS_TABSTOP,688,590,100,30,IDCANCEL);return 0;
 }
 case WM_APP+32:{std::wstring s=L"Scanning... "+wide(std::to_string(wp))+L" files checked";SetWindowTextW(GetDlgItem(h,311),s.c_str());return 0;}
 case WM_APP+31:{WaitForSingleObject(w->thread,INFINITE);CloseHandle(w->thread);w->thread=0;mergeBusy(h,false);auto&j=*w->job;w->valid=j.failure.empty()&&!j.cancel;if(w->closing){DestroyWindow(h);return 0;}
  if(!j.failure.empty())throw std::runtime_error(j.failure);if(j.cancel){SetWindowTextW(GetDlgItem(h,311),L"Scan cancelled. No output created.");EnableWindow(GetDlgItem(h,309),FALSE);return 0;}
  for(size_t row=0;row<j.candidates.size();++row){auto&c=j.candidates[row];std::wstring values[]={leaf(c.path),c.first,c.last,wide(std::to_string(c.hits)+"/"+std::to_string(j.master.rows.size())),wide(std::to_string(c.rows)),wide(sit::fmt(c.maxDelta/1000000.))};LVITEMW item={};item.mask=LVIF_TEXT;item.iItem=int(row);item.pszText=&values[0][0];SendMessageW(w->list,LVM_INSERTITEMW,0,(LPARAM)&item);for(int col=1;col<6;++col){LVITEMW cell={};cell.iSubItem=col;cell.pszText=&values[col][0];SendMessageW(w->list,LVM_SETITEMTEXTW,row,(LPARAM)&cell);}}
  std::wstring s=wide(std::to_string(j.candidates.size()))+L" matching files / "+wide(std::to_string(j.scanned))+L" scanned; "+wide(std::to_string(j.unmatched))+L" without time matches. Master: "+wide(std::to_string(j.master.rows.size()))+L" rows. Select up to 2 files.";SetWindowTextW(GetDlgItem(h,311),s.c_str());SetWindowTextW(GetDlgItem(h,312),j.issues.empty()?L"No unreadable or unsupported files.":j.issues.c_str());EnableWindow(GetDlgItem(h,309),FALSE);InvalidateRect(w->list,0,TRUE);return 0;
 }
 case WM_NOTIFY:{NMHDR*n=(NMHDR*)lp;if(n->hwndFrom!=w->list)break;
  if(n->code==LVN_GETDISPINFOW){auto*di=(NMLVDISPINFOW*)lp;auto&i=di->item;if((i.mask&LVIF_TEXT)&&w->job&&i.iItem>=0&&size_t(i.iItem)<w->job->candidates.size()){auto&c=w->job->candidates[i.iItem];switch(i.iSubItem){case 0:w->cell=leaf(c.path);break;case 1:w->cell=c.first;break;case 2:w->cell=c.last;break;case 3:w->cell=wide(std::to_string(c.hits)+"/"+std::to_string(w->job->master.rows.size()));break;case 4:w->cell=wide(std::to_string(c.rows));break;default:w->cell=wide(sit::fmt(c.maxDelta/1000000.));}i.pszText=&w->cell[0];}return 0;}
  if(n->code==LVN_ITEMCHANGING){auto*c=(NMLISTVIEW*)lp;if((c->uNewState&LVIS_STATEIMAGEMASK)==INDEXTOSTATEIMAGEMASK(2)&&(c->uOldState&LVIS_STATEIMAGEMASK)!=INDEXTOSTATEIMAGEMASK(2)&&mergeSelected(*w)>=2){SetWindowTextW(GetDlgItem(h,311),L"Maximum two additional files. Uncheck one file before selecting another.");return TRUE;}}
  if(n->code==LVN_ITEMCHANGED){int count=mergeSelected(*w);EnableWindow(GetDlgItem(h,309),w->valid&&count>=1&&count<=2);return 0;}break;
 }
 case WM_COMMAND:{int id=LOWORD(wp);
  if((id==301||id==303||id==305)&&HIWORD(wp)==EN_CHANGE){w->valid=false;EnableWindow(GetDlgItem(h,309),FALSE);return 0;}
  if(id==302){std::wstring p=caption(GetDlgItem(h,301));if(mergePick(h,p,false))SetWindowTextW(GetDlgItem(h,301),p.c_str());return 0;}
  if(id==304){BROWSEINFOW bi={};bi.hwndOwner=h;bi.lpszTitle=L"Choose folder containing additional CSV/TXT files";bi.ulFlags=BIF_RETURNONLYFSDIRS|BIF_NEWDIALOGSTYLE;LPITEMIDLIST pid=SHBrowseForFolderW(&bi);if(pid){wchar_t path[MAX_PATH];if(SHGetPathFromIDListW(pid,path))SetWindowTextW(GetDlgItem(h,303),path);CoTaskMemFree(pid);}return 0;}
  if(id==306&&!w->thread){auto j=std::unique_ptr<MergeJob>(new MergeJob);j->hwnd=h;j->tol=sitmerge::tolerance(utf8(caption(GetDlgItem(h,305))));auto master=caption(GetDlgItem(h,301)),folder=caption(GetDlgItem(h,303));if(master.empty()||folder.empty())throw std::runtime_error("Choose a master file and folder first");j->masterPath=fullPath(master);j->folder=fullPath(folder);DWORD attr=GetFileAttributesW(j->folder.c_str());if(attr==INVALID_FILE_ATTRIBUTES||!(attr&FILE_ATTRIBUTE_DIRECTORY))throw std::runtime_error("Choose an existing folder");w->valid=false;ListView_DeleteAllItems(w->list);w->job=std::move(j);mergeBusy(h,true);SetWindowTextW(GetDlgItem(h,311),L"Scanning files...");SetWindowTextW(GetDlgItem(h,312),L"");w->thread=CreateThread(0,0,mergeScanThread,w->job.get(),0,0);if(!w->thread){mergeBusy(h,false);throw std::runtime_error("Cannot start folder scan");}return 0;}
  if(id==309&&!w->thread){mergeSave(h,*w);return 0;}
  if(id==IDCANCEL){if(w->thread){InterlockedExchange(&w->job->cancel,1);SetWindowTextW(GetDlgItem(h,311),L"Cancelling scan...");}else DestroyWindow(h);return 0;}break;
 }
 case WM_CLOSE:if(w->thread){w->closing=true;InterlockedExchange(&w->job->cancel,1);}else DestroyWindow(h);return 0;
 }}catch(const std::exception&e){MessageBoxW(h,wide(e.what()).c_str(),L"SAIV IT - Merge",MB_OK|MB_ICONERROR);if(!w->thread)EnableWindow(GetDlgItem(h,309),w->valid&&mergeSelected(*w)>=1&&mergeSelected(*w)<=2);return 0;}
 return DefWindowProcW(h,msg,wp,lp);
}
extern "C" __declspec(dllexport) int __stdcall SitMerge(HWND owner){
 try{INITCOMMONCONTROLSEX ic={sizeof(ic),ICC_LISTVIEW_CLASSES};InitCommonControlsEx(&ic);WNDCLASSW wc={};wc.hInstance=instance;wc.hIcon=LoadIconW(GetModuleHandleW(0),L"MAINICON");wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=(HBRUSH)(COLOR_BTNFACE+1);wc.lpfnWndProc=mergeProc;wc.lpszClassName=L"SITMerge";RegisterClassW(&wc);MergeWindow state;RECT r;GetWindowRect(owner,&r);HWND h=CreateWindowExW(WS_EX_CONTROLPARENT,L"SITMerge",L"SAIV IT - Merge files",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,r.left+20,r.top+20,822,665,owner,0,instance,&state);if(!h)throw std::runtime_error("Cannot open Merge window");EnableWindow(owner,FALSE);ShowWindow(h,SW_SHOW);MSG msg;while(IsWindow(h)&&GetMessageW(&msg,0,0,0)>0){if(!IsDialogMessageW(h,&msg)){TranslateMessage(&msg);DispatchMessageW(&msg);}}EnableWindow(owner,TRUE);SetActiveWindow(owner);return 1;
 }catch(const std::exception&e){MessageBoxW(owner,wide(e.what()).c_str(),L"SAIV IT - Merge",MB_OK|MB_ICONERROR);return 1;}
}
