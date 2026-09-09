#include "sit_compat.hpp"
#include <fstream>
#include <regex>
#include <cstring>
#include <cmath>
#include <set>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#else
#include <fcntl.h>
#include <unistd.h>
#endif
namespace fs=std::filesystem;
namespace saiv {
static double density0(double S,double T){
 double w=999.842594+.06793952*T-.00909529*T*T+.0001001685*pow(T,3)-1.120083e-6*pow(T,4)+6.536332e-9*pow(T,5);
 double a=.824493-.0040899*T+7.6438e-5*T*T-8.2467e-7*pow(T,3)+5.3875e-9*pow(T,4);
 double b=-.00572466+.00010227*T-1.6546e-6*T*T;
 return w+a*S+b*sqrt(std::abs(S*S*S))+.00048314*S*S;
}
double sitFormula(int kind,double a,double b,double c){
 if(!std::isfinite(a)||!std::isfinite(b)||!std::isfinite(c))return missing;
 if(kind==0){double C=a,T=b,P=c;if(C<.01)return 0;
  double R=C/42.914,rt=.6766097+.0200564*T+.0001104259*T*T-6.9698e-7*pow(T,3)+1.0031e-9*pow(T,4);
  double rp=1+P*(2.07e-5-6.37e-10*P+3.989e-15*P*P)/(1+.03426*T+.0004464*T*T+(.4215-.003107*T)*R);
  double x=sqrt(std::abs(R/(rt*rp))),d=T-15;
  return .008-.1692*x+25.3851*x*x+14.0941*pow(x,3)-7.0261*pow(x,4)+2.7081*pow(x,5)+d/(1+.0162*d)*(.0005-.0056*x-.0066*x*x-.0375*pow(x,3)+.0636*pow(x,4)-.0144*pow(x,5));
 }
 if(kind==3){double x=sin(a*3.14159265358979323846/180);x*=x;return 9.780318*(1+(.0052788+2.36e-5*x)*x)+1.092e-6*b;}
 double P=a,T=b,S=c,p=P/10;
 if(kind==1){
  if(S<0)return missing;
  double D=.001727-7.9836e-6*p;
  double B=-.01922-4.42e-5*T+(7.3637e-5+1.7945e-7*T)*p;
  double A=1.389-.01262*T+7.164e-5*T*T+2.006e-6*pow(T,3)-3.21e-8*pow(T,4);
  A+=(9.4742e-5-1.258e-5*T-6.4885e-8*T*T+1.0507e-8*pow(T,3)-2.0122e-10*pow(T,4))*p;
  A+=(-3.9064e-7+9.1041e-9*T-1.6002e-10*T*T+7.988e-12*pow(T,3))*p*p;
  A+=(1.1e-10+6.649e-12*T-3.389e-13*T*T)*pow(p,3);
  double W=1402.388+5.03711*T-.0580852*T*T+.0003342*pow(T,3)-1.478e-6*pow(T,4)+3.1464e-9*pow(T,5);
  W+=(.153563+.00068982*T-8.1788e-6*T*T+1.3621e-7*pow(T,3)-6.1185e-10*pow(T,4))*p;
  W+=(3.126e-5-1.7107e-6*T+2.5974e-8*T*T-2.5335e-10*pow(T,3)+1.0405e-12*pow(T,4))*p*p;
  W+=(-9.7729e-9+3.8504e-10*T-2.3643e-12*T*T)*pow(p,3);
  return W+A*S+B*sqrt(S*S*S)+D*S*S;
 }
 if(kind==2){
  double kw=19652.21+148.4206*T-2.327105*T*T+.01360477*pow(T,3)-5.155288e-5*pow(T,4);
  double k0=kw+(54.6746-.603459*T+.0109987*T*T-6.167e-5*pow(T,3))*S+(.07944+.016483*T-.00053009*T*T)*sqrt(std::abs(S*S*S));
  double aa=3.239908+.00143713*T+.000116092*T*T-5.77905e-7*pow(T,3)+(.0022838-1.0981e-5*T-1.6078e-6*T*T)*S+.000191075*sqrt(std::abs(S*S*S));
  double bb=8.50935e-5-6.12293e-6*T+5.2787e-8*T*T+(-9.9348e-7+2.0816e-8*T+9.1697e-10*T*T)*S;
  return density0(S,T)/(1-p/(k0+aa*p+bb*p*p))-1000;
 }
 throw std::runtime_error("Unknown SIT calculation");
}
double sitConversionFormula(int kind,double a,double b,double c){return kind==0?sitFormula(0,b,c,a):sitFormula(kind,a,b,c);}
double sitConductivity(double S,double T,double P){
 if(!std::isfinite(S)||S<0||!std::isfinite(T)||!std::isfinite(P))return missing;
 if(S==0)return 0;double lo=.01,hi=100;
 while(sitFormula(0,hi,T,P)<S&&hi<1000)hi*=2;
 if(sitFormula(0,hi,T,P)<S)return missing;
 for(int i=0;i<100;i++){double mid=(lo+hi)/2;if(sitFormula(0,mid,T,P)<S)lo=mid;else hi=mid;}
 return (lo+hi)/2;
}
std::string readDatasetBytes(const fs::path&p){
 auto size=fs::file_size(p);if(size>64*1024*1024)throw std::runtime_error("File exceeds 64 MiB");
 std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("Cannot read "+p.u8string());std::string s(size,'\0');
 if(size&&!f.read(s.data(),static_cast<std::streamsize>(size)))throw std::runtime_error("Incomplete file read");return s;
}
void writeNewFile(const fs::path&p,const std::string&s){
#ifdef _WIN32
 HANDLE f=CreateFileW(p.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,nullptr);
 if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot create new file (choose an unused name): "+p.u8string());DWORD n=0;bool ok=WriteFile(f,s.data(),DWORD(s.size()),&n,nullptr)&&n==s.size()&&FlushFileBuffers(f);CloseHandle(f);
#else
 int f=::open(p.c_str(),O_WRONLY|O_CREAT|O_EXCL,0666);if(f<0)throw std::runtime_error("Cannot create new file: "+p.u8string());size_t pos=0;bool ok=true;while(pos<s.size()){auto n=::write(f,s.data()+pos,s.size()-pos);if(n<=0){ok=false;break;}pos+=n;}if(::fsync(f))ok=false;::close(f);
#endif
 if(!ok){std::error_code ec;fs::remove(p,ec);throw std::runtime_error("File write failed: "+p.u8string());}
}
sit::Data toSit(const Table&t){sit::Data d;d.fields=t.columns;d.rows=t.rows;d.metadata=t.notes;d.source=t.source;
 std::smatch m;for(auto&line:d.metadata)if(d.air<=0&&line.find("M1_header:")==std::string::npos&&line.find("M2_header:")==std::string::npos&&std::regex_search(line,m,std::regex("(?:^|[ ])AP([0-9]+(?:\\.[0-9]+)?)")))d.air=sit::number(m[1]);return d;
}
Table fromSit(const sit::Data&d){Table t;t.columns=d.fields;t.rows=d.rows;t.notes=d.metadata;t.source=d.source;return t;}
std::string fieldsText(const Table&t){auto s=sit::output(toSit(t));auto pos=s.find("SAIV Instrument Terminal");if(pos!=std::string::npos)s.replace(pos,24,"SAIV Instrument Studio");return s;}
Table enrichSit(Table t){
 auto add=[&](const std::string&name,const std::function<double(size_t)>&fn){if(t.column(name)>=0)return;std::vector<std::string> values;for(size_t i=0;i<t.rows.size();i++)values.push_back(format(fn(i)));t.columns.push_back(name);for(size_t i=0;i<t.rows.size();i++)t.rows[i].push_back(values[i]);};
 int ci=t.column("C"),ti=t.column("T"),pi=t.column("P");
 if(ti<0&&t.column("T_degF")>=0){int fi=t.column("T_degF");add("T",[&](size_t i){return (t.value(i,fi)-32)/1.8;});ti=t.column("T");}
 int si=t.column("S");if(si<0)si=t.column("S_from_C");if(si<0)si=t.column("Salinity_SIT");
 if(si<0&&ci>=0&&ti>=0&&pi>=0){add("S_from_C",[&](size_t i){return sitFormula(0,t.value(i,ci),t.value(i,ti),t.value(i,pi));});si=t.column("S_from_C");}
 if(si>=0&&ti>=0&&pi>=0){
  if(t.column("c")<0)add("Sound_velocity_SIT_m_s",[&](size_t i){return sitFormula(1,t.value(i,pi),t.value(i,ti),t.value(i,si));});
  add("Density_anomaly_SIT_kg_m3",[&](size_t i){return sitFormula(2,t.value(i,pi),t.value(i,ti),t.value(i,si));});
 }return t;
}
template<class T> static T get(const std::string&s,size_t p){if(p+sizeof(T)>s.size())throw std::runtime_error("Truncated native file");T value;std::memcpy(&value,s.data()+p,sizeof(T));return value;}
static std::string nativeDate(const std::string&s,size_t p,bool time){char b[32];if(time)std::snprintf(b,sizeof b,"%02u:%02u:%02u",get<uint8_t>(s,p+3),get<uint8_t>(s,p+4),get<uint8_t>(s,p+5));else{int y=get<uint8_t>(s,p);y+=y>=80?1900:2000;std::snprintf(b,sizeof b,"%04d-%02u-%02u",y,get<uint8_t>(s,p+1),get<uint8_t>(s,p+2));}return b;}
Table loadDataset(const fs::path&path){
 std::string bytes=readDatasetBytes(path);auto ext=lower(path.extension().u8string());sit::Data d;d.source=path.u8string();
 if(ext==".csv")return parseCsvDataset(bytes,path.u8string());
 if(ext==".sd2"){
  if(bytes.size()<52||(bytes.size()-52)%52||get<int16_t>(bytes,0)!=12)throw std::runtime_error("Unsupported or damaged SD2 record layout");
  fs::path side=path;side.replace_extension(".SF2");
  if(fs::exists(side)){auto s=readDatasetBytes(side);auto nl=s.find('\n');if(nl==std::string::npos||trim(s.substr(0,nl))!="# SIT native fields 1 "+sitnative::hexhash(bytes))throw std::runtime_error("SF2 does not match this SD2 file. Keep the original dataset files together.");if(!sitnative::parse(s.substr(nl+1),d))throw std::runtime_error("Invalid SF2 contents");return fromSit(d);}
  auto flags=get<uint32_t>(bytes,6);size_t n=(bytes.size()-52)/52;if(!n)throw std::runtime_error("SD2 contains no measurements");
  std::string ox,op,rf;auto member=[&](const char* e){auto p=path;p.replace_extension(e);return fs::exists(p)?readDatasetBytes(p):std::string();};
  if(flags&64){ox=member(".OX2");if(ox.size()!=n*4)throw std::runtime_error("Missing or damaged OX2 companion file");}
  if(flags&768){op=member(".OP2");if(op.size()!=n*8)throw std::runtime_error("Missing or damaged OP2 companion file");}
  rf=member(".RF2");if(rf.empty()||rf.size()%72)throw std::runtime_error("Missing or damaged RF2 companion file");
  d.fields={"SERIES","COUNT","DATE","TIME"};std::vector<std::pair<std::string,int>> fields;
  for(auto f:std::vector<std::pair<std::string,int>>{{"S",0},{"C",1},{"T",2},{"P",3},{"c",4}})if(flags&(1u<<f.second)){fields.push_back(f);d.fields.push_back(f.first);}
  if(flags&64)d.fields.push_back("OX");if(flags&256)d.fields.push_back("OF");if(flags&512)d.fields.push_back("OT");
  for(size_t i=0;i<n;i++){size_t p=52+i*52;std::string date=nativeDate(bytes,p,false),time=nativeDate(bytes,p,true);sit::stamp(date,time);size_t series=0;
   for(size_t j=0;j<rf.size()/72;j++)if(get<uint32_t>(rf,j*72+4)<=i+1)series=j;
   std::vector<std::string> row={std::to_string(get<uint32_t>(rf,series*72)),std::to_string(get<uint32_t>(bytes,p+8)),date,time};
   for(auto&f:fields)row.push_back(format(number(format(get<double>(bytes,p+12+f.second*8)))));
   if(flags&64)row.push_back(format(number(format(get<float>(ox,i*4)))));if(flags&256)row.push_back(format(number(format(get<float>(op,i*8)))));if(flags&512)row.push_back(format(number(format(get<float>(op,i*8+4)))));d.rows.push_back(row);
  }
  d.air=get<float>(rf,16)*1013.25/760.;d.metadata.push_back("SD200 native data Ser No "+std::to_string(get<int32_t>(bytes,2))+" AP"+format(d.air));
  return enrichSit(fromSit(d));
 }
 if(sitnative::parse(bytes,d))return fromSit(d);
 Table t=loadText(bytes,path.u8string());if(t.rows.empty())throw std::runtime_error("No supported measurements found in the file");
 // Historical full N-record files carry dates and sampling intervals in their header.
 if(t.column("DATE")<0){std::smatch m;std::regex header("Date[ ]+([0-9]{2})-([0-9]{2})-([0-9]{2})[ ]+Time[ ]+([0-9]{2})[:.-]([0-9]{2})[:.-]([0-9]{2}).*Interval:[ ]*([0-9]+)(sec|min|hour)",std::regex::icase);
  for(auto&line:t.notes)if(std::regex_search(line,m,header)){int y=std::stoi(m[1]);y+=y>=80?1900:2000;std::string date=std::to_string(y)+"-"+m[2].str()+"-"+m[3].str(),time=m[4].str()+":"+m[5].str()+":"+m[6].str();long long start=sit::stamp(date,time),step=std::stoll(m[7])*(lower(m[8])=="min"?60:lower(m[8])=="hour"?3600:1);
   int tc=t.column("TIME");t.columns.push_back("DATE");if(tc<0){tc=int(t.columns.size());t.columns.push_back("TIME");}
   for(size_t i=0;i<t.rows.size();i++){auto dt=sit::unstamp(start+step*static_cast<long long>(i));t.rows[i].resize(t.columns.size());t.rows[i][t.column("DATE")]=dt.first;if(t.rows[i][tc].empty())t.rows[i][tc]=dt.second;}t.notes.push_back("Full timestamps reconstructed from explicit header and interval");break;
  }
 }return t;
}
void saveNativeDataset(const Table&t,const fs::path&path){
 sit::Data d=toSit(t);if(sit::index(d,"DATE")<0||sit::index(d,"TIME")<0)throw std::runtime_error("Native SD2 export requires measurement DATE and TIME");
 auto f=sitnative::project(d,fieldsText(t),sitFormula);std::vector<std::pair<fs::path,std::string>> outputs;
 for(auto&v:std::vector<std::pair<const char*,std::string>>{{".SD2",f.sd},{".RF2",f.rf},{".OX2",f.ox},{".OP2",f.op},{".SF2",f.sf}}){auto p=path;p.replace_extension(v.first);if(fs::exists(p))throw std::runtime_error("Choose a new dataset name; companion file already exists: "+p.u8string());if(!v.second.empty())outputs.push_back({p,v.second});}
 std::vector<fs::path> created;try{for(auto&o:outputs){writeNewFile(o.first,o.second);created.push_back(o.first);}}catch(...){for(auto&p:created){std::error_code ec;fs::remove(p,ec);}throw;}
}
Table parseCsvDataset(const std::string& input,const std::string& source){
 Table t;t.source=source;std::string bytes=input;if(bytes.compare(0,3,"\xef\xbb\xbf")==0)bytes.erase(0,3);
 size_t p=0;char delimiter=';';bool header=false;
 while(p<bytes.size()){
  if(bytes[p]=='\r'||bytes[p]=='\n'){p++;continue;}
  if(bytes[p]=='#'){size_t end=bytes.find_first_of("\r\n",p);if(end==std::string::npos)end=bytes.size();auto note=bytes.substr(p,end-p);t.notes.push_back(note.rfind("# ",0)==0?note.substr(2):note);p=end;continue;}
  if(!header){auto end=bytes.find_first_of("\r\n",p);auto first=bytes.substr(p,end-p);delimiter=first.find(';')!=std::string::npos?';':first.find('\t')!=std::string::npos?'\t':',';}
  std::vector<std::string> row;std::string cell;bool quoted=false,afterQuote=false,done=false;
  while(p<bytes.size()&&!done){char ch=bytes[p++];if(quoted){if(ch=='"'){if(p<bytes.size()&&bytes[p]=='"'){cell+='"';p++;}else {quoted=false;afterQuote=true;}}else cell+=ch;}
   else if(ch==delimiter||ch=='\r'||ch=='\n'){row.push_back(cell);cell.clear();afterQuote=false;if(ch!=delimiter){done=true;if(ch=='\r'&&p<bytes.size()&&bytes[p]=='\n')p++;}}
   else if(ch=='"'&&cell.empty()&&!afterQuote)quoted=true;
   else {if(afterQuote)throw std::runtime_error("Invalid characters after a CSV quote");cell+=ch;}
  }
  if(quoted)throw std::runtime_error("Unclosed CSV quote");if(!done)row.push_back(cell);
  if(!header){if(row.empty()||row.size()>128)throw std::runtime_error("CSV requires 1-128 named columns");std::set<std::string> seen;for(auto&name:row)if(name.empty()||!seen.insert(name).second)throw std::runtime_error("Empty or duplicate CSV column");t.columns=std::move(row);header=true;}
  else {if(row.size()!=t.columns.size())throw std::runtime_error("CSV row does not match the header width");t.rows.push_back(std::move(row));if(t.rows.size()>200000)throw std::runtime_error("CSV exceeds 200000 rows");}
 }
 if(t.rows.empty())throw std::runtime_error("No measurements in CSV file");return t;
}
std::vector<double> measurementSeconds(const Table&t){std::vector<double> out;int da=t.column("DATE"),ti=t.column("TIME");double start=0;
 for(size_t i=0;i<t.rows.size();i++){double v=double(i);if(da>=0&&ti>=0)try{v=sitnative::timestamp(t.rows[i][da],t.rows[i][ti]);if(i==0)start=v;v-=start;}catch(...){v=missing;}out.push_back(v);}return out;
}
}
