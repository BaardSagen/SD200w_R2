#include "serial.hpp"
#include <windows.h>
#include <setupapi.h>
#include <devguid.h>
#include <algorithm>
#include <chrono>
#include <future>
#include <stdexcept>
namespace saiv {
std::string windowsError(unsigned code){char* p=nullptr;FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER|FORMAT_MESSAGE_FROM_SYSTEM|FORMAT_MESSAGE_IGNORE_INSERTS,nullptr,code,0,reinterpret_cast<char*>(&p),0,nullptr);std::string s=p?p:"Windows error "+std::to_string(code);if(p)LocalFree(p);return trim(s);}
std::vector<PortInfo> enumeratePorts(){
 std::vector<PortInfo> out;HDEVINFO info=SetupDiGetClassDevsA(&GUID_DEVCLASS_PORTS,nullptr,nullptr,DIGCF_PRESENT);
 if(info!=INVALID_HANDLE_VALUE){SP_DEVINFO_DATA item{};item.cbSize=sizeof(item);for(DWORD i=0;SetupDiEnumDeviceInfo(info,i,&item);i++){
  char description[512]{};SetupDiGetDeviceRegistryPropertyA(info,&item,SPDRP_FRIENDLYNAME,nullptr,reinterpret_cast<PBYTE>(description),sizeof(description),nullptr);
  HKEY key=SetupDiOpenDevRegKey(info,&item,DICS_FLAG_GLOBAL,0,DIREG_DEV,KEY_READ);if(key!=INVALID_HANDLE_VALUE){char name[256]{};DWORD size=sizeof(name),type=0;if(RegQueryValueExA(key,"PortName",nullptr,&type,reinterpret_cast<BYTE*>(name),&size)==ERROR_SUCCESS&&std::string(name).rfind("COM",0)==0)out.push_back({name,description});RegCloseKey(key);}
 }SetupDiDestroyDeviceInfoList(info);}
 for(int i=1;i<=256;i++){std::string name="COM"+std::to_string(i);char target[1024]{};if(QueryDosDeviceA(name.c_str(),target,sizeof(target))&&std::none_of(out.begin(),out.end(),[&](auto& p){return p.name==name;}))out.push_back({name,"Serial port"});}
 std::sort(out.begin(),out.end(),[](auto& a,auto& b){return std::atoi(a.name.c_str()+3)<std::atoi(b.name.c_str()+3);});return out;
}
static HANDLE openPort(const SerialSettings& s){
 HANDLE h=CreateFileA(("\\\\.\\"+s.port).c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,0,nullptr);
 if(h==INVALID_HANDLE_VALUE)return h;
 DCB dcb{};dcb.DCBlength=sizeof(dcb);
 if(!GetCommState(h,&dcb)){DWORD e=GetLastError();CloseHandle(h);SetLastError(e);return INVALID_HANDLE_VALUE;}
 dcb.BaudRate=s.baud;dcb.ByteSize=static_cast<BYTE>(s.bits);dcb.Parity=s.parity==1?EVENPARITY:s.parity==2?ODDPARITY:NOPARITY;dcb.StopBits=ONESTOPBIT;
 if(s.parity==1&&s.bits==7){dcb.ByteSize=8;dcb.Parity=NOPARITY;}
 dcb.fBinary=TRUE;dcb.fParity=dcb.Parity!=NOPARITY;dcb.fOutxCtsFlow=FALSE;dcb.fOutxDsrFlow=FALSE;dcb.fDsrSensitivity=FALSE;dcb.fOutX=FALSE;dcb.fInX=FALSE;dcb.fErrorChar=FALSE;dcb.fNull=FALSE;dcb.fAbortOnError=FALSE;
 dcb.fDtrControl=s.dtr?DTR_CONTROL_ENABLE:DTR_CONTROL_DISABLE;dcb.fRtsControl=s.rts?RTS_CONTROL_ENABLE:RTS_CONTROL_DISABLE;
 COMMTIMEOUTS timeouts{MAXDWORD,0,25,0,250};
 if(!SetCommTimeouts(h,&timeouts)||!SetCommState(h,&dcb)){DWORD e=GetLastError();CloseHandle(h);SetLastError(e);return INVALID_HANDLE_VALUE;}
 return h;
}
void Serial::event(SerialEvent::Kind kind,const std::string& text){std::lock_guard<std::mutex> l(mutex_);if(queuedBytes_+text.size()>8*1024*1024){stop_=true;events_.push_back({SerialEvent::Error,"Receive queue full; connection stopped to prevent silent data loss."});return;}events_.push_back({kind,text});queuedBytes_+=text.size();}
void Serial::connect(const SerialSettings& settings){disconnect();{std::lock_guard<std::mutex> l(mutex_);outgoing_.clear();events_.clear();queuedBytes_=0;}stop_=false;worker_=std::thread(&Serial::run,this,settings);}
void Serial::disconnect(){stop_=true;if(worker_.joinable())worker_.join();connected=false;}
void Serial::write(const std::string& data){if(!connected)return;std::lock_guard<std::mutex> l(mutex_);if(outgoing_.size()<128)outgoing_.push_back(data);else {events_.push_back({SerialEvent::Error,"Transmit queue full; command not sent."});}}
std::vector<SerialEvent> Serial::poll(){std::lock_guard<std::mutex> l(mutex_);std::vector<SerialEvent> result(events_.begin(),events_.end());events_.clear();queuedBytes_=0;return result;}
void Serial::run(SerialSettings settings){
 HANDLE h=openPort(settings);if(h==INVALID_HANDLE_VALUE){event(SerialEvent::Error,settings.port+": "+windowsError(GetLastError()));event(SerialEvent::Closed,"");return;}
 connected=true;event(SerialEvent::Connected,settings.port);
 while(!stop_){
  std::string pending;{std::lock_guard<std::mutex> l(mutex_);if(!outgoing_.empty()){pending=std::move(outgoing_.front());outgoing_.pop_front();}}
  if(!pending.empty()){std::string wire=settings.parity==1&&settings.bits==7?encode7E1(pending):pending;size_t total=0;while(total<pending.size()&&!stop_){DWORD done=0;if(!WriteFile(h,wire.data()+total,static_cast<DWORD>(pending.size()-total),&done,nullptr)||done==0){event(SerialEvent::Error,"Serial write failed: "+windowsError(GetLastError()));stop_=true;break;}total+=done;}if(total)event(SerialEvent::Transmitted,pending.substr(0,total));}
  char data[4096];DWORD count=0;if(!ReadFile(h,data,sizeof(data),&count,nullptr)){event(SerialEvent::Error,"Serial read failed: "+windowsError(GetLastError()));break;}if(count){auto payload=std::string(data,count);if(settings.parity==1&&settings.bits==7)payload=decode7E1(std::move(payload));event(SerialEvent::Received,payload);}
 }
 CloseHandle(h);connected=false;event(SerialEvent::Closed,settings.port);
}
void Detector::start(){if(busy)return;if(worker_.joinable())worker_.join();stop_=false;busy=true;{std::lock_guard<std::mutex> l(mutex_);results_.clear();}
 worker_=std::thread([this]{auto ports=enumeratePorts();std::vector<std::future<Detection>> pending;size_t index=0;
 while((index<ports.size()||!pending.empty())&&!stop_){while(index<ports.size()&&pending.size()<4){auto p=ports[index++];pending.push_back(std::async(std::launch::async,[this,p]{Detection d;d.port=p;SerialSettings settings;settings.port=p.name;for(int parity=0;parity<2&&!stop_;parity++){settings.parity=parity;settings.bits=parity?7:8;d.settings=settings;HANDLE h=openPort(settings);if(h==INVALID_HANDLE_VALUE){d.status=windowsError(GetLastError());return d;}auto start=std::chrono::steady_clock::now();Protocol protocol;protocol.connected();protocol.wake(0);bool failed=false;size_t sent=0;
 protocol.send=[&](const std::string& command){auto wire=settings.parity==1?encode7E1(command):command;DWORD count=0;if(!WriteFile(h,wire.data(),static_cast<DWORD>(command.size()),&count,nullptr)||count!=command.size())failed=true;else sent++;};
 while(!stop_&&!failed){double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();if(seconds>15)break;
 char b[1024];DWORD n=0;if(!ReadFile(h,b,sizeof(b),&n,nullptr)){failed=true;break;}
 seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();if(n){if(!settings.parity&&std::any_of(b,b+n,[](unsigned char c){return c>=128;}))break;auto payload=std::string(b,n);if(settings.parity==1)payload=decode7E1(std::move(payload));protocol.ingest(payload,seconds);}
 if(protocol.device.logger){d.identity=protocol.device;break;}
 protocol.tick(seconds);
 if(protocol.mainMenu||protocol.running){d.identity=protocol.device;if(d.identity.model.empty())d.identity.model="SAIV CTD / STD";break;}
 if(protocol.operation==Protocol::Operation::Idle)break;
 }
 CloseHandle(h);d.status=stop_?"Search cancelled":failed?"Serial I/O failed":d.identity.model.empty()?"No complete supported identity or menu at 9600 (8N1 / 7E1)":sent?"Identified using menu-aware probe":"Identified without sending commands";if(!d.identity.model.empty()||failed)break;}return d;}));}
 for(auto it=pending.begin();it!=pending.end();){if(it->wait_for(std::chrono::milliseconds(20))==std::future_status::ready){auto d=it->get();{std::lock_guard<std::mutex> l(mutex_);results_.push_back(std::move(d));}it=pending.erase(it);}else ++it;}
 }pending.clear();busy=false;});
}
std::vector<Detection> Detector::results(){std::lock_guard<std::mutex> l(mutex_);return results_;}
}
