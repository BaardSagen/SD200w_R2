#ifndef SIT_LEGACY_CONVERT_H
#define SIT_LEGACY_CONVERT_H
#include "logger.h"
namespace sit {
// Convert-only adapter. The existing File > Import legacy dispatcher is unchanged.
inline bool parseConversion(const string&input,Data&d){
 if(parse(input,d))return true;
 std::smatch date,header;
 if(!std::regex_search(input,header,std::regex("(?:^|[\\r\\n])((?:CTD|STD|SD204|SD208)[^\\r\\n]*Ser No [0-9]+[^\\r\\n]*)")))return false;
 if(!std::regex_search(input,date,std::regex("Date ([0-9]{2})-([0-9]{2})-([0-9]{2}) Time ([0-9]{2})-([0-9]{2})-([0-9]{2})[^\\r\\n]*Interval: *([0-9]+)sec")))throw std::runtime_error("Legacy Convert requires an explicit Date/Time and whole-second Interval header");
 int yy=std::stoi(date[1]);string iso=std::to_string(yy>=80?1900+yy:2000+yy)+"-"+date[2].str()+"-"+date[3].str();
 string synthetic="SurfaceLogger\nDATE: "+iso+" TIME: "+date[4].str()+":"+date[5].str()+":"+date[6].str()+" INTERVAL_S: "+date[7].str()+"\n";
 Data converted;converted.source=d.source;
 if(!parse(synthetic+input,converted))return false;
 converted.metadata.erase(converted.metadata.begin(),converted.metadata.begin()+2);
 converted.metadata.push_back("# Legacy Convert: row timestamps reconstructed from declared Date/Time and Interval; measurement sequence order, not COUNT, sets elapsed time");
 converted.estimatedTime=true;d=std::move(converted);return true;
}
}
#endif
