#ifndef SIT_FIRMWARE_PROTOCOL_H
#define SIT_FIRMWARE_PROTOCOL_H
#include "update_protocol.h"
#include <regex>
#include <array>
#include <sstream>
#include <functional>

namespace sitfirmware {
inline bool supportedHardware(const std::string&hardware) {
    return hardware=="3.1.2"||hardware=="3.3.0";
}
inline std::string serverForHardware(const std::string&hardware) {
    if(hardware=="3.1.2")return "https://saiv.no/software/firmware/osu107_saiv110/hw_3-1-2/";
    if(hardware=="3.3.0")return "https://saiv.no/software/firmware/osu107_saiv110/hw_3-3-0/";
    throw std::runtime_error("Unsupported logger hardware revision. Supported revisions: 3.1.2 and 3.3.0.");
}
inline std::string lower(std::string s) { for (auto& c:s) c=char(std::tolower((unsigned char)c)); return s; }
inline std::string trim(const std::string& s) {
    auto a=s.find_first_not_of(" \t\r\n"), b=s.find_last_not_of(" \t\r\n");
    return a==std::string::npos ? "" : s.substr(a,b-a+1);
}
// Firmware uses alphabetic revisions (P, Q, ...); SIT's numeric comparator cannot be used.
inline std::array<unsigned,4> version(const std::string& s) {
    std::smatch m;
    if (!std::regex_match(s,m,std::regex("([0-9]{1,5})\\.([0-9]{1,5})\\.([0-9]{1,5})([A-Za-z]?)")))
        throw std::runtime_error("Unrecognized firmware version: "+s);
    std::array<unsigned,4> v={{0,0,0,0}};
    for (int i=0;i<3;++i) { v[i]=std::stoul(m[i+1]); if(v[i]>65535) throw std::runtime_error("Invalid firmware version"); }
    if(!m[4].str().empty()) v[3]=std::tolower((unsigned char)m[4].str()[0])-'a'+1;
    return v;
}
inline bool newer(const std::string&a,const std::string&b) { return version(a)>version(b); }
inline bool equal(const std::string&a,const std::string&b) { return version(a)==version(b); }
inline bool url(const std::string&s,const std::string&ext,const std::string&hardware) {
    const auto server=serverForHardware(hardware);
    return s.compare(0,server.size(),server)==0 && situpdate::url(s,ext)
        && s.substr(server.size()).find('/')==std::string::npos;
}
inline bool url(const std::string&s,const std::string&ext) {
    return url(s,ext,"3.1.2")||url(s,ext,"3.3.0");
}
struct Manifest { std::string release,hardware,filename,download,readme,sha256; };
inline Manifest manifest(const std::string& raw,const std::string&hardware) {
    const auto server=serverForHardware(hardware);
    if(raw.empty()||raw.size()>65536) throw std::runtime_error("Invalid firmware latest.json size");
    auto m=situpdate::Json(raw).object();
    Manifest r{m["version"],m["hardware"],m["filename"],"",m["readme_url"],lower(m["sha256"])};
    if(r.hardware!=hardware)throw std::runtime_error("Server firmware is for a different hardware revision");
    version(r.release);
    std::smatch name;
    if(!std::regex_match(r.filename,name,std::regex("osu_m_update_hw(3\\.1\\.2|3\\.3\\.0)_([0-9]+\\.[0-9]+\\.[0-9]+[A-Za-z]?)\\.bin"))
        ||r.hardware!=name[1]||!equal(name[2],r.release))
        throw std::runtime_error("Firmware filename, version and hardware do not agree");
    r.download=std::string(server)+r.filename;
    if(!url(r.download,".bin",hardware)||!url(r.readme,".txt",hardware)) throw std::runtime_error("Invalid firmware server link");
    if(r.sha256.size()!=64||r.sha256.find_first_not_of("0123456789abcdef")!=std::string::npos)
        throw std::runtime_error("The firmware server must supply a SHA-256 checksum");
    return r;
}
struct Identity { std::string product,serial,hardware,release; };
inline Identity ini(const std::string& raw) {
    if(raw.empty()||raw.size()>262144||raw.find('\0')!=std::string::npos) throw std::runtime_error("Invalid system.ini");
    std::istringstream in(raw); std::string line,section; std::map<std::string,std::string> fields; unsigned count=0;
    while(std::getline(in,line)) {
        line=trim(line); if(line.compare(0,3,"\xef\xbb\xbf")==0) line.erase(0,3);
        if(line.empty()||line[0]==';'||line[0]=='#') continue;
        if(line[0]=='[') { auto end=line.find(']'); if(end==std::string::npos) throw std::runtime_error("Invalid INI section"); section=lower(trim(line.substr(1,end-1))); if(section=="system"&&++count>1) throw std::runtime_error("Duplicate [system] section"); continue; }
        auto sep=line.find('='); if(section!="system"||sep==std::string::npos) continue;
        auto key=lower(trim(line.substr(0,sep))),value=trim(line.substr(sep+1));
        value=trim(value.substr(0,value.find_first_of(";#")));
        if(!fields.emplace(key,value).second) throw std::runtime_error("Duplicate system.ini identity field");
    }
    Identity id{fields["sw_id"],fields["serial"],fields["hw_rev"],fields["sw_ver"]};
    if(id.product=="OSU-107") id.product="OSU107";
    if(lower(fields["initype"])!="osum"||lower(fields["hw_id"])!="osu-m" ||
        (id.product!="OSU107"&&id.product!="SAIV110")||!std::regex_match(id.serial,std::regex("[0-9]{1,10}")))
        throw std::runtime_error("system.ini does not identify a supported SAIV logger");
    version(id.release); if(!std::regex_match(id.hardware,std::regex("[0-9]+\\.[0-9]+\\.[0-9]+"))) throw std::runtime_error("Missing hardware revision");
    return id;
}
inline Identity menuIdentity(const std::string& raw) {
    std::smatch m,h;
    if(!std::regex_search(raw,m,std::regex("Menu: (OSU107|SAIV110), SN: ([0-9]+), ver-([0-9]+\\.[0-9]+\\.[0-9]+[A-Za-z]?)(?:\\.|[ \\r\\n])")) ||
       !std::regex_search(raw,h,std::regex("HW: OSU-M rev-([0-9]+\\.[0-9]+\\.[0-9]+)")))
        throw std::runtime_error("Could not read a fresh logger identity from its local menu");
    Identity id{m[1],m[2],h[1],m[3]}; version(id.release); return id;
}
inline bool sameDevice(const Identity&a,const Identity&b) {
    return a.product==b.product&&a.serial==b.serial&&a.hardware==b.hardware;
}
inline void verifyVersionResponse(const std::string&raw,const Identity&id) {
    std::smatch sw,hw;
    if(!std::regex_search(raw,sw,std::regex("SW: (OSU107|SAIV110) ver-([0-9]+\\.[0-9]+\\.[0-9]+[A-Za-z]?)(?:[ \\r\\n]|$)")) ||
       !std::regex_search(raw,hw,std::regex("HW: OSU-M rev-([0-9]+\\.[0-9]+\\.[0-9]+)(?:[ \\r\\n]|$)")) ||
       sw[1]!=id.product||lower(sw[2])!=lower(id.release)||hw[1]!=id.hardware)
        throw std::runtime_error("Fresh VER response does not match the logger identity/version");
}
inline bool writeLockClear(const std::string&raw) {
    bool clear=false,active=false;std::string line;std::istringstream in(raw);
    while(std::getline(in,line)){line=trim(line);if(line=="FWU write lock: CLEAR")clear=true;if(line=="FWU write lock: ACTIVE")active=true;}
    if(clear==active)throw std::runtime_error("Could not verify the firmware write-lock status");
    return clear;
}
// Server notes can contain service instructions. Only customer release notes are shown.
inline std::string publicNotes(const std::string&raw) {
    std::istringstream in(raw);std::string line,block,out;
    const std::regex internal("ctrl[ +_-]*t|control[ +_-]*t|service menu|servicemeny|\\b(cfg|fwust|fwuclr|fwupdate|fwu|slp|ver|usbd)\\b|\\bf[ /]+y\\b|confirmed_cleanup_pending|\\[config\\]|\\[sleep\\]",std::regex::icase);
    auto flush=[&]{if(!block.empty()&&!std::regex_search(block,internal))out+=block+"\r\n";block.clear();};
    while(std::getline(in,line)) {
        if(!line.empty()&&line.back()=='\r')line.pop_back();
        if(lower(trim(line))=="updating"){flush();break;}
        if(trim(line).empty()){flush();continue;}
        if(line.compare(0,2,"- ")==0)flush();
        block+=line+"\r\n";
    }
    flush();return out;
}
inline std::map<std::string,std::string> configurationValues(const std::string&raw) {
    std::map<std::string,std::string> values;std::string line,section;std::istringstream in(raw);
    while(std::getline(in,line)) {
        line=trim(line);if(line.compare(0,3,"\xef\xbb\xbf")==0)line.erase(0,3);
        if(line.empty()||line[0]==';'||line[0]=='#')continue;
        if(line[0]=='['){auto end=line.find(']');if(end==std::string::npos)throw std::runtime_error("Invalid config section");section=lower(trim(line.substr(1,end-1)));continue;}
        auto sep=line.find('=');if(sep==std::string::npos)continue;
        auto key=section+"."+lower(trim(line.substr(0,sep)));
        if(!values.emplace(key,trim(line.substr(sep+1))).second)throw std::runtime_error("Duplicate config setting: "+key);
    }
    return values;
}
inline void requireSettingsPreserved(const std::string&before,const std::string&after) {
    auto old=configurationValues(before),current=configurationValues(after);
    for(const auto&setting:old) {
        // Product/firmware identity is checked separately against live firmware.
        if(setting.first=="system.sw_ver"||setting.first=="system.sw_id")continue;
        auto found=current.find(setting.first);
        if(found==current.end()||found->second!=setting.second)throw std::runtime_error("A system.ini setting changed during regeneration: "+setting.first);
    }
}
inline void requireIdentity(const Identity&expected,const Identity&actual,const std::string&release) {
    if(!sameDevice(expected,actual)||!equal(actual.release,release)) throw std::runtime_error("Logger identity or firmware version does not match. Update is not verified.");
}
enum class Phase { Idle, Download, Backup, Copy, Start, WaitFirmware, VerifyFirmware, CheckUpdateFolder, WaitCleanup, CleanConfig, Reset, WaitConfig, VerifyConfig, Complete };
struct ReturnCycle {
    bool diskGone=false,portGone=false;
    bool observe(unsigned matchingDisks,unsigned matchingPorts) {
        if(!matchingDisks)diskGone=true;if(!matchingPorts)portGone=true;
        return diskGone&&portGone&&matchingDisks==1&&matchingPorts==1;
    }
};
inline const char* phaseText(Phase p) {
    switch(p) {
    case Phase::Download:return "Downloading and checking firmware...";
    case Phase::Backup:return "Saving a verified configuration backup on this PC...";
    case Phase::Copy:return "Copying firmware to the device and checking the complete file...";
    case Phase::Start:return "Starting the device firmware update. Do not unplug USB.";
    case Phase::WaitFirmware:return "Waiting for the device disk and COM port to return. Allow about 2 minutes. Do not unplug USB.";
    case Phase::VerifyFirmware:return "Reading the running firmware version from the device...";
    case Phase::CheckUpdateFolder:return "Checking that the device has emptied its update folder...";
    case Phase::WaitCleanup:return "Waiting for the device to finish removing its update file. Allow about 15 seconds. Do not unplug USB.";
    case Phase::CleanConfig:return "Firmware verified. Preparing to regenerate config/system.ini...";
    case Phase::Reset:return "Restarting the device. Do not unplug USB.";
    case Phase::WaitConfig:return "Waiting for the regenerated system.ini. Allow about 15 seconds. Do not unplug USB.";
    case Phase::VerifyConfig:return "Checking the new system.ini and the device firmware version...";
    case Phase::Complete:return "Firmware update successful. The device and its new config have been verified.";
    default:return "Ready.";
    }
}
// All device effects go through this interface; fault tests use no physical disk or COM port.
struct Operations {
    virtual ~Operations() {}
    virtual void progress(Phase)=0;
    virtual Identity liveIdentity()=0;
    virtual void download(const Manifest&)=0;
    virtual void backup()=0;
    virtual void stage()=0; // must flush, close and verify the full destination
    virtual void start()=0;
    virtual void reconnect(bool reset)=0; // must observe disappearance AND return of the same USB device
    virtual bool updateFolderEmpty()=0; // the device removes its own update file
    virtual void cleanConfig()=0; // only after live firmware verification; backup must already be verified
    virtual void reset()=0;
    virtual Identity configIdentity()=0;
};
inline void install(Operations&io,const Identity&old,const Manifest&m,Phase&phase) {
    if(!supportedHardware(old.hardware)||old.hardware!=m.hardware||!newer(m.release,old.release)) throw std::runtime_error("No compatible newer firmware is available");
    requireIdentity(old,io.liveIdentity(),old.release);
    auto step=[&](Phase p){phase=p;io.progress(p);};
    step(Phase::Download);io.download(m);
    step(Phase::Backup);io.backup();
    step(Phase::Copy);io.stage();
    requireIdentity(old,io.liveIdentity(),old.release);
    step(Phase::Start);io.start();
    step(Phase::WaitFirmware);io.reconnect(false);
    step(Phase::VerifyFirmware);requireIdentity(old,io.liveIdentity(),m.release);
    step(Phase::CheckUpdateFolder);
    if(!io.updateFolderEmpty()) {
        // One additional reset lets the device finish its own firmware cleanup.
        // Never delete the update image from the host, and never retry indefinitely.
        step(Phase::Reset);io.reset();step(Phase::WaitCleanup);io.reconnect(true);
        step(Phase::VerifyFirmware);requireIdentity(old,io.liveIdentity(),m.release);
        step(Phase::CheckUpdateFolder);
        if(!io.updateFolderEmpty())throw std::runtime_error("The update folder is still not empty after one extra reset. Config has not been deleted. Inspect the device before continuing.");
    }
    step(Phase::CleanConfig);io.cleanConfig();
    step(Phase::Reset);io.reset();
    step(Phase::WaitConfig);io.reconnect(true);
    step(Phase::VerifyConfig);requireIdentity(old,io.configIdentity(),m.release);
    requireIdentity(old,io.liveIdentity(),m.release);
    step(Phase::Complete);
}
}
#endif
