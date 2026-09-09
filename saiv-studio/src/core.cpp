#include "core.hpp"
#include "gswteos-10.h"
#include <algorithm>
#include <cmath>
#include <sstream>
#include <iomanip>
#include <regex>
#include <stdexcept>
#include <cstdlib>
#include <cctype>
namespace saiv {

std::string trim(std::string s) { auto a=s.find_first_not_of(" \t\r\n"); if(a==std::string::npos)return {};return s.substr(a,s.find_last_not_of(" \t\r\n")-a+1); }
std::string lower(std::string s) {for(char& c:s)c=static_cast<char>(std::tolower(static_cast<unsigned char>(c)));return s;}
double number(std::string s) {
 s=trim(s); if(s.empty())return missing;
 if(s.find(',')!=std::string::npos && s.find('.')==std::string::npos)std::replace(s.begin(),s.end(),',','.');
 char* end=nullptr;double x=std::strtod(s.c_str(),&end);
 if(end==s.c_str()||*end||!std::isfinite(x)||std::abs(x)>=1e10||x==-999||x==-9999)return missing;
 return x;
}
std::string format(double x){if(!std::isfinite(x)||std::abs(x)>=1e10)return "";std::ostringstream o;o<<std::setprecision(10)<<x;return o.str();}
std::vector<std::string> splitRecord(const std::string& s,char delimiter){
 std::vector<std::string> out;std::string cell;bool quoted=false;
 for(size_t i=0;i<s.size();i++){char ch=s[i];if(ch=='"'){if(quoted&&i+1<s.size()&&s[i+1]=='"'){cell+='"';i++;}else quoted=!quoted;}
 else if(ch==delimiter&&!quoted){out.push_back(trim(cell));cell.clear();}else cell+=ch;}
 out.push_back(trim(cell));return out;
}
std::string csvQuote(const std::string& s){if(s.find_first_of(";\"\r\n")==std::string::npos)return s;std::string v="\"";for(char c:s){v+=c;if(c=='"')v+='"';}return v+'"';}
int Table::column(const std::string& name)const{for(size_t i=0;i<columns.size();i++)if(columns[i]==name)return static_cast<int>(i);if(name.size()>1)for(size_t i=0;i<columns.size();i++)if(lower(columns[i])==lower(name))return static_cast<int>(i);return -1;}
double Table::value(size_t row,int col)const{if(row>=rows.size()||col<0||static_cast<size_t>(col)>=rows[row].size())return missing;return number(rows[row][col]);}
void Table::append(const std::map<std::string,std::string>& values){
 if(rows.size()>=1000000){++rejected;return;}
 for(auto& p:values)if(std::find(columns.begin(),columns.end(),p.first)==columns.end()){if(columns.size()>=128){++rejected;return;}columns.push_back(p.first);for(auto& r:rows)r.resize(columns.size());}
 std::vector<std::string> row(columns.size());for(auto& p:values)row[column(p.first)]=p.second;rows.push_back(std::move(row));
}
std::string Table::csv()const{std::ostringstream o;for(auto& note:notes)o<<"# "<<note<<"\n";for(size_t i=0;i<columns.size();i++){if(i)o<<';';o<<csvQuote(columns[i]);}o<<'\n';
 for(auto& row:rows){for(size_t i=0;i<columns.size();i++){if(i)o<<';';if(i<row.size())o<<csvQuote(row[i]);}o<<'\n';}return o.str();}
static char delimiter(const std::string& s){if(s.find(';')!=std::string::npos)return ';';if(s.find('\t')!=std::string::npos)return '\t';return ',';}
void Decoder::reset(){partial_.clear();schema_.clear();table={};previousCR_=false;}
void Decoder::feed(const std::string& data){for(char c:data){if(c=='\r'||c=='\n'){if(c=='\n'&&previousCR_){previousCR_=false;continue;}line(std::move(partial_));partial_.clear();previousCR_=c=='\r';}else{previousCR_=false;if(partial_.size()<65536)partial_+=c;else {partial_.clear();++table.rejected;}}}}
void Decoder::finish(){if(!partial_.empty()){line(std::move(partial_));partial_.clear();}}
void Decoder::line(std::string text){
 text=trim(text);if(text.empty())return;
 if(text.size()>=3&&static_cast<unsigned char>(text[0])==0xef&&static_cast<unsigned char>(text[1])==0xbb&&static_cast<unsigned char>(text[2])==0xbf)text.erase(0,3);
 if(text.empty())return;
 auto l=lower(text);
 if(l.rfind("fields:",0)==0){separator_=delimiter(text);schema_=splitRecord(text.substr(7),separator_);return;}
 // Documented full/live rows: N00001 S... T... P..., with configurable ADC keys.
 static const std::regex start(R"(^[NS][0-9]+(?:\s|$))");
 if(std::regex_search(text,start)){
  std::istringstream stream(text);std::string token;stream>>token;std::map<std::string,std::string> vals;vals["COUNT"]=token.substr(1);
  static const std::regex field(R"(^([A-Za-z][A-Za-z_]*?)(?:=)?([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?|nan)(.*)$)",std::regex::icase);
  while(stream>>token){std::smatch m;if(std::regex_match(token,m,field)){vals[m[1].str()]=lower(m[2].str())=="nan"?"":m[2].str();}
   else if(token.size()>=8&&token[2]==':'&&token[5]==':')vals["TIME"]=token;}
  if(vals.size()>1){table.append(vals);return;}
 }
 if(text.find_first_of(";\t,")!=std::string::npos){
  char sep=schema_.empty()?delimiter(text):separator_;auto cells=splitRecord(text,sep);
  // Header detection excludes numeric metadata and does not assume sensor order.
  bool hasHeader=false;for(auto& c:cells){auto h=lower(c);if(h=="count"||h=="meas"||h=="temp"||h=="temperature"||h=="date"||h=="timestamp"||h=="pressure"||h=="c"||h=="t"||h=="p")hasHeader=true;}
  if(hasHeader&&!std::isfinite(number(cells[0]))){schema_=cells;separator_=sep;return;}
  if(!schema_.empty()&&cells.size()==schema_.size()){
   bool numeric=false;for(auto& c:cells)if(std::isfinite(number(c)))numeric=true;
   if(numeric){std::map<std::string,std::string> vals;for(size_t i=0;i<cells.size();i++){auto key=schema_[i].empty()?"Column "+std::to_string(i+1):schema_[i];if(vals.count(key))key+="_"+std::to_string(i+1);vals[key]=cells[i];}table.append(vals);return;}
  }
  if(!schema_.empty()&&std::isfinite(number(cells[0]))){++table.rejected;return;}
 }
 if(table.notes.size()<200)table.notes.push_back(text);
}
Table loadText(const std::string& text,const std::string& source){Decoder d;d.feed(text);d.finish();d.table.source=source;return std::move(d.table);}
Statistics statistics(const Table& t,int c,size_t first,size_t last){Statistics s;double sum=0,m2=0;last=std::min(last,t.rows.size());for(size_t i=first;i<last;i++){double v=t.value(i,c);if(!std::isfinite(v)){s.invalid++;continue;}if(!s.valid){s.min=s.max=v;}s.min=std::min(s.min,v);s.max=std::max(s.max,v);s.valid++;double delta=v-sum;sum+=delta/s.valid;m2+=delta*(v-sum);}if(s.valid){s.mean=sum;s.sd=std::sqrt(m2/s.valid);}return s;}
Table rangeRows(const Table& t,size_t first,size_t last){Table out=t;out.rows.clear();first=std::min(first,t.rows.size());last=std::min(last,t.rows.size());if(first<last)out.rows.assign(t.rows.begin()+first,t.rows.begin()+last);out.notes.push_back("Selected original rows "+std::to_string(first+1)+" to "+std::to_string(last));return out;}
Table filterRange(const Table& t,int col,double minimum,double maximum){Table out=t;out.rows.clear();for(size_t i=0;i<t.rows.size();i++){double v=t.value(i,col);if(std::isfinite(v)&&v>=minimum&&v<=maximum)out.rows.push_back(t.rows[i]);}out.notes.push_back("Filtered "+(col>=0?t.columns[col]:"invalid column")+" to ["+format(minimum)+", "+format(maximum)+"]");return out;}
Table affine(const Table& t,int c,double gain,double offset){if(c<0||c>=static_cast<int>(t.columns.size()))throw std::runtime_error("Select a numeric column.");Table out=t;std::string label=t.columns[c]+" adjusted";out.columns.push_back(label);for(size_t i=0;i<out.rows.size();i++)out.rows[i].push_back(format(t.value(i,c)*gain+offset));out.notes.push_back(label+" = original * "+format(gain)+" + "+format(offset));return out;}
Table despike(const Table& t,int c,int window,double threshold){if(c<0||c>=static_cast<int>(t.columns.size())||window<3||threshold<=0)throw std::runtime_error("Select a column, a window >= 3 and positive threshold.");Table out=t;out.columns.push_back(t.columns[c]+" despiked");for(size_t i=0;i<t.rows.size();i++){std::vector<double> values;size_t begin=i>static_cast<size_t>(window/2)?i-window/2:0,end=std::min(t.rows.size(),i+window/2+1);for(size_t j=begin;j<end;j++){double x=t.value(j,c);if(std::isfinite(x))values.push_back(x);}double v=t.value(i,c);if(values.size()>=3){std::sort(values.begin(),values.end());double median=values[values.size()/2];if(std::isfinite(v)&&std::abs(v-median)>threshold)v=missing;}out.rows[i].push_back(format(v));}out.notes.push_back("Despiked with centred running median; outliers blanked, original column preserved.");return out;}
Table standardDepths(const Table& t,int depth,double step,double maximumGap){
 if(depth<0||depth>=static_cast<int>(t.columns.size())||step<=0||maximumGap<=0)throw std::runtime_error("Select depth/pressure and positive interval / maximum gap.");
 std::vector<std::pair<double,size_t>> points;for(size_t i=0;i<t.rows.size();i++){double x=t.value(i,depth);if(std::isfinite(x))points.push_back({x,i});}
 if(points.size()<2)throw std::runtime_error("At least two valid depth values are needed.");
 // Require one monotonic cast; mixing up/down casts would silently alter profiles.
 int direction=0;for(size_t i=1;i<points.size();i++){double d=points[i].first-points[i-1].first;if(d==0)continue;int sign=d>0?1:-1;if(direction&&sign!=direction)throw std::runtime_error("Select a single monotonic downcast or upcast before interpolation.");direction=sign;}
 if(direction<0)std::reverse(points.begin(),points.end());
 Table out;out.columns=t.columns;out.source=t.source;out.notes=t.notes;out.notes.push_back("Standard levels: linear interpolation, no extrapolation; maximum gap "+format(maximumGap));
 double first=std::ceil(points.front().first/step)*step,last=points.back().first;
 if((last-first)/step>100000)throw std::runtime_error("Too many levels; increase interval.");
 size_t j=0;for(double level=first;level<=last+step*1e-8;level+=step){while(j+1<points.size()&&points[j+1].first<level)j++;if(j+1>=points.size())break;double a=points[j].first,b=points[j+1].first;std::vector<std::string> row(t.columns.size());row[depth]=format(level);for(size_t c=0;c<row.size();c++){if(static_cast<int>(c)==depth)continue;double x=t.value(points[j].second,static_cast<int>(c)),y=t.value(points[j+1].second,static_cast<int>(c));if(level==a)row[c]=format(x);else if(level==b)row[c]=format(y);else if(b>a&&b-a<=maximumGap&&std::isfinite(x)&&std::isfinite(y))row[c]=format(x+(y-x)*(level-a)/(b-a));}out.rows.push_back(std::move(row));}return out;
}
Table calculate(const Table& t,const CalculationOptions& o){
 if(o.temperature<0||o.pressure<0||(o.conductivity<0&&o.salinity<0))throw std::runtime_error("Select temperature, sea pressure, and conductivity or salinity.");
 if(!std::isfinite(o.latitude)||!std::isfinite(o.longitude)||std::abs(o.latitude)>90||o.longitude< -180||o.longitude>360)throw std::runtime_error("Invalid station coordinates.");
 Table out=t;const char* names[]={"SP (PSS-78)","SA (g/kg)","CT (deg C)","Density TEOS-10 (kg/m3)","Sigma0 TEOS-10 (kg/m3)","Sound TEOS-10 (m/s)","Depth TEOS-10 (m)","O2 saturation (umol/kg)","O2 derived (mg/L)"};for(auto n:names)out.columns.push_back(n);
 for(size_t i=0;i<t.rows.size();i++){
  double temp=t.value(i,o.temperature),p=t.value(i,o.pressure),sp=t.value(i,o.salinity),c=t.value(i,o.conductivity);
  std::vector<std::string> derived(9);
  if(o.temperature68)temp/=1.00024;
  bool valid=std::isfinite(temp)&&std::isfinite(p)&&temp>=-5&&temp<=45&&p>=0&&p<=12000;
  if(o.conductivity>=0){if(valid&&std::isfinite(c)&&c>=0&&c<=100)sp=gsw_sp_from_c(c,temp,p);else sp=missing;}
  if(valid&&std::isfinite(sp)&&sp>=0&&sp<=50){
   double sa=gsw_sa_from_sp(sp,p,o.longitude,o.latitude),ct=gsw_ct_from_t(sa,temp,p);
   if(std::isfinite(sa)&&sa<100&&std::isfinite(ct)&&std::abs(ct)<100){double rho=gsw_rho(sa,ct,p),o2=gsw_o2sol(sa,ct,p,o.longitude,o.latitude);derived={format(sp),format(sa),format(ct),format(rho),format(gsw_sigma0(sa,ct)),format(gsw_sound_speed(sa,ct,p)),format(-gsw_z_from_p(p,o.latitude,0,0)),format(o2),""};double percent=t.value(i,o.oxygen);if(std::isfinite(percent)&&percent>=0&&percent<=300)derived[8]=format(o2*(percent/100.0)*0.031998*(rho/1000.0));}
  }
  out.rows[i].insert(out.rows[i].end(),derived.begin(),derived.end());
 }
 out.notes.push_back("GSW TEOS-10; input temperature "+std::string(o.temperature68?"IPTS-68 converted to ITS-90":"ITS-90")+"; sea pressure dbar; conductivity mS/cm; station lon="+format(o.longitude)+", lat="+format(o.latitude));
 out.notes.push_back("O2 uses equilibrium with standard air pressure (101325 Pa), not a barometric correction. Missing/invalid input remains blank. Original columns preserved.");return out;
}
Table demoProfile(){Table t;t.source="Demonstration / synthetic cast";t.columns={"COUNT","T","C","S","P","OX","TIME"};for(int i=0;i<240;i++){double p=i*.35,temp=14-6*(1-std::exp(-p/30)),sp=24+10*(1-std::exp(-p/20));t.rows.push_back({std::to_string(i+1),format(temp),format(gsw_c_from_sp(sp,temp,p)),format(sp),format(p),format(99-65*(1-std::exp(-p/45))),"12:"+std::string(i/60<10?"0":"")+std::to_string(i/60)+":"+(i%60<10?"0":"")+std::to_string(i%60)});}t.notes={"SYNTHETIC DEMONSTRATION DATA - not instrument measurements."};return t;}
Identity identify(const std::string& s){Identity id;std::smatch m;static const std::regex logger(R"((OSU107|OSU017|SAIV110)\s+(?:(?:Instrument|Surface)\s+logger\s+)?SN\s*([A-Za-z0-9-]+)(?:,?\s*Ver:\s*([^\s\r\n]+))?)",std::regex::icase);if(std::regex_search(s,m,logger)){id.model=m[1];id.serial=m[2];id.firmware=m[3];id.logger=true;id.surface=lower(id.model)=="saiv110";return id;}
 static const std::regex legacy(R"((SD20[048]|TD30[134]|STDOX[A-Z]*|STD[A-Z]*)[^\r\n]{0,60}(?:Ser\s*No\.?|S/N|SN)\s*([0-9]+))",std::regex::icase);if(std::regex_search(s,m,legacy)){id.model=m[1];id.serial=m[2];}return id;}

static Protocol::Menu classifyMenu(const std::string& text){
 auto s=lower(text);
 if(s.find("saiv110")!=std::string::npos&&(s.find("<i> for stop")!=std::string::npos||s.find("<i> for start")!=std::string::npos))return Protocol::Menu::Surface;
 // Recognise complete menu endings, not an isolated <M> or <I> in a partial menu.
 if((s.find("start via key-board")!=std::string::npos&&s.find("exit (passive)")!=std::string::npos&&s.find("<h>")!=std::string::npos)||s.find("main menu: <f> dump <e> erase")!=std::string::npos)return Protocol::Menu::Main;
 if(s.find("status/start/menu")!=std::string::npos&&s.find("<s>")!=std::string::npos&&s.find("measurement will start in 10")!=std::string::npos)return Protocol::Menu::Startup;
 if(s.find("<m>")!=std::string::npos&&(s.find("start")!=std::string::npos&&s.find("<i>")!=std::string::npos)&&s.find("set coefficients")==std::string::npos&&s.find("measuring interval")==std::string::npos)return Protocol::Menu::Status;
 if(s.find("- passive -")!=std::string::npos||s.find("hold <i> to wake instrument")!=std::string::npos||s.find("hold <i> to activate")!=std::string::npos)return Protocol::Menu::Passive;
 if(s.find("type/hold <i> to stop")!=std::string::npos||std::regex_search(s,std::regex(R"((^|[\r\n])n[0-9]+[^\r\n]* t[-+0-9][^\r\n]* p[-+0-9])")))return Protocol::Menu::Measuring;
 if(s.find("menu:<g>")!=std::string::npos||s.find("coefficients")!=std::string::npos||s.find("interval")!=std::string::npos)return Protocol::Menu::Submenu;
 return Protocol::Menu::Unknown;
}
const char* Protocol::menuName()const{switch(menu){case Menu::Passive:return "Passive";case Menu::Startup:return "Startup menu (automatic start timer)";case Menu::Status:return "Status / start menu";case Menu::Main:return "Main menu";case Menu::Measuring:return "Measuring";case Menu::Submenu:return "Submenu / incomplete menu";case Menu::Surface:return "Surface logger";default:return "Listening / state unknown";}}
void Protocol::connected(){operation=Operation::Idle;menu=Menu::Unknown;status="Connected - listening";device={};buffer_.clear();pending_.clear();error.clear();mainMenu=passive=running=downloadComplete=false;lastRx_=opened_=0;wakeStage_=0;}
void Protocol::disconnected(){operation=Operation::Idle;menu=Menu::Unknown;status="Disconnected";mainMenu=false;buffer_.clear();pending_.clear();}
bool Protocol::wake(double now){if(operation!=Operation::Idle)return false;operation=Operation::Wake;wakeStage_=0;nextWake_=now;opened_=now;deadline_=now+20;error.clear();status="Identifying current CTD menu";return true;}
bool Protocol::typeCharacters(const std::string& text,double now){if(operation!=Operation::Idle){error="Wait for the current instrument operation.";return false;}if(pending_.size()+text.size()>4096){error="Terminal input queue is full.";return false;}pending_+=text;deadline_=now+10;return true;}
bool Protocol::manual(const std::string& command,double now){if(operation!=Operation::Idle||!pending_.empty()){error="Wait for the current operation before sending another command.";return false;}pending_=command;deadline_=now+10;return true;}
bool Protocol::receiveData(double now){if(operation!=Operation::Idle||!pending_.empty())return false;if(!mainMenu&&!device.logger){error="Open the instrument main menu first (Wake / menu).";return false;}operation=Operation::Download;deadline_=now+30;sentY_=false;requestSent_=false;downloadComplete=false;download.clear();pending_="F";error.clear();status=device.logger?"Requesting logger disk refresh":"Receiving instrument data";return true;}
void Protocol::cancel(){bool dump=operation==Operation::Download&&requestSent_&&!device.logger;operation=Operation::Idle;pending_=dump?"G":"";status="Operation cancelled; received data preserved";buffer_.clear();}
void Protocol::ingest(const std::string& text,double now){
 if(text.empty())return;lastRx_=now;buffer_+=text;if(buffer_.size()>16384)buffer_.erase(0,buffer_.size()-16384);
 auto id=identify(buffer_);if(!id.model.empty())device=id;
 if(operation==Operation::Download&&requestSent_){download+=text;deadline_=now+30;if(download.size()>64*1024*1024){error="Download exceeded 64 MiB; capture stopped.";cancel();}}
}
void Protocol::tick(double now){
 // Never send the next command while a response is arriving; wait >=250 ms
 // since the last received byte. This also applies to refresh acknowledgement.
 if((operation!=Operation::Idle||!pending_.empty())&&now>=deadline_){error=operation==Operation::Refresh?"Disk refresh was not confirmed. Check terminal.":"Operation timed out. Check terminal; partial data is preserved.";operation=Operation::Idle;pending_.clear();status="Timed out";return;}
 bool quiet=now-lastRx_>=.250;
 if(!quiet)return;
 auto low=lower(buffer_);auto detected=classifyMenu(buffer_);
 if(detected!=Menu::Unknown){menu=detected;mainMenu=menu==Menu::Main;passive=menu==Menu::Passive;running=menu==Menu::Measuring;}
 auto transmit=[&](const std::string& s){buffer_.clear();lastRx_=now;if(send)send(s);};
 if(!pending_.empty()){auto cmd=std::move(pending_);pending_.clear();if(operation==Operation::Download)requestSent_=true;transmit(cmd);return;}
 if(operation==Operation::Idle){if(!device.model.empty()&&status=="Connected - listening")status=device.model+" identified";return;}
 if(now>=deadline_){error=operation==Operation::Refresh?"Disk refresh was not confirmed. Check terminal.":"Operation timed out. Check terminal; partial data is preserved.";operation=Operation::Idle;status="Timed out";return;}
 if(operation==Operation::Wake){
  if(menu==Menu::Main){operation=Operation::Idle;status="Instrument main menu - ready";buffer_.clear();return;}
  if(detected==Menu::Startup){transmit("S");wakeStage_=2;menu=Menu::Unknown;status="Startup menu: requesting status";return;}
  if(detected==Menu::Status){transmit("M");wakeStage_=3;menu=Menu::Unknown;status="Status menu: requesting main menu";return;}
  if(detected==Menu::Submenu){status="Waiting for a complete menu; no I or M sent";return;}
  if(detected==Menu::Surface){operation=Operation::Idle;status="Surface logger ready; no CTD wake command sent";return;}
  if(detected==Menu::Measuring){operation=Operation::Idle;status="Instrument is measuring";error="Stop measurement explicitly before requesting a main menu.";return;}
  if(detected==Menu::Passive){wakeStage_=1;menu=Menu::Unknown;buffer_.clear();}
  if(wakeStage_==0&&now-opened_>=1.1){if(!buffer_.empty()){status="Waiting for a complete recognised menu";return;}transmit("G");wakeStage_=4;nextWake_=now+1.1;status="Checking for an already active menu";return;}
  if(wakeStage_==4&&now>=nextWake_){if(buffer_.empty()){wakeStage_=1;nextWake_=now;}else{error="Unrecognised response to G. No I or M sent; inspect the terminal.";operation=Operation::Idle;return;}}
  if(wakeStage_==1&&now>=nextWake_){if(!buffer_.empty()){status="Waiting for complete wake menu";return;}transmit("I");nextWake_=now+.3;return;}
 }
 if(operation==Operation::Download&&requestSent_){if(low.find("refresh disk y/n")!=std::string::npos&&!sentY_){sentY_=true;operation=Operation::Refresh;deadline_=now+8;status="Waiting for disk refresh confirmation";transmit("Y");return;}if(low.find("end of data.")!=std::string::npos){operation=Operation::Idle;downloadComplete=true;status="Download complete - save received data";buffer_.clear();}}
 else if(operation==Operation::Refresh){if(low.find("err: stop surface-logger")!=std::string::npos){error="Stop logging and wait for the current sample to finish. Then request Download again.";operation=Operation::Idle;status="Disk refresh blocked";buffer_.clear();}else if(low.find("system disk refresh will start in 3 seconds.")!=std::string::npos){operation=Operation::Idle;status="Disk refresh confirmed. Wait for the disk to reappear, then copy its files.";buffer_.clear();}}
}
}
