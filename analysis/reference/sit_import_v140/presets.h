#ifndef SIT_PRESETS_H
#define SIT_PRESETS_H
#include "logger.h"
#include <cstdint>
#include <cstring>
namespace sitpreset {
using sit::string;
inline string family(const sit::Data&d){for(auto&m:d.metadata){string s=sit::trim(m);if(s.compare(0,1,"#")==0)s=sit::trim(s.substr(1));for(string f:{"OSU107","SAIV110","SurfaceLogger"})if(s.compare(0,f.size(),f)==0)return f;}return "FIELDS";}
inline string signature(const sit::Data&d){
 // Exact names/order and declared PAR units prevent applying raw-field choices to a different layout.
 string s="SIT-CONVERT-1|"+family(d);for(auto&f:d.fields)s+="|"+std::to_string(f.size())+":"+f;
 for(auto&m:d.metadata){if(m.find("PAR source unit: uEinstein/(cm2*s)")!=string::npos)s+="|PAR:cm2";else if(m.find("PAR source unit: uEinstein/(m2*s)")!=string::npos)s+="|PAR:m2";}
 return s;
}
inline string key(const string&s){uint64_t h=14695981039346656037ULL;for(unsigned char c:s){h^=c;h*=1099511628211ULL;}std::ostringstream o;o<<std::hex<<std::setw(16)<<std::setfill('0')<<h;return o.str();}
struct Record {string signature,date,source;sit::Choices choices;};
struct Writer {string data;void u(unsigned v){for(int i=0;i<4;++i)data+=char(v>>(i*8));}void s(const string&v){u(unsigned(v.size()));data+=v;}void d(double v){static_assert(sizeof(double)==8,"double size");char raw[8];std::memcpy(raw,&v,8);data.append(raw,8);}};
struct Reader {const string&data;size_t at=0;Reader(const string&s):data(s){}void need(size_t n){if(n>data.size()-at)throw std::runtime_error("Incomplete saved choices");}unsigned u(){need(4);unsigned v=0;for(int i=0;i<4;++i)v|=unsigned((unsigned char)data[at++])<<(i*8);return v;}bool b(){unsigned v=u();if(v>1)throw std::runtime_error("Invalid saved checkbox");return v!=0;}int mode(unsigned max){unsigned v=u();if(v>max)throw std::runtime_error("Invalid saved conversion");return int(v);}string s(){unsigned n=u();need(n);string v=data.substr(at,n);at+=n;return v;}double d(){need(8);double v;std::memcpy(&v,data.data()+at,8);at+=8;if(!std::isfinite(v))throw std::runtime_error("Invalid saved number");return v;}};
inline string encode(const Record&r){Writer w;w.s("SIT choices 2");w.s(r.signature);w.s(r.date);w.s(r.source);auto&o=r.choices;
 for(int x:{o.oxygen,o.oxygenOX,o.conductivity,o.depth,o.par,o.parSource})w.u(x);
 for(bool x:{o.soundVelocity,o.keepC,o.keepP,o.keepPar,o.useGPS})w.u(x);
 for(double x:{o.latitude,o.longitude,o.temperature,o.salinity,o.air})w.d(x);
 w.u(o.suppliedT);w.u(o.suppliedS);w.u(unsigned(o.keepOriginal.size()));for(auto&kv:o.keepOriginal){w.s(kv.first);w.u(kv.second);}w.u(o.fahrenheit);return w.data;
}
inline bool decode(const string&data,const string&sig,Record&result){try{
 if(data.size()>65536)return false;Reader r(data);Record v;string version=r.s();if(version!="SIT choices 1"&&version!="SIT choices 2")return false;v.signature=r.s();if(v.signature!=sig)return false;v.date=r.s();v.source=r.s();if(!std::regex_match(v.date,std::regex("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")))return false;auto&o=v.choices;
 o.oxygen=r.mode(3);o.oxygenOX=r.mode(3);o.conductivity=r.mode(1);o.depth=r.mode(1);o.par=r.mode(1);o.parSource=r.mode(2);
 o.soundVelocity=r.b();o.keepC=r.b();o.keepP=r.b();o.keepPar=r.b();o.useGPS=r.b();o.latitude=r.d();o.longitude=r.d();o.temperature=r.d();o.salinity=r.d();o.air=r.d();o.suppliedT=r.b();o.suppliedS=r.b();
 if(std::abs(o.latitude)>90||std::abs(o.longitude)>180||(o.par&&!o.parSource))return false;
 unsigned n=r.u();if(n>100)return false;for(unsigned i=0;i<n;++i){string field=r.s();bool keep=r.b();if(field.empty()||!o.keepOriginal.emplace(field,keep).second)return false;}if(version=="SIT choices 2")o.fahrenheit=r.b();if(r.at!=data.size())return false;result=v;return true;
 }catch(const std::exception&){return false;}}
inline sit::Choices reuse(const Record&r,const sit::Data&d){auto o=r.choices;o.suppliedT=o.suppliedS=false;o.temperature=o.salinity=0;o.air=d.air;o.latitude=45.508368287;o.longitude=0;return o;}
}
#endif
