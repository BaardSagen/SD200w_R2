from pathlib import Path
r=Path(__file__).resolve().parents[1]/'saiv-studio'
p=r/'src/studio_ui.cpp';s=p.read_text();a=s.index('void App::saveNative()');b=s.index('void App::showData',a)
s=s[:a]+'void App::saveMeasurements(){if(auto*t=selected())saveData(t->csv(),L"Save measurements as CSV",L"csv");}\n'+s[b:]
s=s.replace('saveNative()','saveMeasurements()').replace('Save native dataset...','Save measurements as CSV...').replace('Save creates a new SD2 dataset with its companion files; Export offers CSV and FIELDS.','Save writes CSV with the original columns and measurement metadata. Old SD2 datasets can still be opened.')
s=s.replace('ImGui::TextDisabled("SERIAL CONNECTION");','ImGui::TextDisabled("SERIAL CONNECTION");ImGui::BeginDisabled(serial_.connected||connecting_);')
s=s.replace('ImGui::Checkbox("Reconnect after connection loss"','ImGui::EndDisabled();ImGui::Checkbox("Reconnect after connection loss"')
s=s.replace('settings_=r.settings;strncpy_s','settings_=r.settings;baudIndex_=3;strncpy_s')
s=s.replace('if(dataView_==3){int s=', 'if(dataView_==3){int s=')
s=s.replace('plot(d.graph,s,temp,false,ImGui::GetContentRegionAvail());','if(s<0||temp<0){wrapped("Temperature and salinity are required for a T-S diagram.");return;}plot(d.graph,s,temp,false,ImGui::GetContentRegionAvail());')
p.write_text(s)
p=r/'src/main.cpp';s=p.read_text().replace('style.Colors[ImGuiCol_WindowBg]','style.Colors[ImGuiCol_MenuBarBg]={.94f,.96f,.98f,1};style.Colors[ImGuiCol_WindowBg]',1)
# Application shortcuts must not also enter the instrument transmit queue.
s=s.replace('if(activeApp&&msg==WM_CHAR&&activeApp->terminalCharacter','if(activeApp&&msg==WM_CHAR&&(w==15||w==16)&&(GetKeyState(VK_CONTROL)&0x8000))return 0;if(activeApp&&msg==WM_CHAR&&activeApp->terminalCharacter')
p.write_text(s)
p=r/'src/sit/merge.h';s=p.read_text().replace('SAIV IT merged data 1.4.3','SAIV Studio merged data 0.3.0');p.write_text(s)
