#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
#define _WIN32_IE 0x0600
#include <windows.h>
#include <commctrl.h>
#include <commdlg.h>
#include <shellapi.h>
#include <cstdio>
#ifndef LVS_EX_DOUBLEBUFFER
#define LVS_EX_DOUBLEBUFFER 0x10000
#endif
#include <memory>
#include "sit/logger.h"
#include "sit_compat.hpp"
#include "native_dialogs.hpp"
#include "sit/native_data.h"
static HINSTANCE instance;
static HFONT studioDialogFont(){static HFONT f=CreateFontW(-15,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,CLEARTYPE_QUALITY,DEFAULT_PITCH,L"Segoe UI");return f;}

static std::wstring wide(const std::string&s,UINT cp=CP_UTF8){int n=MultiByteToWideChar(cp,0,s.data(),int(s.size()),0,0);std::wstring w(n,L' ');if(n)MultiByteToWideChar(cp,0,s.data(),int(s.size()),&w[0],n);return w;}
static std::string utf8(const std::wstring&w){int n=WideCharToMultiByte(CP_UTF8,0,w.data(),int(w.size()),0,0,0,0);std::string s(n,' ');if(n)WideCharToMultiByte(CP_UTF8,0,w.data(),int(w.size()),&s[0],n,0,0);return s;}
static std::wstring caption(HWND h){int n=GetWindowTextLengthW(h);std::wstring s(n+1,L' ');GetWindowTextW(h,&s[0],n+1);s.resize(n);return s;}
static HWND control(HWND p,const wchar_t*cls,const wchar_t*txt,DWORD style,int x,int y,int w,int h,int id){HWND c=CreateWindowExW(0,cls,txt,WS_CHILD|WS_VISIBLE|style,x,y,w,h,p,(HMENU)(INT_PTR)id,instance,0);SendMessageW(c,WM_SETFONT,(WPARAM)studioDialogFont(),TRUE);return c;}
static std::wstring fieldLabel(const std::string&f){
 if(f.compare(0,3,"M1_")==0||f.compare(0,3,"M2_")==0)return wide(f.substr(0,3))+fieldLabel(f.substr(3));
 if(f=="Delta_seconds")return L"Time difference (seconds)";
 if(f=="C")return L"C - Conductivity (mS/cm)";if(f=="T")return L"T - Temperature (\u00b0C, Celsius)";if(f=="T_degF")return L"T_degF - Temperature (\u00b0F, Fahrenheit)";if(f=="P")return L"P - Pressure (dbar)";
 if(f=="OF")return L"OF - Fluorescence (\u00b5g/L)";if(f=="OT")return L"OT - Turbidity (FTU)";
 if(f=="S"||f=="S_from_C"||f=="Salinity_SIT")return wide(f)+L" - Salinity";
 if(f=="Par")return L"Par - PAR";if(f=="Par_umol_m2_s")return L"PAR (\u00b5mol photons/m\u00b2/s)";
 if(f=="Depth_m")return L"Real depth (m)";
 if(f=="OX")return L"OX - SAIV205 (%)";if(f=="OxR")return L"OxR - RINKO (%)";
 if(f=="OxR_mg_L")return L"OxR (mg/L)";if(f=="OxR_mL_L")return L"OxR (mL/L)";
 if(f=="OX_mg_L")return L"OX (mg/L)";if(f=="OX_mL_L")return L"OX (mL/L)";
 if(f=="Sound_velocity_SIT_m_s")return L"Sound velocity (m/s)";
 if(f=="Density_anomaly_SIT_kg_m3")return L"Density -1000 (kg/m3)";return wide(f);
}
static void error(HWND h,const std::string&s){MessageBoxW(h,wide(s).c_str(),L"SAIV Studio - Import",MB_OK|MB_ICONERROR);}
static double formula(int f,double a,double b,double c){return saiv::sitConversionFormula(f,a,b,c);}
static std::string readFile(const std::wstring&path,bool probe=false){HANDLE h=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot read selected file");LARGE_INTEGER size;if(!GetFileSizeEx(h,&size)||(!probe&&size.QuadPart>20*1024*1024)||size.QuadPart<0){CloseHandle(h);throw std::runtime_error("Import supports files up to 20 MB");}std::string s(size_t(probe?std::min<LONGLONG>(65536,size.QuadPart):size.QuadPart),' ');DWORD got=0;BOOL ok=ReadFile(h,s.empty()?0:&s[0],DWORD(s.size()),&got,0);CloseHandle(h);if(!ok||got!=s.size())throw std::runtime_error("Could not read the complete file");return s;}

static LRESULT studioControlColor(WPARAM wp){HDC dc=reinterpret_cast<HDC>(wp);SetTextColor(dc,RGB(26,38,54));SetBkMode(dc,TRANSPARENT);return reinterpret_cast<LRESULT>(GetStockObject(WHITE_BRUSH));}

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
