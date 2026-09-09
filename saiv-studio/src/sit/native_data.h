#ifndef SIT_NATIVE_DATA_H
#define SIT_NATIVE_DATA_H
#include "logger.h"
#include <cstring>
#include <cstdint>
namespace sitnative {
inline bool suffix(const std::string&s,const std::string&t){return s.size()>=t.size()&&s.compare(s.size()-t.size(),t.size(),t)==0;}
inline bool dateField(const std::string&f){return f=="DATE"||suffix(f,"_DATE");}
inline bool timeField(const std::string&f){return f=="TIME"||suffix(f,"_TIME");}
inline bool separator(const std::string&f){return suffix(f,"_separator");}
inline std::string canon(std::string f){for(auto pre:{"M1_","M2_"})if(f.compare(0,3,pre)==0)return std::string(pre)+sit::canonicalField(f.substr(3));return sit::canonicalField(f);}
inline double timestamp(const std::string&d,const std::string&t){double v=double(sit::stamp(d,t));auto dot=t.find('.');return v+(dot==std::string::npos?0:sit::number("0"+t.substr(dot)));}
inline bool parse(std::string text,sit::Data&d){
 if(text.size()>20*1024*1024)throw std::runtime_error("File exceeds the 20 MB limit");
 if(text.compare(0,3,"\xef\xbb\xbf")==0)text.erase(0,3);
 std::replace(text.begin(),text.end(),'\r','\n');auto lines=sit::split(text,'\n');int fi=-1;
 for(size_t i=0;i<lines.size();++i)if(lines[i].compare(0,7,"FIELDS:")==0){if(fi>=0)throw std::runtime_error("Multiple FIELDS sections are not supported");fi=int(i);}
 if(fi<0)return sit::parse(text,d);
 d.fields=sit::split(lines[fi].substr(7),';');std::set<std::string> seen;
 for(auto&f:d.fields){f=canon(f);if(f.empty()||!seen.insert(f).second)throw std::runtime_error("Duplicate/empty field: "+f);}
 if(d.fields.size()>100)throw std::runtime_error("Too many fields");
 int da=sit::index(d,"DATE"),ti=sit::index(d,"TIME");if(da<0||ti<0)throw std::runtime_error("Master DATE and TIME fields are required");
 for(int i=0;i<fi;++i)if(!lines[i].empty())d.metadata.push_back(lines[i]);
 for(size_t i=fi+1;i<lines.size();++i){auto l=lines[i];if(l.empty()||l=="End of data")continue;if(l[0]=='#'){d.metadata.push_back(l);continue;}auto r=sit::split(l,';');if(r.size()!=d.fields.size())throw std::runtime_error("Measurement has a different number of columns than FIELDS");
  timestamp(r[da],r[ti]);for(size_t j=0;j<r.size();++j){if(r[j].empty())continue;auto f=d.fields[j];if(separator(f)){if(r[j]!="-")throw std::runtime_error("Invalid file separator");}else if(dateField(f)){sit::stamp(r[j],"00:00:00");}else if(timeField(f)){sit::stamp("2000-01-01",r[j]);}else sit::number(r[j]);}
  d.rows.push_back(r);if(d.rows.size()>200000)throw std::runtime_error("Too many measurements");
 }
 if(d.rows.empty())throw std::runtime_error("No measurements found");
 std::smatch m;for(auto&l:d.metadata)if(d.air<=0&&l.find("M1_header:")==std::string::npos&&l.find("M2_header:")==std::string::npos&&std::regex_search(l,m,std::regex("(?:^|[ ])AP([0-9]+(?:\\.[0-9]+)?)")))d.air=sit::number(m[1]);return true;
}
inline double value(const sit::Data&d,size_t row,std::initializer_list<const char*>names){for(auto name:names){int i=sit::index(d,name);if(i>=0&&!d.rows[row][i].empty())return sit::number(d.rows[row][i]);}return -999.;}
template<class T> inline void append(std::string&s,T v){s.append(reinterpret_cast<const char*>(&v),sizeof(v));}
inline uint64_t hash(const std::string&s){uint64_t h=14695981039346656037ULL;for(unsigned char c:s){h^=c;h*=1099511628211ULL;}return h;}
inline std::string hexhash(const std::string&s){std::ostringstream o;o<<std::hex<<hash(s);return o.str();}
struct Files {std::string sd,rf,ox,op,sf;};
inline Files project(const sit::Data&d,const std::string&original,sit::Formula formula){
 Files f;bool hasS=sit::index(d,"S")>=0||sit::index(d,"S_from_C")>=0||sit::index(d,"Salinity_SIT")>=0;
 bool ctd=sit::index(d,"C")>=0&&(sit::index(d,"T")>=0||sit::index(d,"T_degF")>=0)&&sit::index(d,"P")>=0;
 uint32_t flags=(hasS||ctd?1:0)|(sit::index(d,"C")>=0?2:0)|(sit::index(d,"T")>=0||sit::index(d,"T_degF")>=0?4:0)|(sit::index(d,"P")>=0?8:0)|(ctd||(hasS&&(sit::index(d,"T")>=0||sit::index(d,"T_degF")>=0)&&sit::index(d,"P")>=0)||sit::index(d,"Sound_velocity_SIT_m_s")>=0?16:0)|(sit::index(d,"OX")>=0?64:0)|(sit::index(d,"OF")>=0?256:0)|(sit::index(d,"OT")>=0?512:0);
 int32_t serial=0;std::smatch m;for(auto&l:d.metadata)if(l.find("M1_header:")==std::string::npos&&l.find("M2_header:")==std::string::npos&&std::regex_search(l,m,std::regex("Ser No ([0-9]+)"))){serial=std::stoi(m[1]);break;}
 if(!serial)for(auto&l:d.metadata)if(l.find("M1_header:")==std::string::npos&&l.find("M2_header:")==std::string::npos&&std::regex_search(l,m,std::regex("Ser:([0-9]+)"))){serial=std::stoi(m[1]);break;}
 append<int16_t>(f.sd,12);append<int32_t>(f.sd,serial);append<uint32_t>(f.sd,flags);append<uint8_t>(f.sd,5);append<uint8_t>(f.sd,1);append<int16_t>(f.sd,12);f.sd.resize(52,0);
 const int da=sit::index(d,"DATE"),ti=sit::index(d,"TIME");
 for(size_t i=0;i<d.rows.size();++i){auto&r=d.rows[i];auto date=r[da],time=r[ti];int year=std::stoi(date.substr(0,4));if(year<1981||year>2079)throw std::runtime_error("Native SD2 requires years 1981 through 2079");
  append<uint8_t>(f.sd,year%100);append<uint8_t>(f.sd,std::stoi(date.substr(5,2)));append<uint8_t>(f.sd,std::stoi(date.substr(8,2)));append<uint8_t>(f.sd,std::stoi(time.substr(0,2)));append<uint8_t>(f.sd,std::stoi(time.substr(3,2)));append<uint8_t>(f.sd,std::stoi(time.substr(6,2)));append<uint16_t>(f.sd,0);append<uint32_t>(f.sd,uint32_t(i+1));
  double c=value(d,i,{"C"}),t=value(d,i,{"T"}),p=value(d,i,{"P"}),s=value(d,i,{"S","S_from_C","Salinity_SIT"}),v=value(d,i,{"Sound_velocity_SIT_m_s"});
  if(t==-999){double fahrenheit=value(d,i,{"T_degF"});if(fahrenheit!=-999)t=(fahrenheit-32)/1.8;}
  if(s==-999&&c!=-999&&t!=-999&&p!=-999)s=formula(0,c,t,p);
  if(v==-999&&s!=-999&&t!=-999&&p!=-999)v=formula(1,p,t,s);
  for(double n:{s,c,t,p,v})append<double>(f.sd,n);
  if(flags&64)append<float>(f.ox,float(value(d,i,{"OX"})));
  if(flags&768){append<float>(f.op,float(value(d,i,{"OF"})));append<float>(f.op,float(value(d,i,{"OT"})));}
 }
 append<uint32_t>(f.rf,1);append<uint32_t>(f.rf,1);f.rf.append(f.sd,52,6);append<uint16_t>(f.rf,1);append<float>(f.rf,d.air>0?float(d.air*760/1013.25):-999.f);
 for(int i=0;i<4;++i)append<double>(f.rf,-999.);append<int16_t>(f.rf,-2);append<int16_t>(f.rf,0);append<double>(f.rf,35.);append<double>(f.rf,0.);
 f.sf="# SIT native fields 1 "+hexhash(f.sd)+"\r\n"+original;
 return f;
}
}
#endif
