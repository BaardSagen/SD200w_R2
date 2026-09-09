#include "../sit_import/update_protocol.h"
#include <iostream>
using namespace situpdate;
int main(){int checks=0;auto check=[&](bool ok){++checks;if(!ok)throw std::runtime_error("test failed");};
check(newer("1.3.10","1.3.9"));check(newer("2.0.0","1.99.99"));check(!newer("1.4.0","1.4.1"));check(!newer("1.4.0.0","1.4.0"));
for(auto s:{"1.2","1.2.x","1..3","1.2.3.4.5","1.2.65536","-1.2.3","1.2.3garbage",""}){bool failed=false;try{version(s);}catch(...){failed=true;}check(failed);}
const std::string good=R"({"version":"1.4.0","url":"https://saiv.no/software/SAIV_Instrument_Terminal_v1.4.0_Sept2026.zip","readme_url":"https://saiv.no/software/README_v1.4.0.txt"})";
check(parse(good).release=="1.4.0");check(parse("\xef\xbb\xbf"+good).readme.find("README")!=std::string::npos);
for(auto u:{"http://saiv.no/software/a.zip","https://saiv.no.evil/software/a.zip","https://saiv.no/software/../a.zip","https://saiv.no/software/%2e%2e/a.zip","https://saiv.no/software/a.exe","https://saiv.no/software/a.zip?x=1","https://saiv.no/software/a.zip\r\n"})check(!url(u,".zip"));
for(auto s:{"{}","{\"version\":\"1.4.0\",\"version\":\"1.4.1\"}","{\"version\":4}","{\"version\":\"1.4.0\",}","{\"url\":\"bad\\q\"}","[]"}){bool failed=false;try{parse(s);}catch(...){failed=true;}check(failed);}
check(Json("{\"a\":\"line\\n\\u00e5\\/\"}").object()["a"]=="line\n\xc3\xa5/");
bool failed=false;try{parse(good+"garbage");}catch(...){failed=true;}check(failed);
std::cout<<"PASS "<<checks<<" update version/JSON/URL validation checks\n";}
