#include "device_settings.hpp"
#include "sit_compat.hpp"
#include "sit/settings_protocol.h"
#include <windows.h>
namespace saiv {
struct DeviceLink: sitsettings::Link {
 Serial& port; SerialSettings settings; Identity identity; std::string rx,all; ULONGLONG last=0;
 DeviceLink(Serial&p,SerialSettings s,Identity id):port(p),settings(s),identity(id){}
 void collect(){for(auto&e:port.poll()){if(e.kind==SerialEvent::Received){rx+=e.text;all+=e.text;last=GetTickCount64();if(rx.size()>131072)throw std::runtime_error("Instrument response is too large");}if(e.kind==SerialEvent::Error)throw std::runtime_error(e.text);}}
 void send(const std::string&s)override{collect();if(!port.connected)throw std::runtime_error("Connection lost. Run Autodetect again.");rx.clear();last=GetTickCount64();port.write(s);}
 void pause(unsigned ms)override{auto start=GetTickCount64();while(GetTickCount64()-start<ms){Sleep(10);collect();}}
 std::string wait(std::function<bool(const std::string&)>pred,unsigned quiet=250,unsigned timeout=12000)override{auto start=GetTickCount64();while(GetTickCount64()-start<timeout){pause(10);if(sitsettings::deviceError(rx))throw std::runtime_error("Device rejected the operation:\n"+rx);if(pred(rx)&&GetTickCount64()-last>=quiet)return rx;}throw sitsettings::Timeout(rx);}
 std::string freshStatus()override{port.disconnect();port.poll();Sleep(750);rx.clear();last=GetTickCount64();port.connect(settings);auto s=wait([](const std::string&s){return (sitsettings::has(s,"osu107")||sitsettings::has(s,"saiv110"))&&(sitsettings::has(s,"Hold")||sitsettings::has(s,"Type")||sitsettings::has(s,"Surface-logger:"));},350,10000);auto id=identify(s);if(id.serial!=identity.serial||id.surface!=identity.surface||id.logger!=identity.logger)throw std::runtime_error("Instrument identity changed. Run Autodetect again.");return s;}
 sitsettings::Clock now(bool utc,int ahead=0)override{SYSTEMTIME t;if(utc)GetSystemTime(&t);else GetLocalTime(&t);FILETIME f;SystemTimeToFileTime(&t,&f);ULARGE_INTEGER v;v.LowPart=f.dwLowDateTime;v.HighPart=f.dwHighDateTime;v.QuadPart+=ULONGLONG(ahead)*10000000;f.dwLowDateTime=v.LowPart;f.dwHighDateTime=v.HighPart;FileTimeToSystemTime(&f,&t);if(t.wYear<2000||t.wYear>2099)throw std::runtime_error("Instrument clocks require a PC year from 2000 through 2099");char date[20],time[20],wire[30];sprintf_s(date,"%04u-%02u-%02u",t.wYear,t.wMonth,t.wDay);sprintf_s(time,"%02u:%02u:%02u",t.wHour,t.wMinute,t.wSecond);sprintf_s(wire,"%02u-%02u-%02u-%02u-%02u-%02u",t.wYear%100,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond);return {wire,date,time,sitnative::timestamp(date,time)};}
 double timestamp(const std::string&date,const std::string&time)override{return sitnative::timestamp(date,time);}
};
SettingResult changeDeviceSetting(Serial&port,SerialSettings settings,Identity identity,const std::string&context,bool clock,int interval,bool utc,const std::filesystem::path& config){
 DeviceLink l(port,settings,identity);SettingResult result;
 try{auto kind=identity.surface?sitsettings::Surface:identity.logger?sitsettings::OSU:sitsettings::SD200;
  if(clock){if(kind==sitsettings::Surface)sitsettings::stopSurface(l);else {sitsettings::sdClock(l,utc,kind==sitsettings::OSU?l.freshStatus():context);result.message="SD200 clock verified. ";}if(kind!=sitsettings::SD200){sitsettings::loggerClock(l,kind,utc);result.message+="Logger clock verified. ";}result.message+=utc?"UTC.":"PC local time.";}
  else if(kind!=sitsettings::Surface){sitsettings::setInterval(l,interval,kind==sitsettings::OSU?l.freshStatus():context);result.message="Measuring interval verified.";}
  else {if(interval<0||interval>=11||lower(config.filename().u8string())!="system.ini")throw std::runtime_error("Select config/system.ini on the connected logger disk");sitsettings::stopSurface(l);
   sitsettings::request(l,"F",[](const std::string&s){return sitsettings::has(s,"Refresh disk")&&sitsettings::yn(s);},350);
   sitsettings::request(l,"Y",[](const std::string&s){return sitsettings::has(s,"System disk refresh will start in 3 seconds.");},100,8000);
   l.pause(4500);if(!sitsettings::stopped(l.freshStatus()))throw std::runtime_error("Surface did not return stopped after disk refresh");
   auto original=readDatasetBytes(config),modified=sitsettings::replaceSurfaceInterval(original,sitsettings::intervals[interval].seconds);auto backup=config;backup+=L".studio-backup-"+std::to_wstring(GetTickCount64());writeNewFile(backup,original);
   try{HANDLE f=CreateFileW(config.c_str(),GENERIC_WRITE,0,nullptr,TRUNCATE_EXISTING,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,nullptr);if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot write system.ini");DWORD n=0;bool ok=WriteFile(f,modified.data(),DWORD(modified.size()),&n,nullptr)&&n==modified.size()&&FlushFileBuffers(f);CloseHandle(f);if(!ok||readDatasetBytes(config)!=modified)throw std::runtime_error("Configuration write/readback failed");l.pause(10000);sitsettings::request(l,"U",[](const std::string&s){return sitsettings::has(s,"OK SAIV110_UPDATE_CONFIG");},300,60000);if(readDatasetBytes(config)!=modified||!sitsettings::stopped(l.freshStatus()))throw std::runtime_error("Could not verify configuration and stopped state");result.message="Surface interval applied and disk value verified. Logger remains stopped. Backup: "+backup.u8string();}
   catch(const std::exception&e){throw std::runtime_error(std::string(e.what())+"\nOriginal configuration saved at: "+backup.u8string());}
  }
 }catch(const std::exception&e){result.error=result.message+e.what();}result.received=l.all;return result;
}
}
