struct Wizard {sit::Data*d;sit::Choices choices;std::vector<std::string>fields;size_t step=0;bool done=false,accepted=false;HWND combo=0,t=0,s=0,ap=0;std::wstring gps,draftT,draftS,draftAP;};
static int selected(HWND h){return int(SendMessageW(h,CB_GETCURSEL,0,0));}
static bool checked(HWND h){return SendMessageW(h,BM_GETCHECK,0,0)==BST_CHECKED;}
static double inputNumber(HWND h){std::string s=sit::trim(utf8(caption(h)));std::replace(s.begin(),s.end(),',','.');return sit::number(s);}
static HWND checkBox(HWND h,const wchar_t*label,int y,int id,bool value){HWND c=control(h,L"BUTTON",label,BS_AUTOCHECKBOX|WS_TABSTOP,18,y,650,24,id);SendMessageW(c,BM_SETCHECK,value?BST_CHECKED:BST_UNCHECKED,0);return c;}
static HWND modelCombo(HWND h,int id,int y,const std::vector<std::wstring>&items,int value){HWND c=control(h,L"COMBOBOX",L"",CBS_DROPDOWNLIST|WS_TABSTOP|WS_VSCROLL,18,y,650,240,id);for(auto&s:items)SendMessageW(c,CB_ADDSTRING,0,LPARAM(s.c_str()));SendMessageW(c,CB_SETCURSEL,value,0);return c;}
static HWND scaleCombo(HWND h,int y,int value){control(h,L"STATIC",L"Temperature scale of the input values:",0,18,y,650,22,138);return modelCombo(h,131,y+24,{L"As recorded - original SIT convention (scale unspecified)",L"ITS-90 - modern measured Celsius (convert to T68 for legacy equations)",L"IPTS-68 - older measured Celsius (convert to T90 for modern equations)"},value);}
static std::wstring fieldTitle(const std::string&f){if(f=="__WATER")return L"Derived seawater properties";if(f=="C")return L"C - Conductivity (mS/cm)";if(f=="S")return L"S - Practical Salinity (PSS-78)";if(f=="T")return L"T - Temperature (Celsius)";if(f=="P")return L"P - Sea pressure (dbar)";return fieldLabel(f);}
static bool needsPosition(const Wizard&w){return w.choices.depth||sit::gswRequired(w.choices)||(w.choices.soundVelocity&&(w.choices.soundModel==2||w.choices.soundModel==4));}
static const wchar_t* helpTopic(const Wizard&w){if(w.step>=w.fields.size())return L"TEOS-10 and other choices";auto f=w.fields[w.step];if(f=="C"||f=="S")return L"Conductivity and salinity";if(f=="T")return L"Temperature";if(f=="P")return L"Depth: modes and fjords";if(f=="__WATER")return L"Sound velocity";if(f=="OX"||f=="OxR")return L"Oxygen: saturation and units";if(f=="Par")return L"PAR and light units";if(f=="OF")return L"Fluorescence";if(f=="OT")return L"Turbidity: FTU, NTU and FNU";return L"Conversions and formulas";}
static void updateFieldControls(HWND h,Wizard&w){
 if(w.step<w.fields.size()){
  auto f=w.fields[w.step];int mode=selected(w.combo);
  if(f=="C")EnableWindow(GetDlgItem(h,132),mode>0);
  if(f=="P")for(int id:{140,141})ShowWindow(GetDlgItem(h,id),mode==3||mode==5?SW_SHOW:SW_HIDE);
  if(f=="Par")for(int id:{124,125})ShowWindow(GetDlgItem(h,id),mode?SW_SHOW:SW_HIDE);
  if(f=="OX"||f=="OxR")EnableWindow(GetDlgItem(h,134),mode>0);
 }else if(GetDlgItem(h,121)){
  bool use=checked(GetDlgItem(h,121));for(int id:{122,128,126})ShowWindow(GetDlgItem(h,id),use?SW_SHOW:SW_HIDE);
 }
}
static void wizardPage(HWND h,Wizard&w){
 for(HWND c=GetWindow(h,GW_CHILD);c;){HWND next=GetWindow(c,GW_HWNDNEXT);DestroyWindow(c);c=next;}w.t=w.s=w.ap=0;
 control(h,L"STATIC",L"Choose the method, units and original columns to retain. Quick guide explains each method.",0,18,14,650,32,100);
 if(w.step<w.fields.size()){
  auto f=w.fields[w.step];std::wstring title=L"Step "+wide(std::to_string(w.step+1))+L" of "+wide(std::to_string(w.fields.size()))+L": "+fieldTitle(f);
  control(h,L"STATIC",title.c_str(),0,18,52,650,26,101);std::vector<std::wstring>items;int choice=0;std::wstring note;
  if(f=="__WATER"){
   items={L"Do not add sound velocity",L"Sound velocity - original SIT / UNESCO-family",L"Sound velocity - TEOS-10 exact Gibbs",L"Sound velocity - Mackenzie 1981",L"Sound velocity - Del Grosso 1974",L"Sound velocity - NPL / Leroy 2008"};choice=w.choices.soundVelocity?w.choices.soundModel+1:0;
   note=L"Mackenzie and NPL use the selected depth method, or UNESCO depth if pressure is kept. Model validity limits are checked for every row.";
   control(h,L"STATIC",L"Density output:",0,18,190,650,22,136);
   modelCombo(h,135,215,{L"EOS-80 in-situ density anomaly (original SIT)",L"EOS-80 Sigma T (at zero sea pressure)",L"Older SD200W S/T density anomaly",L"TEOS-10 exact density and potential density anomaly sigma0"},w.choices.densityModel);
   scaleCombo(h,265,w.choices.temperatureScale);
   control(h,L"STATIC",L"The density output choice does not change the selected depth equation. Fixed-position and SIT-style profile depth always use EOS-80 in-situ density. TEOS-10 profile depth uses TEOS-10 density.",0,18,345,650,66,139);
   control(h,L"BUTTON",L"Density guide",WS_TABSTOP,18,432,140,28,143);
  }else if(f=="C"){
   items={L"Keep conductivity C (mS/cm)",L"C to S - original SIT PSS-78",L"C to SP - GSW PSS-78 with modified Hill below SP=2",L"C to SP and SA - GSW PSS-78 / TEOS-10"};choice=w.choices.conductivity;
   note=L"Requires C, T and P in each row. SP is Practical Salinity; SA is Absolute Salinity in g/kg. The input temperature scale is selected on the T/conditions page.";
   checkBox(h,L"Use this calculated salinity for the other conversions (instead of existing S)",215,132,w.choices.useCalculatedS);
  }else if(f=="S"){
   items={L"Keep Practical Salinity S (PSS-78)",L"Keep SP and add Absolute Salinity SA / Conservative Temperature CT"};choice=w.choices.absoluteSalinity?1:0;
   note=L"S is a derived Practical Salinity value, not conductivity. SA has a different meaning and unit; it is added as a separate column. See the SAIV CTD recommendation in the guide.";
  }else if(f=="T"){
   items={L"Keep temperature in Celsius",L"Add Fahrenheit (original Celsius * 9/5 + 32)"};choice=w.choices.fahrenheit?1:0;scaleCombo(h,215,w.choices.temperatureScale);
   note=L"A reported temperature is already calibrated. Kelvin constant / Steinhart-Hart changes require the original resistance and calibration coefficients; they are not applied again here.";
  }else if(f=="P"){
   items={L"Keep pressure P (dbar; no depth calculation)",L"Depth - SIT fixed position, EOS-80 density",L"Depth - UNESCO 1983, pressure and latitude",L"Depth - SIT-style profiling, EOS-80 endpoint layers",L"Depth - GSW reference ocean (pressure and latitude)",L"Depth - TEOS-10 profile integration (trapezoid layers)"};choice=w.choices.depth;
   note=L"Pressure must already be sea pressure in dbar. Latitude/position is reviewed before conversion. Profile methods require one continuous cast and use its selected traversal direction.";
   control(h,L"STATIC",L"Profile traversal (one cast per file):",0,18,215,650,22,140);
   modelCombo(h,141,242,{L"Forward / downcast - first to last measurement",L"Reverse / upcast - last to first measurement"},w.choices.profileDirection);
  }else if(f=="OX"||f=="OxR"){
   items={L"Keep oxygen saturation (%)",L"Add oxygen in mg/L",L"Add oxygen in mL/L",L"Add oxygen in mg/L and mL/L",L"Add oxygen in micromol/L",L"Add oxygen in micromol/kg",L"Add all four concentration units"};choice=f=="OX"?w.choices.oxygenOX:w.choices.oxygen;
   note=L"Input is reported percent saturation. Unit conversion does not replace the sensor's pressure compensation, calibration or response correction.";
   control(h,L"STATIC",L"Oxygen solubility model:",0,18,215,650,22,137);
   modelCombo(h,134,242,{L"Original SIT - temperature, salinity and atmospheric pressure",L"GSW Garcia-Gordon - equilibrium at 1 standard atmosphere"},f=="OX"?w.choices.oxygenOXModel:w.choices.oxygenModel);
   control(h,L"STATIC",L"GSW uses potential temperature and reports a mass-based solubility; in-situ TEOS-10 density converts it to per-litre units. File air pressure is not applied to the 1-atmosphere model. See the guide before comparing the two.",0,18,292,650,72,139);
  }else if(f=="Par"){
   items={L"Keep PAR",L"Convert to micromol photons/(m2*s)"};choice=w.choices.par;note=L"1 microeinstein = 1 micromole of photons. Select the area unit; a typical reading does not establish its unit.";
   control(h,L"STATIC",L"Source area unit:",0,18,215,650,22,125);modelCombo(h,124,242,{L"Select source unit...",L"uEinstein/(m2*s) - multiply by 1",L"uEinstein/(cm2*s) - multiply by 10000"},w.choices.parSource);
  }else {items={L"Keep original values"};note=f=="OT"?L"FTU is retained. No universal FTU-to-NTU/FNU conversion exists; changing the label requires the sensor's optical-method specification.":f=="OF"?L"Reported fluorescence is retained without scaling. Recalibration requires sensor-specific raw data and coefficients.":L"This field is retained without an additional model conversion.";}
  w.combo=modelCombo(h,102,83,items,choice);control(h,L"STATIC",note.c_str(),0,18,122,650,59,103);
  if(f!="__WATER")checkBox(h,(L"Keep original "+wide(f)+L" values").c_str(),183,120,!w.choices.keepOriginal.count(f)||w.choices.keepOriginal[f]);
 }else{
  control(h,L"STATIC",L"Review supporting values and calculation conventions",0,18,52,650,26,101);int y=85;
  if(sit::needsWater(w.choices)&&!sit::complete(*w.d,"T")){control(h,L"STATIC",L"Missing temperature (Celsius):",0,18,y+3,400,23,1100);w.t=control(h,L"EDIT",w.draftT.c_str(),WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,470,y,198,25,110);y+=36;}
  if(sit::needsWater(w.choices)&&!sit::canSal(*w.d)){control(h,L"STATIC",L"Missing Practical Salinity (SP):",0,18,y+3,400,23,1101);w.s=control(h,L"EDIT",w.draftS.c_str(),WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,470,y,198,25,111);y+=36;}
  if(sit::needsAir(w.choices)&&w.choices.air<=0){control(h,L"STATIC",L"Atmospheric pressure (hPa / mbar):",0,18,y+3,400,23,1102);w.ap=control(h,L"EDIT",w.draftAP.c_str(),WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,470,y,198,25,112);y+=36;}
  scaleCombo(h,y,w.choices.temperatureScale);y+=67;
  if(sit::gswRequired(w.choices)){control(h,L"STATIC",L"Absolute Salinity composition assumption:",0,18,y,650,22,145);modelCombo(h,144,y+24,{L"Reference Composition (SA=SR; no geographic atlas anomaly)",L"Geographic GSW atlas - requires the actual GPS position"},w.choices.atlas?1:0);y+=65;}
  if(needsPosition(w)){
   checkBox(h,L"Use supplied GPS position (otherwise default latitude 45.508368287 degrees)",y,121,w.choices.useGPS);y+=30;
   control(h,L"STATIC",L"Latitude, longitude in decimal degrees (north/east positive):",0,18,y,650,22,126);y+=24;
   control(h,L"EDIT",w.gps.c_str(),WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,18,y,535,25,122);control(h,L"BUTTON",L"Paste",WS_TABSTOP,566,y,102,25,128);y+=38;
  }
  bool properties=sit::canSal(*w.d)&&sit::complete(*w.d,"T")&&sit::complete(*w.d,"P");
  std::wstring summary=L"Depth: "+wide(sit::depthName(w.choices.depth))+L"\r\nDensity: "+(properties?wide(sit::densityName(w.choices.densityModel)):L"not added (requires complete S/T/P or C/T/P)")+L"\r\nSound: "+(properties&&w.choices.soundVelocity?wide(sit::soundName(w.choices.soundModel)):L"not added");
  control(h,L"STATIC",summary.c_str(),0,18,y+4,650,62,103);
 }
 control(h,L"BUTTON",L"Quick guide",WS_TABSTOP,18,570,136,30,133);
 if(w.step>=w.fields.size()&&needsPosition(w))control(h,L"BUTTON",L"Google Maps",WS_TABSTOP,170,570,130,30,129);
 HWND back=control(h,L"BUTTON",L"< Back",WS_TABSTOP,356,570,92,30,3);EnableWindow(back,w.step>0);
 control(h,L"BUTTON",L"Cancel",WS_TABSTOP,466,570,92,30,IDCANCEL);
 control(h,L"BUTTON",w.step<w.fields.size()?L"Next >":L"Convert",WS_TABSTOP|BS_DEFPUSHBUTTON,576,570,92,30,IDOK);
 updateFieldControls(h,w);SetFocus(w.step<w.fields.size()?w.combo:w.t?w.t:w.s?w.s:w.ap?w.ap:GetDlgItem(h,IDOK));
}
static void rememberField(HWND h,Wizard&w,bool validate){
 if(w.step>=w.fields.size())return;auto f=w.fields[w.step];int value=selected(w.combo);
 if(f!="__WATER")w.choices.keepOriginal[f]=checked(GetDlgItem(h,120));
 if(f=="__WATER"){w.choices.soundVelocity=value>0;w.choices.soundModel=value>0?value-1:0;w.choices.densityModel=selected(GetDlgItem(h,135));}
 if(f=="T"||f=="__WATER")w.choices.temperatureScale=selected(GetDlgItem(h,131));
 if(f=="T")w.choices.fahrenheit=value==1;
 if(f=="C"){w.choices.conductivity=value;w.choices.keepC=checked(GetDlgItem(h,120));w.choices.useCalculatedS=value&&checked(GetDlgItem(h,132));if(validate&&value&&(!sit::complete(*w.d,"C")||!sit::complete(*w.d,"T")||!sit::complete(*w.d,"P")))throw std::runtime_error("C to S requires C/T/P in every row");}
 if(f=="S")w.choices.absoluteSalinity=value>0;
 if(f=="P"){w.choices.depth=value;w.choices.keepP=checked(GetDlgItem(h,120));w.choices.profileDirection=selected(GetDlgItem(h,141));}
 if(f=="Par"){w.choices.par=value;w.choices.keepPar=checked(GetDlgItem(h,120));w.choices.parSource=selected(GetDlgItem(h,124));if(validate&&value&&!w.choices.parSource)throw std::runtime_error("Select the source PAR area unit");}
 if(f=="OX"){w.choices.oxygenOX=value;w.choices.oxygenOXModel=value?selected(GetDlgItem(h,134)):0;}
 if(f=="OxR"){w.choices.oxygen=value;w.choices.oxygenModel=value?selected(GetDlgItem(h,134)):0;}
}
static void rememberConditions(HWND h,Wizard&w,bool validate){
 w.choices.temperatureScale=selected(GetDlgItem(h,131));if(GetDlgItem(h,144))w.choices.atlas=selected(GetDlgItem(h,144))==1;
 if(GetDlgItem(h,121)){w.choices.useGPS=checked(GetDlgItem(h,121));w.gps=caption(GetDlgItem(h,122));if(validate&&w.choices.useGPS){auto p=sit::gpsPair(utf8(w.gps));w.choices.latitude=p.first;w.choices.longitude=p.second;}}
 if(w.t)w.draftT=caption(w.t);if(w.s)w.draftS=caption(w.s);if(w.ap)w.draftAP=caption(w.ap);
 if(!validate)return;
 if(w.t){w.choices.temperature=inputNumber(w.t);if(w.choices.temperature< -5||w.choices.temperature>50)throw std::runtime_error("Temperature must be -5..50 C");w.choices.suppliedT=true;}
 if(w.s){w.choices.salinity=inputNumber(w.s);if(w.choices.salinity<0||w.choices.salinity>60)throw std::runtime_error("SP must be 0..60");w.choices.suppliedS=true;}
 if(w.ap){w.choices.air=inputNumber(w.ap);if(w.choices.air<500||w.choices.air>1200)throw std::runtime_error("Atmospheric pressure must be 500..1200 hPa");}
 if(sit::modernTemperatureRequired(w.choices)&&!w.choices.temperatureScale)throw std::runtime_error("Select ITS-90 or IPTS-68 for the chosen modern method; the guide explains the difference");
 if(w.choices.atlas&&!w.choices.useGPS)throw std::runtime_error("The geographic atlas requires the actual GPS position; alternatively choose Reference Composition");
}
static LRESULT CALLBACK wizardProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){
 Wizard*w=(Wizard*)GetWindowLongPtrW(h,GWLP_USERDATA);if(msg==WM_NCCREATE){w=(Wizard*)((CREATESTRUCTW*)lp)->lpCreateParams;SetWindowLongPtrW(h,GWLP_USERDATA,LONG_PTR(w));}if(!w)return DefWindowProcW(h,msg,wp,lp);
 try{if(msg==WM_COMMAND){int id=LOWORD(wp);
  if(id==133||id==143){guideShow(h,id==143?L"Density and Sigma T":helpTopic(*w));return 0;}
  if(id==129){if((INT_PTR)ShellExecuteW(h,L"open",L"https://www.google.com/maps",0,0,SW_SHOWNORMAL)<=32)error(h,"Could not open Google Maps");return 0;}
  if(id==128){HWND edit=GetDlgItem(h,122);SendMessageW(edit,EM_SETSEL,0,-1);SendMessageW(edit,WM_PASTE,0,0);return 0;}
  if((id==102&&HIWORD(wp)==CBN_SELCHANGE)||id==121){updateFieldControls(h,*w);return 0;}
  if(id==IDCANCEL){w->done=true;DestroyWindow(h);return 0;}
  if(id==3&&w->step>0){if(w->step<w->fields.size())rememberField(h,*w,false);else rememberConditions(h,*w,false);--w->step;wizardPage(h,*w);return 0;}
  if(id==IDOK){if(w->step<w->fields.size()){rememberField(h,*w,true);++w->step;wizardPage(h,*w);}else{rememberConditions(h,*w,true);w->accepted=w->done=true;DestroyWindow(h);}return 0;}
 }if(msg==WM_CLOSE){w->done=true;DestroyWindow(h);return 0;}}catch(const std::exception&e){error(h,e.what());return 0;}return DefWindowProcW(h,msg,wp,lp);
}
static bool choose(HWND owner,sit::Data&data,sit::Choices&choices,const sit::Choices*previous=0){
 Wizard w;w.d=&data;if(previous)w.choices=*previous;w.choices.air=data.air;
 for(auto&f:data.fields)if(f!="COUNT"&&f!="DATE"&&f!="TIME")w.fields.push_back(f);
 if(sit::canSal(data)&&sit::complete(data,"T")&&sit::complete(data,"P"))w.fields.push_back("__WATER");
 for(auto&m:data.metadata){if(m.find("PAR source unit: uEinstein/(m2*s)")!=std::string::npos)w.choices.parSource=1;if(m.find("PAR source unit: uEinstein/(cm2*s)")!=std::string::npos)w.choices.parSource=2;}
 if(w.fields.empty())throw std::runtime_error("No sensor fields found");if(previous)w.step=w.fields.size();
 RECT r;GetWindowRect(owner,&r);int x=std::max(0,std::min(int(r.left+30),GetSystemMetrics(SM_CXSCREEN)-710)),y=std::max(0,std::min(int(r.top+20),GetSystemMetrics(SM_CYSCREEN)-650));
 HWND h=CreateWindowExW(WS_EX_DLGMODALFRAME,L"SITImportChoices",L"SAIV IT - Convert fields",WS_CAPTION|WS_SYSMENU,x,y,710,650,owner,0,instance,&w);if(!h)throw std::runtime_error("Cannot create conversion window");
 EnableWindow(owner,FALSE);wizardPage(h,w);ShowWindow(h,SW_SHOW);MSG m;while(!w.done&&GetMessageW(&m,0,0,0)>0)if(!IsDialogMessageW(h,&m)){TranslateMessage(&m);DispatchMessageW(&m);}EnableWindow(owner,TRUE);SetActiveWindow(owner);choices=w.choices;return w.accepted;
}
