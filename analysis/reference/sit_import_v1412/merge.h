#ifndef SIT_MERGE_H
#define SIT_MERGE_H
#include "logger.h"
#include <cstdint>
namespace sitmerge {
using sit::string;
using sit::Data;
inline string upper(string s){for(char&c:s)if(c>='a'&&c<='z')c-=32;return s;}
// Integer microseconds keep inclusive tolerance boundaries exact across calendar dates.
inline long long ticks(const string&date,const string&time){
 long long t=sit::stamp(date,time)*1000000;size_t dot=time.find('.');if(dot==string::npos)return t;
 string f=time.substr(dot+1);if(f.size()>6){if(f.substr(6).find_first_not_of('0')!=string::npos)throw std::runtime_error("Time precision greater than one microsecond is not supported");f.resize(6);}f.append(6-f.size(),'0');return t+std::atoll(f.c_str());
}
inline long long tolerance(string s){std::replace(s.begin(),s.end(),',','.');double v=sit::number(sit::trim(s));if(v<0||v>10)throw std::runtime_error("Tolerance must be from 0.0 to 10.0 seconds");return std::llround(v*1000000);}
inline std::vector<string> csv(const string&line,char sep){
 std::vector<string> out;string cell;bool quoted=false,closed=false;
 for(size_t i=0;i<line.size();++i){char c=line[i];if(quoted){if(c=='"'){if(i+1<line.size()&&line[i+1]=='"'){cell+='"';++i;}else {quoted=false;closed=true;}}else cell+=c;}
 else if(c==sep){out.push_back(closed?cell:sit::trim(cell));cell.clear();closed=false;}
 else if(c=='"'&&sit::trim(cell).empty()&&!closed){cell.clear();quoted=true;}
 else if(closed){if(c!=' '&&c!='\t')throw std::runtime_error("Unexpected text after quoted CSV cell");}
 else cell+=c;}
 if(quoted)throw std::runtime_error("Multiline or unclosed quoted CSV cells are not supported");out.push_back(closed?cell:sit::trim(cell));return out;
}
inline std::pair<int,int> dateColumns(const Data&d){int da=-1,ti=-1;for(size_t i=0;i<d.fields.size();++i){string f=upper(sit::trim(d.fields[i]));if(f=="DATE"||f=="DATO")da=int(i);if(f=="TIME"||f=="TID")ti=int(i);}return {da,ti};}
inline void validate(Data&d){
 if(d.fields.empty()||d.fields.size()>400||d.rows.empty()||d.rows.size()>200000)throw std::runtime_error("Merge needs 1-400 fields and 1-200000 rows");
 std::set<string> seen;for(auto&f:d.fields)if(f.empty()||!seen.insert(f).second)throw std::runtime_error("Empty or duplicate field: "+f);
 auto c=dateColumns(d);if(c.first<0||c.second<0)throw std::runtime_error("Separate DATE and TIME columns are required (YYYY-MM-DD and HH:MM:SS[.fraction])");
 for(size_t i=0;i<d.rows.size();++i){auto&r=d.rows[i];if(r.size()!=d.fields.size())throw std::runtime_error("Row "+std::to_string(i+1)+": field count differs from header");try{ticks(r[c.first],r[c.second]);}catch(const std::exception&e){throw std::runtime_error("Row "+std::to_string(i+1)+": "+e.what());}}
}
inline Data parse(string text,const string&source){
 if(text.size()>20*1024*1024)throw std::runtime_error("Merge supports files up to 20 MB each");if(text.compare(0,3,"\xef\xbb\xbf")==0)text.erase(0,3);
 std::replace(text.begin(),text.end(),'\r','\n');auto lines=sit::split(text,'\n');Data d;d.source=source;bool header=false;char sep=';';
 for(auto&line:lines){if(line.empty())continue;if(!header){string h=line;if(h.compare(0,7,"FIELDS:")==0)h=sit::trim(h.substr(7));
   for(char s:{';',',','\t'}){Data probe;try{probe.fields=csv(h,s);}catch(const std::exception&){continue;}auto c=dateColumns(probe);if(c.first>=0&&c.second>=0){d.fields=probe.fields;sep=s;header=true;break;}}
   if(!header)d.metadata.push_back(line);
  }else if(line[0]=='#')d.metadata.push_back(line);else if(line!="End of data")d.rows.push_back(csv(line,sep));}
 if(!header){Data full;full.source=source;if(!sit::parse(text,full))throw std::runtime_error("No DATE/TIME header found");if(full.estimatedTime)throw std::runtime_error("Merge requires explicit row timestamps, not reconstructed times");d=std::move(full);}
 sitmerge::validate(d);return d;
}
struct Times {std::vector<std::pair<long long,size_t>> sorted;std::vector<long long> original;};
inline Times times(const Data&d){Times t;auto c=dateColumns(d);for(size_t i=0;i<d.rows.size();++i){long long v=ticks(d.rows[i][c.first],d.rows[i][c.second]);t.original.push_back(v);t.sorted.push_back({v,i});}std::sort(t.sorted.begin(),t.sorted.end());return t;}
struct Match {std::vector<int> row;size_t count=0;long long maxDelta=0;};
inline Match match(const Times&master,const Times&other,long long tol){
 if(tol<0||tol>10000000)throw std::runtime_error("Tolerance outside 0-10 seconds");Match m;
 for(long long t:master.original){auto i=std::lower_bound(other.sorted.begin(),other.sorted.end(),std::make_pair(t,size_t(0)));int best=-1;long long delta=tol+1;
  auto consider=[&](std::pair<long long,size_t> x){long long v=std::llabs(x.first-t);if(v<=tol&&(v<delta||(v==delta&&(best<0||x.first<other.original[best]||(x.first==other.original[best]&&x.second<size_t(best)))))){best=int(x.second);delta=v;}};
  if(i!=other.sorted.end())consider(*i);if(i!=other.sorted.begin()){long long before=(i-1)->first;consider(*std::lower_bound(other.sorted.begin(),other.sorted.end(),std::make_pair(before,size_t(0))));}
  m.row.push_back(best);if(best>=0){++m.count;m.maxDelta=std::max(m.maxDelta,delta);}}
 return m;
}
inline string quote(const string&s){if(s.find_first_of(";\"\r\n")==string::npos)return s;string o="\"";for(char c:s){o+=c;if(c=='"')o+=c;}return o+'"';}
// Keep source headers in a single spreadsheet column.
inline string headerText(string s){std::replace(s.begin(),s.end(),';',',');return s;}
inline bool fixtureNote(const string&s){string t=upper(sit::trim(s));if(t.compare(0,1,"#")==0)t=sit::trim(t.substr(1));return t=="SYNTHETIC TEST DATA - NOT REAL MEASUREMENTS"||(t.compare(0,9,"BASED ON ")==0&&t.find("GENERATED FOR OSU107 TIMESTAMP MATCHING")!=string::npos);}
inline Data merge(const Data&master,const std::vector<Data>&others,long long tol,bool separator,bool includeDateTime=true){
 if(others.empty()||others.size()>2)throw std::runtime_error("Select one or two additional files");
 Data out=master;Times mt=times(master);out.metadata.clear();
 out.metadata.push_back("# SAIV IT merged data 1.4.3 - tolerance "+sit::fmt(tol/1000000.)+" seconds ("+(includeDateTime?string("merged file date/time retained"):string("removed merged file date/time"))+")");
 for(auto&meta:master.metadata)if(!fixtureNote(meta))out.metadata.push_back(meta);
 out.metadata.push_back("# Master source: "+master.source);
 for(size_t f=0;f<others.size();++f){const Data&d=others[f];Times ot=times(d);Match m=match(mt,ot,tol);if(!m.count)throw std::runtime_error("Selected file has no matches: "+d.source);string prefix="M"+std::to_string(f+1)+"_";
  out.metadata[0]+=" - M"+std::to_string(f+1)+" matches "+std::to_string(m.count)+"/"+std::to_string(master.rows.size());
  auto addField=[&](const string&name){string unique=name;int n=2;while(sit::index(out,unique)>=0)unique=name+"_"+std::to_string(n++);out.fields.push_back(unique);};
  auto dc=dateColumns(d);std::vector<size_t> columns;for(size_t c=0;c<d.fields.size();++c)if(includeDateTime||(int(c)!=dc.first&&int(c)!=dc.second))columns.push_back(c);
  if(separator)addField(prefix+"separator");for(size_t c:columns)addField(prefix+d.fields[c]);addField(prefix+"Delta_seconds");
  for(auto&meta:d.metadata)if(!fixtureNote(meta))out.metadata.push_back("# "+prefix+"header: "+meta);
  out.metadata.push_back("# "+prefix+"source: "+d.source);
  for(size_t r=0;r<out.rows.size();++r){auto&dest=out.rows[r];int j=m.row[r];if(separator)dest.push_back("-");if(j<0)dest.insert(dest.end(),columns.size()+1,"");else{for(size_t c:columns)dest.push_back(d.rows[j][c]);dest.push_back(sit::fmt((ot.original[j]-mt.original[r])/1000000.));}}
 }
 return out;
}
inline string output(const Data&d){std::ostringstream o;o<<"\xef\xbb\xbf";for(auto&m:d.metadata)o<<(m.compare(0,1,"#")==0?"":"# ")<<headerText(m)<<"\r\n";o<<"FIELDS: ";for(size_t i=0;i<d.fields.size();++i)o<<(i?";":"")<<quote(d.fields[i]);o<<"\r\n";for(auto&r:d.rows){for(size_t i=0;i<r.size();++i)o<<(i?";":"")<<quote(r[i]);o<<"\r\n";}return o.str();}
inline uint64_t fingerprint(const string&s){uint64_t h=14695981039346656037ULL;for(unsigned char c:s){h^=c;h*=1099511628211ULL;}return h;}
}
#endif
