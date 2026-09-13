// Windows file/USB-discovery layer tests. Native serial calls are hard-disabled in this host.
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
#include <windows.h>
#include <wininet.h>
#include <cwctype>
#include <vector>
#include <map>
#include <stdexcept>
#include <exception>
#include <functional>
#include <iostream>
#include "../sit_import/firmware_protocol.h"
static std::wstring wide(const std::string&s){return std::wstring(s.begin(),s.end());}
static std::string utf8(const std::wstring&s){return std::string(s.begin(),s.end());}
static std::string readFile(const std::wstring&p){HANDLE h=CreateFileW(p.c_str(),GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)throw std::runtime_error("read failed");DWORD len=GetFileSize(h,0),n=0;std::string s(len,' ');bool ok=ReadFile(h,&s[0],len,&n,0)&&n==len;CloseHandle(h);if(!ok)throw std::runtime_error("read incomplete");return s;}
static void settingsPause(unsigned ms){Sleep(ms);}
static uintptr_t settingsComm(){return 0;}
static std::string settingsRx;static DWORD settingsRxAt;
static void nativeAssign(uintptr_t,const std::string&){throw std::runtime_error("Native serial calls disabled in this test");}
static void nc(uintptr_t,uintptr_t,uintptr_t=0){throw std::runtime_error("Native serial calls disabled in this test");}
namespace sitsettings {
inline bool has(const std::string&s,const std::string&t){return sitfirmware::lower(s).find(sitfirmware::lower(t))!=std::string::npos;}
template<class T,class F> std::string request(T&l,const std::string&s,F f,unsigned q){l.send(s);return l.wait(f,q,12000);}
}
struct SettingsLink {
 virtual ~SettingsLink(){};
 virtual void send(const std::string&){throw std::runtime_error("Native serial calls disabled in this test");}
 virtual std::string wait(std::function<bool(const std::string&)>,unsigned,unsigned){throw std::runtime_error("Native serial calls disabled in this test");}
};
struct UpdateHttp {HINTERNET h;explicit UpdateHttp(HINTERNET v):h(v){if(!h)throw std::runtime_error("HTTP failed");}~UpdateHttp(){InternetCloseHandle(h);}operator HINTERNET()const{return h;}};
#include "../sit_import/firmware_windows.inc"
static unsigned checks=0;
void check(bool b){++checks;if(!b)throw std::runtime_error("Check "+std::to_string(checks)+" failed");}
template<class F>void rejects(F f){bool caught=false;try{f();}catch(const std::exception&){caught=true;}check(caught);}
void write(const std::wstring&p,const std::string&s){HANDLE h=CreateFileW(p.c_str(),GENERIC_WRITE,0,0,CREATE_NEW,0,0);check(h!=INVALID_HANDLE_VALUE);DWORD n;bool ok=WriteFile(h,s.data(),DWORD(s.size()),&n,0)&&n==s.size()&&FlushFileBuffers(h);CloseHandle(h);check(ok);}
int main(){try{
 wchar_t cwd[32768];check(GetCurrentDirectoryW(32768,cwd)>0);std::wstring root=cwd;
 // No recursive delete unless the final absolute target is this unique test folder in the workspace.
 check(root.find(L"sd200w_r2")!=std::wstring::npos);
 root+=L"\\analysis\\runtime_test\\firmware1411\\files-"+wide(std::to_string(GetCurrentProcessId()));
 check(SHCreateDirectoryExW(0,root.c_str(),0)==ERROR_SUCCESS);
 check(CreateDirectoryW((root+L"\\config").c_str(),0));check(CreateDirectoryW((root+L"\\config\\nested").c_str(),0));
 write(root+L"\\keep.txt","outside config survives");write(root+L"\\config\\system.ini","test identity");write(root+L"\\config\\nested\\calibration.ini",std::string("a\0b",3));
 std::map<std::wstring,std::string> files;firmwareSnapshot(root+L"\\config",L"",files);check(files.size()==2);check(files[L"nested\\calibration.ini"]==std::string("a\0b",3));
 rejects([&]{firmwareRead(root+L"\\config\\system.ini",2);});rejects([&]{firmwarePlain(root+L"\\config",false);});rejects([&]{firmwarePlain(root+L"\\config\\system.ini",true);});
 firmwareDeleteSystemIni(root+L"\\config");check(firmwareDirectory(root+L"\\config"));check(GetFileAttributesW((root+L"\\config\\system.ini").c_str())==INVALID_FILE_ATTRIBUTES);check(firmwareRead(root+L"\\config\\nested\\calibration.ini")==std::string("a\0b",3));check(firmwareRead(root+L"\\keep.txt")=="outside config survives");
 rejects([&]{firmwareFindDevice();});FirmwareLink link;rejects([&]{link.send("FWU\r");});
 rejects([&]{firmwareFetch("https://example.com/payload.bin",1024);});
 bool done=false;firmwareBackground([&]{done=true;});check(done);rejects([&]{firmwareBackground([]{throw std::runtime_error("worker failure");});});
 // Read-only PnP enumeration; no COM handle is opened and no logger files are read.
 auto ports=firmwarePorts();auto disks=firmwareDisks();
 for(const auto&p:ports)check(p.first>0&&p.first<256&&p.second.find(L"USB\\VID_")==0&&p.second.find(L"&MI_")==std::wstring::npos);
 for(const auto&d:disks)check(d.second.find(L"USB\\VID_")==0);
 check(firmwareRoots(L"USB\\VID_FFFF&PID_FFFF\\SIT-NONEXISTENT-TEST").empty());
 check(CreateDirectoryW((root+L"\\update").c_str(),0));
 firmwareWriteImage(root+L"\\update",std::string(2048,'P'));check(firmwareRead(root+L"\\update\\osu_m_update.bin")==std::string(2048,'P'));
 firmwareWriteImage(root+L"\\update",std::string(32,'Q'));check(firmwareRead(root+L"\\update\\osu_m_update.bin")==std::string(32,'Q'));
 rejects([&]{firmwareWriteImage(root+L"\\update","");});
 std::cout<<"{\"checks\":"<<checks<<",\"passed\":true,\"serial_calls_disabled\":true,\"usb_port_count\":"<<ports.size()<<",\"usb_disk_count\":"<<disks.size()<<"}\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
