from pathlib import Path
R=Path(__file__).resolve().parent.parent/'saiv-studio'
p=R/'src/app.cpp';s=p.read_text(encoding='utf-8')
def replace(a,b):
 global s
 assert a in s,a[:100]
 s=s.replace(a,b)
replace('#include "app.hpp"','#include "app.hpp"\n#include "native_dialogs.hpp"')
replace('documents_.push_back({std::move(t)});document_=static_cast<int>(documents_.size())-1;autoMap();','documents_.push_back({std::move(t)});document_=static_cast<int>(documents_.size())-1;autoMap();updateDocument();')
replace('if(!terminalFocused_||page_!=1||GetForegroundWindow()!=window_', 'if(!terminalFocused_||page_!=1||GetForegroundWindow()!=window_')
replace('downloadWanted_=false;connectionWanted_=false;connecting_=false;serial_.disconnect();','downloadWanted_=false;connectionWanted_=false;connecting_=false;acceptedInstrument_=false;serial_.disconnect();')
replace('log("TX",s);','if(showRawTraffic_)log("TX",s);')
replace('notice_="Connected to "+e.text+". Listening for identification.";log("LINK",notice_);','notice_="Connected to "+e.text+". Listening for identification.";if(acceptedInstrument_&&acceptedPort_==settings_.port)protocol_.device=acceptedIdentity_;')
replace('log("ERROR",e.text);','')
replace('log("LINK","Port closed");','')
replace('loading_=false;try{addDocument(loader_.get());page_=2;}catch(const std::exception& e){error_=e.what();}',
'''loading_=false;try{Table result=loader_.get();if(convertAfterLoad_){convertAfterLoad_=false;if(!convertDialog(window_,result))return;}addDocument(std::move(result));page_=2;dataView_=0;error_.clear();}catch(const std::exception& e){convertAfterLoad_=false;error_=e.what();}''')
replace('return loadText(readFile(p),utf8(p.filename()));','return loadDataset(p);')
replace('std::min<size_t>(t.columns.size(),64)','t.columns.size()')
# The direct terminal, dataset views and dialogs live in the readable Studio UI unit.
start=s.index('void App::drawTerminal()');end=s.index('void App::drawUtilities()',start)
s=s[:start]+s[end:]
start=s.index('void App::drawAbout()');s=s[:start]+'\n}\n'
# Keep the existing data tools but use SIT calculations in the default workflow.
s=s.replace('Oceanographic calculations (TEOS-10)','SIT calculations')
s=s.replace('Official GSW TEOS-10 routines. Oxygen assumes standard atmospheric pressure. Results may differ from legacy SD200W calculations.','Salinity, sound velocity and density use the documented SIT routines.')
s=s.replace('preview_=calculate(*t,calc_);','preview_=enrichSit(*t);')
# Keep original tool functions available through their own dialog rather than a top-level page.
p.write_text(s,encoding='utf-8')
p=R/'src/serial.cpp';s=p.read_text(encoding='utf-8')
s=s.replace(' if(s.parity==1&&s.bits==7){dcb.ByteSize=8;dcb.Parity=NOPARITY;}\n','')
s=s.replace('settings.parity==1&&settings.bits==7?encode7E1(pending):pending','pending')
s=s.replace('if(settings.parity==1&&settings.bits==7)payload=decode7E1(std::move(payload));','')
s=s.replace('settings.parity==1?encode7E1(command):command','command')
s=s.replace('if(settings.parity==1)payload=decode7E1(std::move(payload));','')
s=s.replace(' return h;',' DCB actual{};actual.DCBlength=sizeof(actual);if(!GetCommState(h,&actual)||actual.ByteSize!=dcb.ByteSize||actual.Parity!=dcb.Parity||actual.StopBits!=ONESTOPBIT){CloseHandle(h);SetLastError(ERROR_INVALID_PARAMETER);return INVALID_HANDLE_VALUE;}\n return h;',1)
p.write_text(s,encoding='utf-8')
p=R/'src/main.cpp';s=p.read_text(encoding='utf-8').replace('0.2.0','0.3.0').replace('m->ptMinTrackSize={1024,720}','m->ptMinTrackSize={920,600}')
s=s.replace('std::min(1280L','std::min(1180L').replace('std::min(900L','std::min(780L')
s=s.replace('style.WindowPadding={10,8};style.FramePadding={8,5};style.ItemSpacing={8,6};style.WindowRounding=0;style.ChildRounding=0;style.FrameRounding=2;',
'style.WindowPadding={16,14};style.FramePadding={12,8};style.ItemSpacing={10,9};style.WindowRounding=10;style.ChildRounding=8;style.FrameRounding=6;style.PopupRounding=8;style.ScrollbarSize=13;style.ScrollbarRounding=7;style.FrameBorderSize=0;style.WindowBorderSize=1;')
s=s.replace('style.Colors[ImGuiCol_WindowBg]={.94f,.95f,.96f,1};style.Colors[ImGuiCol_ChildBg]={1,1,1,1};style.Colors[ImGuiCol_Text]={.04f,.08f,.14f,1};style.Colors[ImGuiCol_Button]={.77f,.85f,.93f,1};',
'''style.Colors[ImGuiCol_WindowBg]={.96f,.97f,.98f,1};style.Colors[ImGuiCol_ChildBg]={1,1,1,1};style.Colors[ImGuiCol_Text]={.10f,.15f,.21f,1};style.Colors[ImGuiCol_TextDisabled]={.42f,.47f,.53f,1};style.Colors[ImGuiCol_Button]={.88f,.92f,.95f,1};style.Colors[ImGuiCol_ButtonHovered]={.75f,.86f,.94f,1};style.Colors[ImGuiCol_ButtonActive]={.58f,.76f,.90f,1};style.Colors[ImGuiCol_FrameBg]={.91f,.94f,.96f,1};style.Colors[ImGuiCol_Header]={.82f,.9f,.96f,1};style.Colors[ImGuiCol_Border]={.80f,.85f,.89f,1};''')
p.write_text(s,encoding='utf-8')
print('Updated data routing, modern UI style and actual UART parity.')
