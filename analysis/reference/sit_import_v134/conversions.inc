struct Choices {
 int oxygen=0,oxygenOX=0,conductivity=0,depth=0,par=0,parSource=0;
 bool soundVelocity=true;
 bool keepC=true,keepP=true,keepPar=true,useGPS=false;
 double latitude=45.508368287,longitude=0,temperature=0,salinity=0,air=0;
 bool suppliedT=false,suppliedS=false;
 std::map<string,bool> keepOriginal;
};
// Callbacks 0 salinity, 1 sound velocity, 2 in-situ density anomaly, 3 gravity.
// The production callback calls original SIT machine-code routines directly.
typedef double (*Formula)(int,double,double,double);
inline double oxygen(double S,double T,double air_hPa) {
 double k=T+273.15;
 double a=std::exp(-139.34411+157570.1/k-66423080/(k*k)+12438000000./std::pow(k,3)-862194900000./std::pow(k,4));
 double b=std::exp(-S*(.017674-10.754/k+2140.7/(k*k)));
 double theta=.000975-1.426e-5*T+6.436e-8*T*T,vapor=std::exp(11.8571-3840.7/k-216961/(k*k));
 double p=(air_hPa*760./1013.25)*.00131578955679,divisor=(1-vapor)*(1-theta);
 return a*b*(divisor?(1-theta*p)*(p-vapor)/divisor:1);
}
inline bool complete(const Data&d,const string&f) {int c=index(d,f);if(c<0)return false;for(auto&r:d.rows)if(r[c].empty())return false;return true;}
inline bool canSal(const Data&d){return complete(d,"S")||(complete(d,"C")&&complete(d,"T")&&complete(d,"P"));}
inline bool hasValue(const Data&d,size_t row,const string&f){int i=index(d,f);return i>=0&&!d.rows[row][i].empty();}
inline bool wantsOxygen(const Data&d,const Choices&o){return (o.oxygen&&index(d,"OxR")>=0)||(o.oxygenOX&&index(d,"OX")>=0);}
inline void append(Data&d,const string&f,const std::vector<string>&v){
 if(v.size()!=d.rows.size())throw std::runtime_error("Calculated column row count mismatch: "+f);
 if(index(d,f)>=0)throw std::runtime_error("Calculated field already exists: "+f+". Keep the existing field or start from the original input file.");
 d.fields.push_back(f);for(size_t i=0;i<d.rows.size();++i)d.rows[i].push_back(v[i]);
}
inline void removeField(Data&d,const string&f){int i=index(d,f);if(i<0)return;d.fields.erase(d.fields.begin()+i);for(auto&r:d.rows)r.erase(r.begin()+i);}
inline std::pair<double,double> gpsPair(string text){
 text=trim(text);
 if(text.size()>1&&((text.front()=='"'&&text.back()=='"')||(text.front()=='\''&&text.back()=='\'')))text=trim(text.substr(1,text.size()-2));
 size_t comma=text.find(',');
 if(comma==string::npos||text.find(',',comma+1)!=string::npos)throw std::runtime_error("Paste GPS as latitude, longitude; for example 60.3936119227684, 5.29588169849683. Use decimal points.");
 double latitude=number(trim(text.substr(0,comma))),longitude=number(trim(text.substr(comma+1)));
 if(std::abs(latitude)>90||std::abs(longitude)>180)throw std::runtime_error("Latitude must be -90 to 90 and longitude -180 to 180 degrees");
 return {latitude,longitude};
}
inline double realDepth(double pressure,double densityAnomaly,double gravity){
 double rho=1000+densityAnomaly;if(rho<=0||gravity<=0)throw std::runtime_error("Invalid density/gravity for depth calculation");
 return pressure*10000/(rho*gravity);
}
inline void calculate(Data&d,const Choices&o,Formula formula) {
 const bool ctd=canSal(d)&&complete(d,"T")&&complete(d,"P"),convertOxygen=wantsOxygen(d,o);
 if(o.conductivity&&(!complete(d,"C")||!complete(d,"T")||!complete(d,"P")))throw std::runtime_error("Converting C to S requires conductivity, temperature and pressure in every measurement");
 if(o.depth&&!complete(d,"P"))throw std::runtime_error("Real depth requires pressure in every measurement");
 if(o.depth&&o.useGPS&&(!std::isfinite(o.latitude)||!std::isfinite(o.longitude)||std::abs(o.latitude)>90||std::abs(o.longitude)>180))throw std::runtime_error("GPS latitude must be -90 to 90 and longitude -180 to 180 degrees");
 if(o.par&&(o.parSource<1||o.parSource>2))throw std::runtime_error("Select whether source PAR is per square metre or per square centimetre");
 double air=o.air>0?o.air:d.air,latitude=o.useGPS?o.latitude:45.508368287;
 const size_t count=d.rows.size();std::vector<string> svals(count),sound(count),density(count),depth(count),par(count);
 std::map<string,std::vector<string> > oxMg,oxMl;
 for(string field:{"OxR","OX"})if(index(d,field)>=0&&(field=="OxR"?o.oxygen:o.oxygenOX)){oxMg[field].resize(count);oxMl[field].resize(count);}
 for(size_t r=0;r<count;++r){
  bool rowS=hasValue(d,r,"S"),rowT=hasValue(d,r,"T");
  bool rowSal=rowS||(rowT&&hasValue(d,r,"C")&&hasValue(d,r,"P"));
  double s=rowS?val(d,r,"S"):rowSal?formula(0,val(d,r,"P"),val(d,r,"C"),val(d,r,"T")):o.salinity;
  double t=rowT?val(d,r,"T"):o.temperature,p=hasValue(d,r,"P")?val(d,r,"P"):0;
  if(o.conductivity)svals[r]=fmt(formula(0,p,val(d,r,"C"),t));
  if(ctd){if(s<0)throw std::runtime_error("Negative salinity cannot be used for CTD calculations");if(o.soundVelocity)sound[r]=fmt(formula(1,p,t,s));density[r]=fmt(formula(2,p,t,s));}
  if(o.depth||convertOxygen){
   if((!rowT&&!o.suppliedT)||(!rowSal&&!o.suppliedS))throw std::runtime_error("Missing temperature or salinity for conversion");
   if(!std::isfinite(t)||!std::isfinite(s)||t<-5||t>50||s<0||s>60)throw std::runtime_error("Conversion requires temperature -5 to 50 C and salinity 0 to 60");
  }
  if(o.depth)depth[r]=fmt(realDepth(p,formula(2,p,t,s),formula(3,latitude,p,0)));
  for(auto&item:oxMg){const string&field=item.first;if(!hasValue(d,r,field))continue;if(air<=0||!std::isfinite(air))throw std::runtime_error("Air pressure is required for oxygen conversion");double v=oxygen(s,t,air)*val(d,r,field)/100.;item.second[r]=fmt(v);oxMl[field][r]=fmt(v*22.391/31.998);}
  if(o.par&&hasValue(d,r,"Par"))par[r]=fmt(val(d,r,"Par")*(o.parSource==2?10000:1));
 }
 if(o.conductivity){append(d,index(d,"S")<0?"S":"S_from_C",svals);if(!o.keepC)removeField(d,"C");d.metadata.push_back("# Salinity calculated from C/T/P using the original SIT PSS-78 routine. Conductivity "+string(o.keepC?"retained":"excluded by user"));}
 if(ctd){if(o.soundVelocity&&index(d,"Sound_velocity_SIT_m_s")<0)append(d,"Sound_velocity_SIT_m_s",sound);if(index(d,"Density_anomaly_SIT_kg_m3")<0)append(d,"Density_anomaly_SIT_kg_m3",density);}
 if(o.depth){
  append(d,"Depth_m",depth);
  d.metadata.push_back("# Real depth (m): P*10000 / (in-situ density * gravity); SIT fixed-position equation, EOS-80 density using S/T/P; latitude="+fmt(latitude)+(o.useGPS?" (GPS supplied by user)":" (SIT default; GPS not selected)"));
  if(o.useGPS)d.metadata.push_back("# GPS position: "+fmt(o.latitude)+", "+fmt(o.longitude)+"; Units=decimal degrees; North/East positive; Source=user");
  if(!o.keepP){removeField(d,"P");d.metadata.push_back("# Original pressure P excluded by user; depth retained in metres");}
 }
 for(auto&item:oxMg){string f=item.first;int mode=f=="OxR"?o.oxygen:o.oxygenOX;if(mode==1||mode==3)append(d,f+"_mg_L",item.second);if(mode==2||mode==3)append(d,f+"_mL_L",oxMl[f]);d.metadata.push_back("# Oxygen input: "+f+" percent saturation. Air pressure hPa="+fmt(air));}
 if(o.par){append(d,"Par_umol_m2_s",par);d.metadata.push_back("# PAR source unit: "+string(o.parSource==1?"uEinstein/(m2*s); multiplier=1":"uEinstein/(cm2*s); multiplier=10000")+"; Output=umol photons/(m2*s)");if(!o.keepPar)removeField(d,"Par");}
 if(o.suppliedT&&(o.depth||convertOxygen))d.metadata.push_back("# User-supplied temperature C="+fmt(o.temperature)+"; applied only where measured temperature is missing");
 if(o.suppliedS&&(o.depth||convertOxygen))d.metadata.push_back("# User-supplied salinity="+fmt(o.salinity)+"; applied only where measured/calculated salinity is missing");
 if(index(d,"OF")>=0)d.metadata.push_back("# OF: Fluorescence (ug/L), native SIT units; no rescaling");
 if(index(d,"OT")>=0)d.metadata.push_back("# OT: Turbidity (FTU), native SIT units; no rescaling");
 for(auto&choice:o.keepOriginal)if(!choice.second){removeField(d,choice.first);d.metadata.push_back("# Original field excluded by user: "+choice.first);}
 if(d.estimatedTime)d.metadata.push_back("# Full timestamps reconstructed from explicit logger header and interval; not measured per row");
}
