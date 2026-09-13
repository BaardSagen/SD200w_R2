// Settings share the native terminal's existing serial port and receive stream.
#include "settings_protocol.h"
static uintptr_t settingsMain=0;
static sitsettings::Kind settingsKind=sitsettings::None,settingsPending=sitsettings::None;
static unsigned settingsPort=0,settingsPendingPort=0;
static bool settingsBusy=false,settingsReopen=false,settingsAwaiting=false;
static bool firmwareQuiet=false;
static DWORD settingsAccepted=0,settingsRxAt=0;
static std::string settingsRx,settingsContext,settingsPendingContext,settingsSerial;
static std::string settingsSerialFrom(const std::string&s){std::smatch m;if(std::regex_search(s,m,std::regex("SN([0-9]+)",std::regex::icase)))return m[1];return "";}
static HWND settingsDialog=0;
static uintptr_t settingsComm(){return settingsMain?nd(settingsMain+0x510):0;}
static bool settingsConnected(){auto comm=settingsComm();return settingsKind!=sitsettings::None&&comm&&*reinterpret_cast<unsigned char*>(comm+0x24)&&*reinterpret_cast<unsigned char*>(comm+0x34)==settingsPort;}
static void settingsPause(unsigned ms){DWORD start=GetTickCount();while(GetTickCount()-start<ms){MSG msg;while(PeekMessageW(&msg,0,0,0,PM_REMOVE)){if(msg.message==WM_QUIT)throw std::runtime_error("Application closing");TranslateMessage(&msg);DispatchMessageW(&msg);}Sleep(10);}}
struct SettingsSearch{const wchar_t*text;HWND result;};
static BOOL CALLBACK settingsFindButton(HWND h,LPARAM arg){auto&s=*reinterpret_cast<SettingsSearch*>(arg);wchar_t text[100];GetWindowTextW(h,text,100);if(wcscmp(text,s.text)==0){s.result=h;return FALSE;}return TRUE;}
static HWND settingsButton(const wchar_t*caption){SettingsSearch s={caption,0};EnumChildWindows(HWND(nd(settingsMain+0x14c)),settingsFindButton,LPARAM(&s));return s.result;}

static void settingsEnable(){if(!settingsMain)return;auto comm=settingsComm();if(settingsAwaiting){if(settingsConnected())settingsAwaiting=false;else if(GetTickCount()-settingsAccepted>7000){settingsAwaiting=false;settingsKind=sitsettings::None;}}else if(!settingsBusy&&!settingsConnected())settingsKind=sitsettings::None;bool ready=settingsConnected()&&!settingsBusy;
 for(auto name:{L"&Interval",L"TIME/D&ATE"}){HWND h=settingsButton(name);if(h)EnableWindow(h,ready);}
 if(nd(settingsMain+0x374))nv(nd(settingsMain+0x374),0x5c,ready);
}
struct SettingsLink: sitsettings::Link {
 void send(const std::string&s)override{if(!settingsConnected())throw std::runtime_error("Connection lost. Run Detect again.");settingsRx.clear();settingsRxAt=GetTickCount();uintptr_t str=0;nativeAssign(uintptr_t(&str),s);nc(0x7ffc4,settingsComm(),str);nc(0x3f98,uintptr_t(&str));}
 std::string wait(std::function<bool(const std::string&)>pred,unsigned quiet=250,unsigned timeout=12000)override{DWORD start=GetTickCount();while(GetTickCount()-start<timeout){settingsPause(10);auto s=settingsRx;if(sitsettings::deviceError(s))throw std::runtime_error("Device rejected the operation:\n"+s);if(pred(s)&&GetTickCount()-settingsRxAt>=quiet){settingsContext=s;return s;}}
 throw sitsettings::Timeout(settingsRx);}
 void pause(unsigned ms)override{settingsPause(ms);}
 std::string freshStatus()override{settingsReopen=true;nc(0x7f9c4,settingsComm());pause(750);settingsRx.clear();settingsRxAt=GetTickCount();nc(0x7e8f8,settingsComm());settingsReopen=false;
 auto result=wait([](const std::string&s){return (sitsettings::has(s,"osu107")||sitsettings::has(s,"saiv110"))&&(sitsettings::has(s,"Hold")||sitsettings::has(s,"Type")||sitsettings::has(s,"Surface-logger:"));},350,8000);if(!settingsSerial.empty()&&settingsSerialFrom(result)!=settingsSerial)throw std::runtime_error("Logger serial number changed. Run Detect again.");if(!sitsettings::has(result,settingsKind==sitsettings::Surface?"SAIV110 Surface logger":"OSU107 Instrument logger"))throw std::runtime_error("Detected logger mode changed. Run Detect again.");return result;}
 sitsettings::Clock now(bool gmt,int ahead=0)override{SYSTEMTIME t;if(gmt)GetSystemTime(&t);else GetLocalTime(&t);if(ahead){FILETIME file;SystemTimeToFileTime(&t,&file);ULARGE_INTEGER value;value.LowPart=file.dwLowDateTime;value.HighPart=file.dwHighDateTime;value.QuadPart+=ULONGLONG(ahead)*10000000;file.dwLowDateTime=value.LowPart;file.dwHighDateTime=value.HighPart;FileTimeToSystemTime(&file,&t);}if(t.wYear<2000||t.wYear>2099)throw std::runtime_error("Logger clocks require a PC year from 2000 through 2099");char date[20],time[20],wire[30];sprintf(date,"%04u-%02u-%02u",t.wYear,t.wMonth,t.wDay);sprintf(time,"%02u:%02u:%02u",t.wHour,t.wMinute,t.wSecond);sprintf(wire,"%02u-%02u-%02u-%02u-%02u-%02u",t.wYear%100,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond);return {wire,date,time,sitnative::timestamp(date,time)};}
 double timestamp(const std::string&date,const std::string&time)override{return sitnative::timestamp(date,time);}
};
static void settingsWrite(const std::wstring&path,const std::string&data,DWORD creation){HANDLE file=CreateFileW(path.c_str(),GENERIC_WRITE,0,0,creation,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,0);if(file==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot write "+utf8(path));DWORD written=0;bool ok=WriteFile(file,data.data(),DWORD(data.size()),&written,0)&&written==data.size()&&FlushFileBuffers(file);CloseHandle(file);if(!ok)throw std::runtime_error("Writing or flushing failed: "+utf8(path));}
static std::wstring settingsConfig(HWND owner){wchar_t name[32768]={};OPENFILENAMEW o={sizeof(o)};o.hwndOwner=owner;o.lpstrFilter=L"Surface system.ini\0system.ini\0\0";o.lpstrFile=name;o.nMaxFile=32768;o.lpstrTitle=L"Select config/system.ini on the connected SAIV110 USB disk";o.Flags=OFN_FILEMUSTEXIST|OFN_PATHMUSTEXIST|OFN_NOCHANGEDIR;if(!GetOpenFileNameW(&o))return L"";std::wstring path=name;auto slash=path.find_last_of(L"\\/");if(slash==std::wstring::npos||lstrcmpiW(path.substr(slash+1).c_str(),L"system.ini"))throw std::runtime_error("Select the connected logger's config/system.ini");return path;}
static void settingsSurfaceInterval(SettingsLink&link,int index,HWND owner){
 auto status=sitsettings::stopSurface(link);
 // Refresh first, before trusting the host's mounted filesystem cache.
 sitsettings::request(link,"F",[](const std::string&s){return sitsettings::has(s,"Refresh disk")&&sitsettings::yn(s);},350);
 settingsReopen=true;sitsettings::request(link,"Y",[](const std::string&s){return sitsettings::has(s,"System disk refresh will start in 3 seconds.");},100,8000);
 link.pause(4500);status=link.freshStatus();if(!sitsettings::has(status,"saiv110")||!sitsettings::stopped(status))throw std::runtime_error("Surface did not return stopped after disk refresh");
 auto path=settingsConfig(owner);if(path.empty())return;auto original=readFile(path);auto modified=sitsettings::replaceSurfaceInterval(original,sitsettings::intervals[index].seconds);auto backup=path+L".sit-backup-"+wide(std::to_string(GetTickCount()));settingsWrite(backup,original,CREATE_NEW);
 try {settingsWrite(path,modified,TRUNCATE_EXISTING);if(readFile(path)!=modified)throw std::runtime_error("Disk readback differs from the requested configuration");link.pause(10000);
 sitsettings::request(link,"U",[](const std::string&s){return sitsettings::has(s,"OK SAIV110_UPDATE_CONFIG");},300,60000);
 if(readFile(path)!=modified)throw std::runtime_error("Configuration changed during APPLY");auto final=link.freshStatus();if(!sitsettings::has(final,"saiv110")||!sitsettings::stopped(final))throw std::runtime_error("Could not confirm stopped Surface after APPLY");
 MessageBoxW(owner,(L"Surface interval applied and disk value verified. Logger remains stopped.\nOriginal configuration saved as:\n"+backup).c_str(),L"SAIV IT - Interval",MB_OK|MB_ICONINFORMATION);
 }catch(const std::exception&e){throw std::runtime_error(std::string(e.what())+"\nOriginal configuration retained at: "+utf8(backup));}
}
static LRESULT CALLBACK settingsDialogProc(HWND h,UINT m,WPARAM w,LPARAM l){
 if(m==WM_CLOSE){if(!settingsBusy)DestroyWindow(h);return 0;}
 if(m==WM_COMMAND&&LOWORD(w)==2){if(!settingsBusy)DestroyWindow(h);return 0;}
 if(m==WM_COMMAND&&LOWORD(w)==1&&HIWORD(w)==BN_CLICKED){
  if(settingsBusy)return 0;
  bool clock=GetWindowLongPtrW(h,GWLP_USERDATA)==2;int choice=int(SendDlgItemMessageW(h,101,CB_GETCURSEL,0,0));bool gmt=SendDlgItemMessageW(h,102,BM_GETCHECK,0,0)==BST_CHECKED;
  if(!settingsConnected()){MessageBoxW(h,L"Run Detect first.",L"SAIV IT",MB_OK);return 0;}settingsBusy=true;settingsEnable();EnableWindow(GetDlgItem(h,1),FALSE);EnableWindow(GetDlgItem(h,2),FALSE);SetDlgItemTextW(h,103,L"Communicating with the detected device. Please wait...");
  std::string progress;
  try{SettingsLink link;if(clock){if(settingsKind==sitsettings::Surface)sitsettings::stopSurface(link);else {std::string context=settingsContext;if(settingsKind==sitsettings::OSU)context=link.freshStatus();sitsettings::sdClock(link,gmt,context);progress="SD200 clock verified. ";}
    if(settingsKind==sitsettings::OSU||settingsKind==sitsettings::Surface){sitsettings::loggerClock(link,settingsKind,gmt);progress+="Logger clock verified. ";}
    MessageBoxW(h,wide(progress+(gmt?"PC time: GMT/UTC.":"PC time: LT.")).c_str(),L"SAIV IT - TIME/DATE",MB_OK|MB_ICONINFORMATION);
   }else if(settingsKind==sitsettings::Surface)settingsSurfaceInterval(link,choice,h);else {auto context=settingsKind==sitsettings::OSU?link.freshStatus():settingsContext;sitsettings::setInterval(link,choice,context);MessageBoxW(h,L"SD200 measuring interval verified.",L"SAIV IT - Interval",MB_OK|MB_ICONINFORMATION);}
  }catch(const std::exception&e){MessageBoxW(h,wide(progress+e.what()).c_str(),L"SAIV IT - Settings",MB_OK|MB_ICONERROR);}
  settingsBusy=false;settingsReopen=false;settingsEnable();EnableWindow(GetDlgItem(h,1),TRUE);EnableWindow(GetDlgItem(h,2),TRUE);SetDlgItemTextW(h,103,L"Ready. Settings are reported successful only after verification.");return 0;
 }
 return DefWindowProcW(h,m,w,l);
}
static void settingsShow(bool clock){if(settingsDialog&&IsWindow(settingsDialog)){SetForegroundWindow(settingsDialog);return;}if(!settingsConnected())return;WNDCLASSW wc={};wc.hInstance=instance;wc.lpfnWndProc=settingsDialogProc;wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=HBRUSH(COLOR_BTNFACE+1);wc.lpszClassName=L"SITDeviceSettings";RegisterClassW(&wc);HWND owner=HWND(nd(settingsMain+0x14c));settingsDialog=CreateWindowExW(WS_EX_DLGMODALFRAME,wc.lpszClassName,clock?L"SAIV IT - TIME/DATE":L"SAIV IT - Interval",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,CW_USEDEFAULT,CW_USEDEFAULT,520,240,owner,0,instance,0);HWND h=settingsDialog;SetWindowLongPtrW(h,GWLP_USERDATA,clock?2:1);
 std::wstring unit=settingsKind==sitsettings::Surface?L"SAIV110 Surface":settingsKind==sitsettings::OSU?L"OSU107 + SD200":L"SD200";control(h,L"STATIC",(unit+L" - COM"+wide(std::to_string(settingsPort))).c_str(),0,16,12,480,22,100);
 if(clock){control(h,L"STATIC",L"Set the device clock(s) from the PC clock:",0,16,42,475,24,104);control(h,L"BUTTON",L"&LT - PC local time",BS_AUTORADIOBUTTON|WS_GROUP|WS_TABSTOP,16,75,210,24,101);control(h,L"BUTTON",L"&GMT - UTC",BS_AUTORADIOBUTTON|WS_TABSTOP,260,75,180,24,102);SendDlgItemMessageW(h,101,BM_SETCHECK,BST_CHECKED,0);}
 else {control(h,L"STATIC",L"Measuring interval:",0,16,45,155,24,104);HWND cb=control(h,L"COMBOBOX",L"",CBS_DROPDOWNLIST|WS_VSCROLL|WS_TABSTOP,175,42,290,320,101);for(const auto&i:sitsettings::intervals)SendMessageW(cb,CB_ADDSTRING,0,LPARAM(wide(i.label).c_str()));SendMessageW(cb,CB_SETCURSEL,1,0);}
 control(h,L"STATIC",L"The device is left stopped after changing settings.",0,16,112,475,35,103);control(h,L"BUTTON",L"&Set",BS_DEFPUSHBUTTON|WS_TABSTOP,270,158,100,28,1);control(h,L"BUTTON",L"Close",WS_TABSTOP,382,158,100,28,2);ShowWindow(h,SW_SHOW);EnableWindow(owner,FALSE);
 MSG msg;while(IsWindow(h)&&GetMessageW(&msg,0,0,0)>0){if(!IsDialogMessageW(h,&msg)){TranslateMessage(&msg);DispatchMessageW(&msg);}}EnableWindow(owner,TRUE);SetForegroundWindow(owner);settingsDialog=0;
}
static LRESULT CALLBACK settingsMainProc(HWND h,UINT m,WPARAM w,LPARAM l,UINT_PTR,DWORD_PTR){auto result=DefSubclassProc(h,m,w,l);if(m==WM_TIMER&&w==139)settingsEnable();return result;}
static int settingsNative(unsigned op,uintptr_t a,uintptr_t b,uintptr_t c){
 if(op==20){settingsMain=a;HWND h=HWND(nd(a+0x14c));if(h){SetWindowSubclass(h,settingsMainProc,139,0);SetTimer(h,139,250,0);}return 0;}
 if(op==30){settingsPending=sitsettings::None;settingsPendingPort=0;settingsPendingContext.clear();uintptr_t rows=nd(a+0x330);if(!rows)return 0;int count=int(nd(rows-4));for(int i=0;i<count;++i,rows+=20){uintptr_t label=nd(rows+16),worker=nd(rows);if(!label||!worker||nd(label-4)!=5||memcmp(reinterpret_cast<void*>(label),"Instr",5))continue;if(*reinterpret_cast<unsigned char*>(worker+0x60)||*reinterpret_cast<unsigned char*>(worker+0x62)!=1||*reinterpret_cast<unsigned char*>(worker+0x71)!=2)break;auto serial=nd(worker+0x64);if(!serial)break;settingsPendingPort=*reinterpret_cast<unsigned char*>(serial+0x34);uintptr_t text=nd(worker+0x5c);if(text){settingsPendingContext=reinterpret_cast<const char*>(text);auto&t=settingsPendingContext;settingsPending=sitsettings::has(t,"OSU107 Instrument logger")?sitsettings::OSU:sitsettings::has(t,"SAIV110 Surface logger")?sitsettings::Surface:(sitsettings::mainMenu(t)||sitsettings::has(t,"status/start/menu")||sitsettings::has(t,"current set up:")||sitsettings::has(t,"measuring interval")||sitsettings::has(t,"hold <i> to activate")||sitsettings::has(t,"- passive -"))?sitsettings::SD200:sitsettings::None;}break;}return 0;}
 if(op==31){if(a==1){settingsKind=settingsPending;settingsPort=settingsPendingPort;settingsContext=settingsPendingContext;settingsSerial=settingsSerialFrom(settingsPendingContext);settingsAwaiting=true;settingsAccepted=GetTickCount();}return 0;}
 if(op==32){char ch=char(a);settingsRx+=ch;if(settingsRx.size()>65536)settingsRx.erase(0,32768);settingsRxAt=GetTickCount();return firmwareQuiet?1:0;}
 if(op==34){if(a==settingsComm()&&!settingsReopen&&!settingsAwaiting)settingsKind=sitsettings::None;return 0;}
 if(op==40&&b){auto tag=nd(b+12);if(tag==0x53495449||tag==0x53495454){settingsMain=a;settingsShow(tag==0x53495454);return 1;}}
 if(op==41&&b==nd(a+0x374)&&(!settingsConnected()||settingsBusy))return 1;
 return 0;
}
