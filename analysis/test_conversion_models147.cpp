#include "../sit_import/legacy_convert.h"
#include "../sit_import/presets.h"
#include "../sit_import/native_data.h"
#include "models147/reference.h"
#include <fstream>
namespace gsw_reference {
#include "../saiv-studio/vendor/gsw/gsw_check_data.h"
}
#include <iostream>
int checks=0;
#define CHECK(x) do{++checks;if(!(x))throw std::runtime_error(std::string("line ")+std::to_string(__LINE__)+": "+#x);}while(0)
void close(double a,double b,double tol=1e-8){if(std::abs(a-b)>=tol)std::cerr<<"comparison "<<checks<<": "<<std::setprecision(17)<<a<<" expected "<<b<<"\n";CHECK(std::abs(a-b)<tol);}
double formula(int f,double a,double b,double c){switch(f){case 0:return reference::salinity(b,c,a);case 1:return reference::sound_velocity(c,b,a);case 2:return reference::density_anomaly(c,b,a);case 3:return reference::gravity(a,b);}throw std::runtime_error("callback");}
sit::Data example(){sit::Data d;d.fields={"COUNT","S","C","T","P","OX","OxR","Par","OF","OT","DATE","TIME"};d.rows={{"1","32.539","33.71963249253746","7.773","16.72","3.47","100","2.5","5.67","1.08","2026-09-01","12:00:00"}};d.air=925;return d;}
void rejected(sit::Data d,sit::Choices o){auto before=sit::output(d);bool fail=false;try{sit::calculate(d,o,formula);}catch(const std::exception&){fail=true;}CHECK(fail);CHECK(before==sit::output(d));}
int main(){try{
 // Published GSW examples: independent reference numbers, six pressures.
 double sa[]={34.7118,34.8915,35.0256,34.8472,34.7366,34.7324},t[]={28.7856,28.4329,22.8103,10.2600,6.8863,4.4036},p[]={10,50,125,250,600,1000};
 double rho[]={1021.840173185531,1022.262689926782,1024.427715941676,1027.790201811623,1029.837714725961,1032.002404116447},sound[]={1542.615803587414,1542.703534065789,1530.844979136360,1494.409996920661,1487.377102518027,1483.934609078705};
 for(int i=0;i<6;++i){close(gsw_rho_t_exact(sa[i],t[i],p[i]),rho[i]);close(gsw_sound_speed_t_exact(sa[i],t[i],p[i]),sound[i]);}
 close(gsw_sp_from_c(34.5487,28.7856,10),20.009869599086951);
 close(gsw_o2sol_sp_pt(34.7118,28.8099),194.6825431692940);
 close(gsw_z_from_p(1000,4,0,0),-992.0919060719987);
 // Atlas values must match the bundled 3.06.16 reference data, not the older
 // 3.05 web-page example (which differs by 0.0000154 g/kg here).
 for(int i=0;i<135;++i)if(std::isfinite(gsw_reference::sa_from_sp[i])&&std::abs(gsw_reference::sa_from_sp[i])<1e10)close(gsw_sa_from_sp(gsw_reference::sp[i],gsw_reference::p[i],gsw_reference::long_cast[i/45],gsw_reference::lat_cast[i/45]),gsw_reference::sa_from_sp[i],sa_from_sp_ca);

 for(int model=0;model<=4;++model){auto deep=example();deep.rows[0][1]="35";deep.rows[0][3]="10";deep.rows[0][4]="4000";sit::Choices deepChoice;deepChoice.temperatureScale=1;deepChoice.soundModel=model;deepChoice.depth=4;deepChoice.densityModel=3;deepChoice.oxygenOX=6;deepChoice.oxygenOXModel=1;sit::calculate(deep,deepChoice,formula);CHECK(sit::val(deep,0,"Depth_m")>3900);CHECK(sit::val(deep,0,"Density_TEOS10_kg_m3")>1040);CHECK(sit::val(deep,0,"OX_umol_kg")>0);}

 close(sitmodels::mackenzie(35,10,0),1489.8034);close(sitmodels::delGrosso(35,10,0),1489.7805236851375);close(sitmodels::npl(35,10,0,45),1489.8195);
 // Defaults retain every legacy output and metadata; all old field/unit choices.
 for(int depth=0;depth<=1;++depth)for(int ox=0;ox<=3;++ox)for(int C=0;C<=1;++C){auto a=example(),b=a;sit::Choices o;o.depth=depth;o.oxygenOX=o.oxygen=ox;o.conductivity=C;o.par=1;o.parSource=2;o.fahrenheit=true;sit::calculateLegacy(a,o,formula);sit::calculate(b,o,formula);CHECK(sit::output(a)==sit::output(b));}
 // Each model dispatch through production conversion, not only helpers.
 for(int mode=0;mode<=4;++mode){auto d=example();sit::Choices o;o.temperatureScale=1;o.soundModel=mode;o.densityModel=3;sit::calculate(d,o,formula);CHECK(d.rows.size()==1);close(sit::val(d,0,"Density_TEOS10_kg_m3"),gsw_rho_t_exact(gsw_sr_from_sp(32.539),7.773,16.72));}
 for(int mode=0;mode<=3;++mode){auto d=example();sit::Choices o;o.temperatureScale=2;o.densityModel=mode;sit::calculate(d,o,formula);CHECK(d.fields.size()>12);}
 for(int mode=1;mode<=5;++mode){auto d=example();auto second=d.rows[0];d.rows[0][1]="23.738";d.rows[0][3]="14.461";d.rows[0][4]="0.30";second[0]="2";d.rows.push_back(second);sit::Choices o;o.depth=mode;o.temperatureScale=2;sit::calculate(d,o,formula);CHECK(sit::val(d,1,"Depth_m")>16);if(mode==3)close(sit::val(d,1,"Depth_m"),16.628819227954484);}
 // Profile reversals interpolate existing knots; reverse traversal yields same knots.
 auto profile=example();auto low=profile.rows[0];low[0]="1";low[4]="1";profile.rows.insert(profile.rows.begin(),low);profile.rows[1][0]="2";auto mid=low;mid[0]="3";mid[4]="8";profile.rows.push_back(mid);
 for(int mode:{3,5}){sit::Choices o;o.depth=mode;o.temperatureScale=2;auto d=profile;sit::calculate(d,o,formula);double expected=sit::val(d,0,"Depth_m")+7*(sit::val(d,1,"Depth_m")-sit::val(d,0,"Depth_m"))/15.72;close(sit::val(d,2,"Depth_m"),expected);auto rev=profile;rev.rows.resize(2);std::reverse(rev.rows.begin(),rev.rows.end());rev.rows[0][0]="1";rev.rows[1][0]="2";o.profileDirection=1;sit::calculate(rev,o,formula);close(sit::val(rev,0,"Depth_m"),sit::val(d,1,"Depth_m"));}
 for(int units=1;units<=6;++units)for(int model=0;model<=1;++model){auto d=example();sit::Choices o;o.oxygenOX=units;o.oxygen=units;o.oxygenModel=o.oxygenOXModel=model;o.temperatureScale=model?2:0;sit::calculate(d,o,formula);if(units==6){double mg=sit::val(d,0,"OX_mg_L");close(sit::val(d,0,"OX_umol_L"),mg*1000/31.998);close(sit::val(d,0,"OX_mL_L"),mg*22.391/31.998);if(!model)close(mg,.3048739540923254);}}
 // Deliberate source priority; C and transmitted S may disagree.
 auto source=example();source.rows[0][1]="35";
 for(int mode=1;mode<=3;++mode){sit::Choices o;o.conductivity=mode;o.temperatureScale=2;o.useCalculatedS=true;auto d=source;sit::calculate(d,o,formula);double sp=sit::val(d,0,"S_from_C");close(sit::val(d,0,"Density_anomaly_SIT_kg_m3"),reference::density_anomaly(sp,7.773,16.72));close(sit::val(d,0,"S"),35);auto files=sitnative::project(d,sit::output(d),formula);double stored;std::memcpy(&stored,files.sd.data()+64,8);close(stored,sp);}
 // Native sound channel remains flagged when original CTD columns are excluded.
 auto soundOnly=example();soundOnly.fields={"COUNT","Sound_velocity_TEOS10_m_s","DATE","TIME"};soundOnly.rows={{"1","1500","2026-09-01","12:00:00"}};auto onlyFile=sitnative::project(soundOnly,sit::output(soundOnly),formula);uint32_t flags;std::memcpy(&flags,onlyFile.sd.data()+6,4);CHECK(flags&16);
 // Failure is atomic, including physical domains, missing inputs and duplicate output.
 sit::Choices o;o.soundModel=1;rejected(example(),o);o.temperatureScale=1;o.atlas=true;rejected(example(),o);o.useGPS=true;o.latitude=91;rejected(example(),o);
 o=sit::Choices();o.depth=5;o.temperatureScale=1;rejected(example(),o);auto bad=example();bad.rows[0][4]="-1";o.depth=1;rejected(bad,o);bad=example();bad.rows[0][1]="0.1";o.depth=0;o.soundModel=2;rejected(bad,o);
 o=sit::Choices();o.temperatureScale=1;o.oxygenOX=6;bad=example();bad.rows[0][5]="-1";rejected(bad,o);bad=example();sit::calculate(bad,o,formula);rejected(bad,o);
 auto excessive=example();excessive.rows[0][4]="10001";o=sit::Choices();o.depth=4;rejected(excessive,o);
 auto ctdOnly=example();sit::removeField(ctdOnly,"S");auto projected=sitnative::project(ctdOnly,sit::output(ctdOnly),formula);double projectedS;std::memcpy(&projectedS,projected.sd.data()+64,8);close(projectedS,reference::salinity(33.71963249253746,7.773,16.72));
 ctdOnly.metadata={"# SIT conversion methods 1.4.7; temperature input=ITS-90"};projected=sitnative::project(ctdOnly,sit::output(ctdOnly),formula);std::memcpy(&projectedS,projected.sd.data()+64,8);close(projectedS,reference::salinity(33.71963249253746,7.773*1.00024,16.72));double projectedSound;std::memcpy(&projectedSound,projected.sd.data()+96,8);close(projectedSound,reference::sound_velocity(projectedS,7.773*1.00024,16.72));
 o=sit::Choices();o.temperatureScale=1;o.oxygenOX=6;
 // Missing cells and empty optional columns are retained without invented readings.
 auto empty=example();empty.rows[0][5]="";empty.rows[0][7]="";o.par=1;o.parSource=1;sit::calculate(empty,o,formula);CHECK(empty.rows[0][sit::index(empty,"OX_mg_L")].empty());CHECK(empty.rows[0][sit::index(empty,"Par_umol_m2_s")].empty());
 // Newly exposed legacy file adapter preserves values and marks reconstructed time.
 std::ifstream in("data/26090606_18.11.51.txt",std::ios::binary);std::string raw((std::istreambuf_iterator<char>(in)),{});sit::Data legacy;CHECK(sit::parseConversion(raw,legacy));CHECK(legacy.rows.size()==43);CHECK(legacy.estimatedTime);CHECK(sit::index(legacy,"C")==-1);close(legacy.air,925);CHECK(legacy.rows[0][sit::index(legacy,"DATE")]=="2026-09-06");
 // Presets v3, truncation, old v2/v1 migrations and fresh supporting values.
 sitpreset::Record r;r.signature="test";r.date="2026-09-10 12:00:00";r.choices.temperatureScale=1;r.choices.depth=5;r.choices.conductivity=3;r.choices.oxygen=6;r.choices.soundModel=4;r.choices.densityModel=3;r.choices.atlas=true;r.choices.useGPS=true;r.choices.useCalculatedS=true;
 auto bytes=sitpreset::encode(r);sitpreset::Record rr;CHECK(sitpreset::decode(bytes,r.signature,rr));CHECK(sitpreset::encode(rr)==bytes);for(size_t i=0;i<bytes.size();++i)CHECK(!sitpreset::decode(bytes.substr(0,i),r.signature,rr));
 r.choices=sit::Choices();bytes=sitpreset::encode(r);bytes.replace(4,13,"SIT choices 2");bytes.resize(bytes.size()-36);CHECK(sitpreset::decode(bytes,r.signature,rr));CHECK(rr.choices.temperatureScale==0);bytes.replace(4,13,"SIT choices 1");bytes.resize(bytes.size()-4);CHECK(sitpreset::decode(bytes,r.signature,rr));CHECK(!rr.choices.fahrenheit);
 std::cout<<"PASS "<<checks<<" numerical, dispatch, legacy regression, domain, atomicity, profile, parser and preset checks\n";
 auto d=example();o=sit::Choices();o.temperatureScale=1;o.densityModel=3;o.soundModel=1;o.oxygenOX=6;o.oxygenOXModel=1;o.depth=4;sit::calculate(d,o,formula);std::ofstream("analysis/models147/modern_example.txt")<<sit::output(d);
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
