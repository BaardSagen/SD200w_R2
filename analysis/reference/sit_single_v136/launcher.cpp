#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
#include <windows.h>
#include <shlobj.h>
#include <string>
#include <vector>
#include <stdexcept>
#include "bundle_config.h"
static void fail(const char*s){throw std::runtime_error(s);}
static void directory(const std::wstring&p){if(!CreateDirectoryW(p.c_str(),0)&&GetLastError()!=ERROR_ALREADY_EXISTS)fail("Cannot create the program folder in AppData.");DWORD a=GetFileAttributesW(p.c_str());if(a==INVALID_FILE_ATTRIBUTES||!(a&FILE_ATTRIBUTE_DIRECTORY)||(a&FILE_ATTRIBUTE_REPARSE_POINT))fail("The program cache folder is not a regular directory.");}
struct Resource {const BYTE*data;DWORD size;Resource(HINSTANCE i,int id){HRSRC r=FindResourceW(i,MAKEINTRESOURCEW(id),MAKEINTRESOURCEW(10));if(!r)fail("The embedded program is missing.");size=SizeofResource(i,r);HGLOBAL h=LoadResource(i,r);data=h?(const BYTE*)LockResource(h):0;if(!data||!size)fail("Cannot read the embedded program.");}};
static HANDLE verified(const std::wstring&p,const Resource&r){
 HANDLE f=CreateFileW(p.c_str(),GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);if(f==INVALID_HANDLE_VALUE)return f;
 LARGE_INTEGER size;bool ok=GetFileSizeEx(f,&size)&&size.QuadPart==r.size;BYTE buf[16384];DWORD pos=0;
 while(ok&&pos<r.size){DWORD want=(r.size-pos<sizeof(buf))?r.size-pos:sizeof(buf),got=0;ok=ReadFile(f,buf,want,&got,0)&&got==want&&!memcmp(buf,r.data+pos,want);pos+=want;}
 if(!ok){CloseHandle(f);return INVALID_HANDLE_VALUE;}return f;
}
static HANDLE ensure(HINSTANCE i,int id,const std::wstring&p){
 Resource r(i,id);HANDLE f=verified(p,r);if(f!=INVALID_HANDLE_VALUE)return f;
 // Only exact files owned by this versioned cache are repaired. Never touch customer files.
 if(!DeleteFileW(p.c_str())&&GetLastError()!=ERROR_FILE_NOT_FOUND)fail("Cannot repair a program component. Close other SAIV IT windows and try again.");
 f=CreateFileW(p.c_str(),GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);if(f==INVALID_HANDLE_VALUE)fail("Cannot install the program component in AppData.");DWORD written=0;BOOL ok=WriteFile(f,r.data,r.size,&written,0);BOOL flushed=FlushFileBuffers(f);CloseHandle(f);
 if(!ok||written!=r.size||!flushed){DeleteFileW(p.c_str());fail("Could not write the complete program component.");}
 f=verified(p,r);if(f==INVALID_HANDLE_VALUE)fail("Cannot verify the installed program component.");return f;
}
static std::wstring arguments(){const wchar_t*p=GetCommandLineW();bool quoted=false;while(*p){if(*p==L'"')quoted=!quoted;else if(!quoted&&(*p==L' '||*p==L'\t'))break;++p;}return p;}
int WINAPI WinMain(HINSTANCE instance,HINSTANCE,LPSTR,int show){
 HANDLE exeFile=INVALID_HANDLE_VALUE,dllFile=INVALID_HANDLE_VALUE,mutex=0;bool locked=false;PROCESS_INFORMATION pi={};DWORD result=1;
 try{
  wchar_t appdata[MAX_PATH];if(FAILED(SHGetFolderPathW(0,CSIDL_LOCAL_APPDATA|CSIDL_FLAG_CREATE,0,0,appdata)))fail("Cannot find the user's AppData folder.");
  std::wstring parent=std::wstring(appdata)+L"\\SAIV_IT";directory(parent);std::wstring folder=parent+L"\\"+SIT_CACHE_TAG;directory(folder);
  // Serialize first install and repair for this user/session; ready files are never rewritten.
  unsigned long hash=2166136261UL;for(wchar_t ch:folder){hash^=ch;hash*=16777619UL;}wchar_t suffix[20];wsprintfW(suffix,L"%08lx",hash);std::wstring mutexName=L"Local\\SAIV_IT_install_"+std::wstring(suffix);
  mutex=CreateMutexW(0,FALSE,mutexName.c_str());if(!mutex)fail("Cannot prepare program components.");DWORD wait=WaitForSingleObject(mutex,30000);if(wait!=WAIT_OBJECT_0&&wait!=WAIT_ABANDONED)fail("Another SAIV IT start is still preparing its files. Try again.");locked=true;
  wchar_t shortPath[32768];DWORD n=GetShortPathNameW(folder.c_str(),shortPath,32768);std::wstring runtime=(n&&n<32768)?shortPath:folder;
  BOOL substituted=FALSE;char ansi[32768];int bytes=WideCharToMultiByte(CP_ACP,WC_NO_BEST_FIT_CHARS,runtime.c_str(),-1,ansi,sizeof(ansi),0,&substituted);if(!bytes||substituted||bytes>200)fail("The AppData path is too long or cannot be used by this program.");
  exeFile=ensure(instance,101,folder+L"\\SAIV_IT_Runtime.exe");dllFile=ensure(instance,102,folder+L"\\SIT_Import136.dll");ReleaseMutex(mutex);locked=false;CloseHandle(mutex);mutex=0;
  std::wstring launch=runtime+L"\\SAIV_IT_Runtime.exe",command=L"\""+launch+L"\""+arguments();std::vector<wchar_t> writable(command.begin(),command.end());writable.push_back(0);
  STARTUPINFOW inherited={};inherited.cb=sizeof(inherited);GetStartupInfoW(&inherited);STARTUPINFOW si={};si.cb=sizeof(si);si.lpDesktop=inherited.lpDesktop;si.dwFlags=STARTF_USESHOWWINDOW;si.wShowWindow=(WORD)show;
  if(!CreateProcessW(launch.c_str(),writable.data(),0,0,FALSE,0,0,0,&si,&pi))fail("Cannot start SAIV Instrument Terminal.");CloseHandle(pi.hThread);pi.hThread=0;
  if(WaitForSingleObject(pi.hProcess,INFINITE)!=WAIT_OBJECT_0)fail("Cannot wait for SAIV Instrument Terminal.");GetExitCodeProcess(pi.hProcess,&result);CloseHandle(pi.hProcess);pi.hProcess=0;
 }catch(const std::exception&e){std::string msg=e.what();msg+="\r\nStart this EXE again to retry the automatic setup.";MessageBoxA(0,msg.c_str(),"SAIV Instrument Terminal",MB_OK|MB_ICONERROR);}
 if(locked)ReleaseMutex(mutex);if(mutex)CloseHandle(mutex);if(pi.hThread)CloseHandle(pi.hThread);if(pi.hProcess)CloseHandle(pi.hProcess);if(exeFile!=INVALID_HANDLE_VALUE)CloseHandle(exeFile);if(dllFile!=INVALID_HANDLE_VALUE)CloseHandle(dllFile);return (int)result;
}
