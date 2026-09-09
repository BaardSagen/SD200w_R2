#include "../sit_import/presets.h"
#include <iostream>
int checks=0;
#define CHECK(x) do{++checks;if(!(x))throw std::runtime_error(#x);}while(0)
double formula(int,double,double,double){throw std::runtime_error("Unexpected CTD formula");}
int main(){try{
 for(auto par:{"Par","PAR"})for(auto ox:{"OxR","OXR"}){
  std::string fields=std::string("FIELDS: T;S;")+par+";"+ox+";OX;DATE;TIME\n10;35;2;100;90;2026-09-09;12:00:00\n";
  sit::Data a,b;CHECK(sit::parse(fields,a));CHECK(sit::parse("FIELDS: T;S;Par;OxR;OX;DATE;TIME\n10;35;2;100;90;2026-09-09;12:00:00\n",b));CHECK(a.fields==b.fields&&a.rows==b.rows);CHECK(sitpreset::signature(a)==sitpreset::signature(b));
  sit::Choices o;o.par=1;o.parSource=2;o.oxygen=3;o.air=1013.25;sit::calculate(a,o,formula);sit::calculate(b,o,formula);CHECK(a.fields==b.fields&&a.rows==b.rows);CHECK(sit::val(a,0,"Par_umol_m2_s")==20000);CHECK(sit::val(a,0,"OX")==90);CHECK(sit::index(a,"OxR_mg_L")>=0);
  for(auto prefix:{std::string(""),std::string("N00001 ")}){sit::Data full;CHECK(sit::parse(prefix+par+"2 "+ox+"100 2026-09-09 12:00:00",full));CHECK(sit::val(full,0,"Par")==2&&sit::val(full,0,"OxR")==100);}
 }
 for(auto input:{"FIELDS: Par;PAR;DATE;TIME\n1;2;2026-09-09;12:00:00", "FIELDS: OxR;OXR;DATE;TIME\n1;2;2026-09-09;12:00:00", "Par1 PAR2 2026-09-09 12:00:00", "OxR1 OXR2 2026-09-09 12:00:00"}){bool rejected=false;try{sit::Data d;sit::parse(input,d);}catch(const std::exception&){rejected=true;}CHECK(rejected);}
 sit::Data legacy;CHECK(!sit::parse("STDOXOFOT Ser No 1237 AP0925.000\nN00001 S00.036 T+14.126 P0000.00 OX098.92 OF000.38 OT000.03",legacy));
 std::cout<<"PASS "<<checks<<" aliases, calculations, preset signatures, Full/ FIELDS and duplicates\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
