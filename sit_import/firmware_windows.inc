#include <setupapi.h>
#include <winioctl.h>
#include <shlobj.h>
// The preserved 32-bit MinGW SDK has the import library, but no cfgmgr32.h.
extern "C" __declspec(dllimport) ULONG WINAPI CM_Get_Device_IDW(ULONG,PWSTR,ULONG,ULONG);
extern "C" __declspec(dllimport) ULONG WINAPI CM_Get_Parent(PULONG,ULONG,ULONG);
struct FirmwareStorageNumber {DWORD DeviceType,DeviceNumber,PartitionNumber;};

// Bind disk and CDC to their common physical USB ancestor, not a drive letter or COM number.
static std::wstring firmwareUsbAncestor(ULONG dev) {
    for(unsigned depth=0;depth<16;++depth) {
        wchar_t id[1024]={};
        if(CM_Get_Device_IDW(dev,id,1024,0)!=0) break;
        std::wstring s=id; for(auto&c:s)c=std::towupper(c);
        if(s.find(L"USB\\VID_")==0&&s.find(L"&MI_")==std::wstring::npos) return s;
        ULONG parent; if(CM_Get_Parent(&parent,dev,0)!=0) break; dev=parent;
    }
    return L"";
}
struct FirmwareDevSet {
    HDEVINFO h;
    explicit FirmwareDevSet(const GUID*guid,DWORD flags):h(SetupDiGetClassDevsW(guid,0,0,flags)) {}
    ~FirmwareDevSet(){if(h!=INVALID_HANDLE_VALUE)SetupDiDestroyDeviceInfoList(h);}
};
static std::map<unsigned,std::wstring> firmwarePorts() {
    static const GUID ports={0x4d36e978,0xe325,0x11ce,{0xbf,0xc1,0x08,0x00,0x2b,0xe1,0x03,0x18}};
    FirmwareDevSet set(&ports,DIGCF_PRESENT); std::map<unsigned,std::wstring> out;
    if(set.h==INVALID_HANDLE_VALUE)return out;
    for(DWORD i=0;;++i) {
        SP_DEVINFO_DATA dev={sizeof(dev)};if(!SetupDiEnumDeviceInfo(set.h,i,&dev))break;
        HKEY key=SetupDiOpenDevRegKey(set.h,&dev,DICS_FLAG_GLOBAL,0,DIREG_DEV,KEY_READ);
        if(key==INVALID_HANDLE_VALUE)continue;
        wchar_t port[100]={};DWORD bytes=sizeof(port),type=0;
        LONG rc=RegQueryValueExW(key,L"PortName",0,&type,reinterpret_cast<BYTE*>(port),&bytes);RegCloseKey(key);
        if(rc!=ERROR_SUCCESS||type!=REG_SZ||bytes>=sizeof(port))continue;
        std::wstring p=port;if(p.compare(0,3,L"COM")||p.size()<4||p.find_first_not_of(L"0123456789",3)!=std::wstring::npos)continue;
        unsigned n=wcstoul(port+3,0,10);auto usb=firmwareUsbAncestor(dev.DevInst);
        if(n&&n<256&&!usb.empty())out[n]=usb;
    }
    return out;
}
static std::map<DWORD,std::wstring> firmwareDisks() {
    static const GUID disks={0x53f56307,0xb6bf,0x11d0,{0x94,0xf2,0x00,0xa0,0xc9,0x1e,0xfb,0x8b}};
    FirmwareDevSet set(&disks,DIGCF_PRESENT|DIGCF_DEVICEINTERFACE);std::map<DWORD,std::wstring> out;
    if(set.h==INVALID_HANDLE_VALUE)return out;
    for(DWORD i=0;;++i) {
        SP_DEVICE_INTERFACE_DATA face={sizeof(face)};if(!SetupDiEnumDeviceInterfaces(set.h,0,&disks,i,&face))break;
        DWORD need=0;SetupDiGetDeviceInterfaceDetailW(set.h,&face,0,0,&need,0);if(!need||need>65536)continue;
        std::vector<BYTE> buf(need);auto detail=reinterpret_cast<SP_DEVICE_INTERFACE_DETAIL_DATA_W*>(buf.data());detail->cbSize=sizeof(*detail);
        SP_DEVINFO_DATA dev={sizeof(dev)};if(!SetupDiGetDeviceInterfaceDetailW(set.h,&face,detail,need,0,&dev))continue;
        HANDLE h=CreateFileW(detail->DevicePath,0,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)continue;
        FirmwareStorageNumber num={};DWORD done;bool ok=DeviceIoControl(h,IOCTL_STORAGE_GET_DEVICE_NUMBER,0,0,&num,sizeof(num),&done,0)!=0;CloseHandle(h);
        auto usb=firmwareUsbAncestor(dev.DevInst);if(ok&&!usb.empty())out[num.DeviceNumber]=usb;
    }
    return out;
}
static std::vector<std::wstring> firmwareRoots(const std::wstring&usb) {
    auto disks=firmwareDisks();std::vector<std::wstring> roots;DWORD mask=GetLogicalDrives();
    for(int i=0;i<26;++i)if(mask&(1u<<i)) {
        std::wstring root=L"A:\\";root[0]=wchar_t(L'A'+i);UINT type=GetDriveTypeW(root.c_str());
        if(type!=DRIVE_REMOVABLE&&type!=DRIVE_FIXED)continue;
        auto volume=L"\\\\.\\"+root.substr(0,2);HANDLE h=CreateFileW(volume.c_str(),0,FILE_SHARE_READ|FILE_SHARE_WRITE,0,OPEN_EXISTING,0,0);
        if(h==INVALID_HANDLE_VALUE)continue;
        FirmwareStorageNumber num={};DWORD done;bool ok=DeviceIoControl(h,IOCTL_STORAGE_GET_DEVICE_NUMBER,0,0,&num,sizeof(num),&done,0)!=0;CloseHandle(h);
        auto it=disks.find(num.DeviceNumber);if(ok&&it!=disks.end()&&it->second==usb)roots.push_back(root);
    }
    return roots;
}
static bool firmwareDirectory(const std::wstring&p) {DWORD a=GetFileAttributesW(p.c_str());return a!=INVALID_FILE_ATTRIBUTES&&(a&FILE_ATTRIBUTE_DIRECTORY)&&!(a&FILE_ATTRIBUTE_REPARSE_POINT);}
static void firmwarePlain(const std::wstring&p,bool directory) {
    DWORD a=GetFileAttributesW(p.c_str());if(a==INVALID_FILE_ATTRIBUTES||(a&FILE_ATTRIBUTE_REPARSE_POINT)||bool(a&FILE_ATTRIBUTE_DIRECTORY)!=directory)
        throw std::runtime_error("Expected a regular "+std::string(directory?"folder: ":"file: ")+utf8(p));
}
static std::string firmwareRead(const std::wstring&p,size_t limit=262144) {
    firmwarePlain(p,false);WIN32_FILE_ATTRIBUTE_DATA info={};
    if(!GetFileAttributesExW(p.c_str(),GetFileExInfoStandard,&info)||info.nFileSizeHigh||info.nFileSizeLow>limit)throw std::runtime_error("Firmware file is too large: "+utf8(p));
    return readFile(p);
}
static void firmwareWriteImage(const std::wstring&folder,const std::string&bytes) {
    firmwarePlain(folder,true);if(bytes.size()<32||bytes.size()>4*1024*1024)throw std::runtime_error("Invalid firmware image size");
    const auto path=folder+L"\\osu_m_update.bin";DWORD creation=CREATE_NEW;
    if(GetFileAttributesW(path.c_str())!=INVALID_FILE_ATTRIBUTES){firmwarePlain(path,false);creation=TRUNCATE_EXISTING;}
    HANDLE file=CreateFileW(path.c_str(),GENERIC_WRITE,0,0,creation,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,0);
    if(file==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot write the firmware image on the device");
    DWORD written=0;bool ok=WriteFile(file,bytes.data(),DWORD(bytes.size()),&written,0)&&written==bytes.size()&&FlushFileBuffers(file);CloseHandle(file);
    if(!ok)throw std::runtime_error("Firmware copy or flush failed. Firmware update was not started.");
    if(firmwareRead(path,4*1024*1024)!=bytes)throw std::runtime_error("Firmware copy verification failed. Firmware update was not started.");
}
static std::string firmwareFetch(const std::string&url,size_t limit) {
    if(!sitfirmware::url(url,".json")&&!sitfirmware::url(url,".txt")&&!sitfirmware::url(url,".bin"))throw std::runtime_error("Invalid firmware URL");
    UpdateHttp session(InternetOpenW(L"SAIV-IT-Firmware/1.4.12",INTERNET_OPEN_TYPE_PRECONFIG,0,0,0));
    DWORD timeout=8000;for(DWORD option:{INTERNET_OPTION_CONNECT_TIMEOUT,INTERNET_OPTION_SEND_TIMEOUT,INTERNET_OPTION_RECEIVE_TIMEOUT})InternetSetOptionW(session,option,&timeout,sizeof(timeout));
    auto link=wide(url);UpdateHttp request(InternetOpenUrlW(session,link.c_str(),L"Cache-Control: no-cache\r\n",DWORD(-1),INTERNET_FLAG_SECURE|INTERNET_FLAG_RELOAD|INTERNET_FLAG_NO_CACHE_WRITE|INTERNET_FLAG_NO_AUTO_REDIRECT|INTERNET_FLAG_NO_UI|INTERNET_FLAG_NO_COOKIES,0));
    DWORD status=0,size=sizeof(status);if(!HttpQueryInfoW(request,HTTP_QUERY_STATUS_CODE|HTTP_QUERY_FLAG_NUMBER,&status,&size,0)||status!=200)
        throw std::runtime_error("Firmware server returned HTTP "+std::to_string(status)+". The latest.json / README may not be published yet.");
    std::string out;DWORD start=GetTickCount();char block[16384];
    for(;;) {DWORD count=0;if(GetTickCount()-start>120000)throw std::runtime_error("Firmware download timed out");if(!InternetReadFile(request,block,sizeof(block),&count))throw std::runtime_error("Firmware download was interrupted");if(!count)break;if(out.size()+count>limit)throw std::runtime_error("Firmware server file is too large");out.append(block,count);}
    return out;
}
// Network work runs off the UI thread. The owning modal dialog cannot close during a job.
template<class F> static void firmwareBackground(F fn) {
    struct Job {F fn;std::exception_ptr failure;explicit Job(F f):fn(f){} static DWORD WINAPI run(void*p){auto&j=*static_cast<Job*>(p);try{j.fn();}catch(...){j.failure=std::current_exception();}return 0;}} job(fn);
    HANDLE thread=CreateThread(0,0,Job::run,&job,0,0);if(!thread)throw std::runtime_error("Cannot start firmware worker");
    // Never leave a worker holding references to a destroyed dialog or stack.
    while(WaitForSingleObject(thread,0)==WAIT_TIMEOUT) {try{settingsPause(20);}catch(...){WaitForSingleObject(thread,INFINITE);CloseHandle(thread);throw;}}
    CloseHandle(thread);if(job.failure)std::rethrow_exception(job.failure);
}
struct FirmwareLink:SettingsLink {
    std::string wait(std::function<bool(const std::string&)>pred,unsigned quiet=250,unsigned timeout=12000) override {
        try{return SettingsLink::wait(pred,quiet,timeout);}
        catch(const std::exception&){throw std::runtime_error("The device did not complete the requested operation. Keep USB connected and check the device before retrying.");}
    }
    void send(const std::string&s) override {
        auto comm=settingsComm();if(!comm||!*reinterpret_cast<unsigned char*>(comm+0x24))throw std::runtime_error("Firmware COM port is closed");
        settingsRx.clear();settingsRxAt=GetTickCount();uintptr_t str=0;nativeAssign(uintptr_t(&str),s);nc(0x7ffc4,comm,str);nc(0x3f98,uintptr_t(&str));
    }
    std::string localMenu() {
        sitsettings::request(*this,std::string(1,'\x14')+"\r",[](const std::string&s){return sitsettings::has(s,"DEACTIVATED")&&sitsettings::has(s,"to reactivate.");},300);
        return sitsettings::request(*this,"M\r",[](const std::string&s){return sitsettings::has(s,"Menu: ")&&sitsettings::has(s,"HW: ")&&sitsettings::has(s,"> to execute Leds.");},300);
    }
};
struct FirmwareDevice {
    std::wstring usb,root;unsigned port=0;sitfirmware::Identity identity;
};
static FirmwareDevice firmwareFindDevice() {
    auto comm=settingsComm();if(!comm||!*reinterpret_cast<unsigned char*>(comm+0x24))throw std::runtime_error("Connect the logger in SIT first, then check again.");
    unsigned port=*reinterpret_cast<unsigned char*>(comm+0x34);auto ports=firmwarePorts();auto it=ports.find(port);
    if(it==ports.end())throw std::runtime_error("The active COM port cannot be identified as a USB logger");
    FirmwareDevice d;d.port=port;d.usb=it->second;unsigned found=0;
    for(const auto&root:firmwareRoots(d.usb)) {
        if(!firmwareDirectory(root+L"config")||(!firmwareDirectory(root+L"instrument")&&!firmwareDirectory(root+L"surface")))continue;
        auto id=sitfirmware::ini(firmwareRead(root+L"config\\system.ini"));
        d.root=root;d.identity=id;++found;
    }
    if(found!=1)throw std::runtime_error("Could not identify exactly one logger disk with config and instrument/surface folders on the active USB connection");
    sitfirmware::serverForHardware(d.identity.hardware); // Reject unknown hardware before network access.
    return d;
}
// A bounded recursive snapshot; no links, junctions, wildcards or paths outside config are followed.
static void firmwareSnapshot(const std::wstring&folder,const std::wstring&relative,std::map<std::wstring,std::string>&files,unsigned depth=0) {
    if(depth>8||files.size()>512)throw std::runtime_error("Unexpected config folder structure");firmwarePlain(folder,true);
    WIN32_FIND_DATAW item={};HANDLE find=FindFirstFileW((folder+L"\\*").c_str(),&item);
    if(find==INVALID_HANDLE_VALUE){if(GetLastError()==ERROR_FILE_NOT_FOUND)return;throw std::runtime_error("Cannot read config folder");}
    try {do {
        std::wstring name=item.cFileName;if(name==L"."||name==L"..")continue;
        if(item.dwFileAttributes&FILE_ATTRIBUTE_REPARSE_POINT)throw std::runtime_error("Config contains a link or junction");
        if(item.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)firmwareSnapshot(folder+L"\\"+name,relative+name+L"\\",files,depth+1);
        else {if(files.size()>=512)throw std::runtime_error("Config contains too many files");files[relative+name]=firmwareRead(folder+L"\\"+name,4*1024*1024);size_t total=0;for(const auto&f:files)total+=f.second.size();if(total>32*1024*1024)throw std::runtime_error("Config backup exceeds 32 MB");}
    }while(FindNextFileW(find,&item));if(GetLastError()!=ERROR_NO_MORE_FILES)throw std::runtime_error("Config enumeration failed");}
    catch(...){FindClose(find);throw;}FindClose(find);
}
// Only system.ini is regenerated. Calibration and all other config files stay in place.
static void firmwareDeleteSystemIni(const std::wstring&folder) {
    firmwarePlain(folder,true);
    const auto path=folder+L"\\system.ini";
    firmwarePlain(path,false);
    if(!DeleteFileW(path.c_str()))throw std::runtime_error("Could not remove config/system.ini for regeneration");
}
