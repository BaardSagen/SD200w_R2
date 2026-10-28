// Exercise the production WinINet fetch and channel parser against both servers.
// No logger discovery, COM access, configuration write or flashing is performed.
#define main windowsFileLayerMain
#include "test_firmware1413_windows.cpp"
#undef main
#include <wincrypt.h>
#ifndef CALG_SHA_256
#define CALG_SHA_256 0x800c
#endif
static std::string digest(const std::string&bytes) {
    HCRYPTPROV provider=0;HCRYPTHASH hash=0;
    if(!CryptAcquireContextW(&provider,0,0,PROV_RSA_AES,CRYPT_VERIFYCONTEXT))throw std::runtime_error("Hash provider failed");
    if(!CryptCreateHash(provider,CALG_SHA_256,0,0,&hash)){CryptReleaseContext(provider,0);throw std::runtime_error("Hash creation failed");}
    BYTE result[32];DWORD size=32;
    bool ok=CryptHashData(hash,reinterpret_cast<BYTE*>(const_cast<char*>(bytes.data())),DWORD(bytes.size()),0)&&CryptGetHashParam(hash,HP_HASHVAL,result,&size,0);
    CryptDestroyHash(hash);CryptReleaseContext(provider,0);
    if(!ok||size!=32)throw std::runtime_error("SHA-256 failed");
    std::string out;const char*hex="0123456789abcdef";
    for(auto b:result){out+=hex[b>>4];out+=hex[b&15];}return out;
}
int main(){try{
    std::cout<<"{\"channels\":[";
    bool comma=false;
    for(auto hardware:{"3.1.2","3.3.0"}) {
        auto raw=firmwareFetch(sitfirmware::serverForHardware(hardware)+"latest.json",65536);
        auto manifest=sitfirmware::manifest(raw,hardware);
        auto notes=firmwareFetch(manifest.readme,131072);
        auto customer=sitfirmware::publicNotes(notes);
        check(!customer.empty());
        const std::regex forbidden("ctrl[ +_-]*t|control[ +_-]*t|service menu|\\b(cfg|fwust|fwuclr|fwupdate|fwu|slp|ver|usbd)\\b|\\bf[ /]+y\\b",std::regex::icase);
        check(!std::regex_search(customer,forbidden));
        auto bytes=firmwareFetch(manifest.download,4*1024*1024);
        check(bytes.size()>=32);
        check((unsigned char)bytes[0]==0x3d&&(unsigned char)bytes[1]==0xb8&&(unsigned char)bytes[2]==0xf3&&(unsigned char)bytes[3]==0x96);
        auto sha=digest(bytes);check(sha==manifest.sha256);
        const auto other=std::string(hardware)=="3.1.2"?"3.3.0":"3.1.2";
        rejects([&]{sitfirmware::manifest(raw,other);});
        if(comma)std::cout<<",";comma=true;
        std::cout<<"{\"hardware\":\""<<hardware<<"\",\"version\":\""<<manifest.release<<"\",\"bytes\":"<<bytes.size()<<",\"sha256\":\""<<sha<<"\",\"checksum_matches\":true,\"customer_notes_filtered\":true,\"cross_hardware_rejected\":true}";
    }
    std::cout<<"],\"passed\":true,\"physical_device_io\":false}\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
