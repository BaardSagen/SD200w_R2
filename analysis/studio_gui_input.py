from pathlib import Path
r=Path(__file__).resolve().parents[1]/'saiv-studio'
p=r/'src/main.cpp';s=p.read_text();s=s.replace('static UINT resizeW=0,resizeH=0;', '''static UINT resizeW=0,resizeH=0;
// File-transport GUI tests enqueue pointer input after the OS backend refresh.
// These messages are ignored in normal instrument sessions.
static bool testInputEnabled=false;
struct TestPointer {int action,x,y;};
static std::vector<TestPointer> testPointers;''')
s=s.replace('if(activeApp&&msg==WM_CHAR&&(w==15', 'if(testInputEnabled&&msg==WM_APP+17){testPointers.push_back({int(w),int(short(LOWORD(l))),int(short(HIWORD(l)))});return 1;}if(activeApp&&msg==WM_CHAR&&(w==15',1)
s=s.replace('LocalFree(args);','LocalFree(args);testInputEnabled=!testWire.empty();',1)
s=s.replace('ImGui_ImplWin32_NewFrame();ImGui::NewFrame();','ImGui_ImplWin32_NewFrame();for(auto&e:testPointers){io.AddMousePosEvent(float(e.x),float(e.y));if(e.action<2)io.AddMouseButtonEvent(0,e.action==1);}testPointers.clear();ImGui::NewFrame();',1)
p.write_text(s)
