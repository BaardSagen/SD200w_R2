#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
#include <windows.h>
#include <objbase.h>
#include <commctrl.h>
#include <shellapi.h>
#include <memory>
#include <vector>
#include <string>
#include <stdexcept>
#include <cstdint>
#include "../sit_import/settings_protocol.h"
static HINSTANCE instance;
static std::wstring wide(const std::string&s){int n=MultiByteToWideChar(CP_UTF8,0,s.data(),int(s.size()),0,0);std::wstring w(n,0);if(n)MultiByteToWideChar(CP_UTF8,0,s.data(),int(s.size()),&w[0],n);return w;}
static HWND control(HWND p,const wchar_t*cls,const wchar_t*txt,DWORD style,int x,int y,int w,int h,int id){HWND c=CreateWindowExW(0,cls,txt,WS_CHILD|WS_VISIBLE|style,x,y,w,h,p,(HMENU)(INT_PTR)id,instance,0);SendMessageW(c,WM_SETFONT,(WPARAM)GetStockObject(DEFAULT_GUI_FONT),TRUE);return c;}
static std::string readFile(const std::wstring&p){HANDLE f=CreateFileW(p.c_str(),GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);if(f==INVALID_HANDLE_VALUE)throw std::runtime_error("Cannot read test launcher");DWORD size=GetFileSize(f,0),got=0;std::string s(size,0);bool ok=ReadFile(f,&s[0],size,&got,0)&&got==size;CloseHandle(f);if(!ok)throw std::runtime_error("Cannot read test launcher");return s;}
#define SIT_UPDATE_VERSION "1.3.9"
#include "../sit_import/update_ui.inc"
static LRESULT CALLBACK host(HWND h,UINT m,WPARAM w,LPARAM l){if(m==WM_DESTROY){PostQuitMessage(0);return 0;}return DefWindowProcW(h,m,w,l);}
int WINAPI WinMain(HINSTANCE i,HINSTANCE,LPSTR,int){instance=i;wchar_t own[32768],pid[30];GetModuleFileNameW(0,own,32768);wsprintfW(pid,L"%lu",GetCurrentProcessId());SetEnvironmentVariableW(L"SIT_LAUNCHER_PATH",own);SetEnvironmentVariableW(L"SIT_LAUNCHER_PID",pid);WNDCLASSW wc={};wc.hInstance=i;wc.lpfnWndProc=host;wc.lpszClassName=L"SITUpdateTestHost";RegisterClassW(&wc);HWND h=CreateWindowW(wc.lpszClassName,L"Isolated update test host",WS_OVERLAPPEDWINDOW,0,0,600,400,0,0,i,0);ShowWindow(h,SW_SHOW);updateShow(h);MSG msg;while(GetMessageW(&msg,0,0,0)>0){if(!updateWindow||!IsDialogMessageW(updateWindow,&msg)){TranslateMessage(&msg);DispatchMessageW(&msg);}}return 0;}
