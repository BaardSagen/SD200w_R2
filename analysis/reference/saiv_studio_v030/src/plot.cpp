#include "app.hpp"
#include <algorithm>
#include <cmath>
namespace saiv {
static std::string axisLabel(const std::string&name){
 if(name=="T")return "Temperature (C)";if(name=="T_degF")return "Temperature (F)";if(name=="P")return "Pressure (dbar)";if(name=="Depth_m")return "Depth (m)";
 if(name=="S"||name=="S_from_C"||name=="Salinity_SIT")return "Salinity (PSS-78)";if(name=="C")return "Conductivity (mS/cm)";
 if(name=="OF")return "Fluorescence (ug/L)";if(name=="OT")return "Turbidity (FTU)";if(name=="OX"||name=="OxR")return name+" (%)";
 if(name=="c"||name=="Sound_velocity_SIT_m_s")return "Sound velocity (m/s)";if(name=="Density_anomaly_SIT_kg_m3")return "Density - 1000 (kg/m3)";return name;
}
void App::plot(const Table&t,int xc,int yc,bool profile,ImVec2 size){
 size.x=std::max(170.f,size.x);size.y=std::max(145.f,size.y);auto origin=ImGui::GetCursorScreenPos();unsigned id=ImGui::GetID("##plot");ImGui::InvisibleButton("##plot",size);auto*d=ImGui::GetWindowDrawList();ImVec2 a(origin.x+65,origin.y+28),b(origin.x+size.x-18,origin.y+size.y-43);auto text=IM_COL32(76,96,116,255);d->AddRectFilled(origin,ImVec2(origin.x+size.x,origin.y+size.y),IM_COL32(255,255,255,255),8);d->AddRect(origin,ImVec2(origin.x+size.x,origin.y+size.y),IM_COL32(215,226,233,255),8);
 if(yc<0||yc>=int(t.columns.size())){d->AddText(ImVec2(a.x,a.y+20),text,"Channel not present in this dataset");return;}
 auto times=xc==-2?measurementSeconds(t):std::vector<double>();auto values=[&](size_t i){double x=xc==-2?times[i]:xc<0?double(i+1):t.value(i,xc),y=t.value(i,yc);if(profile)std::swap(x,y);return std::pair<double,double>(x,y);};
 double xmin=0,xmax=0,ymin=0,ymax=0;size_t valid=0;for(size_t i=0;i<t.rows.size();i++){auto v=values(i);double x=v.first,y=v.second;if(!std::isfinite(x)||!std::isfinite(y))continue;if(!valid){xmin=xmax=x;ymin=ymax=y;}xmin=std::min(xmin,x);xmax=std::max(xmax,x);ymin=std::min(ymin,y);ymax=std::max(ymax,y);valid++;}
 if(!valid){d->AddText(ImVec2(a.x,a.y+20),text,"No valid numeric pairs to plot");return;}if(xmin==xmax){xmin-=.5;xmax+=.5;}if(ymin==ymax){ymin-=.5;ymax+=.5;}
 auto&zoom=zooms_[id];bool hovered=ImGui::IsItemHovered();if(hovered&&ImGui::IsMouseDoubleClicked(0))zoom.active=false;if(zoom.active){if(profile){ymin=zoom.lo;ymax=zoom.hi;}else{xmin=zoom.lo;xmax=zoom.hi;}}
 if(hovered&&ImGui::GetIO().MouseWheel!=0){double lo=profile?ymin:xmin,hi=profile?ymax:xmax;auto mouse=ImGui::GetMousePos();double f=std::clamp(profile?double(mouse.y-a.y)/(b.y-a.y):double(mouse.x-a.x)/(b.x-a.x),0.,1.);double c=lo+(hi-lo)*f,range=(hi-lo)*pow(.8,ImGui::GetIO().MouseWheel);if(range>1e-9&&range<1e12){zoom={true,c-range*f,c+range*(1-f)};if(profile){ymin=zoom.lo;ymax=zoom.hi;}else{xmin=zoom.lo;xmax=zoom.hi;}}}
 auto px=[&](double x){return a.x+float((x-xmin)/(xmax-xmin))*(b.x-a.x);};auto py=[&](double y){double f=(y-ymin)/(ymax-ymin);return profile?a.y+float(f)*(b.y-a.y):b.y-float(f)*(b.y-a.y);};
 std::string axis=xc==-2?(t.column("DATE")>=0&&t.column("TIME")>=0?"Elapsed time (s)":"Measurement index"):xc<0?"Measurement number":axisLabel(t.columns[xc]);std::string xl=profile?axisLabel(t.columns[yc]):axis,yl=profile?axis:axisLabel(t.columns[yc]);d->AddText(ImVec2(a.x,origin.y+8),text,yl.c_str());d->AddText(ImVec2(a.x+(b.x-a.x-ImGui::CalcTextSize(xl.c_str()).x)/2,b.y+25),text,xl.c_str());
 for(int i=0;i<=4;i++){float f=i/4.f,xx=a.x+f*(b.x-a.x),yy=a.y+f*(b.y-a.y);d->AddLine(ImVec2(xx,a.y),ImVec2(xx,b.y),IM_COL32(229,237,242,255));d->AddLine(ImVec2(a.x,yy),ImVec2(b.x,yy),IM_COL32(229,237,242,255));char s[48];sprintf_s(s,"%.4g",xmin+(xmax-xmin)*f);d->AddText(ImVec2(xx-12,b.y+7),text,s);sprintf_s(s,"%.4g",profile?ymin+(ymax-ymin)*f:ymax-(ymax-ymin)*f);d->AddText(ImVec2(origin.x+4,yy-7),text,s);}
 d->PushClipRect(a,b,true);bool previous=false;ImVec2 last;size_t stride=std::max<size_t>(1,t.rows.size()/20000);for(size_t i=0;i<t.rows.size();i++){auto v=values(i);if(!std::isfinite(v.first)||!std::isfinite(v.second)){previous=false;continue;}if(i%stride&&i+1<t.rows.size())continue;ImVec2 next(px(v.first),py(v.second));if(previous)d->AddLine(last,next,IM_COL32(12,117,169,255),1.8f);if(showPoints_||!previous)d->AddCircleFilled(next,2.3f,IM_COL32(12,117,169,255));last=next;previous=true;}
 if(hovered){auto m=ImGui::GetMousePos();if(m.x>=a.x&&m.x<=b.x&&m.y>=a.y&&m.y<=b.y){double x=xmin+(xmax-xmin)*(m.x-a.x)/(b.x-a.x),y=profile?ymin+(ymax-ymin)*(m.y-a.y)/(b.y-a.y):ymax-(ymax-ymin)*(m.y-a.y)/(b.y-a.y);d->AddLine(ImVec2(m.x,a.y),ImVec2(m.x,b.y),IM_COL32(45,105,140,100));d->AddLine(ImVec2(a.x,m.y),ImVec2(b.x,m.y),IM_COL32(45,105,140,100));ImGui::BeginTooltip();ImGui::Text("%s: %.6g",xl.c_str(),x);ImGui::Text("%s: %.6g",yl.c_str(),y);ImGui::EndTooltip();}}d->PopClipRect();
}
}
