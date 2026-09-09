from pathlib import Path
r=Path(__file__).resolve().parents[1]/'saiv-studio'
p=r/'src/native_dialogs.cpp';s=p.read_text();marker='#include "sit/wizard.inc"';s=s.replace(marker,'static LRESULT studioControlColor(WPARAM wp){HDC dc=reinterpret_cast<HDC>(wp);SetTextColor(dc,RGB(26,38,54));SetBkMode(dc,TRANSPARENT);return reinterpret_cast<LRESULT>(GetStockObject(WHITE_BRUSH));}\n\n'+marker);p.write_text(s)
for name in ('wizard.inc','merge_ui.inc'):
 p=r/'src/sit'/name;s=p.read_text();needle='WPARAM wp,LPARAM lp){';s=s.replace(needle,needle+'\n if(msg==WM_CTLCOLORSTATIC||msg==WM_CTLCOLORBTN)return studioControlColor(wp);',1);s=s.replace('(HBRUSH)(COLOR_BTNFACE+1)','(HBRUSH)(COLOR_WINDOW+1)').replace('calculated by SIT.','using SIT routines.');p.write_text(s)
p=r/'src/studio_ui.cpp';s=p.read_text();s=s.replace('if(selected()){if(page_!=1)','if(selected()&&page_!=2){if(page_!=1)')
s=s.replace('std::isfinite(statistics(d.graph,int(i)).mean)', 'd.graph.columns[i]!="COUNT"&&d.graph.columns[i]!="SERIES"&&std::isfinite(statistics(d.graph,int(i)).mean)')
p.write_text(s)
p=r/'src/plot.cpp';s=p.read_text();marker='void App::plot';s=s.replace(marker,'''static std::string axisLabel(const std::string&name){
 if(name=="T")return "Temperature (C)";if(name=="T_degF")return "Temperature (F)";if(name=="P")return "Pressure (dbar)";if(name=="Depth_m")return "Depth (m)";
 if(name=="S"||name=="S_from_C"||name=="Salinity_SIT")return "Salinity (PSS-78)";if(name=="C")return "Conductivity (mS/cm)";
 if(name=="OF")return "Fluorescence (ug/L)";if(name=="OT")return "Turbidity (FTU)";if(name=="OX"||name=="OxR")return name+" (%)";
 if(name=="c"||name=="Sound_velocity_SIT_m_s")return "Sound velocity (m/s)";if(name=="Density_anomaly_SIT_kg_m3")return "Density - 1000 (kg/m3)";return name;
}
'''+marker,1)
s=s.replace('t.columns[xc];std::string xl=profile?t.columns[yc]:axis,yl=profile?axis:t.columns[yc];','axisLabel(t.columns[xc]);std::string xl=profile?axisLabel(t.columns[yc]):axis,yl=profile?axis:axisLabel(t.columns[yc]);');p.write_text(s)
p=r/'src/app.cpp';s=p.read_text().replace('auto p=fileDialog(true,heading,extension,L"Data files\\0*.csv;*.txt;*.log\\0All files\\0*.*\\0\\0");','auto p=fileDialog(true,heading,extension,wcscmp(extension,L"csv")==0?L"CSV measurements\\0*.csv\\0\\0":L"Text files\\0*.txt;*.log\\0All files\\0*.*\\0\\0");')
s=s.replace('notice_="Ready. Connect an instrument, open data, or try the demonstration."','notice_="Ready. Choose Autodetect to connect an instrument."');p.write_text(s)
# Remove an unused pressure-only depth approximation. Real depth is the SIT fixed-position calculation.
p=r/'src/sit_compat.hpp';s=p.read_text().replace('double sitDepth(double latitude,double pressure);\n','');p.write_text(s)
p=r/'src/sit_compat.cpp';s=p.read_text();s='\n'.join(line for line in s.split('\n') if not line.startswith('double sitDepth('));p.write_text(s)
