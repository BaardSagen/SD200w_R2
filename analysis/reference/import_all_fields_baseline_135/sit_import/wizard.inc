struct Wizard {
 sit::Data*d; sit::Choices choices; std::vector<std::string> fields;
 size_t step=0; bool done=false,accepted=false,environment=false;
 HWND combo=0,t=0,s=0,ap=0; std::wstring gps;
};
static std::wstring fieldTitle(const std::string&f){
 if(f=="C")return L"C - Conductivity (mS/cm)";
 if(f=="S"||f=="S_from_C")return wide(f)+L" - Salinity (PSS-78)";
 if(f=="T")return L"T - Temperature (\u00b0C, Celsius)";
 if(f=="P")return L"P - Pressure (dbar)";
 if(f=="OF")return L"OF - Fluorescence (\u00b5g/L)";
 if(f=="OT")return L"OT - Turbidity (FTU)";
 if(f=="Par")return L"Par - Photosynthetically Active Radiation (output: \u00b5mol photons/(m\u00b2\u00b7s))";
 if(f=="OxR")return L"OxR - RINKO Oxygen (% saturation)";
 if(f=="OX")return L"OX - SAIV205 Oxygen (% saturation)";
 if(f=="Tilt")return L"Tilt - Instrument tilt";
 return fieldLabel(f);
}
static int selected(HWND h){return int(SendMessageW(h,CB_GETCURSEL,0,0));}
static bool checked(HWND h){return SendMessageW(h,BM_GETCHECK,0,0)==BST_CHECKED;}
static double inputNumber(HWND h){std::string s=sit::trim(utf8(caption(h)));std::replace(s.begin(),s.end(),',','.');return sit::number(s);}
static HWND checkBox(HWND h,const wchar_t*label,int y,int id,bool value){HWND c=control(h,L"BUTTON",label,BS_AUTOCHECKBOX|WS_TABSTOP,18,y,552,23,id);SendMessageW(c,BM_SETCHECK,value?BST_CHECKED:BST_UNCHECKED,0);return c;}
static void updateFieldControls(HWND h,Wizard&w){
 if(w.step>=w.fields.size())return;
 std::string f=w.fields[w.step];bool convert=selected(w.combo)>0;

 if(f=="P"){
  ShowWindow(GetDlgItem(h,121),convert?SW_SHOW:SW_HIDE);
  bool gps=convert&&checked(GetDlgItem(h,121));
  for(int id:{122,126,128,129})ShowWindow(GetDlgItem(h,id),gps?SW_SHOW:SW_HIDE);
  SetWindowTextW(GetDlgItem(h,103),gps?L"Depth uses salinity, temperature, pressure and latitude. Both coordinates will be saved above the data.":L"Depth uses salinity, temperature and pressure. Without GPS, SIT's default latitude (45.508368287\u00b0) is used and recorded.");
 }
 if(f=="Par"){ShowWindow(GetDlgItem(h,124),convert?SW_SHOW:SW_HIDE);ShowWindow(GetDlgItem(h,125),convert?SW_SHOW:SW_HIDE);}
}
static bool needsConditions(const Wizard&w){
 bool oxygen=sit::wantsOxygen(*w.d,w.choices);
 return (w.choices.depth||oxygen)&&(!sit::complete(*w.d,"T")||!sit::canSal(*w.d)||(oxygen&&w.choices.air<=0));
}
static void wizardPage(HWND h,Wizard&w){
 for(HWND c=GetWindow(h,GW_CHILD);c;){HWND next=GetWindow(c,GW_HWNDNEXT);DestroyWindow(c);c=next;}
 control(h,L"STATIC",L"Choose conversions and which original columns to keep.",0,18,14,570,30,100);
 w.t=w.s=w.ap=0;
 if(w.step<w.fields.size()){
  std::string f=w.fields[w.step];std::wstring title=L"Field "+wide(std::to_string(w.step+1))+L" of "+wide(std::to_string(w.fields.size()))+L": "+fieldTitle(f);
  control(h,L"STATIC",title.c_str(),0,18,53,574,25,101);
  w.combo=control(h,L"COMBOBOX",L"",CBS_DROPDOWNLIST|WS_TABSTOP|WS_VSCROLL,18,83,570,180,102);
  std::vector<std::wstring> items;int choice=0;std::wstring note;
  if(f=="C"){
   items={L"Keep conductivity C (mS/cm)",L"Convert conductivity C to salinity S (PSS-78)"};choice=w.choices.conductivity;
   note=L"Salinity uses the conductivity, temperature and pressure of each measurement, calculated by SIT.";

  }else if(f=="P"){
   items={L"Keep pressure P (dbar)",L"Real depth (m) - salinity, temperature and pressure corrected"};choice=w.choices.depth;

   checkBox(h,L"Use GPS position for depth and save it in the header",199,121,w.choices.useGPS);
   control(h,L"STATIC",L"GPS position (latitude, longitude) - paste from Google Maps",0,18,228,570,20,126);
   control(h,L"EDIT",w.gps.c_str(),WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,18,251,570,24,122);
   if(!control(h,L"SysLink",L"<a>Google Maps</a>",WS_TABSTOP,18,284,170,26,129))control(h,L"BUTTON",L"Google Maps",WS_TABSTOP|BS_FLAT,18,284,125,26,129);
   control(h,L"BUTTON",L"Paste",WS_TABSTOP,496,284,92,26,128);
  }else if(f=="Par"){
   items={L"Keep original PAR value",L"Convert PAR to \u00b5mol photons/(m\u00b2\u00b7s)"};choice=w.choices.par;
   note=L"PAR is photon flux density. 1 \u00b5Einstein = 1 \u00b5mol photons. Area and time units must also match.";

   control(h,L"STATIC",L"Unit of the PAR values stored in this file:",0,18,203,570,23,125);
   HWND unit=control(h,L"COMBOBOX",L"",CBS_DROPDOWNLIST|WS_TABSTOP|WS_VSCROLL,18,230,570,145,124);
   for(const wchar_t*x:{L"Select source unit...",L"\u00b5Einstein/(m\u00b2\u00b7s) - same numeric value (\u00d71)",L"\u00b5Einstein/(cm\u00b2\u00b7s) - multiply by 10 000"})SendMessageW(unit,CB_ADDSTRING,0,(LPARAM)x);
   SendMessageW(unit,CB_SETCURSEL,w.choices.parSource,0);
  }else if(f=="OxR"||f=="OX"){
   items={L"Keep oxygen saturation (%)",L"Add oxygen in mg/L",L"Add oxygen in mL/L",L"Add oxygen in both mg/L and mL/L"};choice=f=="OxR"?w.choices.oxygen:w.choices.oxygenOX;
   note=L"The source unit is % saturation. Temperature, salinity and air pressure are read automatically; only missing values are requested.";
  }else{
   if(f=="T"){items={L"Keep temperature (\u00b0C, Celsius)",L"Convert temperature to Fahrenheit (\u00b0F)"};choice=w.choices.fahrenheit?1:0;}else if(f=="OF")items={L"Keep fluorescence (\u00b5g/L)"};else if(f=="OT")items={L"Keep turbidity (FTU)"};else items={L"Keep original values"};
   note=(f=="OF"||f=="OT")?L"This is already in the physical unit used by SIT. No additional calibration or scaling is applied.":L"The original measurement values are retained.";
  }
  if(f=="T")note=L"Fahrenheit = Celsius \u00d7 9/5 + 32. Calculations use the original Celsius values. Keep original values to retain both temperature columns.";
  if(f=="T"&&sit::canSal(*w.d)&&sit::complete(*w.d,"T")&&sit::complete(*w.d,"P"))checkBox(h,L"Calculate sound velocity (m/s)",199,130,w.choices.soundVelocity);
  for(auto&x:items)SendMessageW(w.combo,CB_ADDSTRING,0,(LPARAM)x.c_str());SendMessageW(w.combo,CB_SETCURSEL,choice,0);
  control(h,L"STATIC",note.c_str(),0,18,120,570,45,103);
  std::wstring keep=L"Keep original "+wide(f)+(f=="T"?L" values (\u00b0C)":L" values");checkBox(h,keep.c_str(),172,120,!w.choices.keepOriginal.count(f)||w.choices.keepOriginal[f]);updateFieldControls(h,w);
 }else{
  control(h,L"STATIC",L"Provide missing conversion conditions",0,18,53,570,25,101);
  int y=90;
  if(!sit::complete(*w.d,"T")){control(h,L"STATIC",L"Water temperature (\u00b0C, Celsius):",0,18,y+3,360,23,1100);w.t=control(h,L"EDIT",w.choices.suppliedT?wide(sit::fmt(w.choices.temperature)).c_str():L"",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,412,y,176,25,110);y+=40;}
  if(!sit::canSal(*w.d)){control(h,L"STATIC",L"Salinity (PSS-78):",0,18,y+3,360,23,1101);w.s=control(h,L"EDIT",w.choices.suppliedS?wide(sit::fmt(w.choices.salinity)).c_str():L"",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,412,y,176,25,111);y+=40;}
  if(sit::wantsOxygen(*w.d,w.choices)&&w.choices.air<=0){control(h,L"STATIC",L"Air pressure (hPa / mbar):",0,18,y+3,360,23,1102);w.ap=control(h,L"EDIT",L"",WS_BORDER|WS_TABSTOP|ES_AUTOHSCROLL,412,y,176,25,112);y+=40;}
  control(h,L"STATIC",L"These values apply only where data is missing. They will be identified in the exported header.",0,18,y+12,570,42,103);
 }
 HWND back=control(h,L"BUTTON",L"< Back",WS_TABSTOP,276,326,92,28,3);EnableWindow(back,w.step>0);
 control(h,L"BUTTON",L"Cancel",WS_TABSTOP,386,326,92,28,IDCANCEL);
 control(h,L"BUTTON",w.step<w.fields.size()?L"Next >":L"Convert",WS_TABSTOP|BS_DEFPUSHBUTTON,496,326,92,28,IDOK);
 SetFocus(w.step<w.fields.size()?w.combo:w.t?w.t:w.s?w.s:w.ap?w.ap:GetDlgItem(h,IDOK));
}
static void rememberField(HWND h,Wizard&w,bool validate){
 if(w.step>=w.fields.size())return;
 std::string f=w.fields[w.step];int value=selected(w.combo);w.choices.keepOriginal[f]=checked(GetDlgItem(h,120));
 if(f=="T")w.choices.fahrenheit=value==1;
 if(f=="T"&&GetDlgItem(h,130))w.choices.soundVelocity=checked(GetDlgItem(h,130));
 if(f=="C"){
  w.choices.conductivity=value;w.choices.keepC=checked(GetDlgItem(h,120));
  if(validate&&value&&(!sit::complete(*w.d,"C")||!sit::complete(*w.d,"T")||!sit::complete(*w.d,"P")))throw std::runtime_error("C to S conversion needs C, T and P in every measurement");
 }else if(f=="P"){
  w.choices.depth=value;w.choices.keepP=checked(GetDlgItem(h,120));w.choices.useGPS=checked(GetDlgItem(h,121));
  w.gps=caption(GetDlgItem(h,122));
  if(validate&&value&&w.choices.useGPS){auto position=sit::gpsPair(utf8(w.gps));w.choices.latitude=position.first;w.choices.longitude=position.second;}
 }else if(f=="Par"){
  w.choices.par=value;w.choices.keepPar=checked(GetDlgItem(h,120));w.choices.parSource=selected(GetDlgItem(h,124));
  if(validate&&value&&!w.choices.parSource)throw std::runtime_error("Select the area unit of PAR in the input file before converting");
 }else if(f=="OxR")w.choices.oxygen=value;else if(f=="OX")w.choices.oxygenOX=value;
}
static void openGoogleMaps(HWND owner){
 if((INT_PTR)ShellExecuteW(owner,L"open",L"https://www.google.com/maps",0,0,SW_SHOWNORMAL)<=32)error(owner,"Could not open Google Maps in the default browser");
}
static LRESULT CALLBACK wizardProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){
 Wizard*w=(Wizard*)GetWindowLongPtrW(h,GWLP_USERDATA);
 if(msg==WM_NCCREATE){w=(Wizard*)((CREATESTRUCTW*)lp)->lpCreateParams;SetWindowLongPtrW(h,GWLP_USERDATA,(LONG_PTR)w);}
 if(!w)return DefWindowProcW(h,msg,wp,lp);
 try{
  if(msg==WM_NOTIFY){NMHDR*note=(NMHDR*)lp;if(note->idFrom==129&&(note->code==NM_CLICK||note->code==NM_RETURN)){openGoogleMaps(h);return 0;}}
  if(msg==WM_COMMAND){
   int id=LOWORD(wp);
   if(id==129){openGoogleMaps(h);return 0;}
   if(id==128){
    HWND edit=GetDlgItem(h,122);
    if(IsClipboardFormatAvailable(CF_UNICODETEXT)||IsClipboardFormatAvailable(CF_TEXT)){SendMessageW(edit,EM_SETSEL,0,-1);SendMessageW(edit,WM_PASTE,0,0);SetFocus(edit);}else MessageBoxW(h,L"Copy a coordinate pair from Google Maps first.",L"SAIV IT - GPS",MB_OK|MB_ICONINFORMATION);
    return 0;
   }
   if((id==102&&HIWORD(wp)==CBN_SELCHANGE)||id==121){updateFieldControls(h,*w);return 0;}
   if(id==IDCANCEL){w->done=true;DestroyWindow(h);return 0;}
   if(id==3&&w->step>0){rememberField(h,*w,false);--w->step;w->environment=false;wizardPage(h,*w);return 0;}
   if(id==IDOK){
    if(w->step<w->fields.size()){
     rememberField(h,*w,true);++w->step;
     if(w->step==w->fields.size()){
      w->environment=needsConditions(*w);
      if(!w->environment){w->accepted=w->done=true;DestroyWindow(h);return 0;}
     }
     wizardPage(h,*w);
    }else{
     if(w->t){w->choices.temperature=inputNumber(w->t);if(w->choices.temperature<-5||w->choices.temperature>50)throw std::runtime_error("Water temperature must be between -5 and 50 C");w->choices.suppliedT=true;}
     if(w->s){w->choices.salinity=inputNumber(w->s);if(w->choices.salinity<0||w->choices.salinity>60)throw std::runtime_error("Salinity must be between 0 and 60");w->choices.suppliedS=true;}
     if(w->ap){w->choices.air=inputNumber(w->ap);if(w->choices.air<500||w->choices.air>1200)throw std::runtime_error("Air pressure must be between 500 and 1200 hPa");}
     w->accepted=w->done=true;DestroyWindow(h);
    }
    return 0;
   }
  }
  if(msg==WM_CLOSE){w->done=true;DestroyWindow(h);return 0;}
 }catch(const std::exception&e){error(h,e.what());return 0;}
 return DefWindowProcW(h,msg,wp,lp);
}
static bool choose(HWND owner,sit::Data&data,sit::Choices&choices,const sit::Choices*previous=0){
 Wizard w;w.d=&data;if(previous)w.choices=*previous;w.choices.air=data.air;
 for(auto&f:data.fields)if(f!="COUNT"&&f!="DATE"&&f!="TIME")w.fields.push_back(f);
 for(auto&m:data.metadata){std::smatch match;if(std::regex_search(m,match,std::regex("GPS position: Latitude=([+0-9.eE-]+); Longitude=([+0-9.eE-]+)"))){w.gps=wide(match[1].str()+", "+match[2].str());}if(std::regex_search(m,match,std::regex("GPS position: ([+0-9.eE-]+), *([+0-9.eE-]+)")))w.gps=wide(match[1].str()+", "+match[2].str());if(m.find("PAR source unit: uEinstein/(m2*s)")!=std::string::npos)w.choices.parSource=1;if(m.find("PAR source unit: uEinstein/(cm2*s)")!=std::string::npos)w.choices.parSource=2;}
 if(w.fields.empty())throw std::runtime_error("No sensor fields found");
 if(previous){bool reviewGPS=w.choices.depth&&w.choices.useGPS;w.fields.clear();if(reviewGPS)w.fields.push_back("P");else if(!needsConditions(w)){choices=w.choices;return true;}}
 RECT r;GetWindowRect(owner,&r);HWND h=CreateWindowExW(WS_EX_DLGMODALFRAME,L"SITImportChoices",L"SAIV IT - Convert fields",WS_CAPTION|WS_SYSMENU,r.left+45,r.top+45,622,400,owner,0,instance,&w);
 if(!h)throw std::runtime_error("Cannot create import choices window");
 EnableWindow(owner,FALSE);wizardPage(h,w);ShowWindow(h,SW_SHOW);MSG m;
 while(!w.done&&GetMessageW(&m,0,0,0)>0){if(!IsDialogMessageW(h,&m)){TranslateMessage(&m);DispatchMessageW(&m);}}
 EnableWindow(owner,TRUE);SetActiveWindow(owner);choices=w.choices;return w.accepted;
}
