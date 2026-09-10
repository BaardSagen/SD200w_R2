// Native Delphi interoperability. All entry points are relative to the loaded image.
#include "native_data.h"
#include <array>
extern "C" uintptr_t sit_native_call(uintptr_t,uintptr_t,uintptr_t,uintptr_t,const uint32_t*,unsigned);
static uintptr_t nativeBase(){return uintptr_t(GetModuleHandleW(0));}
static uintptr_t& nd(uintptr_t a){return *reinterpret_cast<uintptr_t*>(a);}
static uintptr_t nc(unsigned rva,uintptr_t a=0,uintptr_t b=0,uintptr_t c=0,const uint32_t*s=0,unsigned n=0){return sit_native_call(nativeBase()+rva,a,b,c,s,n);}
static uintptr_t nv(uintptr_t obj,unsigned off,uintptr_t b=0,uintptr_t c=0,const uint32_t*s=0,unsigned n=0){return sit_native_call(nd(nd(obj)+off),obj,b,c,s,n);}
static void nativeText(uintptr_t obj,unsigned method,const std::string&s){uintptr_t str=0;nc(0x4080,uintptr_t(&str),uintptr_t(s.data()),s.size());nc(method,obj,str);nc(0x3f98,uintptr_t(&str));}
static void nativeAssign(uintptr_t dest,const std::string&s){nc(0x4080,dest,uintptr_t(s.data()),s.size());}
static HWND nh(uintptr_t obj){return HWND(nd(obj+0x14c));}
static sit::Data nativeData;
static bool nativeActive=false;
static std::wstring pendingNativeOpen;
static std::vector<double> nativeTimes;
static std::wstring nativePath;
static uintptr_t nativeGraph=0;
static int nativeList(HWND owner);
static LRESULT CALLBACK nativeMainSubclass(HWND h,UINT m,WPARAM w,LPARAM l,UINT_PTR,DWORD_PTR){if(m==WM_APP+137){if(nativeActive){std::wstring title=L"SAIV Instrument Terminal - Imported - "+nativePath.substr(nativePath.find_last_of(L"\\/")+1);SetWindowTextW(h,title.c_str());}return 0;}return DefSubclassProc(h,m,w,l);}
static bool drawingNative=false;
static std::array<int,10> nativeSlots;
static std::vector<int> nativeColumns;
static HWND channelPanel=0;
static bool singleNative=false;
static void layoutNativeSelectors(HWND h){if(!channelPanel||!IsWindow(channelPanel))return;RECT r;GetClientRect(h,&r);MoveWindow(channelPanel,0,0,r.right,94,TRUE);int width=std::max(40,(int(r.right)-16)/5);for(int i=0;i<10;++i){HWND combo=GetDlgItem(channelPanel,700+i);if(combo)MoveWindow(combo,8+(i%5)*width,25+(i/5)*30,width-7,300,TRUE);}}
static LRESULT CALLBACK nativeGraphSubclass(HWND h,UINT m,WPARAM w,LPARAM l,UINT_PTR,DWORD_PTR){LRESULT result=DefSubclassProc(h,m,w,l);if(m==WM_SIZE)layoutNativeSelectors(h);if(m==WM_NCDESTROY){channelPanel=0;RemoveWindowSubclass(h,nativeGraphSubclass,137);}return result;}
static const unsigned seriesOff[10]={0x330,0x334,0x33c,0x338,0x340,0x344,0x354,0x370,0x374,0x3d8};
static const unsigned checkOff[10]={0x2dc,0x2e4,0x2ec,0x2f4,0x2fc,0x304,0x30c,0x380,0x388,0x3d4};
static const unsigned editOff[10]={0x2e0,0x2e8,0x2f0,0x2f8,0x300,0x308,0x310,0x384,0x38c,0x3cc};
// Native published property records, including inherited properties.
static uintptr_t prop(uintptr_t obj,const char*name,bool setter){
 uintptr_t type=nd(nd(obj)-60);
 while(type){auto p=reinterpret_cast<unsigned char*>(type);p+=2+p[1];uintptr_t parent=nd(uintptr_t(p)+4);p+=10;p+=1+*p;unsigned count=*reinterpret_cast<unsigned short*>(p);p+=2;
  for(unsigned i=0;i<count;++i){unsigned len=p[26];if(std::strlen(name)==len&&!std::memcmp(p+27,name,len))return nd(uintptr_t(p)+(setter?8:4));p+=27+len;}type=parent?nd(parent):0;
 }return 0;
}
static uintptr_t property(uintptr_t obj,const char*name){uintptr_t a=prop(obj,name,false);if((a&0xff000000)==0xff000000)return nd(obj+(a&0xffffff));if((a&0xff000000)==0xfe000000)return nv(obj,a&0xffffff);return a?sit_native_call(a,obj,0,0,0,0):0;}
static void textProperty(uintptr_t obj,const char*name,const std::string&text){uintptr_t a=prop(obj,name,true);if(!a)return;uintptr_t str=0;nc(0x4080,uintptr_t(&str),uintptr_t(text.data()),text.size());if((a&0xff000000)==0xff000000)nc(0x3fec,obj+(a&0xffffff),str);else if((a&0xff000000)==0xfe000000)nv(obj,a&0xffffff,str);else sit_native_call(a,obj,str,0,0,0);nc(0x3f98,uintptr_t(&str));}
static void nativeReadout(uintptr_t form,int row){if(row<0||size_t(row)>=nativeData.rows.size())return;for(int i=0;i<10;++i){int col=nativeSlots[i];nativeText(nd(form+editOff[i]),0x3795c,col<0?"":nativeData.rows[row][col]);}}
static void fillNativeGraph(uintptr_t form){
 if(drawingNative||!nativeActive||!form)return;drawingNative=true;
 uintptr_t chart=nd(form+0x32c);nc(0xbee14,chart);nc(0x156a20,form);
 nd(form+0x3e4)=0;nd(form+0x3e8)=nativeData.rows.size()-1;nd(form+0x3ec)=uint32_t(-1);
 size_t first=nd(nd(nativeBase()+0x1b1c84)),last=nd(nd(nativeBase()+0x1b2234));if(first>=nativeData.rows.size()||last>=nativeData.rows.size()||first>last){first=0;last=nativeData.rows.size()-1;}
 const bool depth=nd(nd(form+0x350)+0x200)==0;
 int depthCol=sit::index(nativeData,"Depth_m");if(depthCol<0)depthCol=sit::index(nativeData,"P");
 nc(0xbe684,chart,depth?1:0);
 for(int slot=0;slot<10;++slot){uintptr_t series=nd(form+seriesOff[slot]),chk=nd(form+checkOff[slot]);int col=nativeSlots[slot];bool enabled=col>=0;
  nv(chk,0x5c,enabled);nv(chk,0xb8,enabled);std::string label=enabled?nativeData.fields[col]:"Unused";nativeText(chk,0x3795c,label);textProperty(series,"Title",label);nv(nd(form+editOff[slot]),0x5c,enabled);
  uintptr_t axis=nc(0x97b08,nd(chart+0x2d8),nd(chk+12));uintptr_t title=property(axis,"Title");if(title)textProperty(title,"Caption",label);nc(0x90078,axis,1);
  if(enabled){for(size_t row=first;row<=last;++row){const std::string&cell=nativeData.rows[row][col];double x=depth?(depthCol>=0&&!nativeData.rows[row][depthCol].empty()?sit::number(nativeData.rows[row][depthCol]):NAN):nativeTimes[row]-nativeTimes.front();if(!std::isfinite(x))continue;double y=cell.empty()?0:sit::number(cell);uint32_t args[4];std::memcpy(args,&y,8);std::memcpy(args+2,&x,8);nv(series,0xbc,0,cell.empty()?0x1fffffff:0x20000000,args,4);
    // Delphi clNone marks a null point; use the series color for ordinary values.
    if(cell.empty()){uintptr_t colors=nd(series+0x88);(void)colors;}
  }}
  nc(0x156080,form,chk);
 }
 uintptr_t baseAxis=nd(chart+0x2ec);uintptr_t title=property(baseAxis,"Title");if(title)textProperty(title,"Caption",depth?(depthCol>=0?nativeData.fields[depthCol]:"No depth field"):"Time (seconds from first measurement)");nc(0x90078,baseAxis,1);
 nc(0xbee34,chart);nc(0xbe9dc,chart);nc(0xbf004,chart);nativeReadout(form,int(first));drawingNative=false;
}
static LRESULT CALLBACK nativePanelProc(HWND h,UINT msg,WPARAM wp,LPARAM lp){if(msg==WM_COMMAND&&LOWORD(wp)>=700&&LOWORD(wp)<710&&HIWORD(wp)==CBN_SELCHANGE){int slot=LOWORD(wp)-700;HWND combo=HWND(lp);int ix=int(SendMessageW(combo,CB_GETCURSEL,0,0));nativeSlots[slot]=ix<=0?-1:nativeColumns[ix-1];fillNativeGraph(nativeGraph);return 0;}return DefWindowProcW(h,msg,wp,lp);}
static void nativeSelectors(uintptr_t form,bool single){
 HWND h=nh(form);if(!channelPanel||!IsWindow(channelPanel)){WNDCLASSW wc={};wc.lpfnWndProc=nativePanelProc;wc.hInstance=instance;wc.hbrBackground=(HBRUSH)(COLOR_BTNFACE+1);wc.lpszClassName=L"SITNativeChannels";RegisterClassW(&wc);channelPanel=CreateWindowExW(0,L"SITNativeChannels",L"",WS_CHILD|WS_VISIBLE,0,0,600,94,h,0,instance,0);}
 RECT rc;GetClientRect(h,&rc);MoveWindow(channelPanel,0,0,rc.right,94,TRUE);SetWindowPos(channelPanel,HWND_TOP,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE);
 if(!GetDlgItem(channelPanel,690))control(channelPanel,L"STATIC",single?L"Graph fields (choose fields below)":L"Multigraph fields (up to 10 visible at once)",0,8,3,440,18,690);
 for(int i=0;i<10;++i){HWND combo=GetDlgItem(channelPanel,700+i);if(!combo){combo=control(channelPanel,L"COMBOBOX",L"",CBS_DROPDOWNLIST|WS_VSCROLL|WS_TABSTOP,8+(i%5)*155,25+(i/5)*30,148,300,700+i);SendMessageW(combo,CB_SETDROPPEDWIDTH,310,0);SendMessageW(combo,CB_ADDSTRING,0,LPARAM(L"(none)"));for(int col:nativeColumns){auto label=fieldLabel(nativeData.fields[col]);SendMessageW(combo,CB_ADDSTRING,0,LPARAM(label.c_str()));}}
  int selected=0;for(size_t j=0;j<nativeColumns.size();++j)if(nativeColumns[j]==nativeSlots[i])selected=int(j+1);SendMessageW(combo,CB_SETCURSEL,selected,0);
 }
 // Keep the existing chart and all native graph controls below the field selector.
 uintptr_t panel=nd(form+0x390);nc(0x371b0,panel,94); // top panel height
 nc(0x37844,nd(form+0x394),0);
 layoutNativeSelectors(h);SetWindowSubclass(h,nativeGraphSubclass,137,0); // no fabricated GPS on imported logger data
}
static void openNativeGraph(uintptr_t main,bool single,int tag=-1,bool depth=false){
 if(nativeGraph&&IsWindow(nh(nativeGraph))&&!single&&singleNative==single){nc(0x52d0c,nativeGraph);return;}
 uintptr_t slot=nd(nativeBase()+0x1b2268);if(nd(slot)){nc(0x324c,nd(slot));nd(slot)=0;}
 nativeGraph=nc(0x4ed74,nd(nativeBase()+0x153b18),1,main);nd(slot)=nativeGraph;singleNative=single;channelPanel=0;
 nativeSlots.fill(-1);nativeColumns.clear();for(size_t i=0;i<nativeData.fields.size();++i){auto f=nativeData.fields[i];if(!sitnative::separator(f)&&!sitnative::dateField(f)&&!sitnative::timeField(f))nativeColumns.push_back(int(i));}
 int n=0;for(int col:nativeColumns){auto f=nativeData.fields[col];if(f=="COUNT"||sitnative::suffix(f,"_COUNT")||sitnative::suffix(f,"_Delta_seconds"))continue;nativeSlots[n++]=col;if(n==(single?1:10))break;}if(n==0&&!nativeColumns.empty())nativeSlots[0]=nativeColumns[0];
 if(single){std::vector<std::string> wanted;if(tag==0)wanted={"S","S_from_C","Salinity_SIT","T","T_degF"};else if(tag==6)wanted={"C","T","T_degF"};else if(tag==1)wanted={"Sound_velocity_TEOS10_m_s","Sound_velocity_Mackenzie_m_s","Sound_velocity_DelGrosso_m_s","Sound_velocity_NPL_m_s","Sound_velocity_SIT_m_s","Density_TEOS10_kg_m3","SigmaT_EOS80_kg_m3","Density_anomaly_legacy_kg_m3","Density_anomaly_SIT_kg_m3"};else if(tag==2)wanted={"OX","OxR","OxR_mg_L","OxR_mL_L"};else if(tag==3)wanted={"Depth_m","P"};else if(tag==4)wanted={"OF","Par"};else if(tag==5)wanted={"OT","Tilt"};else wanted={"T","T_degF","Par"};int selected=0;for(auto&name:wanted){int col=sit::index(nativeData,name);if(col>=0){if(selected==0)nativeSlots.fill(-1);nativeSlots[selected++]=col;if(selected==2)break;}}}
 nd(nd(nativeGraph+0x350)+0x200)=depth&&(sit::index(nativeData,"Depth_m")>=0||sit::index(nativeData,"P")>=0)?0:1;
 nativeText(nativeGraph,0x3795c,std::string(single?"Graph - ":"Multigraph - ")+utf8(nativePath.substr(nativePath.find_last_of(L"\\/")+1)));
 nc(0x52d0c,nativeGraph);nativeSelectors(nativeGraph,single);fillNativeGraph(nativeGraph);
 HWND group=nh(nd(nativeGraph+0x350));HWND child=GetWindow(group,GW_CHILD);bool hasDepth=sit::index(nativeData,"Depth_m")>=0||sit::index(nativeData,"P")>=0;while(child){auto t=caption(child);if(t.find(L"Time")==std::wstring::npos){SetWindowTextW(child,sit::index(nativeData,"Depth_m")>=0?L"Depth (m)":L"Pressure (dbar)");EnableWindow(child,hasDepth);}child=GetWindow(child,GW_HWNDNEXT);}
}
static void writeNativeFiles(HWND owner,const std::wstring&path,const sitnative::Files&f){
 std::vector<std::pair<std::wstring,std::string>> files={{path,f.sd},{path.substr(0,path.size()-4)+L".RF2",f.rf},{path.substr(0,path.size()-4)+L".SF2",f.sf}};if(!f.ox.empty())files.push_back({path.substr(0,path.size()-4)+L".OX2",f.ox});if(!f.op.empty())files.push_back({path.substr(0,path.size()-4)+L".OP2",f.op});
 for(auto ext:{L".SD2",L".RF2",L".SF2",L".OX2",L".OP2"})if(GetFileAttributesW((path.substr(0,path.size()-4)+ext).c_str())!=INVALID_FILE_ATTRIBUTES)throw std::runtime_error("This dataset name already exists. Choose a new name to keep existing files.");
 std::vector<std::wstring> made;try{for(auto&file:files){HANDLE h=CreateFileW(file.first.c_str(),GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);if(h==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot create native dataset");made.push_back(file.first);DWORD count=0;bool ok=WriteFile(h,file.second.data(),DWORD(file.second.size()),&count,0)&&count==file.second.size();CloseHandle(h);if(!ok)throw std::runtime_error("Cannot write complete native dataset");}}catch(...){for(auto&name:made)DeleteFileW(name.c_str());throw;}
}
static bool importNativeData(HWND owner,uintptr_t main,const sit::Data&data,const std::string&original,const std::wstring&source){auto files=sitnative::project(data,original,formula);
 wchar_t path[MAX_PATH]={};std::wstring stem=source.substr(source.find_last_of(L"\\/")+1);stem=stem.substr(0,stem.find_last_of(L'.'))+L"_imported.SD2";wcsncpy(path,stem.c_str(),MAX_PATH-1);OPENFILENAMEW of={sizeof(of)};of.hwndOwner=owner;std::wstring folder=source.substr(0,source.find_last_of(L"\\/"));of.lpstrInitialDir=folder.c_str();of.lpstrFilter=L"SAIV native dataset (*.SD2)\0*.SD2\0\0";of.lpstrFile=path;of.nMaxFile=MAX_PATH;of.lpstrDefExt=L"SD2";of.lpstrTitle=L"Import CSV/TXT - Save native dataset";of.Flags=OFN_PATHMUSTEXIST|OFN_NOCHANGEDIR;if(!GetSaveFileNameW(&of))return false;writeNativeFiles(of.hwndOwner,path,files);pendingNativeOpen=path;nc(0x1a09f4,main,0);pendingNativeOpen.clear();if(nativeActive)nativeList(HWND(nd(main+0x14c)));return true;}
static int importNative(uintptr_t main,const char*file){std::wstring source=wide(file,CP_ACP);auto original=readFile(source);sit::Data data;data.source=utf8(source);if(!sitnative::parse(original,data))return 0;importNativeData(HWND(nd(main+0x14c)),main,data,original,source);return 1;}
static bool importConverted(HWND owner,const sit::Data&data){return importNativeData(owner,nd(nativeBase()+0x1c8964),data,sit::output(data),wide(data.source));}

static void closeNativeGraph(){uintptr_t slot=nd(nativeBase()+0x1b2268);if(nativeGraph&&nd(slot)==nativeGraph){uintptr_t form=nativeGraph;nativeGraph=0;nd(slot)=0;nc(0x324c,form);}nativeGraph=0;channelPanel=0;}
static void loadNative(){
 closeNativeGraph();nativeActive=false;nativeGraph=0;channelPanel=0;nativeData=sit::Data();nativeTimes.clear();uintptr_t root=nd(nd(nativeBase()+0x1b16d8));if(!root)return;nativePath=wide(reinterpret_cast<const char*>(root),CP_ACP)+L".SD2";auto sf=nativePath.substr(0,nativePath.size()-4)+L".SF2";if(GetFileAttributesW(sf.c_str())==INVALID_FILE_ATTRIBUTES)return;
 auto raw=readFile(sf);auto end=raw.find('\n');auto header=sit::trim(raw.substr(0,end));if(end==std::string::npos||header!="# SIT native fields 1 "+sitnative::hexhash(readFile(nativePath)))throw std::runtime_error("The SD2 and SF2 files do not match. Import the source again to restore the complete dataset.");
 nativeData.source=utf8(nativePath);if(!sitnative::parse(raw.substr(end+1),nativeData))throw std::runtime_error("Invalid native extra-field file");int da=sit::index(nativeData,"DATE"),ti=sit::index(nativeData,"TIME");for(auto&r:nativeData.rows)nativeTimes.push_back(sitnative::timestamp(r[da],r[ti]));auto sd=readFile(nativePath);if(sd.size()!=52+52*nativeData.rows.size())throw std::runtime_error("Native row count mismatch");
 auto addDerived=[&](const char*name,int offset){std::vector<std::string> values;bool any=false;for(size_t i=0;i<nativeData.rows.size();++i){double v;std::memcpy(&v,sd.data()+52+i*52+offset,8);values.push_back(v==-999.?"":sit::fmt(v));any=any||v!=-999.;}if(any)sit::append(nativeData,name,values);};
 // Model exports are complete: do not relabel their projected sound speed as
 // legacy SIT, or silently append density with an unspecified temperature scale.
 bool explicitModels=false;for(auto&m:nativeData.metadata)if(m.find("SIT conversion methods 1.4.7")!=std::string::npos)explicitModels=true;
 if(!explicitModels){
 if(sit::index(nativeData,"S")<0&&sit::index(nativeData,"S_from_C")<0&&sit::index(nativeData,"Salinity_SIT")<0)addDerived("S_from_C",12);
 if(sit::index(nativeData,"Sound_velocity_SIT_m_s")<0)addDerived("Sound_velocity_SIT_m_s",44);
 if(sit::index(nativeData,"Density_anomaly_SIT_kg_m3")<0){std::vector<std::string> values;bool any=false;for(size_t i=0;i<nativeData.rows.size();++i){double sal,t,p;std::memcpy(&sal,sd.data()+52+i*52+12,8);std::memcpy(&t,sd.data()+52+i*52+28,8);std::memcpy(&p,sd.data()+52+i*52+36,8);bool valid=sal!=-999&&t!=-999&&p!=-999;values.push_back(valid?sit::fmt(formula(2,p,t,sal)):"");any=any||valid;}if(any)sit::append(nativeData,"Density_anomaly_SIT_kg_m3",values);}
 }

 nativeActive=true;uintptr_t main=nd(nativeBase()+0x1c8964);HWND h=HWND(nd(main+0x14c));SetWindowSubclass(h,nativeMainSubclass,137,0);PostMessageW(h,WM_APP+137,0,0);
}
static int nativeList(HWND owner){registerClasses();std::unique_ptr<View>v(new View);v->data=nativeData;v->path=nativePath;v->allowNative=false;View*raw=v.release();HWND h=CreateWindowExW(0,L"SITImportData",L"SAIV IT - Imported fields",WS_OVERLAPPEDWINDOW,CW_USEDEFAULT,CW_USEDEFAULT,1050,650,owner,0,instance,raw);if(!h){delete raw;throw std::runtime_error("Cannot show imported data");}ShowWindow(h,SW_SHOW);return 1;}
 #include "settings_ui.inc"
 #include "update_ui.inc"
extern "C" __declspec(dllexport) int __stdcall SitNative(unsigned op,uintptr_t a,uintptr_t b,uintptr_t c){try{
 if(op>=30)return settingsNative(op,a,b,c);
 if(op==20){settingsNative(op,a,b,c);updateInit(HWND(nd(a+0x14c)));}
 if(op==1)return importNative(a,reinterpret_cast<const char*>(b));
 if(op==2){loadNative();return 0;}
 if(op==11){closeNativeGraph();nativeActive=false;return 0;}
 if(op==10&&a==nativeGraph){uintptr_t slot=nd(nativeBase()+0x1b2268);if(nd(slot)==a)nd(slot)=0;nativeGraph=0;channelPanel=0;return 0;}
 if(op==9){if(pendingNativeOpen.empty())return 0;std::string path= utf8(pendingNativeOpen);int len=WideCharToMultiByte(CP_ACP,WC_NO_BEST_FIT_CHARS,pendingNativeOpen.c_str(),-1,0,0,0,0);path.resize(len);BOOL used=FALSE;WideCharToMultiByte(CP_ACP,WC_NO_BEST_FIT_CHARS,pendingNativeOpen.c_str(),-1,&path[0],len,0,&used);if(used)throw std::runtime_error("Native file paths must use characters supported by Windows system locale");nativeAssign(a+0x70,path.c_str());return 1;}
 if(!nativeActive)return 0;
 if(op==20){PostMessageW(HWND(nd(a+0x14c)),WM_APP+137,0,0);return 0;}
 if(op==3||op==4||op==17){openNativeGraph(a,op!=4,-1,op==17);return 1;}
 if(op==21||op==22||op==23){openNativeGraph(a,true,b?int(nd(b+12)):-1,op==22||(op==23&&*reinterpret_cast<unsigned char*>(a+0xc00)));return 1;}
 if(op==5)return nativeList(HWND(nd(a+0x14c)));
 if((op==6||op==18||op==19)&&a==nativeGraph){fillNativeGraph(a);return 1;}
 if(op==8&&a==nativeGraph){nativeReadout(a,int(b));return 1;}
 if(op==12&&a<nativeTimes.size()){*reinterpret_cast<double*>(b)=nativeTimes[a]-nativeTimes.front();return 1;}
 if(op==13&&a<nativeTimes.size()){*reinterpret_cast<double*>(b)=nativeTimes[a]/86400.+2.;return 1;}
 return 0;
 }catch(const std::exception&e){drawingNative=false;error(GetActiveWindow(),e.what());return op==1?1:0;}catch(...){drawingNative=false;error(GetActiveWindow(),"Native import failed");return op==1?1:0;}}
