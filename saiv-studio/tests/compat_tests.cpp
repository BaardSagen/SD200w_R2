#include "sit_compat.hpp"
#include "sit/merge.h"
#include <iostream>
#include <fstream>
#include <cmath>
#include <chrono>
using namespace saiv;
namespace fs=std::filesystem;
int checks=0;
void require(bool condition,const char*msg){++checks;if(!condition)throw std::runtime_error(msg);}
template<class F> void rejected(F fn,const char*msg){bool threw=false;try{fn();}catch(const std::exception&){threw=true;}require(threw,msg);}
int main(int argc,char**argv){try{fs::path fixtures=argv[1],output=argv[2];fs::create_directories(output);output/=std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());fs::create_directories(output);
 struct Reference{int kind;double a,b,c,expected;};
 const Reference refs[]={
 {0,42.914,15,0,34.99999992412808},{0,30,10,100,26.82414973414006},{0,50,20,1000,36.357615121365036},{0,.02,20,0,.01702767147330211},
 {1,0,15,35,1506.663262608542},{1,0,0,0,1402.388},{1,100,8,32,1480.3900033749287},{1,1000,20,35,1538.1161454020735},{1,4000,2,40,1531.9453539915671},
 {2,0,15,35,25.97275386538328},{2,0,0,0,-.157406},{2,100,8,32,25.376992971749043},{2,1000,20,35,29.087115066672997}};
 for(auto&r:refs)require(std::abs(sitFormula(r.kind,r.a,r.b,r.c)-r.expected)<1e-9,"SIT binary numerical reference");
 require(std::abs(sitConductivity(35,15,0)-42.914)<1e-6,"inverse salinity roundtrip");
 auto logger=loadDataset(fixtures/"logger.txt");require(logger.rows.size()==79&&logger.columns.size()==10,"logger has all 79 rows and 10 fields");
 auto surface=loadDataset(fixtures/"surface.txt");require(surface.rows.size()==3,"surface has 3 rows");
 auto legacy=loadDataset(fixtures/"legacy.txt");require(legacy.rows.size()==43,"legacy has 43 rows");require(legacy.column("DATE")>=0&&legacy.rows[0][legacy.column("TIME")]=="18:28:35","legacy header timestamps");require(measurementSeconds(legacy)[1]==10,"time graph uses seconds rather than row numbers");
 auto native=loadDataset(fixtures/"reference.SD2");require(native.rows.size()==7,"original native SD2 loads");
 for(auto t:{logger,surface,legacy}){auto path=output/(std::to_string(t.rows.size())+".SD2");saveNativeDataset(t,path);auto restored=loadDataset(path);require(restored.columns==t.columns&&restored.rows==t.rows,"native SF2 roundtrip preserves every original field and row");auto original=readDatasetBytes(path);rejected([&]{saveNativeDataset(t,path);},"native files cannot be overwritten");require(readDatasetBytes(path)==original,"native collision leaves source untouched");}
 for(auto t:{logger,surface,legacy,native}){auto restored=parseCsvDataset(t.csv(),"CSV roundtrip");require(restored.columns==t.columns&&restored.rows==t.rows&&restored.notes==t.notes,"CSV preserves every column, row and metadata line");}
 Table text;text.columns={"unknown channel","TIME","T"};text.rows={{"alpha;beta\nquoted \"value\"","12:00:00.125",""},{"","12:00:01.500",""}};auto csv=parseCsvDataset(text.csv(),"quoted CSV");require(csv.rows==text.rows&&csv.columns==text.columns,"CSV preserves multiline quoted values, fractional timestamps and all-missing sensor rows");
 rejected([&]{parseCsvDataset("T;T\n1;2\n","duplicate");},"duplicate CSV column rejected");rejected([&]{parseCsvDataset("T;P\n1\n","short row");},"incomplete CSV row rejected");
 auto fields=fieldsText(logger);require(fields.find("SAIV Studio export 0.3.1")!=std::string::npos,"export identifies Studio");
 Table sample;sample.columns={"DATE","TIME","C","T","P","OX","Par","OF","OT"};sample.rows={{"2026-09-09","12:00:00","42.914","15","0","100","2","1.2","3.4"}};sample.source="reference";sample.notes={"CTD Ser No 1237 AP1013.25"};sit::Choices choices;choices.conductivity=1;choices.depth=1;choices.oxygenOX=3;choices.par=1;choices.parSource=2;choices.fahrenheit=true;
 auto converted=toSit(sample);sit::calculate(converted,choices,sitConversionFormula);auto result=fromSit(converted);require(std::abs(result.value(0,result.column("S"))-35)<1e-6,"wizard callback salinity has correct P,C,T order");require(std::abs(result.value(0,result.column("Sound_velocity_SIT_m_s"))-1506.6632625)<1e-6,"wizard sound velocity uses computed salinity");require(result.value(0,result.column("T_degF"))==59,"Fahrenheit conversion");require(result.value(0,result.column("Par_umol_m2_s"))==20000,"PAR square centimetre scaling");require(result.value(0,result.column("T"))==15&&result.value(0,result.column("OF"))==1.2,"original Celsius and fluorescence retained");
 require(std::abs(sit::oxygen(35,10,1013.25)-9.02425974628226)<1e-9,"SIT oxygen reference");sample.rows[0][sample.column("P")]="100";converted=toSit(sample);sit::calculate(converted,choices,sitConversionFormula);require(std::abs(sit::val(converted,0,"Depth_m")-1000000/((1000+sitFormula(2,100,15,sitFormula(0,42.914,15,100)))*sitFormula(3,choices.latitude,100,0)))<1e-8,"SIT fixed-position real depth");
 auto npath=output/"raw.SD2";saveNativeDataset(sample,npath);auto side=npath;side.replace_extension(".SF2");fs::remove(side);auto raw=loadDataset(npath);require(std::abs(raw.value(0,raw.column("S"))-sitFormula(0,42.914,15,100))<1e-7,"native projected salinity");
 auto broken=output/"damaged.SD2";saveNativeDataset(sample,broken);{std::fstream f(broken,std::ios::binary|std::ios::in|std::ios::out);f.seekp(51);f.put('x');}rejected([&]{loadDataset(broken);},"mismatched SF2 fingerprint rejected");
 auto master=sitmerge::parse("FIELDS: DATE;TIME;T\n2026-09-09;12:00:00.250;10\n2026-09-09;12:00:01.500;11\n","master");auto other=sitmerge::parse("FIELDS: DATE;TIME;P\n2026-09-09;12:00:00.000;1\n2026-09-09;12:00:00.500;2\n","other");auto merged=sitmerge::merge(master,{other},250000,false,true);require(sit::val(merged,0,"M1_P")==1,"merge tie selects earlier timestamp");require(merged.rows[1][sit::index(merged,"M1_P")].empty(),"unmatched merge fields stay empty");require(sit::val(merged,0,"M1_Delta_seconds")==-.25,"merge retains fractional time difference");
 Table missing=sample;missing.rows[0][missing.column("T")]="";auto mp=output/"missing.SD2";saveNativeDataset(missing,mp);side=mp;side.replace_extension(".SF2");fs::remove(side);auto mt=loadDataset(mp);require(mt.rows[0][mt.column("T")].empty(),"native missing sentinel becomes missing");
 std::cout<<"PASS "<<checks<<" compatibility checks\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}}
