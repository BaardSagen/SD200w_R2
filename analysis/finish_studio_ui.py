from pathlib import Path
r=Path(__file__).resolve().parents[1]/'saiv-studio'
p=r/'src/app.cpp';s=p.read_text()
s=s.replace('App::~App(){serial_.disconnect();','App::~App(){if(settingFuture_.valid())settingFuture_.wait();serial_.disconnect();')
s=s.replace('if(testWire_.is_open())return;try{fs::create_directories','if(testWire_.is_open()||demo_)return;try{fs::create_directories')
s=s.replace('void App::poll(){for(auto& e:serial_.poll())','''void App::poll(){
 if(settingBusy_){if(settingFuture_.wait_for(std::chrono::seconds(0))!=std::future_status::ready)return;auto result=settingFuture_.get();settingBusy_=false;protocol_.connected();protocol_.device=acceptedIdentity_;acceptRx(result.received);if(result.error.empty()){notice_=result.message;error_.clear();}else{error_=result.error;acceptedInstrument_=false;}return;}
 for(auto& e:serial_.poll())''')
s=s.replace('if(!terminalFocused_||page_!=1','if(settingBusy_||!terminalFocused_||page_!=1')
a=s.index('void App::plot(');b=s.index('void App::grid(',a);s=s[:a]+s[b:]
a=s.index(' if(utility_==0){',s.index('void App::drawUtilities'));b=s.index('\n else if(utility_==1)',a)
s=s[:a]+''' if(utility_==0){paragraph("Add salinity, sound velocity and density anomaly using the documented SIT routines and available C, T, P and S columns. Existing fields are retained. Use Data > Convert current dataset for unit choices, real depth, oxygen and PAR.");}'''+s[b:]
s=s.replace('ImGui::BeginDisabled(utility_==0&&!locationConfirmed_);','ImGui::BeginDisabled(false);')
p.write_text(s)
p=r/'src/sit_compat.cpp';s=p.read_text();s=s.replace('#include <set>','#include <set>\n#ifdef _WIN32\n#define NOMINMAX\n#include <windows.h>\n#else\n#include <fcntl.h>\n#include <unistd.h>\n#endif')
a=s.index('void writeNewFile(');b=s.index('sit::Data toSit',a)
s=s[:a]+'''void writeNewFile(const fs::path&p,const std::string&s){
#ifdef _WIN32
 HANDLE f=CreateFileW(p.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,nullptr);
 if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot create new file (choose an unused name): "+p.u8string());DWORD n=0;bool ok=WriteFile(f,s.data(),DWORD(s.size()),&n,nullptr)&&n==s.size()&&FlushFileBuffers(f);CloseHandle(f);
#else
 int f=::open(p.c_str(),O_WRONLY|O_CREAT|O_EXCL,0666);if(f<0)throw std::runtime_error("Cannot create new file: "+p.u8string());size_t pos=0;bool ok=true;while(pos<s.size()){auto n=::write(f,s.data()+pos,s.size()-pos);if(n<=0){ok=false;break;}pos+=n;}if(::fsync(f))ok=false;::close(f);
#endif
 if(!ok){std::error_code ec;fs::remove(p,ec);throw std::runtime_error("File write failed: "+p.u8string());}
}
'''+s[b:]
s=s.replace('std::string fieldsText(const Table&t){return sit::output(toSit(t));}','std::string fieldsText(const Table&t){auto s=sit::output(toSit(t));auto pos=s.find("SAIV Instrument Terminal");if(pos!=std::string::npos)s.replace(pos,24,"SAIV Instrument Studio");return s;}')
s=s.replace('format(get<double>(bytes,p+12+f.second*8))','format(number(format(get<double>(bytes,p+12+f.second*8))))')
s=s.replace('format(get<float>(ox,i*4))','format(number(format(get<float>(ox,i*4))))').replace('format(get<float>(op,i*8))','format(number(format(get<float>(op,i*8))))').replace('format(get<float>(op,i*8+4))','format(number(format(get<float>(op,i*8+4))))')
p.write_text(s)
# Remove the unused software parity implementation and its obsolete tests.
p=r/'src/core.cpp';s=p.read_text();import re
s=re.sub(r'std::string (?:encode7E1|decode7E1)\([^\n]*\n','',s);p.write_text(s)
p=r/'src/core.hpp';s=p.read_text();s=s.replace('std::string encode7E1(std::string data);\n','').replace('std::string decode7E1(std::string data);\n','');p.write_text(s)
p=r/'tests/core_tests.cpp';s=p.read_text();s='\n'.join(x for x in s.split('\n') if 'encode7E1' not in x);p.write_text(s)
