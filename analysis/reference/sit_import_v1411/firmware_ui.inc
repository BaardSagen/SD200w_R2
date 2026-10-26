#include "firmware_protocol.h"
#include "firmware_windows.inc"
static const UINT firmwareMenuId=0x7e51;
static HWND firmwareWindow=0;

struct FirmwareOperations:sitfirmware::Operations {
    HWND window;FirmwareDevice device;FirmwareLink link;std::string bytes;
    std::wstring backupPath;std::map<std::wstring,std::string> saved;bool local=false;
    explicit FirmwareOperations(HWND h,const FirmwareDevice&d):window(h),device(d){}
    void progress(sitfirmware::Phase p)override {SetDlgItemTextW(window,501,wide(sitfirmware::phaseText(p)).c_str());UpdateWindow(window);}
    void bound(bool needConfig=true) {
        auto ports=firmwarePorts();auto p=ports.find(device.port);
        if(p==ports.end()||p->second!=device.usb)throw std::runtime_error("The USB COM connection changed. No further commands will be sent.");
        auto roots=firmwareRoots(device.usb);
        if(std::find(roots.begin(),roots.end(),device.root)==roots.end())throw std::runtime_error("The logger disk changed or disappeared");
        firmwarePlain(device.root,true);
        if(needConfig) {
            firmwarePlain(device.root+L"config",true);
            auto current=sitfirmware::ini(firmwareRead(device.root+L"config\\system.ini"));
            if(!sitfirmware::sameDevice(current,device.identity))throw std::runtime_error("Disk configuration belongs to a different device");
        }
    }
    sitfirmware::Identity liveIdentity()override {
        bound();auto text=link.localMenu();local=true;
        auto id=sitfirmware::menuIdentity(text);
        if(!sitfirmware::sameDevice(id,device.identity))throw std::runtime_error("The logger menu and USB config identify different devices");
        auto ver=sitsettings::request(link,"VER\r",[](const std::string&s){return sitsettings::has(s,"Firmware version:")&&sitsettings::has(s,"Build:");},300);
        sitfirmware::verifyVersionResponse(ver,id);
        return id;
    }
    void download(const sitfirmware::Manifest&m)override {
        firmwareBackground([&]{bytes=firmwareFetch(m.download,4*1024*1024);
            if(bytes.size()<32||updateHash(bytes)!=m.sha256)throw std::runtime_error("Firmware download checksum mismatch. The device has not been updated.");
            // MCUboot signed image header: reject an HTML/error page even if a manifest was mispublished.
            if((unsigned char)bytes[0]!=0x3d||(unsigned char)bytes[1]!=0xb8||(unsigned char)bytes[2]!=0xf3||(unsigned char)bytes[3]!=0x96)
                throw std::runtime_error("The server file is not a MCUboot firmware image");
        });
        SetDlgItemTextW(window,502,wide("Download verified: "+std::to_string(bytes.size())+" bytes.\r\nSHA-256 matches the firmware manifest.\r\n\r\nThe complete file will now be copied to the device and read back before the update starts.").c_str());
    }
    void backup()override {
        bound();firmwareSnapshot(device.root+L"config",L"",saved);
        wchar_t appdata[MAX_PATH];if(FAILED(SHGetFolderPathW(0,CSIDL_LOCAL_APPDATA,0,SHGFP_TYPE_CURRENT,appdata)))throw std::runtime_error("Cannot locate the PC backup folder");
        auto base=std::wstring(appdata)+L"\\SAIV_IT\\FirmwareBackups";
        int rc=SHCreateDirectoryExW(window,base.c_str(),0);if(rc!=ERROR_SUCCESS&&rc!=ERROR_ALREADY_EXISTS)throw std::runtime_error("Cannot create firmware backup folder");
        backupPath=base+L"\\SN"+wide(device.identity.serial)+L"-"+wide(std::to_string(GetCurrentProcessId()))+L"-"+wide(std::to_string(GetTickCount()));
        if(!CreateDirectoryW(backupPath.c_str(),0))throw std::runtime_error("Cannot create a unique config backup");
        for(const auto&file:saved) {
            auto dest=backupPath+L"\\"+file.first;auto folder=dest.substr(0,dest.find_last_of(L'\\'));
            int made=SHCreateDirectoryExW(window,folder.c_str(),0);if(made!=ERROR_SUCCESS&&made!=ERROR_ALREADY_EXISTS)throw std::runtime_error("Cannot create config backup subfolder");
            settingsWrite(dest,file.second,CREATE_NEW);if(firmwareRead(dest,4*1024*1024)!=file.second)throw std::runtime_error("Config backup verification failed");
        }
        SetDlgItemTextW(window,507,(L"Configuration backup: "+backupPath).c_str());
    }
    void stage()override {
        bound();auto folder=device.root+L"update";
        if(!CreateDirectoryW(folder.c_str(),0)&&GetLastError()!=ERROR_ALREADY_EXISTS)throw std::runtime_error("Cannot create update folder on the logger disk");
        firmwarePlain(folder,true);auto file=folder+L"\\osu_m_update.bin";
        firmwareWriteImage(folder,bytes);
        link.pause(10000);bound();
        if(firmwareRead(file,4*1024*1024)!=bytes)throw std::runtime_error("Firmware file changed after copying. Update was not started.");
        SetDlgItemTextW(window,502,wide("Firmware file verified on the device: "+std::to_string(bytes.size())+" / "+std::to_string(bytes.size())+" bytes.\r\nThe complete file was read back and matches the SHA-256-verified download byte for byte.\r\n\r\nKeep USB connected. The disk and COM port will disappear during the update. SIT will wait for this device to return and verify its firmware version.").c_str());
    }
    void closePort() {auto comm=settingsComm();if(comm&&*reinterpret_cast<unsigned char*>(comm+0x24))nc(0x7f9c4,comm);}
    void start()override {
        bound();sitsettings::request(link,"CFG\r",[](const std::string&s){return sitsettings::has(s,"[Config]>")&&sitsettings::has(s,"FWU");},300);
        // Both full copy readback and the complete Config prompt precede this irreversible command.
        bound();if(firmwareRead(device.root+L"update\\osu_m_update.bin",4*1024*1024)!=bytes)throw std::runtime_error("Staged firmware changed");
        link.send("FWU\r");local=false;
    }
    void reconnect(bool resetCycle)override {
        sitfirmware::ReturnCycle cycle;bool closed=false;DWORD start=GetTickCount();unsigned limit=resetCycle?90000:300000;
        while(GetTickCount()-start<limit) {
            auto roots=firmwareRoots(device.usb);auto ports=firmwarePorts();unsigned returnedPort=0,portCount=0;
            for(const auto&p:ports)if(p.second==device.usb){returnedPort=p.first;++portCount;}
            bool returned=cycle.observe(unsigned(roots.size()),portCount);
            if(cycle.portGone&&!closed){closePort();closed=true;}
            if(returned) {
                auto root=roots[0];if(!firmwareDirectory(root+L"config")){link.pause(250);continue;}
                // A transient/incomplete system.ini may be visible during mount; do not accept it yet.
                try {auto id=sitfirmware::ini(firmwareRead(root+L"config\\system.ini"));if(!sitfirmware::sameDevice(id,device.identity))throw std::runtime_error("Unexpected returning logger");}
                catch(...){link.pause(250);continue;}
                device.root=root;device.port=returnedPort;settingsPort=returnedPort;
                auto comm=settingsComm();if(!comm)throw std::runtime_error("SIT terminal is no longer available");
                *reinterpret_cast<unsigned char*>(comm+0x34)=static_cast<unsigned char>(returnedPort);
                settingsRx.clear();settingsRxAt=GetTickCount();nc(0x7e8f8,comm);link.pause(750);
                if(!*reinterpret_cast<unsigned char*>(comm+0x24))throw std::runtime_error("Logger returned but its COM port could not be opened");
                return;
            }
            if(sitsettings::deviceError(settingsRx)||sitsettings::has(settingsRx,"FWUPDATE aborted")||sitsettings::has(settingsRx,"FWUPDATE denied"))throw std::runtime_error("The device rejected the firmware operation. Keep USB connected and check the device before retrying.");
            link.pause(200);
        }
        throw std::runtime_error("Timed out waiting for the same device disk and COM port to disappear and return. The update is not verified. Keep USB connected and inspect the device before retrying.");
    }
    void cleanConfig()override {
        bound();if(backupPath.empty()||saved.empty())throw std::runtime_error("No verified config backup is available");
        // Back up changes regenerated by the firmware too; never silently delete data absent from the PC backup.
        std::map<std::wstring,std::string> current;firmwareSnapshot(device.root+L"config",L"",current);
        auto after=backupPath+L"\\before-regeneration";if(!CreateDirectoryW(after.c_str(),0))throw std::runtime_error("Cannot back up configuration before regeneration");
        for(const auto&file:current) {auto dest=after+L"\\"+file.first;auto folder=dest.substr(0,dest.find_last_of(L'\\'));int rc=SHCreateDirectoryExW(window,folder.c_str(),0);if(rc!=ERROR_SUCCESS&&rc!=ERROR_ALREADY_EXISTS)throw std::runtime_error("Config backup failed");settingsWrite(dest,file.second,CREATE_NEW);if(firmwareRead(dest,4*1024*1024)!=file.second)throw std::runtime_error("Config backup verification failed");}
        if(!updateFolderEmpty())throw std::runtime_error("Update folder is no longer empty; config regeneration was stopped");
        bound();std::map<std::wstring,std::string> recheck;firmwareSnapshot(device.root+L"config",L"",recheck);if(recheck!=current)throw std::runtime_error("Config changed while it was being backed up; regeneration was stopped");
        // root is the resolved, same-USB mounted volume; exact child 'config' only.
        if(device.root.size()!=3||device.root[1]!=L':'||device.root[2]!=L'\\')throw std::runtime_error("Invalid logger root");
        firmwareDeleteSystemIni(device.root+L"config");link.pause(3000);
    }
    bool updateFolderEmpty()override {
        bound();link.localMenu();local=true;
        sitsettings::request(link,"CFG\r",[](const std::string&s){return sitsettings::has(s,"[Config]>");},300);
        auto status=sitsettings::request(link,"FWUST\r",[](const std::string&s){return sitsettings::has(s,"[Config]>");},300);
        sitsettings::request(link,"Q\r",[](const std::string&s){return sitsettings::has(s,"Returning to main menu");},300);
        link.localMenu();local=true;
        return sitfirmware::writeLockClear(status)&&diskUpdateFolderEmpty();
    }
    bool diskUpdateFolderEmpty() {
        bound();auto folder=device.root+L"update";DWORD attributes=GetFileAttributesW(folder.c_str());
        if(attributes==INVALID_FILE_ATTRIBUTES){DWORD error=GetLastError();if(error==ERROR_FILE_NOT_FOUND||error==ERROR_PATH_NOT_FOUND)return true;throw std::runtime_error("Could not inspect the device update folder");}
        firmwarePlain(folder,true);WIN32_FIND_DATAW item={};HANDLE find=FindFirstFileW((folder+L"\\*").c_str(),&item);
        if(find==INVALID_HANDLE_VALUE){if(GetLastError()==ERROR_FILE_NOT_FOUND)return true;throw std::runtime_error("Could not inspect the device update folder");}
        bool empty=true;do{std::wstring name=item.cFileName;if(name!=L"."&&name!=L"..")empty=false;}while(FindNextFileW(find,&item));DWORD error=GetLastError();FindClose(find);
        if(error!=ERROR_NO_MORE_FILES)throw std::runtime_error("Could not finish inspecting the device update folder");return empty;
    }
    void reset()override {
        bound(false);
        sitsettings::request(link,"SLP\r",[](const std::string&s){return sitsettings::has(s,"[Sleep]>")&&sitsettings::has(s,"RESET / RST / REBOOT");},300);
        link.send("RESET\r");local=false;
    }
    sitfirmware::Identity configIdentity()override {
        if(!updateFolderEmpty())throw std::runtime_error("Firmware cleanup is not complete after configuration restart");
        bound();std::map<std::wstring,std::string> current;firmwareSnapshot(device.root+L"config",L"",current);
        for(const auto&file:saved) {
            auto found=current.find(file.first);
            if(found==current.end())throw std::runtime_error("A configuration file is missing after restart: "+utf8(file.first));
            if(lstrcmpiW(file.first.c_str(),L"system.ini")!=0&&found->second!=file.second)
                throw std::runtime_error("A retained configuration/calibration file changed: "+utf8(file.first));
            if(lstrcmpiW(file.first.c_str(),L"system.ini")==0)sitfirmware::requireSettingsPreserved(file.second,found->second);
        }
        return sitfirmware::ini(firmwareRead(device.root+L"config\\system.ini"));
    }
    void leaveLocal() {if(local){bound();link.send("Q\r");link.pause(300);local=false;}}
};
struct FirmwareDialog {
    HWND h=0;bool busy=false,checked=false,available=false;FirmwareDevice device;sitfirmware::Manifest manifest;
    DWORD started=0;bool installing=false;
    std::wstring notes;std::unique_ptr<FirmwareOperations> operations;sitfirmware::Phase phase=sitfirmware::Phase::Idle;
};
static void firmwareLayout(HWND h) {
    RECT r;GetClientRect(h,&r);int w=r.right,z=r.bottom;
    MoveWindow(GetDlgItem(h,501),16,14,w-32,76,TRUE);
    MoveWindow(GetDlgItem(h,508),16,92,w-32,18,TRUE);
    MoveWindow(GetDlgItem(h,509),16,116,w-32,46,TRUE);
    MoveWindow(GetDlgItem(h,502),16,168,w-32,z-296,TRUE);
    MoveWindow(GetDlgItem(h,507),16,z-116,w-32,58,TRUE);
    MoveWindow(GetDlgItem(h,504),16,z-44,155,28,TRUE);MoveWindow(GetDlgItem(h,505),w-302,z-44,165,28,TRUE);MoveWindow(GetDlgItem(h,506),w-122,z-44,106,28,TRUE);
}
static LRESULT CALLBACK firmwareDialogProc(HWND h,UINT msg,WPARAM w,LPARAM l) {
    auto*s=reinterpret_cast<FirmwareDialog*>(GetWindowLongPtrW(h,GWLP_USERDATA));
    if(msg==WM_NCCREATE){s=static_cast<FirmwareDialog*>(reinterpret_cast<CREATESTRUCTW*>(l)->lpCreateParams);s->h=h;SetWindowLongPtrW(h,GWLP_USERDATA,LONG_PTR(s));}
    if(!s)return DefWindowProcW(h,msg,w,l);
    if(msg==WM_TIMER&&w==508) {
        InvalidateRect(GetDlgItem(h,508),0,FALSE);
        unsigned seconds=(GetTickCount()-s->started)/1000;
        auto text=s->installing?L"Update in progress. Keep USB connected and leave the device powered on.\r\n":L"Checking firmware. Please wait...\r\n";
        SetDlgItemTextW(h,509,(std::wstring(text)+L"Elapsed: "+wide(std::to_string(seconds/60))+L" min "+wide(std::to_string(seconds%60))+L" sec"+(s->installing?L". Usually about 2 minutes; restarts may take longer.":L"")).c_str());return 0;
    }
    if(msg==WM_DRAWITEM&&w==508) {
        auto*d=reinterpret_cast<DRAWITEMSTRUCT*>(l);RECT r=d->rcItem;
        FillRect(d->hDC,&r,GetSysColorBrush(COLOR_BTNFACE));
        if(s->busy) {int width=r.right-r.left,chunk=width/5;int x=int(((GetTickCount()-s->started)/12)%unsigned(width+chunk))-chunk;
            RECT part={std::max(0,x),r.top,std::min(width,x+chunk),r.bottom};
            FillRect(d->hDC,&part,GetSysColorBrush(COLOR_HIGHLIGHT));}
        return TRUE;
    }
    if(msg==WM_DESTROY){KillTimer(h,508);return 0;}
    if(msg==WM_SIZE){firmwareLayout(h);return 0;}
    if(msg==WM_GETMINMAXINFO){reinterpret_cast<MINMAXINFO*>(l)->ptMinTrackSize={680,490};return 0;}
    if(msg==WM_CLOSE){if(!s->busy)DestroyWindow(h);return 0;}
    if(msg==WM_QUERYENDSESSION)return !s->busy;
    if(msg==WM_COMMAND) {
        int id=LOWORD(w);if(id==2||id==506){SendMessageW(h,WM_CLOSE,0,0);return 0;}
        if((id!=504&&id!=505)||s->busy)return 0;
        if(id==505) {
            if(!s->checked||!s->available)return 0;
            auto prompt=wide(s->device.identity.product+" SN"+s->device.identity.serial+": "+s->device.identity.release+" -> "+s->manifest.release)+
                L"\r\n\r\nThis updates the connected device itself.\r\nDo not unplug USB or power off the device during the update.\r\nFirmware takes about 2 minutes, followed by about 15 seconds to regenerate config.\r\n\r\nSIT will back up config on this PC, then delete only config/system.ini after verifying the new firmware. The device will regenerate that file on restart. Other configuration and calibration files are retained.\r\n\r\nUpdate this device now?";
            if(MessageBoxW(h,prompt.c_str(),L"Update device firmware",MB_YESNO|MB_ICONWARNING|MB_DEFBUTTON2)!=IDYES)return 0;
        }
        s->busy=true;firmwareQuiet=true;settingsBusy=true;settingsReopen=true;settingsEnable();for(int c:{504,505,506})EnableWindow(GetDlgItem(h,c),FALSE);
        s->installing=id==505;s->started=GetTickCount();
        ShowWindow(GetDlgItem(h,508),SW_SHOW);ShowWindow(GetDlgItem(h,509),SW_SHOW);
        SetWindowTextW(h,s->installing?L"SAIV IT - Firmware update in progress":L"SAIV IT - Firmware");
        SetTimer(h,508,80,0);SendMessageW(h,WM_TIMER,508,0);UpdateWindow(h);
        try {
            if(id==504) {
                s->checked=s->available=false;s->operations.reset();s->phase=sitfirmware::Phase::Idle;
                SetDlgItemTextW(h,501,L"Identifying the connected logger and checking saiv.no...");SetDlgItemTextW(h,502,L"");SetDlgItemTextW(h,507,L"");
                s->device=firmwareFindDevice();s->operations.reset(new FirmwareOperations(h,s->device));
                auto current=s->operations->liveIdentity();s->device.identity=current;s->operations->device.identity=current;
                s->operations->leaveLocal();
                firmwareBackground([&]{s->manifest=sitfirmware::manifest(firmwareFetch(std::string(sitfirmware::server)+"latest.json",65536));s->notes=wide(sitfirmware::publicNotes(utf8(updateText(firmwareFetch(s->manifest.readme,131072)))));if(s->notes.empty())throw std::runtime_error("Firmware release notes are empty. Check again after publication.");});
                if(current.hardware!=s->manifest.hardware)throw std::runtime_error("Server firmware is for a different hardware revision");
                s->available=sitfirmware::newer(s->manifest.release,current.release);s->checked=true;
                // A manual check can also finish verification after an interrupted update.
                // This path performs no flash, reset or configuration deletion.
                if(sitfirmware::equal(s->manifest.release,current.release)) {
                    sitfirmware::requireIdentity(current,s->operations->configIdentity(),s->manifest.release);
                    s->operations->leaveLocal();
                }
                auto status=wide(current.product+" SN"+current.serial+" | HW "+current.hardware+" | COM"+std::to_string(s->device.port)+" | "+utf8(s->device.root)+"\r\nInstalled firmware: "+current.release+"\r\n"+(s->available?"New firmware available: ":"No newer firmware available. Server version: ")+s->manifest.release);
                if(sitfirmware::equal(s->manifest.release,current.release))status+=L"\r\nVerified: device version, system.ini and firmware cleanup.";
                SetDlgItemTextW(h,501,status.c_str());SetDlgItemTextW(h,502,s->notes.c_str());
            } else {
                sitfirmware::install(*s->operations,s->device.identity,s->manifest,s->phase);s->available=false;
                s->operations->leaveLocal();settingsKind=sitsettings::None;
                KillTimer(h,508);ShowWindow(GetDlgItem(h,508),SW_HIDE);SetDlgItemTextW(h,509,L"Firmware update completed and verified.");SetWindowTextW(h,L"SAIV IT - Firmware");
                MessageBoxW(h,(L"Firmware update successful.\r\n\r\n"+wide(s->device.identity.product+" SN"+s->device.identity.serial+" now runs "+s->manifest.release)+L"\r\nThe new config/system.ini and the COM response both match.\r\n\r\nConfiguration backup:\r\n"+s->operations->backupPath+L"\r\n\r\nRun Detect before the next instrument operation.").c_str(),L"SAIV IT - Firmware",MB_OK|MB_ICONINFORMATION);
            }
        } catch(const std::exception&e) {
            s->checked=s->available=false;
            std::wstring error=wide(e.what());
            if(s->phase>=sitfirmware::Phase::Start)error+=L"\r\n\r\nThe update is not verified. Keep USB connected. Do not start another update until the device state has been checked.";
            SetDlgItemTextW(h,501,s->phase>=sitfirmware::Phase::Start?L"Firmware update not verified.":L"Firmware check/update stopped.");SetDlgItemTextW(h,502,error.c_str());
            if(s->operations&&!s->operations->backupPath.empty())SetDlgItemTextW(h,507,(L"Configuration backup: "+s->operations->backupPath).c_str());
            if(s->phase<sitfirmware::Phase::Start&&s->operations){try{s->operations->leaveLocal();}catch(...){}}
        }
        firmwareQuiet=false;settingsBusy=false;settingsReopen=false;s->busy=false;settingsEnable();
        KillTimer(h,508);ShowWindow(GetDlgItem(h,508),SW_HIDE);ShowWindow(GetDlgItem(h,509),SW_HIDE);SetWindowTextW(h,L"SAIV IT - Firmware");
        EnableWindow(GetDlgItem(h,504),TRUE);EnableWindow(GetDlgItem(h,505),s->checked&&s->available);EnableWindow(GetDlgItem(h,506),TRUE);return 0;
    }
    return DefWindowProcW(h,msg,w,l);
}
static void firmwareShow(HWND owner) {
    if(firmwareWindow&&IsWindow(firmwareWindow)){SetForegroundWindow(firmwareWindow);return;}
    if(settingsBusy)return;
    if(updateWindow&&IsWindow(updateWindow)){SetForegroundWindow(updateWindow);MessageBoxW(updateWindow,L"Close the software update window before opening device firmware.",L"SAIV IT - Firmware",MB_OK);return;}
    WNDCLASSW wc={};wc.hInstance=instance;wc.lpfnWndProc=firmwareDialogProc;wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=HBRUSH(COLOR_BTNFACE+1);wc.lpszClassName=L"SITFirmwareUpdate";RegisterClassW(&wc);
    FirmwareDialog state;HWND h=CreateWindowExW(WS_EX_CONTROLPARENT,wc.lpszClassName,L"SAIV IT - Firmware",WS_OVERLAPPEDWINDOW,CW_USEDEFAULT,CW_USEDEFAULT,750,570,owner,0,instance,&state);if(!h)return;firmwareWindow=h;
    control(h,L"STATIC",L"Firmware updates the SAIV110 or OSU107 device connected to this PC and SIT.\r\nWould you like to check for new firmware?",0,16,14,700,76,501);
    control(h,L"EDIT",L"Choose Check firmware to identify the connected device and search saiv.no.\r\n\r\nThis is a manual check. No firmware server is contacted when SIT starts or when this window opens.\r\n\r\nYou will see the installed version, the available version and release notes before deciding whether to update.\r\n\r\nConnect the logger USB cable and select its COM port in SIT first.",ES_MULTILINE|ES_READONLY|ES_AUTOVSCROLL|WS_VSCROLL|WS_BORDER|WS_TABSTOP,16,94,700,330,502);SendDlgItemMessageW(h,502,EM_SETLIMITTEXT,262144,0);
    control(h,L"STATIC",L"Supported devices: SAIV110 / OSU107, hardware 3.1.2.",0,16,440,700,58,507);
    control(h,L"STATIC",L"",SS_OWNERDRAW,16,92,700,18,508);
    control(h,L"STATIC",L"",0,16,116,700,46,509);
    ShowWindow(GetDlgItem(h,508),SW_HIDE);ShowWindow(GetDlgItem(h,509),SW_HIDE);
    control(h,L"BUTTON",L"&Check firmware",WS_TABSTOP|BS_DEFPUSHBUTTON,16,482,155,28,504);control(h,L"BUTTON",L"&Update device",WS_TABSTOP,430,482,165,28,505);EnableWindow(GetDlgItem(h,505),FALSE);control(h,L"BUTTON",L"&Close",WS_TABSTOP,610,482,106,28,506);
    firmwareLayout(h);EnableWindow(owner,FALSE);ShowWindow(h,SW_SHOW);SetFocus(GetDlgItem(h,504));
    MSG msg;while(IsWindow(h)&&GetMessageW(&msg,0,0,0)>0){if(!IsDialogMessageW(h,&msg)){TranslateMessage(&msg);DispatchMessageW(&msg);}}
    firmwareWindow=0;EnableWindow(owner,TRUE);SetForegroundWindow(owner);
}
