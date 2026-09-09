from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];studio=r/'saiv-studio';archive=r/'analysis/reference/saiv_studio_v030'
assert not archive.exists(),'Preserve the existing source archive'
archive.mkdir()
for name in ['src','tests','docs']:shutil.copytree(studio/name,archive/name)
for name in ['CMakeLists.txt','README.md','build.cmd']:shutil.copy2(studio/name,archive/name)
p=studio/'src/studio_ui.cpp';s=p.read_text();old=' ImGui::SameLine(ImGui::GetWindowWidth()-275);if(page_!=1&&ImGui::Button("Terminal")){page_=1;focusTerminal_=true;}if(selected()&&page_!=2){if(page_!=1)ImGui::SameLine();if(ImGui::Button("Measurements"))page_=2;}if(serial_.connected){ImGui::SameLine();if(ImGui::SmallButton("Disconnect"))disconnect();}'
new=''' // Keep the next workspace on its own row when no header action is visible.
 if(page_!=1||selected()||serial_.connected){
  ImGui::SameLine(ImGui::GetWindowWidth()-275);
  if(page_!=1&&ImGui::Button("Terminal")){page_=1;focusTerminal_=true;}
  if(selected()&&page_!=2){if(page_!=1)ImGui::SameLine();if(ImGui::Button("Measurements"))page_=2;}
  if(serial_.connected){ImGui::SameLine();if(ImGui::SmallButton("Disconnect"))disconnect();}
 }'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
for name in ['CMakeLists.txt','src/main.cpp','src/studio.rc','src/studio_ui.cpp','src/sit/logger.h','src/sit/merge.h','tests/compat_tests.cpp']:
 p=studio/name;s=p.read_text().replace('0.3.0','0.3.1').replace('0,3,0,0','0,3,1,0');p.write_text(s)
print('Startup layout fixed. Studio 0.3.0 sources preserved.')
