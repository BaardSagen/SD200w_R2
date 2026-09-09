#include "../sit_import/native_data.h"
#include <fstream>
#include <iostream>
int checks=0,calls=0;
#define CHECK(x) do{++checks;if(!(x))throw std::runtime_error(#x);}while(0)
double formula(int id,double,double,double){++calls;return id==0?35:1500;}
int main(){try{
 for(auto file:{"2026_09_03_20-28-52_C.txt","2026_09_07_19-34-42_C.txt","2026_09_03_20-28-52_C_merged-3.txt"}){
  std::ifstream in(std::string("analysis/reference/import137_inputs/")+file,std::ios::binary);std::string raw((std::istreambuf_iterator<char>(in)),{});sit::Data d;CHECK(sitnative::parse(raw,d));auto f=sitnative::project(d,raw,formula);CHECK(f.sd.size()==52+52*d.rows.size());CHECK(f.rf.size()==72);CHECK(f.sf.substr(f.sf.find('\n')+1)==raw);CHECK(f.sf.find(sitnative::hexhash(f.sd))!=std::string::npos);sit::Data round;CHECK(sitnative::parse(f.sf.substr(f.sf.find('\n')+1),round));CHECK(round.fields==d.fields&&round.rows==d.rows);
  int da=sit::index(d,"DATE"),ti=sit::index(d,"TIME");for(size_t r=0;r<d.rows.size();++r){auto&t=d.rows[r];CHECK(uint8_t(f.sd[52+r*52+5])==std::stoi(t[ti].substr(6,2)));}
 }
 sit::Data d;CHECK(sitnative::parse("FIELDS: COUNT;T_degF;S_from_C;P;Sound_velocity_SIT_m_s;M1_PAR;M1_DATE;M1_TIME;M1_separator;DATE;TIME\n1;50;34;10;1490;2;2026-09-09;12:00:00.5;-;2026-09-09;12:00:00.5\n2;;34;10;1491;;;;-;2026-09-09;12:00:02.125",d));int before=calls;auto f=sitnative::project(d,"original",formula);CHECK(calls==before);double t;std::memcpy(&t,f.sd.data()+52+28,8);CHECK(t==10);std::memcpy(&t,f.sd.data()+104+28,8);CHECK(t==-999);CHECK(sit::index(d,"M1_Par")>=0);CHECK(sitnative::timestamp("2026-09-09","12:00:02.125")-sitnative::timestamp("2026-09-09","12:00:00.5")==1.625);
 for(auto bad:{"FIELDS: DATE;TIME;PAR;Par\n2026-09-09;12:00:00;1;2", "FIELDS: DATE;TIME;M1_separator\n2026-09-09;12:00:00;bad", "FIELDS: DATE;TIME;T\n2026-09-09;12:00:00;", "FIELDS: DATE;TIME\n2026-02-30;12:00:00"}){try{sit::Data v;if(sitnative::parse(bad,v)){if(v.fields.size()==3&&v.fields[2]=="T")continue;throw std::logic_error("expected rejection");}}catch(const std::logic_error&){throw;}catch(const std::exception&){++checks;}}
 std::cout<<"PASS "<<checks<<" native records, raw preservation, merged aliases, fractions, missing values and no double conversion\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
