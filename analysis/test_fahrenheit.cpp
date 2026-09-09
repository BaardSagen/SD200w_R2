#include "../sit_import/presets.h"
#include <iostream>
#include <tuple>
int checks=0;
#define CHECK(x) do{++checks;if(!(x))throw std::runtime_error(#x);}while(0)
std::vector<std::tuple<int,double,double,double>> calls;
double formula(int id,double a,double b,double c){calls.push_back(std::make_tuple(id,a,b,c));return id==0?35:id==1?1500:id==2?25:9.81;}
int main(){try{
 sit::Data t;t.fields={"COUNT","T","DATE","TIME"};t.rows={{"1","-40","2026-09-09","12:00:00"},{"2","0","2026-09-09","12:00:01"},{"3","100","2026-09-09","12:00:02"},{"4","23","2026-09-09","12:00:03"},{"5","","2026-09-09","12:00:04"}};
 sit::Choices o;o.fahrenheit=true;auto both=t;sit::calculate(both,o,formula);CHECK(sit::index(both,"T")>=0);CHECK(sit::index(both,"T_degF")>=0);
 const char* expected[]={"-40","32","212","73.4",""};for(size_t i=0;i<t.rows.size();++i){CHECK(both.rows[i][sit::index(both,"T_degF")]==expected[i]);CHECK(both.rows[i][sit::index(both,"T")]==t.rows[i][1]);}
 o.keepOriginal["T"]=false;auto only=t;sit::calculate(only,o,formula);CHECK(sit::index(only,"T")==-1);CHECK(sit::index(only,"T_degF")>=0);
 sit::Choices off;auto unchanged=t;sit::calculate(unchanged,off,formula);CHECK(unchanged.fields==t.fields&&unchanged.rows==t.rows);
 bool rejected=false;try{sit::calculate(both,o,formula);}catch(const std::exception&){rejected=true;}CHECK(rejected);
 sit::Data ctd;ctd.fields={"C","T","P","OxR","DATE","TIME"};ctd.rows={{"42.914","10","100","100","2026-09-09","12:00:00"}};ctd.air=1013.25;
 sit::Choices full;full.conductivity=full.depth=1;full.oxygen=3;auto celsius=ctd;sit::calculate(celsius,full,formula);auto originalCalls=calls;calls.clear();full.fahrenheit=true;full.keepOriginal["T"]=false;auto fahrenheit=ctd;sit::calculate(fahrenheit,full,formula);CHECK(calls==originalCalls);
 for(size_t i=0;i<celsius.fields.size();++i)if(celsius.fields[i]!="T")CHECK(celsius.rows[0][i]==fahrenheit.rows[0][sit::index(fahrenheit,celsius.fields[i])]);CHECK(fahrenheit.rows[0][sit::index(fahrenheit,"T_degF")]=="50");
 sitpreset::Record r;r.signature=sitpreset::signature(t);r.date="2026-09-09 12:00:00";r.source="test.txt";r.choices=full;auto bytes=sitpreset::encode(r);sitpreset::Record decoded;CHECK(sitpreset::decode(bytes,r.signature,decoded));CHECK(decoded.choices.fahrenheit);CHECK(sitpreset::reuse(decoded,t).fahrenheit);
 auto old=bytes;old.replace(old.find("SIT choices 2"),13,"SIT choices 1");old.resize(old.size()-4);CHECK(sitpreset::decode(old,r.signature,decoded));CHECK(!decoded.choices.fahrenheit);CHECK(decoded.choices.oxygen==3&&decoded.choices.keepOriginal["T"]==false);
 std::cout<<"PASS "<<checks<<" Fahrenheit values, blank cells, originals, unchanged sensor calculations and preset compatibility\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
