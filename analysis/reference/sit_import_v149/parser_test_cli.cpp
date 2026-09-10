#include "logger.h"
#include <fstream>
#include <iostream>
#include <io.h>
#include <fcntl.h>
static double unused(int,double,double,double){throw std::runtime_error("Native CTD callback must be tested inside SIT");}
int main(int argc,char**argv){try{_setmode(1,_O_BINARY);if(argc<2)return 3;std::ifstream f(argv[1],std::ios::binary);std::string s((std::istreambuf_iterator<char>(f)),{});sit::Data d;if(!sit::parse(s,d)){std::cout<<"LEGACY";return 0;}if(argc>2){sit::Choices o;o.oxygen=3;o.suppliedT=o.suppliedS=true;o.temperature=10;o.salinity=35;o.air=1013.25;sit::calculate(d,o,unused);}std::cout<<sit::output(d);return 0;}catch(const std::exception&e){std::cerr<<e.what();return 2;}}
