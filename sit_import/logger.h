#ifndef SIT_LOGGER_H
#define SIT_LOGGER_H
#include <string>
#include <cstdio>
#include <vector>
#include <map>
#include <set>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <regex>
#include <cmath>
#include <cstdlib>
#include <algorithm>
namespace sit {
using std::string;
struct Data { std::vector<string> metadata,fields; std::vector<std::vector<string> > rows; double air=0; bool estimatedTime=false; string source; };
inline string trim(string s) { size_t a=s.find_first_not_of(" \r\n\t"),b=s.find_last_not_of(" \r\n\t"); return a==string::npos?"":s.substr(a,b-a+1); }
inline std::vector<string> split(const string&s,char sep) { std::vector<string> v; size_t p=0,q; do {q=s.find(sep,p);v.push_back(trim(s.substr(p,q==string::npos?q:q-p)));p=q+1;}while(q!=string::npos);return v; }
inline double number(const string&s) { if(s.empty())throw std::runtime_error("Missing numeric value"); char* e=0; double v=std::strtod(s.c_str(),&e); if(e!=s.c_str()+s.size()||!std::isfinite(v))throw std::runtime_error("Invalid numeric value: "+s); return v; }
inline string fmt(double v) { if(!std::isfinite(v))throw std::runtime_error("Calculation produced a non-finite value");std::ostringstream o;o<<std::setprecision(15)<<v;return o.str(); }
inline string canonicalField(string f) { if(f=="PAR")return "Par"; if(f=="OXR")return "OxR"; return f; }
inline int index(const Data&d,const string&f) { auto it=std::find(d.fields.begin(),d.fields.end(),f);return it==d.fields.end()?-1:int(it-d.fields.begin()); }
inline double val(const Data&d,size_t r,const string&f) { int i=index(d,f);if(i<0)throw std::runtime_error("Missing field: "+f);return number(d.rows[r][i]); }
inline bool leap(int y) {return y%4==0&&(y%100!=0||y%400==0);}
inline long long stamp(const string&date,const string&time) {
 static const std::regex datePattern("[0-9]{4}-[0-9]{2}-[0-9]{2}"),timePattern("[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?"); if(!std::regex_match(date,datePattern)||!std::regex_match(time,timePattern))throw std::runtime_error("Invalid DATE/TIME: "+date+" "+time);
 int y=std::atoi(date.substr(0,4).c_str()),m=std::atoi(date.substr(5,2).c_str()),d=std::atoi(date.substr(8,2).c_str()),h=std::atoi(time.substr(0,2).c_str()),mi=std::atoi(time.substr(3,2).c_str()),s=std::atoi(time.substr(6,2).c_str());
 int md[]={31,28,31,30,31,30,31,31,30,31,30,31};if(y<1900||y>2199||m<1||m>12||d<1||d>md[m-1]+(m==2&&leap(y))||h>23||mi>59||s>59)throw std::runtime_error("Invalid calendar date/time: "+date+" "+time);
 long long days=0;for(int n=1900;n<y;++n)days+=leap(n)?366:365;for(int n=1;n<m;++n)days+=md[n-1]+(n==2&&leap(y));return ((days+d-1)*24+h)*3600+mi*60+s;
}
inline std::pair<string,string> unstamp(long long t) {int sec=int(t%60);t/=60;int mi=int(t%60);t/=60;int h=int(t%24);t/=24;int y=1900;while(t>=(leap(y)?366:365)){t-=leap(y)?366:365;++y;}int md[]={31,28,31,30,31,30,31,31,30,31,30,31};int m=1;while(t>=md[m-1]+(m==2&&leap(y))){t-=md[m-1]+(m==2&&leap(y));++m;}char a[32],b[32];std::sprintf(a,"%04d-%02d-%02d",y,m,int(t)+1);std::sprintf(b,"%02d:%02d:%02d",h,mi,sec);return {a,b};}
inline void validate(Data&d) {
 if(d.fields.size()>100||d.rows.size()>200000)throw std::runtime_error("File exceeds import limit (100 fields / 200000 rows)");
 std::set<string> seen;for(auto& f:d.fields)if(f.empty()||!seen.insert(f).second)throw std::runtime_error("Empty or duplicate field: "+f);
 int da=index(d,"DATE"),ti=index(d,"TIME");if(da<0||ti<0)throw std::runtime_error("Measurement DATE and TIME are required");if(d.rows.empty())throw std::runtime_error("No measurements found");
 for(size_t r=0;r<d.rows.size();++r)try {if(d.rows[r].size()!=d.fields.size())throw std::runtime_error("Number of values does not match FIELDS");for(size_t c=0;c<d.fields.size();++c)if(int(c)!=da&&int(c)!=ti&&!d.rows[r][c].empty())number(d.rows[r][c]);stamp(d.rows[r][da],d.rows[r][ti]);}catch(const std::exception&e){throw std::runtime_error("Measurement "+std::to_string(r+1)+": "+e.what());}
}
// Returns false for legacy files, which must continue through the original importer.
inline bool parse(const string&input,Data&d) {
 if(input.size()>20*1024*1024)throw std::runtime_error("File is larger than the 20 MB import limit");
 string text=input;if(text.compare(0,3,"\xef\xbb\xbf")==0)text.erase(0,3);
 std::replace(text.begin(),text.end(),'\r','\n'); auto lines=split(text,'\n');int fi=-1;bool logger=false,extra=false;std::smatch m;
 static const std::regex extraPattern("(^|[ ;])(?:Par|PAR|OxR|OXR)[+-]?[0-9]"); for(size_t i=0;i<lines.size();++i){const string& l=lines[i];if(l.compare(0,7,"FIELDS:")==0){if(fi>=0)throw std::runtime_error("Multiple FIELDS sections: split the file before importing");fi=int(i);}if(l.compare(0,6,"OSU107")==0||l.compare(0,7,"SAIV110")==0||l.compare(0,14,"SurfaceLogger")==0)logger=true;if(std::regex_search(l,extraPattern))extra=true;}
 if(fi<0&&!logger&&!extra)return false;
 if(fi>=0) {
  d.fields=split(lines[fi].substr(7),';');for(auto& f:d.fields)f=canonicalField(f);
  for(int i=0;i<fi;++i)if(!lines[i].empty())d.metadata.push_back(lines[i]);
  for(size_t i=fi+1;i<lines.size();++i){string l=lines[i];if(l.empty()||l=="End of data")continue;if(l[0]=='#'){d.metadata.push_back(l);continue;}d.rows.push_back(split(l,';'));}
 } else {
  std::vector<std::map<string,string> > records;long long start=-1;double interval=0;
  std::regex tags("([A-Za-z_]+)([+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?)");
  for(const auto& line:lines){if(line.empty())continue;string l=line,date,time;
   bool measurement=std::regex_search(l,std::regex("^(?:N[0-9]|COUNT[ =:]|(?:Par|PAR)[+-]?[0-9]|(?:OxR|OXR)[+-]?[0-9]|[0-9]{4}-[0-9]{2}-[0-9]{2})"));
   if(!measurement){d.metadata.push_back(l);
    if(std::regex_search(l,m,std::regex("DATE[ =:]+([0-9]{4}-[0-9]{2}-[0-9]{2}).*TIME[ =:]+([0-9]{2}:[0-9]{2}:[0-9]{2})")))start=stamp(m[1],m[2]);
    if(std::regex_search(l,m,std::regex("(?:INTERVAL_S[ =:]+|Interval: *)([0-9]+(?:\\.[0-9]+)?)")))interval=number(m[1]);
    continue;
   }
   std::regex dt("(?:DATE[ =:]+)?([0-9]{4}-[0-9]{2}-[0-9]{2})[ T;]+(?:TIME[ =:]+)?([0-9]{2}:[0-9]{2}:[0-9]{2}(?:\\.[0-9]+)?)");
   if(std::regex_search(l,m,dt)){date=m[1];time=m[2];l=std::regex_replace(l,dt,"");}
   std::map<string,string> row;size_t pos=0;
   for(std::sregex_iterator it(l.begin(),l.end(),tags),end;it!=end;++it){string gap=l.substr(pos,size_t(it->position())-pos);if(gap.find_first_not_of(" ;\t")==string::npos){}else throw std::runtime_error("Unrecognized Full measurement text: "+line);string key=canonicalField((*it)[1]),v=(*it)[2];if(key=="N")key="COUNT";if(!row.emplace(key,v).second)throw std::runtime_error("Duplicate Full field: "+key);if(index(d,key)<0)d.fields.push_back(key);pos=size_t(it->position()+it->length());}
   if(l.substr(pos).find_first_not_of(" ;\t")!=string::npos||row.empty())throw std::runtime_error("Unrecognized Full measurement: "+line);
   if(date.empty()) {if(start<0||interval<=0||interval!=std::floor(interval))throw std::runtime_error("Full measurements need timestamps, or an explicit DATE/TIME and whole-second interval in the header");auto t=unstamp(start+static_cast<long long>(records.size()*interval));date=t.first;time=t.second;d.estimatedTime=true;}
   row["DATE"]=date;row["TIME"]=time;records.push_back(row);
  }
  d.fields.push_back("DATE");d.fields.push_back("TIME");for(auto&r:records){std::vector<string> values;for(auto&f:d.fields)values.push_back(r.count(f)?r[f]:"");d.rows.push_back(values);}
 }
 for(auto&line:d.metadata){if(line.find("Full timestamps reconstructed")!=string::npos)d.estimatedTime=true;if(std::regex_search(line,m,std::regex("(?:^|[ ])AP([0-9]+(?:\\.[0-9]+)?)")))d.air=number(m[1]);}
 validate(d);return true;
}
#include "conversions.inc"
inline string output(const Data&d){std::ostringstream o;o<<"\xef\xbb\xbf# SAIV IT logger export 1.4.3\r\n# Source: "<<d.source<<"\r\n";for(auto&m:d.metadata)o<<(m.compare(0,1,"#")==0?"":"# ")<<m<<"\r\n";o<<"FIELDS: ";for(size_t i=0;i<d.fields.size();++i)o<<(i?";":"")<<d.fields[i];o<<"\r\n";for(auto&r:d.rows){for(size_t i=0;i<r.size();++i)o<<(i?";":"")<<r[i];o<<"\r\n";}return o.str();}
}
#endif
