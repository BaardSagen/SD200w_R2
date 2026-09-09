"""Adapt the preserved SIT import UI source for independent Studio callbacks."""
from pathlib import Path
R=Path(__file__).resolve().parent.parent
source=(R/'sit_import/sit_import.cpp').read_text(encoding='utf-8')
prefix=source.split('#include "wizard.inc"')[0]
start=prefix.index('static double formula(')
end=prefix.index('static std::string readFile',start)
prefix=prefix[:start]+'static double formula(int f,double a,double b,double c){return saiv::sitFormula(f,a,b,c);}\n'+prefix[end:]
prefix=prefix.replace('#include "logger.h"','#include "sit/logger.h"\n#include "sit_compat.hpp"\n#include "native_dialogs.hpp"')
prefix=prefix.replace('#include "native_data.h"','#include "sit/native_data.h"')
prefix=prefix.replace('GetStockObject(DEFAULT_GUI_FONT)','studioDialogFont()')
prefix=prefix.replace('static HINSTANCE instance;','''static HINSTANCE instance;
static HFONT studioDialogFont(){static HFONT f=CreateFontW(-15,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,CLEARTYPE_QUALITY,DEFAULT_PITCH,L"Segoe UI");return f;}
''')
prefix+='''
#include "sit/wizard.inc"
#include "sit/presets_ui.inc"
#include "sit/merge_ui.inc"
namespace saiv {
static void initializeDialogs(){
 instance=GetModuleHandleW(nullptr);INITCOMMONCONTROLSEX ic={sizeof(ic),ICC_LISTVIEW_CLASSES|ICC_LINK_CLASS};InitCommonControlsEx(&ic);
 WNDCLASSW wc={};wc.hInstance=instance;wc.hCursor=LoadCursor(nullptr,IDC_ARROW);wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);wc.lpfnWndProc=wizardProc;wc.lpszClassName=L"SITImportChoices";RegisterClassW(&wc);
}
bool convertDialog(HWND owner,Table&table){
 initializeDialogs();sit::Data data=toSit(table);sit::Choices choices;sitpreset::Record previous;bool reused=false;
 if(loadPreset(data,previous)){int answer=offerPreset(owner,data,previous);if(answer==IDCANCEL)return false;if(answer==IDYES){choices=sitpreset::reuse(previous,data);reused=true;}}
 sit::Choices saved=choices;if(!choose(owner,data,choices,reused?&saved:nullptr))return false;
 auto signature=sitpreset::signature(data);sit::calculate(data,choices,formula);
 if(!savePreset(signature,data.source,choices))MessageBoxW(owner,L"Conversion completed, but the choices could not be saved.",L"SAIV Studio",MB_OK|MB_ICONINFORMATION);
 table=fromSit(data);return true;
}
void mergeDialog(HWND owner){initializeDialogs();SitMerge(owner);}
}
'''
prefix=prefix.replace('SAIV IT','SAIV Studio')
(R/'saiv-studio/src/native_dialogs.cpp').write_text(prefix,encoding='utf-8')
for name in ['wizard.inc','presets_ui.inc','merge_ui.inc']:
 p=R/'saiv-studio/src/sit'/name
 text=p.read_text(encoding='utf-8').replace('SAIV IT','SAIV Studio')
 if name=='presets_ui.inc':text=text.replace('Software\\\\MHP\\\\SdInstr\\\\ConvertPresetsV1','Software\\\\SAIV\\\\InstrumentStudio\\\\ConvertPresetsV1')
 p.write_text(text,encoding='utf-8')
print('Prepared standalone Studio dialog integration; formula calls use C++ and presets use Studio registry.')
