#pragma once
#include <string>
#include <vector>
#include <map>
#include <functional>
#include <limits>
#include <deque>
namespace saiv {
constexpr double missing = std::numeric_limits<double>::quiet_NaN();
std::string trim(std::string s);
std::string lower(std::string s);
double number(std::string s);
std::string format(double value);
std::vector<std::string> splitRecord(const std::string& s, char delimiter);
std::string csvQuote(const std::string& s);
struct Table {
 std::vector<std::string> columns;
 std::vector<std::vector<std::string>> rows;
 std::vector<std::string> notes;
 std::string source;
 size_t rejected=0;
 int column(const std::string& name) const;
 double value(size_t row,int col) const;
 void append(const std::map<std::string,std::string>& values);
 std::string csv() const;
};
class Decoder {
 std::string partial_;
 std::vector<std::string> schema_;
 char separator_=';';
 bool previousCR_=false;
public:
 Table table;
 void feed(const std::string& data);
 void finish();
 void line(std::string text);
 void reset();
};
Table loadText(const std::string& text,const std::string& source);
Table demoProfile();
struct Statistics { size_t valid=0,invalid=0; double min=missing,max=missing,mean=missing,sd=missing; };
Statistics statistics(const Table&,int column,size_t first=0,size_t last=SIZE_MAX);
Table rangeRows(const Table&,size_t first,size_t last);
Table filterRange(const Table&,int column,double minimum,double maximum);
Table despike(const Table&,int column,int window,double threshold);
Table affine(const Table&,int column,double gain,double offset);
Table standardDepths(const Table&,int depth,double step,double maximumGap);
struct CalculationOptions { int conductivity=-1,salinity=-1,temperature=-1,pressure=-1,oxygen=-1; double latitude=0,longitude=0; bool temperature68=false; };
Table calculate(const Table&,const CalculationOptions&);
struct Identity { std::string model,serial,firmware; bool logger=false,surface=false; };
Identity identify(const std::string&);
class Protocol {
public:
 enum class Operation { Idle,Wake,Download,Refresh };
 enum class Menu { Unknown,Passive,Startup,Status,Main,Measuring,Submenu,Surface };
 Menu menu=Menu::Unknown;
 Operation operation=Operation::Idle;
 std::string status="Disconnected", error, download;
 Identity device;
 bool mainMenu=false,passive=false,running=false,downloadComplete=false;
 std::function<void(const std::string&)> send;
 void connected();
 void disconnected();
 bool wake(double now);
 bool receiveData(double now);
 void cancel();
 void ingest(const std::string& text,double now);
 void tick(double now);
 bool manual(const std::string&, double now);
 bool typeCharacters(const std::string&, double now);
 const char* menuName() const;
private:
 std::string buffer_;
 double deadline_=0,nextWake_=0,lastRx_=0,opened_=0;
 std::string pending_;
 bool requestSent_=false;
 int wakeStage_=0;
 bool sentY_=false;
};
}
