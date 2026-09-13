#include "../sit_import/firmware_protocol.h"
#include <iostream>
#include <cassert>
using namespace sitfirmware;
static unsigned checks=0;
static void check(bool b){++checks;if(!b)throw std::runtime_error("Test assertion "+std::to_string(checks));}
template<class F> void rejects(F f){bool caught=false;try{f();}catch(const std::exception&){caught=true;}check(caught);}
static const std::string raw=R"({"version":"0.9.9q","hardware":"3.1.2","filename":"osu_m_update_hw3.1.2_0.9.9q.bin","readme_url":"https://saiv.no/software/firmware/osu107_saiv110/hw_3-1-2/README.txt","sha256":"3e6840e8a3ea84564b635fbcf20e6b6ece48b86551226d14bf2f259bfb30b47c"})";
static std::string changed(std::string s,const std::string&a,const std::string&b){auto p=s.find(a);assert(p!=std::string::npos);s.replace(p,a.size(),b);return s;}
struct Fake:Operations {
    std::vector<std::string> events;std::string fail;int reads=0,emptyChecks=0;bool wrongLive=false,wrongDisk=false,wrongSerial=false,needsCleanupReset=false,cleanupStuck=false;
    Identity old{"OSU107","107","3.1.2","0.9.9P"};
    void action(const std::string&s){events.push_back(s);if(fail==s)throw std::runtime_error("injected "+s);}
    void progress(Phase p)override{action("phase:"+std::to_string(int(p)));}
    Identity liveIdentity()override{++reads;action("live"+std::to_string(reads));auto id=old;if(reads>=3)id.release=wrongLive?"0.9.9P":"0.9.9Q";if(reads>=3&&wrongSerial)id.serial="999";return id;}
    void download(const Manifest&)override{action("download");}
    void backup()override{action("backup");}
    void stage()override{action("stage-flush-close-readback");}
    void start()override{action("FWU");}
    void reconnect(bool reset)override{action(reset?"reset-cycle":"firmware-cycle");}
    bool updateFolderEmpty()override{++emptyChecks;action("update-empty"+std::to_string(emptyChecks));return !cleanupStuck&&(!needsCleanupReset||emptyChecks>1);}
    void cleanConfig()override{action("delete-config");}
    void reset()override{action("RESET");}
    Identity configIdentity()override{action("new-config");auto id=old;id.release=wrongDisk?"0.9.9P":"0.9.9q";return id;}
    bool has(const std::string&s)const{return std::find(events.begin(),events.end(),s)!=events.end();}
};
int main(){try{
    auto customer=publicNotes("Release R\n\n- Cleanup improved.\n- Use FWUST\n  for internal status.\n\nUpdating\nUse Ctrl+T, CFG, SLP.\n");
    check(customer.find("Cleanup improved")!=std::string::npos);check(customer.find("FWUST")==std::string::npos);check(customer.find("internal status")==std::string::npos);check(customer.find("Ctrl+T")==std::string::npos);
    check(publicNotes("Control T opens service menu\n").empty());
    check(equal("0.9.9Q","0.9.9q"));check(newer("0.9.9q","0.9.9P"));check(!newer("0.9.9Q","0.9.9q"));
    check(newer("0.10.0","0.9.99Z"));check(newer("1.0.0","0.99.99Z"));check(newer("0.9.10","0.9.9Z"));check(newer("0.9.9A","0.9.9"));
    for(auto s:{"","0.9","0.9.9qq","0.9.9q.bin","-1.9.9","0.9.9.1","0.9.9q/","0.9.65536","999999.0.0","0.9.9 q"})rejects([&]{version(s);});
    auto m=manifest(raw);check(m.release=="0.9.9q");check(m.download==std::string(server)+m.filename);
    rejects([&]{manifest(changed(raw,"0.9.9q","0.9.9P"));});
    rejects([&]{manifest(changed(raw,"\"hardware\":\"3.1.2\"","\"hardware\":\"3.3.0\""));});
    rejects([&]{manifest(changed(raw,"osu_m_update_hw","../osu_m_update_hw"));});
    rejects([&]{manifest(changed(raw,"https://saiv.no","https://example.com"));});
    rejects([&]{manifest(changed(raw,"README.txt","../README.txt"));});
    rejects([&]{manifest(changed(raw,"README.txt","README.txt?x"));});
    rejects([&]{manifest(changed(raw,"3e6840","ze6840"));});
    rejects([&]{manifest(changed(raw,"\"version\":","\"version\":\"0.9.9q\",\"version\":"));});
    rejects([&]{manifest(raw+"garbage");});
    rejects([&]{manifest(changed(raw,"\"version\":\"0.9.9q\"","\"version\":9"));});
    check(!url(std::string(server)+"nested/a.bin",".bin"));check(!url("http://saiv.no/software/a.bin",".bin"));
    std::string config="[system]\r\niniType=OSUM\r\nserial=107\r\nhw_id=OSU-M\r\nhw_rev=3.1.2\r\nsw_id=OSU107\r\nsw_ver=0.9.9Q\r\n[surface]\r\nusbDtrInfo=never\r\n";
    auto id=ini(config);check(id.serial=="107"&&id.release=="0.9.9Q"&&id.hardware=="3.1.2");
    std::string ver="Firmware version:\n\r  SW: OSU107 ver-0.9.9Q\n\r  HW: OSU-M rev-3.1.2\n\r  Build: Sep 13 2026\n\r";
    verifyVersionResponse(ver,id);++checks;
    rejects([&]{verifyVersionResponse(changed(ver,"0.9.9Q","0.9.9P"),id);});
    rejects([&]{verifyVersionResponse(changed(ver,"3.1.2","3.3.0"),id);});
    rejects([&]{verifyVersionResponse(changed(ver,"OSU107","SAIV110"),id);});
    rejects([&]{verifyVersionResponse("Firmware version:",id);});
    check(writeLockClear("FWU write lock: CLEAR\r\n[Config]>"));
    check(!writeLockClear("FWU write lock: ACTIVE\r\nphase=CONFIRMED_CLEANUP_PENDING\r\n[Config]>"));
    rejects([&]{writeLockClear("Unknown command\r\n[Config]>");});
    rejects([&]{writeLockClear("FWU write lock: CLEAR\r\nFWU write lock: ACTIVE\r\n");});
    rejects([&]{writeLockClear("FWU write lock: CLEARING\r\n");});
    check(ini(changed(config,"sw_id=OSU107","sw_id=OSU-107")).product=="OSU107");
    check(ini(changed(config,"sw_id=OSU107","sw_id=SAIV110")).product=="SAIV110");
    check(ini("\xef\xbb\xbf"+config).serial=="107");
    requireSettingsPreserved(config,changed(config,"sw_ver=0.9.9Q","sw_ver=0.9.9R"));++checks;
    requireSettingsPreserved(config,config+"newOption=1\n");++checks;
    rejects([&]{requireSettingsPreserved(config,changed(config,"serial=107","serial=108"));});
    rejects([&]{requireSettingsPreserved(config,changed(config,"usbDtrInfo=never","usbDtrInfo=both"));});
    rejects([&]{requireSettingsPreserved(config,changed(config,"usbDtrInfo=never", ""));});
    requireSettingsPreserved("[surface]\nseparator=;\n", "[surface]\nseparator=;\n");++checks;
    rejects([&]{requireSettingsPreserved("[surface]\nseparator=;\n", "[surface]\nseparator=,\n");});
    rejects([&]{ini(config+"[system]\nserial=999\n");});rejects([&]{ini(changed(config,"serial=107","serial=107\nserial=999"));});
    rejects([&]{ini(changed(config,"sw_id=OSU107","sw_id=SD208"));});rejects([&]{ini(changed(config,"sw_ver=0.9.9Q","sw_ver=unknown"));});
    rejects([&]{ini(changed(config,"serial=107","serial="));});rejects([&]{ini(changed(config,"hw_id=OSU-M","hw_id=OTHER"));});
    std::string menu="\n\rMenu: OSU107, SN: 107, ver-0.9.9Q.\n\rHW: OSU-M rev-3.1.2.\n\r<LEDS>, <LED> to execute Leds.\n\r";
    requireIdentity(id,menuIdentity(menu),"0.9.9q");++checks;
    for(size_t n=0;n<menu.find("3.1.2")+5;++n)rejects([&]{menuIdentity(menu.substr(0,n));});
    rejects([&]{requireIdentity(id,menuIdentity(changed(menu,"SN: 107","SN: 108")),"0.9.9Q");});
    rejects([&]{requireIdentity(id,menuIdentity(changed(menu,"rev-3.1.2","rev-3.3.0")),"0.9.9Q");});
    Fake f;Phase phase=Phase::Idle;install(f,f.old,m,phase);check(phase==Phase::Complete);
    std::vector<std::string> operations;for(auto&e:f.events)if(e.find("phase:")!=0)operations.push_back(e);
    check(operations==std::vector<std::string>({"live1","download","backup","stage-flush-close-readback","live2","FWU","firmware-cycle","live3","update-empty1","delete-config","RESET","reset-cycle","new-config","live4"}));
    for(const auto&failure:operations){Fake fault;fault.fail=failure;phase=Phase::Idle;rejects([&]{install(fault,fault.old,m,phase);});check(phase!=Phase::Complete);check(fault.events.back()==failure);}
    for(auto early:{"live1","download","backup","stage-flush-close-readback","live2"}){Fake fault;fault.fail=early;phase=Phase::Idle;rejects([&]{install(fault,fault.old,m,phase);});check(!fault.has("FWU")&&!fault.has("delete-config"));}
    for(int scenario=0;scenario<3;++scenario){Fake fault;fault.wrongLive=scenario==0;fault.wrongSerial=scenario==1;fault.wrongDisk=scenario==2;phase=Phase::Idle;rejects([&]{install(fault,fault.old,m,phase);});check(phase!=Phase::Complete);if(scenario<2)check(!fault.has("delete-config")&&!fault.has("RESET"));}
    for(auto release:{"0.9.9Q","0.9.9R","1.0.0"}){Fake fault;fault.old.release=release;phase=Phase::Idle;rejects([&]{install(fault,fault.old,m,phase);});check(fault.events.empty());}
    Fake wrongHw;wrongHw.old.hardware="3.3.0";rejects([&]{install(wrongHw,wrongHw.old,m,phase);});check(wrongHw.events.empty());
    ReturnCycle cycle;check(!cycle.observe(1,1));check(!cycle.observe(0,1));check(!cycle.observe(1,1));check(!cycle.observe(1,0));check(cycle.observe(1,1));
    ReturnCycle simultaneous;check(!simultaneous.observe(0,0));check(!simultaneous.observe(2,1));check(!simultaneous.observe(1,2));check(simultaneous.observe(1,1));
    Fake cleanup;cleanup.needsCleanupReset=true;install(cleanup,cleanup.old,m,phase);check(phase==Phase::Complete);check(cleanup.emptyChecks==2);check(std::count(cleanup.events.begin(),cleanup.events.end(),"RESET")==2);check(cleanup.has("live5"));
    auto deletion=std::find(cleanup.events.begin(),cleanup.events.end(),"delete-config");check(std::find(cleanup.events.begin(),deletion,"update-empty2")!=deletion);
    Fake stuck;stuck.cleanupStuck=true;rejects([&]{install(stuck,stuck.old,m,phase);});check(phase!=Phase::Complete);check(!stuck.has("delete-config"));check(std::count(stuck.events.begin(),stuck.events.end(),"RESET")==1);
    std::cout<<"{\"checks\":"<<checks<<",\"passed\":true,\"physical_device_io\":false}\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
