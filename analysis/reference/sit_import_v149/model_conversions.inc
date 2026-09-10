// Included within namespace sit, after the preserved legacy converter.
inline bool gswRequired(const Choices&o){return o.absoluteSalinity||o.atlas||o.conductivity==3||o.densityModel==3||(o.soundVelocity&&o.soundModel==1)||o.depth==5||(o.oxygen&&o.oxygenModel)||(o.oxygenOX&&o.oxygenOXModel);}
inline bool modernTemperatureRequired(const Choices&o){return gswRequired(o)||o.conductivity>=2||(o.soundVelocity&&o.soundModel>0);}
inline bool needsAir(const Choices&o){return (o.oxygen&&o.oxygenModel==0)||(o.oxygenOX&&o.oxygenOXModel==0);}
inline bool needsWater(const Choices&o){return (o.depth&&o.depth!=2&&o.depth!=4)||o.oxygen||o.oxygenOX||gswRequired(o);}
inline const char* depthName(int n){static const char*a[]={"Pressure only","SIT fixed position / EOS-80","UNESCO 1983 pressure/latitude","SIT-style profiling / EOS-80 endpoint layers","GSW pressure/latitude reference ocean","TEOS-10 hydrostatic profile / trapezoid layers"};return a[n];}
inline const char* densityName(int n){static const char*a[]={"EOS-80 in-situ density anomaly","EOS-80 Sigma T (zero sea pressure)","Older SD200W S/T density anomaly","TEOS-10 exact in-situ density and sigma0"};return a[n];}
inline const char* soundName(int n){static const char*a[]={"Original SIT / UNESCO-family","TEOS-10 exact Gibbs","Mackenzie 1981 (T68, depth)","Del Grosso 1974 (T68, kgf/cm2)","NPL Leroy et al. 2008 (T90, depth, absolute latitude)"};return a[n];}
inline const char* oxygenName(int n){return n?"GSW Garcia-Gordon at one standard atmosphere, SP/potential temperature":"Original SIT T/S and barometric pressure";}
inline void calculate(Data&d,const Choices&o,Formula formula){
 if(o.conductivity<0||o.conductivity>3||o.depth<0||o.depth>5||o.densityModel<0||o.densityModel>3||o.soundModel<0||o.soundModel>4||o.oxygen<0||o.oxygen>6||o.oxygenOX<0||o.oxygenOX>6||o.oxygenModel<0||o.oxygenModel>1||o.oxygenOXModel<0||o.oxygenOXModel>1||o.temperatureScale<0||o.temperatureScale>2||o.profileDirection<0||o.profileDirection>1)throw std::runtime_error("Invalid conversion method");
 bool advanced=o.conductivity>1||o.depth>1||o.densityModel||o.soundModel||o.oxygenModel||o.oxygenOXModel||o.oxygen>3||o.oxygenOX>3||o.temperatureScale||o.absoluteSalinity||o.atlas||o.useCalculatedS;
 Data result=d;
 if(!advanced){calculateLegacy(result,o,formula);d=std::move(result);return;}
 if(modernTemperatureRequired(o)&&!o.temperatureScale)throw std::runtime_error("Select the input temperature scale (ITS-90 or IPTS-68) before using a modern calculation method");
 if(o.atlas&&!o.useGPS)throw std::runtime_error("GSW atlas salinity requires a supplied geographic position");
 if(o.useGPS&&(!std::isfinite(o.latitude)||!std::isfinite(o.longitude)||std::abs(o.latitude)>90||std::abs(o.longitude)>180))throw std::runtime_error("Invalid latitude/longitude");
 if(o.conductivity&&(!complete(d,"C")||!complete(d,"T")||!complete(d,"P")))throw std::runtime_error("C to S requires C/T/P in every measurement");
 if(o.useCalculatedS&&!o.conductivity)throw std::runtime_error("Using calculated salinity requires a C-to-S conversion");
 if(o.depth&&!complete(d,"P"))throw std::runtime_error("Depth requires sea pressure in every measurement");
 if(o.par&&(o.parSource<1||o.parSource>2))throw std::runtime_error("Select the PAR source area unit");
 const bool ctd=canSal(d)&&complete(d,"T")&&complete(d,"P"),gsw=gswRequired(o);
 const size_t count=d.rows.size();double lat=o.useGPS?o.latitude:45.508368287,lon=o.useGPS?o.longitude:0,air=o.air>0?o.air:d.air;
 std::map<string,std::vector<string> > outputs;
 if(o.fahrenheit&&index(d,"T")>=0)outputs["T_degF"].resize(count);
 if(o.par&&index(d,"Par")>=0)outputs["Par_umol_m2_s"].resize(count);
 auto put=[&](const string&f,size_t i,double v){auto&x=outputs[f];if(x.empty())x.resize(count);x[i]=fmt(sitmodels::valid(v,f.c_str()));};
 std::vector<double> pressure(count),factor(count),depth(count),sal(count),tLegacy(count),tModern(count);std::vector<sitmodels::Water> water(count);
 for(size_t r=0;r<count;++r)try{
  bool rowT=hasValue(d,r,"T"),rowS=hasValue(d,r,"S"),fromC=rowT&&hasValue(d,r,"C")&&hasValue(d,r,"P");
  double rawT=rowT?val(d,r,"T"):o.temperature,t=sitmodels::t68(rawT,o.temperatureScale),t90=sitmodels::t90(rawT,o.temperatureScale),p=hasValue(d,r,"P")?val(d,r,"P"):0;
  double derived=fromC?(o.conductivity>=2?sitmodels::valid(gsw_sp_from_c(val(d,r,"C"),t90,p),"GSW Practical Salinity"):formula(0,p,val(d,r,"C"),t)):o.salinity;
  double s=(o.useCalculatedS&&o.conductivity)?derived:rowS?val(d,r,"S"):derived;
  if((needsWater(o)||ctd)&&((!rowT&&!o.suppliedT)||(!rowS&&!fromC&&!o.suppliedS)))throw std::runtime_error("Missing supporting temperature or Practical Salinity");
  if((needsWater(o)||ctd)&&(s<0||s>60||rawT< -5||rawT>50))throw std::runtime_error("Supporting T/S outside converter limits");
  if(o.conductivity)put(index(d,"S")<0?"S":"S_from_C",r,derived);
  sal[r]=s;tLegacy[r]=t;tModern[r]=t90;pressure[r]=p;
  if(gsw){water[r]=sitmodels::water(s,t90,p,lon,lat,o.atlas);put("SA_TEOS10_g_kg",r,water[r].sa);put("CT_TEOS10_degC",r,water[r].ct);}
  if(ctd){
   if(o.densityModel==3){put("Density_TEOS10_kg_m3",r,water[r].rho);put("Sigma0_TEOS10_kg_m3",r,water[r].sigma0);}
   else if(o.densityModel==2)put("Density_anomaly_legacy_kg_m3",r,sitmodels::oldDensity(s,t));
   else if(o.densityModel==1)put("SigmaT_EOS80_kg_m3",r,formula(2,0,t,s));
   else if(index(d,"Density_anomaly_SIT_kg_m3")<0)put("Density_anomaly_SIT_kg_m3",r,formula(2,p,t,s));
  }
  if(o.depth){
   if(p<0)throw std::runtime_error("Depth conversion needs non-negative sea pressure; check the pressure reference");
   if((o.depth==4||o.depth==5)&&p>10000)throw std::runtime_error("GSW depth is limited to 0..10000 dbar in this converter");
   if(o.depth==2)depth[r]=sitmodels::unescoDepth(p,lat);
   else if(o.depth==4)depth[r]=-sitmodels::valid(gsw_z_from_p(p,lat,0,0),"GSW height");
   else if(o.depth==5){factor[r]=10000/(water[r].rho*gsw_grav(lat,p));}
   else {factor[r]=10000/((1000+formula(2,p,t,s))*formula(3,lat,p,0));depth[r]=p*factor[r];}
  }
  for(const string&f:{string("OX"),string("OxR")}){
   int units=f=="OX"?o.oxygenOX:o.oxygen,model=f=="OX"?o.oxygenOXModel:o.oxygenModel;
   if(!units||index(d,f)<0)continue;
   auto init=[&](const string&suffix){outputs[f+suffix].resize(count);};
   if(units==1||units==3||units==6)init("_mg_L");if(units==2||units==3||units==6)init("_mL_L");if(units==4||units==6)init("_umol_L");if(units==5||units==6)init("_umol_kg");
   if(!hasValue(d,r,f))continue;
   double percent=val(d,r,f);if(percent<0||percent>300)throw std::runtime_error("Oxygen percentage must be 0..300");
   double rho=model?water[r].rho:1000+formula(2,p,t,s),mg;
   if(model)mg=water[r].o2*(percent/100)*.031998*(rho/1000);
   else {if(air<500||air>1200||!std::isfinite(air))throw std::runtime_error("SIT oxygen needs atmospheric pressure 500..1200 hPa");mg=oxygen(s,o.temperatureScale?t90:rawT,air)*percent/100;}
   if(units==1||units==3||units==6)put(f+"_mg_L",r,mg);
   if(units==2||units==3||units==6)put(f+"_mL_L",r,mg*22.391/31.998);
   if(units==4||units==6)put(f+"_umol_L",r,mg*1000/31.998);
   if(units==5||units==6)put(f+"_umol_kg",r,model?water[r].o2*percent/100:mg*22.391*1000/(716.467218*(rho/1000)));
  }
  if(o.fahrenheit&&rowT)put("T_degF",r,rawT*9/5+32);
  if(o.par&&hasValue(d,r,"Par"))put("Par_umol_m2_s",r,val(d,r,"Par")*(o.parSource==2?10000:1));
 }catch(const std::exception&e){throw std::runtime_error("Measurement "+std::to_string(r+1)+": "+e.what());}
 if(o.depth==3||o.depth==5){
  // Explicit single-cast traversal. New maxima build knots; reversals interpolate.
  if(count<2)throw std::runtime_error("Profile depth requires at least two measurements");
  for(size_t i=1;i<count;++i)if(hasValue(d,i,"COUNT")&&hasValue(d,i-1,"COUNT")&&val(d,i,"COUNT")<=val(d,i-1,"COUNT"))throw std::runtime_error("Profile depth requires one continuous cast; split files with restarted COUNT before conversion");
  std::vector<double> kp,kz;double previousFactor=0;
  for(size_t n=0;n<count;++n){size_t i=o.profileDirection?count-1-n:n;double p=pressure[i];if(p<=0){depth[i]=0;continue;}
   if(kp.empty()||p>kp.back()){
    double z=kp.empty()?p*factor[i]:kz.back()+(p-kp.back())*(o.depth==5?(factor[i]+previousFactor)/2:factor[i]);
    kp.push_back(p);kz.push_back(z);previousFactor=factor[i];depth[i]=z;
   }else {auto hi=std::lower_bound(kp.begin(),kp.end(),p);size_t k=size_t(hi-kp.begin());depth[i]=k?kz[k-1]+(p-kp[k-1])*(kz[k]-kz[k-1])/(kp[k]-kp[k-1]):p*kz[0]/kp[0];}
  }
  result.metadata.push_back("# Profile depth: one cast; "+string(o.profileDirection?"reverse/upcast":"forward/downcast")+" traversal; first positive knot extrapolated to zero; new-pressure knots and linear interpolation on reversals; "+string(o.depth==5?"trapezoid reciprocal-density/gravity integration":"endpoint reciprocal-density/gravity integration (SIT-style normal rule, not every native fallback)"));
 }
 for(size_t r=0;r<count;++r)try{
  if(o.depth)put("Depth_m",r,depth[r]);
  if(ctd&&o.soundVelocity){double value=0,s=sal[r],t=tLegacy[r],p=pressure[r],z=o.depth?depth[r]:sitmodels::unescoDepth(p,lat);string name;
   switch(o.soundModel){case 0:name="Sound_velocity_SIT_m_s";value=formula(1,p,t,s);break;case 1:name="Sound_velocity_TEOS10_m_s";value=water[r].sound;break;case 2:name="Sound_velocity_Mackenzie_m_s";value=sitmodels::mackenzie(s,t,z);break;case 3:name="Sound_velocity_DelGrosso_m_s";value=sitmodels::delGrosso(s,t,p);break;case 4:name="Sound_velocity_NPL_m_s";value=sitmodels::npl(s,tModern[r],z,lat);break;}
   if(index(d,name)<0)put(name,r,value);
  }
 }catch(const std::exception&e){throw std::runtime_error("Measurement "+std::to_string(r+1)+": "+e.what());}
 for(auto&entry:outputs)append(result,entry.first,entry.second);
 result.metadata.push_back("# SIT conversion methods 1.4.7; temperature input="+string(o.temperatureScale==1?"ITS-90; legacy equations receive T90*1.00024":o.temperatureScale==2?"IPTS-68; modern equations receive T68/1.00024":"as recorded; historical SIT convention, scale unspecified"));
 result.metadata.push_back("# Salinity input="+string(o.useCalculatedS?"selected C-derived salinity":"existing S first, otherwise C-derived salinity, otherwise explicitly supplied SP")+"; C-to-SP="+string(o.conductivity>=2?"GSW PSS-78 / modified Hill":"original SIT PSS-78"));
 if(gsw)result.metadata.push_back("# SA/CT: GSW; "+string(o.atlas?"SA_from_SP with geographic atlas":"Reference Composition SA=SR_from_SP (no atlas anomaly)")+"; rho/sound use exact Gibbs routines; SP retained separately");
 if(ctd)result.metadata.push_back("# Density output: "+string(densityName(o.densityModel))+"; sound: "+string(o.soundVelocity?soundName(o.soundModel):"not added"));
 if(o.depth)result.metadata.push_back("# Depth_m: "+string(depthName(o.depth))+"; sea pressure in dbar; no atmospheric subtraction from P");
 if(o.depth||gsw||(ctd&&o.soundVelocity&&(o.soundModel==2||o.soundModel==4)))result.metadata.push_back("# Position: latitude="+fmt(lat)+"; longitude="+fmt(lon)+string(o.useGPS?"; user supplied":"; default latitude; longitude unused for atlas (not selected)"));
 if(ctd&&o.soundVelocity&&(o.soundModel==2||o.soundModel==4))result.metadata.push_back("# Sound-speed depth input: "+string(o.depth?depthName(o.depth):"UNESCO 1983 (pressure kept; depth derived internally)"));
 for(const string&f:{string("OX"),string("OxR")}){int unit=f=="OX"?o.oxygenOX:o.oxygen,model=f=="OX"?o.oxygenOXModel:o.oxygenModel;if(unit&&index(d,f)>=0)result.metadata.push_back("# "+f+" conversion: "+oxygenName(model)+(model?"; equilibrium reference 1013.25 hPa; file AP not applied; in-situ TEOS-10 density for per-litre units":"; AP_hPa="+fmt(air)+"; EOS-80 in-situ density for mass units")+"; no additional sensor pressure/response correction; source percent saturation");}
 if((o.oxygen||o.oxygenOX)&&!complete(d,"P"))result.metadata.push_back("# Oxygen supporting pressure: missing P treated as zero sea pressure for density/potential temperature; verify this is appropriate");
 if(o.suppliedT)result.metadata.push_back("# Missing T supplied by user: "+fmt(o.temperature));if(o.suppliedS)result.metadata.push_back("# Missing SP supplied by user: "+fmt(o.salinity));
 if(o.fahrenheit)result.metadata.push_back("# T_degF=original Celsius T*9/5+32; sensor calculations use the stated temperature scale");
 if(o.par)result.metadata.push_back("# PAR source unit: "+string(o.parSource==1?"uEinstein/(m2*s); multiplier=1":"uEinstein/(cm2*s); multiplier=10000")+"; output umol photons/(m2*s)");
 if(index(d,"OF")>=0)result.metadata.push_back("# OF: fluorescence ug/L; no rescaling");if(index(d,"OT")>=0)result.metadata.push_back("# OT: turbidity FTU; no conversion to NTU/FNU");
 if(o.conductivity&&!o.keepC)removeField(result,"C");if(o.depth&&!o.keepP)removeField(result,"P");if(o.par&&!o.keepPar)removeField(result,"Par");
 for(auto&entry:o.keepOriginal)if(!entry.second){removeField(result,entry.first);result.metadata.push_back("# Original field excluded by user: "+entry.first);}
 d=std::move(result);
}
