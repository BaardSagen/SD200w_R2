#include "presets.h"
static const wchar_t* presetRegistry=L"Software\\SAIV\\InstrumentStudio\\ConvertPresetsV1";
static bool loadPreset(const sit::Data&data,sitpreset::Record&record){
 HKEY h;LONG status=RegOpenKeyExW(HKEY_CURRENT_USER,presetRegistry,0,KEY_QUERY_VALUE,&h);if(status!=ERROR_SUCCESS)return false;
 std::string sig=sitpreset::signature(data);std::wstring name=wide(sitpreset::key(sig));DWORD type=0,size=0;status=RegQueryValueExW(h,name.c_str(),0,&type,0,&size);
 if(status!=ERROR_SUCCESS||type!=REG_BINARY||size>65536){RegCloseKey(h);return false;}
 std::string bytes(size,'\0');status=RegQueryValueExW(h,name.c_str(),0,&type,(BYTE*)&bytes[0],&size);RegCloseKey(h);return status==ERROR_SUCCESS&&type==REG_BINARY&&sitpreset::decode(bytes,sig,record);
}
static bool savePreset(const std::string&signature,const std::string&source,const sit::Choices&choices){
 SYSTEMTIME t;GetLocalTime(&t);char date[32];std::sprintf(date,"%04d-%02d-%02d %02d:%02d:%02d",t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond);
 sitpreset::Record r;r.signature=signature;r.source=source;r.date=date;r.choices=choices;std::string bytes=sitpreset::encode(r);if(bytes.size()>65536)return false;
 HKEY h;if(RegCreateKeyExW(HKEY_CURRENT_USER,presetRegistry,0,0,0,KEY_SET_VALUE,0,&h,0)!=ERROR_SUCCESS)return false;std::wstring name=wide(sitpreset::key(signature));LONG status=RegSetValueExW(h,name.c_str(),0,REG_BINARY,(const BYTE*)bytes.data(),DWORD(bytes.size()));RegCloseKey(h);return status==ERROR_SUCCESS;
}
static int offerPreset(HWND owner,const sit::Data&data,const sitpreset::Record&r){
 std::string leaf=r.source.substr(r.source.find_last_of("\\/")+1);
 std::wstring text=L"This file has the same instrument type and column layout as a previous conversion.\r\n\r\nLast used: "+wide(r.date)+L" (local time)\r\nPrevious file: "+wide(leaf)+L"\r\n\r\nUse the same column and conversion choices?\r\n\r\nYes: reuse the choices.\r\nNo: go through each column with Next.\r\nCancel: stop this conversion.\r\n\r\nGPS and any missing temperature, salinity or air pressure will be requested again when needed.";
 return MessageBoxW(owner,text.c_str(),L"SAIV Studio - Previous conversion",MB_YESNOCANCEL|MB_ICONQUESTION);
}
