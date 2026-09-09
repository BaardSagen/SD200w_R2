#include "../sit_import/presets.h"
#include <iostream>
int checks=0;
#define CHECK(x) do{++checks;if(!(x))throw std::runtime_error(#x);}while(0)
int main(){try{
 sit::Data a;a.fields={"COUNT","C","T","P","Par","OxR","DATE","TIME"};a.metadata={"OSU107 Ser:107 DATE=2026-09-03 TIME=20:28:52", "CTDOF Par OxR Ser No 1240 AP1006.175"};a.source="old.txt";
 auto b=a;b.source="new.csv";b.metadata={"OSU107 Ser:200 DATE=2027-01-01 TIME=01:02:03","CTDOF Par OxR Ser No 1240 AP900"};CHECK(sitpreset::signature(a)==sitpreset::signature(b));
 b.fields.push_back("OT");CHECK(sitpreset::signature(a)!=sitpreset::signature(b));b=a;std::swap(b.fields[1],b.fields[2]);CHECK(sitpreset::signature(a)!=sitpreset::signature(b));
 b=a;b.metadata={"SAIV110 Ser:107"};CHECK(sitpreset::signature(a)!=sitpreset::signature(b));b=a;b.metadata.push_back("# PAR source unit: uEinstein/(cm2*s)");CHECK(sitpreset::signature(a)!=sitpreset::signature(b));
 sitpreset::Record r;r.signature=sitpreset::signature(a);r.date="2026-09-09 18:22:33";r.source="C:\\data\\old.txt";auto&o=r.choices;o.oxygen=3;o.oxygenOX=2;o.conductivity=o.depth=o.par=1;o.parSource=2;o.keepC=o.keepP=o.keepPar=false;o.soundVelocity=false;o.keepOriginal["C"]=false;o.keepOriginal["T"]=true;o.useGPS=true;o.latitude=60.393;o.longitude=5.295;o.suppliedT=o.suppliedS=true;o.temperature=10;o.salinity=35;o.air=1013.25;
 auto bytes=sitpreset::encode(r);sitpreset::Record round;CHECK(sitpreset::decode(bytes,r.signature,round));CHECK(sitpreset::encode(round)==bytes);CHECK(!sitpreset::decode(bytes,"other",round));CHECK(!sitpreset::decode(bytes+"trailing",r.signature,round));
 for(size_t n=0;n<bytes.size();++n)CHECK(!sitpreset::decode(bytes.substr(0,n),r.signature,round));
 r.choices.parSource=0;CHECK(!sitpreset::decode(sitpreset::encode(r),r.signature,round));r.choices.parSource=2;r.choices.oxygen=4;CHECK(!sitpreset::decode(sitpreset::encode(r),r.signature,round));r.choices.oxygen=3;
 b.air=900;auto reused=sitpreset::reuse(r,b);CHECK(reused.air==900);CHECK(!reused.suppliedT&&!reused.suppliedS);CHECK(reused.latitude==45.508368287&&reused.longitude==0);CHECK(reused.conductivity==1&&!reused.keepC&&reused.oxygen==3&&!reused.soundVelocity);CHECK(reused.keepOriginal==r.choices.keepOriginal);
 std::cout<<"PASS "<<checks<<" preset signature, serialization, corruption and fresh-condition checks\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
