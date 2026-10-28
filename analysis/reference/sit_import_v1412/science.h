#ifndef SIT_SCIENCE_H
#define SIT_SCIENCE_H
#include "vendor/gsw/gswteos-10.h"
#include <cmath>
#include <stdexcept>
#include <string>
namespace sitmodels {
inline double valid(double v,const char*name){if(!std::isfinite(v)||std::abs(v)>1e10)throw std::runtime_error(std::string(name)+" is outside the supported domain");return v;}
inline double t90(double t,int scale){return scale==2?t/1.00024:t;}
inline double t68(double t,int scale){return scale==1?t*1.00024:t;}
inline double gravity(double lat,double p){double x=std::sin(lat*3.14159265358979323846/180);x*=x;return 9.780318*(1+(.0052788+.0000236*x)*x)+1.092e-6*p;}
inline double unescoDepth(double p,double lat){return (((-1.82e-15*p+2.279e-10)*p-2.2512e-5)*p+9.72659)*p/gravity(lat,p);}
inline double oldDensity(double S,double T){double s=S-35,q=28.1263+.806*s+.00023*s*s+.0000068*s*s*s;
 double a=(4.7867*T-.098185*T*T+.0010843*T*T*T)*.001,b=(18.03*T-.8164*T*T+.01667*T*T*T)*.000001,w=-(T+283)*(T-3.98)*(T-3.98)/(503.57*(T+67.26));return (1-a+(q-.1324)*b)*(q+.1324)+w;}
struct Water {double sa,ct,rho,sigma0,sound,o2;};
inline Water water(double sp,double temp90,double p,double lon,double lat,bool atlas){
 if(sp<0||sp>42||temp90< -2||temp90>40||p<0||p>10000)throw std::runtime_error("TEOS-10 requires SP 0..42, temperature -2..40 C and sea pressure 0..10000 dbar in this converter");
 Water w;w.sa=valid(atlas?gsw_sa_from_sp(sp,p,lon,lat):gsw_sr_from_sp(sp),"Absolute Salinity");
 w.ct=valid(gsw_ct_from_t(w.sa,temp90,p),"Conservative Temperature");
 // Exact Gibbs routines avoid silent extrapolation of the 75-term funnel fit.
 w.rho=valid(gsw_rho_t_exact(w.sa,temp90,p),"TEOS-10 density");
 double pt=gsw_pt0_from_t(w.sa,temp90,p);
 w.sigma0=valid(gsw_rho_t_exact(w.sa,pt,0)-1000,"TEOS-10 sigma0");
 w.sound=valid(gsw_sound_speed_t_exact(w.sa,temp90,p),"TEOS-10 sound speed");
 // With reference composition, use the explicit SP/pt interface, avoiding
 // reinterpreting SA through an atlas at a fictitious geographic position.
 w.o2=valid(gsw_o2sol_sp_pt(sp,pt),"Garcia-Gordon oxygen solubility");return w;
}
inline double mackenzie(double S,double T68,double z){
 if(S<25||S>40||T68<2||T68>30||z<0||z>8000)throw std::runtime_error("Mackenzie requires S 25..40, T68 2..30 C, depth 0..8000 m; choose another sound-speed method for these rows");
 double t=T68;return 1448.96+4.591*t-.05304*t*t+.0002374*t*t*t+1.340*(S-35)+.01630*z+1.675e-7*z*z-.01025*t*(S-35)-7.139e-13*t*z*z*z;
}
inline double delGrosso(double S,double T68,double dbar){
 // Original 1974 coefficients, IPTS-68, pressure in kgf/cm2.
 // 1 kgf/cm2 = 9.80665 dbar; this is a unit conversion, not local gravity.
 double t=T68,p=dbar/9.80665;
 if(S<30||S>40||t<0||t>30||p<0||p>1000)throw std::runtime_error("Del Grosso requires S 30..40, T68 0..30 C, pressure 0..9806.65 dbar; choose another method for these rows");
 return 1402.392+(5.01109398873-.0550946843172*t+.000221535969240*t*t)*t+(1.32952290781+.000128955756844*S)*S
  +(.156059257041+.0000244998688441*p-.00000000883392332513*p*p)*p
  -.0127562783426*t*S+.00635191613389*t*p+2.65484716608e-8*t*t*p*p-1.59349479045e-6*t*p*p
  +5.22116437235e-10*t*p*p*p-4.38031096213e-7*t*t*t*p-1.61674495909e-9*S*S*p*p
  +.0000968403156410*t*t*S+4.85639620015e-6*t*S*S*p-.000340597039004*t*S*p;
}
inline double npl(double S,double t,double z,double lat){
 if(S<0||S>42||t< -2||t>40||z<0||z>11000)throw std::runtime_error("NPL requires S 0..42, temperature -2..40 C and depth 0..11000 m in this converter");
 return 1402.5+5*t-.0544*t*t+.00021*t*t*t+1.33*S-.0123*S*t+.000087*S*t*t+.0156*z+2.55e-7*z*z-7.3e-12*z*z*z
  +1.2e-6*z*(std::abs(lat)-45)-9.5e-13*t*z*z*z+3e-7*t*t*z+1.43e-5*S*z;
}
}
#endif
