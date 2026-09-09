#pragma once
#include "core.hpp"
#include "serial.hpp"
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <future>
#include <optional>
#include "imgui.h"
namespace saiv {
struct Document { Table table; int x=-1,y=-1; bool profile=false; };
class App {
 HWND window_; Serial serial_; Detector detector_; Protocol protocol_; Decoder live_;
 std::vector<PortInfo> ports_; SerialSettings settings_;
 bool connectionWanted_=false,connecting_=false,reconnect_=false; double nextReconnect_=0;
 std::vector<Document> documents_; int document_=0,page_=1,baudIndex_=3;
 bool demo_=false,follow_=true; std::deque<std::string> terminal_;
 std::string terminalPartial_,notice_="Ready. Connect an instrument, open data, or try the demonstration.",error_;
 char portName_[32]{};
 bool terminalFocused_=false,focusTerminal_=true,downloadWanted_=false; std::ofstream testWire_;
 std::ofstream record_; std::filesystem::path recordPath_; size_t rxBytes_=0,txBytes_=0;
 std::future<Table> loader_; std::future<std::string> copier_; bool loading_=false,copying_=false;
 std::filesystem::path disk_; std::vector<std::filesystem::path> diskFiles_; std::vector<bool> diskSelected_;
 std::future<std::vector<std::filesystem::path>> scanner_; bool scanning_=false;
 int utility_=0,utilCol_=0,rangeFirst_=1,rangeLast_=1,windowSize_=5;
 double minimum_=0,maximum_=100,gain_=1,offset_=0,threshold_=1,step_=1,maxGap_=5;
 CalculationOptions calc_; bool locationConfirmed_=false; double latitude_=60.39,longitude_=5.32;
 ImFont* heading_=nullptr; ImFont* mono_=nullptr; std::optional<Table> preview_;
 void addDocument(Table); void log(const std::string&,const std::string&); void acceptRx(const std::string&);
 void send(const std::string&); void poll(); void connect(); void disconnect();
 void loadFile(const std::filesystem::path&); void saveData(const std::string&,const wchar_t*,const wchar_t*);
 std::filesystem::path fileDialog(bool,const wchar_t*,const wchar_t*,const wchar_t*);
 std::filesystem::path folderDialog(const wchar_t*);
 void drawTerminal(); void drawData(); void drawUtilities(); void drawLogger(); void drawAbout();
 void plot(const Table&,int,int,bool,ImVec2); void grid(const Table&,float);
 bool columnPicker(const char*,const Table&,int&,bool=false); Table* selected(); void autoMap();
public:
 App(HWND,ImFont*,ImFont*,bool,const std::filesystem::path& testWire={}); ~App(); void render();
 bool terminalCharacter(unsigned character);
 void open(const std::filesystem::path& path){loadFile(path);} void demo(); void setPage(int p){page_=p;}
 const std::vector<Document>& documents()const{return documents_;}
};
}
