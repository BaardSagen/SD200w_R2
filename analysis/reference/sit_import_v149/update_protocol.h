#ifndef SIT_UPDATE_PROTOCOL_H
#define SIT_UPDATE_PROTOCOL_H
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <cctype>
#include <algorithm>
namespace situpdate {
inline std::vector<unsigned> version(const std::string&s){
 std::vector<unsigned> v;unsigned n=0,digits=0;
 for(size_t i=0;i<=s.size();++i){char c=i<s.size()?s[i]:'.';if(c=='.'){if(!digits||v.size()==4)throw std::runtime_error("Invalid software version");v.push_back(n);n=digits=0;}else{if(c<'0'||c>'9'||++digits>5)throw std::runtime_error("Invalid software version");n=n*10+c-'0';if(n>65535)throw std::runtime_error("Invalid software version");}}
 if(v.size()<3)throw std::runtime_error("Invalid software version");v.resize(4);return v;
}
inline bool newer(const std::string&a,const std::string&b){return version(a)>version(b);}
inline bool url(const std::string&s,const std::string&extension){
 const std::string prefix="https://saiv.no/software/";
 if(s.size()>2048||s.compare(0,prefix.size(),prefix)||s.size()<=prefix.size()+extension.size()||s.substr(s.size()-extension.size())!=extension)return false;
 auto path=s.substr(prefix.size());if(path.find("..")!=std::string::npos)return false;
 for(unsigned char c:path)if(!std::isalnum(c)&&c!='_'&&c!='-'&&c!='.'&&c!='/')return false;
 return true;
}
// The public manifest is a flat JSON object containing string values.
struct Json {
 const std::string&s;size_t p=0;
 explicit Json(const std::string&v):s(v){if(s.compare(0,3,"\xef\xbb\xbf")==0)p=3;}
 void space(){while(p<s.size()&&(s[p]==' '||s[p]=='\r'||s[p]=='\n'||s[p]=='\t'))++p;}
 void expect(char c){space();if(p>=s.size()||s[p++]!=c)throw std::runtime_error("Invalid update manifest JSON");}
 unsigned hex(){unsigned n=0;for(int i=0;i<4;++i){if(p>=s.size())throw std::runtime_error("Invalid JSON escape");char c=s[p++];unsigned d=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:16;if(d==16)throw std::runtime_error("Invalid JSON escape");n=n*16+d;}return n;}
 std::string string(){expect('"');std::string v;while(p<s.size()){unsigned char c=s[p++];if(c=='"')return v;if(c<32)throw std::runtime_error("Invalid JSON string");if(c!='\\'){v+=c;continue;}if(p==s.size())break;c=s[p++];switch(c){case '"':case '\\':case '/':v+=c;break;case 'b':v+='\b';break;case 'f':v+='\f';break;case 'n':v+='\n';break;case 'r':v+='\r';break;case 't':v+='\t';break;case 'u':{unsigned n=hex();if(n>=0xd800&&n<=0xdfff)throw std::runtime_error("Unsupported JSON surrogate");if(n<128)v+=char(n);else if(n<2048){v+=char(0xc0|(n>>6));v+=char(0x80|(n&63));}else{v+=char(0xe0|(n>>12));v+=char(0x80|((n>>6)&63));v+=char(0x80|(n&63));}break;}default:throw std::runtime_error("Invalid JSON escape");}}throw std::runtime_error("Unterminated JSON string");}
 std::map<std::string,std::string> object(){std::map<std::string,std::string> out;expect('{');space();if(p<s.size()&&s[p]=='}')++p;else for(;;){auto key=string();expect(':');auto value=string();if(!out.emplace(key,value).second)throw std::runtime_error("Duplicate manifest key");space();if(p<s.size()&&s[p]=='}'){++p;break;}expect(',');}space();if(p!=s.size())throw std::runtime_error("Unexpected manifest data");return out;}
};
struct Manifest {std::string release,download,readme,sha256;};
inline Manifest parse(const std::string&s){
 if(s.empty()||s.size()>65536)throw std::runtime_error("Invalid update manifest size");auto m=Json(s).object();Manifest r{m["version"],m["url"],m["readme_url"],m["sha256"]};version(r.release);
 if(!url(r.download,".zip"))throw std::runtime_error("Invalid SAIV download link");
 if(!r.readme.empty()&&!url(r.readme,".txt"))throw std::runtime_error("Invalid SAIV release notes link");
 if(!r.sha256.empty()){if(r.sha256.size()!=64)throw std::runtime_error("Invalid ZIP checksum");for(unsigned char c:r.sha256)if(!std::isxdigit(c))throw std::runtime_error("Invalid ZIP checksum");}return r;
}
}
#endif
