#include "../sit_import/merge.h"
#include <fstream>
#include <iostream>
static std::string read(const char*p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("Cannot read fixture");return std::string(std::istreambuf_iterator<char>(f),{});}
int main(int argc,char**argv){try{if(argc<4)return 2;auto a=sitmerge::parse(read(argv[1]),argv[1]),b=sitmerge::parse(read(argv[2]),argv[2]);auto tol=sitmerge::tolerance(argv[3]);auto m=sitmerge::match(sitmerge::times(a),sitmerge::times(b),tol);std::cout<<m.count<<" "<<m.maxDelta<<"\n";for(auto i:m.row)std::cout<<i<<" ";std::cout<<"\n";if(argc>4){std::vector<sit::Data> others={b};if(argc>6)others.push_back(sitmerge::parse(read(argv[6]),argv[6]));auto d=sitmerge::merge(a,others,tol,argc>5&&std::string(argv[5])=="1");std::ofstream f(argv[4],std::ios::binary);f<<sitmerge::output(d);}return 0;}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
