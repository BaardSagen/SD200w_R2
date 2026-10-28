#ifndef PBS_MARQUEE
#define PBS_MARQUEE 0x08
#define PBM_SETMARQUEE (WM_USER+10)
#endif
// Multi-file Convert. Source files are read-only; every output uses CREATE_NEW.
static const UINT batchNext=WM_APP+212,batchComplete=WM_APP+213;
struct BatchConvert {
 std::vector<std::wstring> files;
 std::wstring folder,output,log;
 std::map<std::string,sitpreset::Record> choices;
 sitpreset::Record pending;
 sit::Data data;sit::Choices choice;
 HWND window=0;HANDLE thread=0;
 size_t index=0,converted=0,failed=0;
 int phase=0;bool stop=false,finished=false;
 unsigned short fpControl=0;
 std::string error;
};
static std::wstring batchLeaf(const std::wstring&p){return p.substr(p.find_last_of(L"\\/")+1);}
static void batchLog(BatchConvert&s,const std::wstring&line){
 s.log+=line+L"\r\n";SetDlgItemTextW(s.window,604,s.log.c_str());
 SendDlgItemMessageW(s.window,604,EM_SETSEL,s.log.size(),s.log.size());SendDlgItemMessageW(s.window,604,EM_SCROLLCARET,0,0);
}
static std::wstring batchWrite(const std::wstring&folder,const std::wstring&source,const std::string&bytes){
 std::wstring stem=batchLeaf(source);size_t dot=stem.find_last_of(L'.');if(dot!=std::wstring::npos)stem.resize(dot);
 for(unsigned n=0;n<10000;++n){
  std::wstring path=folder+L"\\"+stem+L"_SIT"+(n?L"_"+wide(std::to_string(n+1)):L"")+L".txt";
  HANDLE file=CreateFileW(path.c_str(),GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
  if(file==INVALID_HANDLE_VALUE){if(GetLastError()==ERROR_FILE_EXISTS||GetLastError()==ERROR_ALREADY_EXISTS)continue;throw std::runtime_error("Cannot create an output file in the selected folder");}
  DWORD wrote=0;bool ok=WriteFile(file,bytes.data(),DWORD(bytes.size()),&wrote,0)&&wrote==bytes.size();bool flushed=FlushFileBuffers(file)!=0;CloseHandle(file);
  if(!ok||!flushed){DeleteFileW(path.c_str());throw std::runtime_error("Export failed; incomplete output removed");}return path;
 }
 throw std::runtime_error("Too many output files have the same name; choose another folder");
}
static DWORD WINAPI batchWorker(void*arg){
 auto&s=*static_cast<BatchConvert*>(arg);
 // Delphi configures the x87 precision/rounding mode on the UI thread.
 // Carry it into each worker so legacy results retain identical rounding.
 __asm__ __volatile__("fldcw %0"::"m"(s.fpControl));
 try{if(s.phase==0){s.data=sit::Data();s.data.source=utf8(s.files[s.index]);if(!sit::parseConversion(readFile(s.files[s.index]),s.data))throw std::runtime_error("Unsupported Convert input; use FIELDS/Full or CTD/STD text with Date/Time and Interval");}
 else{sit::calculate(s.data,s.choice,formula);s.output=batchWrite(s.folder,s.files[s.index],sit::output(s.data));}}
 catch(const std::exception&e){s.error=e.what();}catch(...){s.error="Conversion failed. The source file was not changed.";}
 PostMessageW(s.window,batchComplete,0,0);return 0;
}
static void batchStart(BatchConvert&s,int phase){
 s.phase=phase;s.error.clear();__asm__ __volatile__("fnstcw %0":"=m"(s.fpControl));s.thread=CreateThread(0,0,batchWorker,&s,0,0);
 if(!s.thread)throw std::runtime_error("Cannot start the conversion worker");
}
static bool batchConditions(const sit::Data&d,const sit::Choices&c){
 return c.useGPS||(sit::needsWater(c)&&(!sit::complete(d,"T")||!sit::canSal(d)))||(sit::needsAir(c)&&c.air<=0)||(sit::modernTemperatureRequired(c)&&!c.temperatureScale);
}
static void batchFinish(BatchConvert&s){
 s.finished=true;SendDlgItemMessageW(s.window,603,PBM_SETMARQUEE,FALSE,0);
 std::wstring text=wide(std::to_string(s.converted))+L" converted, "+wide(std::to_string(s.failed))+L" failed, "+wide(std::to_string(s.files.size()-s.index))+L" not processed.";
 SetDlgItemTextW(s.window,601,text.c_str());SetDlgItemTextW(s.window,605,L"Close");EnableWindow(GetDlgItem(s.window,605),TRUE);
 batchLog(s,s.stop?L"Stopped. Completed output files have been kept.":L"Finished.");
}
static LRESULT CALLBACK batchProc(HWND h,UINT m,WPARAM w,LPARAM l){
 auto*s=reinterpret_cast<BatchConvert*>(GetWindowLongPtrW(h,GWLP_USERDATA));
 if(m==WM_NCCREATE){s=static_cast<BatchConvert*>(reinterpret_cast<CREATESTRUCTW*>(l)->lpCreateParams);s->window=h;SetWindowLongPtrW(h,GWLP_USERDATA,LONG_PTR(s));}
 if(!s)return DefWindowProcW(h,m,w,l);
 try{
  if(m==WM_CREATE){
   control(h,L"STATIC",L"Preparing conversion...",0,18,15,710,40,601);
   control(h,L"STATIC",(L"Output folder: "+s->folder).c_str(),0,18,58,710,40,602);
   HWND p=control(h,PROGRESS_CLASSW,L"",PBS_MARQUEE,18,104,710,18,603);SendMessageW(p,PBM_SETMARQUEE,TRUE,35);
   control(h,L"EDIT",L"",ES_MULTILINE|ES_READONLY|ES_AUTOVSCROLL|WS_VSCROLL|WS_BORDER|WS_TABSTOP,18,135,710,265,604);
   control(h,L"BUTTON",L"Cancel remaining",BS_DEFPUSHBUTTON|WS_TABSTOP,548,416,180,30,605);
   PostMessageW(h,batchNext,0,0);return 0;
  }
  if(m==batchNext){
   if(s->stop||s->index==s->files.size()){batchFinish(*s);return 0;}
   SetDlgItemTextW(h,601,(L"File "+wide(std::to_string(s->index+1))+L" of "+wide(std::to_string(s->files.size()))+L": "+batchLeaf(s->files[s->index])).c_str());
   batchStart(*s,0);return 0;
  }
  if(m==batchComplete){
   WaitForSingleObject(s->thread,INFINITE);CloseHandle(s->thread);s->thread=0;
   if(!s->error.empty()){++s->failed;batchLog(*s,L"FAILED: "+batchLeaf(s->files[s->index])+L" - "+wide(s->error));++s->index;PostMessageW(h,batchNext,0,0);return 0;}
   if(s->phase==1){
    ++s->converted;batchLog(*s,L"Saved: "+s->output);
    s->choices[s->pending.signature]=s->pending;
    if(!savePreset(s->pending.signature,s->pending.source,s->pending.choices))batchLog(*s,L"Converted successfully; choices could not be saved for next time.");
    ++s->index;PostMessageW(h,batchNext,0,0);return 0;
   }
   if(s->stop){batchFinish(*s);return 0;}
   auto sig=sitpreset::signature(s->data);auto found=s->choices.find(sig);sitpreset::Record prior;bool reused=false;
   if(found!=s->choices.end()){s->choice=sitpreset::reuse(found->second,s->data);reused=true;
    if(batchConditions(s->data,s->choice)){auto initial=s->choice;if(!choose(h,s->data,s->choice,&initial)){s->stop=true;batchFinish(*s);return 0;}}
   }else{
    s->choice=sit::Choices();
    if(loadPreset(s->data,prior)){int answer=offerPreset(h,s->data,prior);if(answer==IDCANCEL){s->stop=true;batchFinish(*s);return 0;}if(answer==IDYES){s->choice=sitpreset::reuse(prior,s->data);reused=true;}}
    auto initial=s->choice;if(!choose(h,s->data,s->choice,reused?&initial:0)){s->stop=true;batchFinish(*s);return 0;}
   }
   s->pending.signature=sig;s->pending.source=s->data.source;s->pending.choices=s->choice;
   // Presets are persisted only once this file has converted successfully.
   batchStart(*s,1);return 0;
  }
  if((m==WM_COMMAND&&LOWORD(w)==605)||m==WM_CLOSE){
   if(s->finished){DestroyWindow(h);return 0;}
   s->stop=true;SetDlgItemTextW(h,605,L"Stopping...");EnableWindow(GetDlgItem(h,605),FALSE);
   if(!s->thread)batchFinish(*s);return 0;
  }
 }catch(const std::exception&e){batchLog(*s,wide(e.what()));s->stop=true;if(!s->thread)batchFinish(*s);return 0;}
 return DefWindowProcW(h,m,w,l);
}
static void batchRun(HWND owner,const std::vector<std::wstring>&files,const std::wstring&folder){
 BatchConvert s;s.files=files;s.folder=folder;
 INITCOMMONCONTROLSEX ic={sizeof(ic),ICC_PROGRESS_CLASS};InitCommonControlsEx(&ic);
 WNDCLASSW wc={};wc.hInstance=instance;wc.lpfnWndProc=batchProc;wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=(HBRUSH)(COLOR_BTNFACE+1);wc.lpszClassName=L"SITBatchConvert";RegisterClassW(&wc);
 HWND h=CreateWindowExW(WS_EX_DLGMODALFRAME,wc.lpszClassName,L"SAIV IT - Convert multiple files",WS_CAPTION|WS_SYSMENU,CW_USEDEFAULT,CW_USEDEFAULT,764,495,owner,0,instance,&s);
 if(!h)throw std::runtime_error("Cannot open the conversion window");EnableWindow(owner,FALSE);ShowWindow(h,SW_SHOW);MSG m;
 while(IsWindow(h)&&GetMessageW(&m,0,0,0)>0)if(!IsDialogMessageW(h,&m)){TranslateMessage(&m);DispatchMessageW(&m);}
 if(s.thread){WaitForSingleObject(s.thread,INFINITE);CloseHandle(s.thread);s.thread=0;}
 if(IsWindow(h))DestroyWindow(h);
 EnableWindow(owner,TRUE);SetActiveWindow(owner);
}
static int CALLBACK batchBrowseProc(HWND h,UINT m,LPARAM,LPARAM path){if(m==BFFM_INITIALIZED)SendMessageW(h,BFFM_SETSELECTIONW,TRUE,path);return 0;}
extern "C" __declspec(dllexport) int __stdcall SitConvert(HWND owner){
 try{
  registerClasses();std::vector<wchar_t> names(262144,0);OPENFILENAMEW of={};of.lStructSize=sizeof(of);of.hwndOwner=owner;
  of.lpstrFilter=L"CSV/TXT files (*.csv;*.txt)\0*.csv;*.txt\0All files (*.*)\0*.*\0\0";of.lpstrFile=names.data();of.nMaxFile=DWORD(names.size());of.lpstrTitle=L"Convert - select one or more files (Ctrl or Shift)";
  wchar_t initial[32768]={};if(GetCurrentDirectoryW(32768,initial))of.lpstrInitialDir=initial;
  of.Flags=OFN_EXPLORER|OFN_ALLOWMULTISELECT|OFN_FILEMUSTEXIST|OFN_PATHMUSTEXIST|OFN_NOCHANGEDIR|OFN_DONTADDTORECENT;
  if(!GetOpenFileNameW(&of)){if(CommDlgExtendedError())throw std::runtime_error("Could not select files. Try selecting fewer files at once.");return 1;}
  std::vector<std::wstring> files;const wchar_t*next=names.data()+wcslen(names.data())+1;
  if(!*next)files.push_back(names.data());else while(*next){files.push_back(std::wstring(names.data())+L"\\"+next);next+=wcslen(next)+1;}
  if(files.size()==1){ // Existing one-file result window and SD2 import stay available.
   return importOne(owner,files.front());
  }
  std::wstring sourceFolder=files.front().substr(0,files.front().find_last_of(L"\\/"));
  BROWSEINFOW browse={};browse.hwndOwner=owner;browse.lpszTitle=L"Choose the output folder for the converted files. Originals are kept.";browse.ulFlags=BIF_RETURNONLYFSDIRS|BIF_NEWDIALOGSTYLE|BIF_EDITBOX;
  browse.lParam=reinterpret_cast<LPARAM>(sourceFolder.c_str());
  browse.lpfn=batchBrowseProc;
  HRESULT initialized=CoInitializeEx(0,COINIT_APARTMENTTHREADED);LPITEMIDLIST selection=SHBrowseForFolderW(&browse);wchar_t folder[MAX_PATH]={};bool ok=selection&&SHGetPathFromIDListW(selection,folder);if(selection)CoTaskMemFree(selection);if(SUCCEEDED(initialized))CoUninitialize();if(!ok)return 1;
  batchRun(owner,files,folder);return 1;
 }catch(const std::exception&e){error(owner,e.what());return 1;}catch(...){error(owner,"Conversion failed. Original files were not changed.");return 1;}
}
