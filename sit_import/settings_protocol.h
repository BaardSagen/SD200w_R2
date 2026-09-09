#ifndef SIT_SETTINGS_PROTOCOL_H
#define SIT_SETTINGS_PROTOCOL_H
#include <string>
#include <vector>
#include <regex>
#include <functional>
#include <stdexcept>
#include <algorithm>
#include <cmath>
#include <exception>
namespace sitsettings {
enum Kind {None=0,OSU=1,Surface=2,SD200=3};
inline std::string lower(std::string s){for(auto&c:s)c=char(std::tolower((unsigned char)c));return s;}
inline bool has(const std::string&s,const std::string&t){return lower(s).find(lower(t))!=std::string::npos;}
inline bool deviceError(const std::string&s){return std::regex_search(s,std::regex("(?:^|[\\r\\n])[ \\t]*(?:ERROR\\b|ERR[: ]|FAIL(?:ED|URE)?\\b)|APPLY aborted|Stop logging before Update",std::regex::icase));}
inline bool mainMenu(const std::string&s){return has(s,"start via key-board")&&has(s,"exit (passive)");}
inline bool yn(const std::string&s){return has(s,"y/n");}
inline bool format(const std::string&s){return has(s,"format:")&&has(s,"yy-mm-dd-hh-mm-ss");}
inline bool stopped(const std::string&s){return has(s,"surface-logger: stopped")||has(s,"stopped, type");}
inline bool running(const std::string&s){return has(s,"surface-logger: running")||has(s,"type <i> for stop");}
struct Interval {int seconds;const char* label;char code;};
static const Interval intervals[]={{1,"1 second",'L'},{2,"2 seconds",'M'},{5,"5 seconds",'N'},{10,"10 seconds",'O'},{20,"20 seconds",'P'},{60,"1 minute",'Q'},{300,"5 minutes",'R'},{600,"10 minutes",'S'},{1800,"30 minutes",'T'},{3600,"1 hour",'V'},{10800,"3 hours",'W'}};
inline int intervalValue(const std::string&s){std::smatch m;if(!std::regex_search(s,m,std::regex("measuring interval\\s*[:=]?\\s*([0-9]+)\\s*(sec|min|hour)",std::regex::icase)))return -1;return std::stoi(m[1])*(lower(m[2])=="min"?60:lower(m[2])=="hour"?3600:1);}
inline bool advertised(const std::string&s,const Interval&v){
 std::string code(1,v.code);std::smatch m;std::string token="(?:<"+code+">|\\b"+code+"[=:.)])";
 for(int direction=0;direction<2;++direction){std::regex pattern(direction==0?token+"[ \\t]*([0-9]+)[ \\t]*(sec|min|hour)":"([0-9]+)[ \\t]*(sec|min|hour)[^\\r\\n<>]{0,8}"+token,std::regex::icase);
 for(auto it=std::sregex_iterator(s.begin(),s.end(),pattern);it!=std::sregex_iterator();++it){int value=std::stoi((*it)[1])*(lower((*it)[2])=="min"?60:lower((*it)[2])=="hour"?3600:1);if(value==v.seconds)return true;}}
 return false;
}
inline char zoneAnswer(const std::string&s,bool gmt){std::smatch m;std::string current;if(std::regex_search(s,m,std::regex("current timezone is\\s*\\(?(LT|GMT)",std::regex::icase)))current=lower(m[1]);else if(std::regex_search(s,m,std::regex("Time[^\\r\\n]*\\b(LT|GMT)\\b",std::regex::icase)))current=lower(m[1]);else if(std::regex_search(s,m,std::regex("(GMT|LT)[^\\r\\n]*change",std::regex::icase)))current=lower(m[1]);else if(std::regex_search(s,m,std::regex("change[^\\r\\n]*to\\s*(GMT|LT)",std::regex::icase)))current=lower(m[1])=="gmt"?"lt":"gmt";else throw std::runtime_error("Unrecognized LT/GMT question; clock may already have been written.");if(!yn(s))throw std::runtime_error("Incomplete timezone question");return ((current=="gmt")==gmt)?'N':'Y';}
struct Clock {std::string wire,date,time;double epoch;};
struct Timeout:std::runtime_error {std::string received;Timeout(const std::string&s):std::runtime_error("Timed out waiting for a complete device response. A setting may already have been written.\n"+s),received(s){}};
struct Link {
 virtual ~Link(){};
 virtual void send(const std::string&)=0;
 virtual std::string wait(std::function<bool(const std::string&)>,unsigned quiet=250,unsigned timeout=12000)=0;
 virtual void pause(unsigned)=0;
 virtual std::string freshStatus()=0;
 virtual Clock now(bool,int ahead=0)=0;
 virtual double timestamp(const std::string&,const std::string&)=0;
};
inline std::string request(Link&l,const std::string&cmd,std::function<bool(const std::string&)>pred,unsigned quiet=250,unsigned timeout=12000){l.send(cmd);return l.wait(pred,quiet,timeout);}
inline void normalize(Link&l,const std::string&initial){
 std::string s=initial;
 if(mainMenu(s)){try{s=request(l,"G",mainMenu,1000);}catch(const Timeout&e){if(!e.received.empty())throw;s="- passive -";}}
 for(int attempt=0;attempt<12;++attempt){
  if(mainMenu(s)){l.pause(350);return;}
  if(has(s,"status/start/menu")||has(s,"measurement will start in 10 sec")||has(s,"instrument will go passive in 10 sec"))s=request(l,"S",[](const std::string&t){return has(t,"Press <M> for menu or wait 10sec")||(has(t,"current set up:")&&yn(t));},500);
  else if(has(s,"Press <M> for menu or wait 10sec"))s=request(l,"M",mainMenu,1000);
  else if(has(s,"hold")&&has(s,"<i>")||has(s,"- passive -")){
   auto ready=[](const std::string&t){return mainMenu(t)||has(t,"status/start/menu")||has(t,"instrument will go passive")||has(t,"Press <M> for menu or wait 10sec")||(has(t,"current set up:")&&yn(t));};
   bool received=false;for(int wake=0;wake<100;++wake){l.send("I");try{s=l.wait(ready,500,60);received=true;break;}catch(const Timeout&e){if(!e.received.empty()){s=l.wait(ready,500,12000);received=true;break;}}}if(!received)throw std::runtime_error("SD200 did not answer the bounded wake sequence. No setting was written.");
  } else if(has(s,"change:")&&yn(s))s=request(l,"N",[](const std::string&t){return mainMenu(t)||has(t,"<g>");},500);
  else s=request(l,"G",[](const std::string&t){return mainMenu(t)||(has(t,"change:")&&yn(t))||has(t,"status/start/menu")||has(t,"hold")||has(t,"<h>");},1000);
 }
 throw std::runtime_error("Could not confirm the SD200 main menu. Use Detect and try again.");
}
inline void setInterval(Link&l,int index,const std::string&context){
 if(index<0||index>=11)throw std::runtime_error("Invalid interval");const auto&v=intervals[index];normalize(l,context);
 request(l,"I",[](const std::string&s){return intervalValue(s)>0&&yn(s);},300);l.pause(300);
 auto menu=request(l,"Y",[](const std::string&s){return has(s,"select measuring interval:")&&advertised(s,intervals[10]);},500);
 std::string code(1,v.code);if(!advertised(menu,v))throw std::runtime_error("The requested interval was not found in the instrument menu. No interval was written.");
 l.pause(450);l.send(code);l.pause(120);request(l,"\r",mainMenu,500);l.pause(350);
 auto got=request(l,"I",[](const std::string&s){return intervalValue(s)>0&&yn(s);},300);bool match=intervalValue(got)==v.seconds;l.pause(250);request(l,"G",mainMenu,500);if(!match)throw std::runtime_error("SD200 interval readback does not match the requested value.");
}
inline void verifyClock(Link&l,const std::string&s,bool gmt,bool logger,double*offset=0){
 std::smatch m;std::string date,time,zone;
 if(logger){if(!std::regex_search(s,m,std::regex("Date/time:\\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\\s+([0-9]{2}:[0-9]{2}:[0-9]{2})\\s*\\(?(LT|GMT)",std::regex::icase)))throw std::runtime_error("Fresh logger status did not contain date, time and LT/GMT.");date=m[1];time=m[2];zone=m[3];}
 else {if(!std::regex_search(s,m,std::regex("Date\\s*[:=]?\\s*([0-9]{2})-([0-9]{2})-([0-9]{2})",std::regex::icase)))throw std::runtime_error("SD200 date readback missing");date="20"+m[1].str()+"-"+m[2].str()+"-"+m[3].str();if(!std::regex_search(s,m,std::regex("Time\\s*[:=]?\\s*([0-9]{2})[:-]([0-9]{2})[:-]([0-9]{2})\\s*\\(?(LT|GMT)",std::regex::icase)))throw std::runtime_error("SD200 time/zone readback missing");time=m[1].str()+":"+m[2].str()+":"+m[3].str();zone=m[4];}
 auto pc=l.now(gmt);double delta=pc.epoch-l.timestamp(date,time);if((lower(zone)=="gmt")!=gmt)throw std::runtime_error("Clock timezone readback does not match the selected LT/GMT.");if(offset)*offset=delta;
 if(std::abs(delta)>5)throw std::runtime_error("Clock readback differs from PC time (tolerance 5 seconds). Device: "+date+" "+time+" "+zone+"; PC: "+pc.date+" "+pc.time+"; difference: "+std::to_string(delta)+" seconds.");
}
inline void sdClock(Link&l,bool gmt,const std::string&context){
 normalize(l,context);int lead=0;for(int attempt=0;attempt<2;++attempt){request(l,"S",[](const std::string&s){return has(s,"change:")&&yn(s);},300);
 request(l,"Y",format,250);auto value=l.now(gmt,lead);if(value.date.substr(0,4)>"2079")throw std::runtime_error("SD200 requires a year through 2079");
 for(char ch:value.wire){auto echo=request(l,std::string(1,ch),[ch](const std::string&s){return s.find(ch)!=std::string::npos;},0,8000);l.pause(60);}
 auto prompt=request(l,"\r",[](const std::string&s){return yn(s)&&(has(s,"gmt")||has(s,"lt"));},300,8000);request(l,std::string(1,zoneAnswer(prompt,gmt)),mainMenu,500);
 auto status=request(l,"S",[](const std::string&s){return has(s,"change:")&&yn(s)&&has(s,"date");},300);double offset=NAN;std::exception_ptr failure;try{verifyClock(l,status,gmt,false,&offset);}catch(...){failure=std::current_exception();}request(l,"N",mainMenu,500);if(failure){if(attempt==0&&offset>5&&offset<=30){lead=int(std::ceil(offset));continue;}std::rethrow_exception(failure);}return;}
}
inline std::string stopSurface(Link&l){auto s=l.freshStatus();if(!has(s,"saiv110"))throw std::runtime_error("The connected unit no longer identifies as SAIV110");if(running(s))s=request(l,"I",stopped,500);if(!stopped(s))throw std::runtime_error("Surface stopped state could not be confirmed. No settings were sent.");return s;}
inline void loggerClock(Link&l,Kind kind,bool gmt){
 request(l,"X",format,100,8000);auto value=l.now(gmt);auto prompt=request(l,value.wire+"\r",[](const std::string&s){return yn(s)&&has(s,"timezone");},100,8000);
 request(l,std::string(1,zoneAnswer(prompt,gmt)),[](const std::string&s){return has(s,"OK: logger clock")||has(s,"<ESC> Menu:")||has(s,"<G> for Menu")||has(s,"Hold I to wake instrument");},250,8000);
 auto status=l.freshStatus();if(!has(status,kind==Surface?"saiv110":"osu107"))throw std::runtime_error("Logger identity changed during clock verification");verifyClock(l,status,gmt,true);
}
inline std::string replaceSurfaceInterval(const std::string&raw,int seconds){
 if(seconds<1||seconds>86400)throw std::runtime_error("Surface interval must be 1-86400 seconds");
 std::string out,section;bool found=false,enabled=false,other=false;size_t pos=0;int sectionCount=0;
 while(pos<raw.size()){auto end=raw.find('\n',pos);if(end==std::string::npos)end=raw.size();else ++end;auto line=raw.substr(pos,end-pos);auto body=line.substr(0,line.find_first_of("\r\n"));std::smatch m;
 if(std::regex_search(body,m,std::regex("^\\s*\\[([A-Za-z0-9_. -]+)\\]"))){section=lower(m[1]);if(section=="surface")++sectionCount;}
 if(std::regex_search(body,m,std::regex("^([ \\t]*)([A-Za-z0-9_]+)([ \\t]*=[ \\t]*)([^;#\\r\\n]*)(.*)$"))){auto key=lower(m[2]);if(key=="enable"){if(section=="surface")enabled=std::stoi(m[4])==1;if(section=="instrument0")other=std::stoi(m[4])!=0;}
 if(section=="surface"&&key=="intervalseconds"){if(found)throw std::runtime_error("Duplicate surface intervalSeconds");found=true;auto start=size_t(m.position(4));auto value=m[4].str();auto stop=value.find_last_not_of(" \t");if(stop==std::string::npos)throw std::runtime_error("Empty surface intervalSeconds");line.replace(start,stop+1,std::to_string(seconds));}}
 out+=line;pos=end;
 }
 if(sectionCount!=1||!enabled||other||!found)throw std::runtime_error("system.ini must already be Surface-only, with one [surface].intervalSeconds. No mode change will be made.");return out;
}
}
#endif
