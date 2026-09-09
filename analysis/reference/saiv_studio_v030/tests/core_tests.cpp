#include "core.hpp"
#include "gswteos-10.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <stdexcept>
#include <filesystem>
using namespace saiv;
int checks=0;
void require(bool x,const char* message){++checks;if(!x)throw std::runtime_error(message);}
std::string read(const std::filesystem::path& p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("fixture missing");return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char** argv){try{
 require(std::isnan(number("nan"))&&std::isnan(number("-999"))&&std::isnan(number("1e99")),"missing values");
 require(number("12,345")==12.345&&std::isnan(number("12junk")),"decimal comma and strict parse");
 Decoder d;d.feed("FIELDS: COUNT;T;C;DATE;TIME\r");d.feed("\n1;nan;34.5;2026-09-08;12:00:00\r\n2;13.2;35.1;2026-09-08;12:00:10\n");d.finish();
 require(d.table.rows.size()==2&&std::isnan(d.table.value(0,d.table.column("T")))&&d.table.value(0,d.table.column("C"))==34.5,"compact NaN alignment");
 d.line("3;bad;4");require(d.table.rejected==1,"reject column mismatch");
 d.reset();d.feed("N00001 S23.4 T+14.1 P0000.30 OX093.19 OFnan OT001.20\nN00002 C34.5 T+13.2 P1.0\n");
 require(d.table.rows.size()==2&&d.table.value(0,d.table.column("S"))==23.4,"full data tokens");
 require(std::isnan(d.table.value(0,d.table.column("OF")))&&d.table.value(0,d.table.column("OT"))==1.2,"full NaN slot");
 require(std::isnan(d.table.value(1,d.table.column("S"))),"absent channel is missing not stale");
 d.line("N02744 C00.00 T+23.759 P0000.00 c1493.31");require(d.table.column("C")!=d.table.column("c")&&d.table.value(2,d.table.column("C"))==0&&d.table.value(2,d.table.column("c"))==1493.31,"conductivity C and sound speed c are distinct");
 auto rt=loadText(d.table.csv(),"roundtrip");require(rt.rows.size()==3&&rt.columns.size()==d.table.columns.size(),"CSV roundtrip");
 auto fixture=std::filesystem::path(argc>1?argv[1]:"samples");
 for(auto name:{"saiv_export.txt","ctd_profile.txt","surface_compact.txt"}){auto t=loadText(read(fixture/name),name);require(!t.rows.empty(),name);std::cout<<name<<": "<<t.rows.size()<<" rows\n";}
 auto real=loadText(read(fixture/"saiv_export.txt"),"export");require(real.rows.size()==43,"real export row count");
 Table t;t.columns={"P","T","S"};t.rows={{"0","10","35"},{"1","11","35"},{"2","100","35"},{"3","13","35"},{"4","14","35"}};
 require(std::isnan(despike(t,1,3,10).value(2,3)),"spike blanked");require(t.value(2,1)==100,"source preserved");
 require(affine(t,1,2,-1).value(0,3)==19,"gain offset");require(rangeRows(t,1,3).rows.size()==2,"split / selected rows");require(filterRange(t,0,1,3).rows.size()==3,"range filter inclusive");
 auto grid=standardDepths(t,0,.5,2);require(grid.rows.size()==9&&grid.value(1,1)==10.5,"linear depth interpolation");
 t.rows.push_back({"3","1","35"});bool rejected=false;try{standardDepths(t,0,1,2);}catch(...){rejected=true;}require(rejected,"reject mixed casts");
 require(std::abs(gsw_sp_from_c(42.914,15/1.00024,0)-35)<1e-6,"PSS-78 standard seawater reference");
 Table calc;calc.columns={"C","T","P","OX"};calc.rows={{"42.914","15","0","100"},{"-1","15","0","100"},{"0","15","0","100"},{"","15","0","100"}};
 CalculationOptions options;options.conductivity=0;options.temperature=1;options.pressure=2;options.oxygen=3;options.temperature68=true;auto result=calculate(calc,options);
 require(std::abs(result.value(0,4)-35)<1e-6,"temperature conversion exactly once");require(std::isnan(result.value(1,4))&&std::isnan(result.value(3,4)),"invalid C not fresh water");require(result.value(2,4)==0,"valid fresh water preserved");require(result.value(0,9)>1400&&result.value(0,9)<1600,"sound velocity plausible");

 std::vector<std::string> tx;Protocol p;p.send=[&](const std::string& s){tx.push_back(s);};p.connected();p.ingest("Refresh disk Y/N",0);p.tick(.3);require(tx.empty(),"unsolicited prompt ignored");p.ingest("OSU107 Instrument logger SN107, Ver: 0.9.9P\n",.4);p.tick(.7);require(p.device.logger,"logger identity");
 require(p.receiveData(1),"download started");p.tick(1);p.ingest("Refresh disk Y/",1.1);p.ingest("N",1.2);p.tick(1.449);require(tx.size()==1,"no TX before 250 ms quiet");p.tick(1.451);require(tx.size()==2&&tx[0]=="F"&&tx[1]=="Y","fragmented prompt sends one bare Y");p.ingest("ERR: stop surface-logger and wait for the current sample to finish\nRefresh disk Y/N",1.5);p.tick(1.76);require(tx.size()==2&&p.operation==Protocol::Operation::Idle&&!p.error.empty(),"blocked response never sends repeated Y");
 p.receiveData(2);p.tick(2);p.ingest("Refresh disk Y/N",2.1);p.tick(2.36);p.ingest("System disk refresh will start in 3 seconds.",2.4);p.tick(2.66);require(p.operation==Protocol::Operation::Idle&&p.error.empty(),"refresh confirmed");
 p.receiveData(3);p.tick(3);p.ingest("Refresh disk Y/N",3.1);p.tick(3.36);p.tick(12);require(!p.error.empty()&&p.operation==Protocol::Operation::Idle,"refresh timeout");
 const std::string startup="Stored air pressure\r\nChange air pressure <A>\r\nStatus/Start/Menu <S>\r\nPassive <H>\r\nIf no command, measurement will start in 10 sec.\r\n";
 const std::string status="Status: battery good\r\nStart measuring <I>\r\nGo to menu <M>\r\n";
 const std::string main="Menu:\r\nMeasuring interval <I>\r\nDump stored data <F>\r\nErase memory <E>\r\nSet coefficients <M>\r\nStart via key-board <R>\r\nExit (passive) <H>\r\n";
 p.connected();tx.clear();p.wake(0);p.ingest(startup,.1);p.tick(.349);require(tx.empty(),"startup must finish and settle");p.tick(.351);require(tx==std::vector<std::string>{"S"},"startup sends S, never I or M");p.ingest(status,.5);p.tick(.76);require(tx==std::vector<std::string>({"S","M"}),"status sends M only after quiet");p.ingest(main,.8);p.tick(1.06);p.tick(2);require(tx.size()==2&&p.mainMenu&&p.operation==Protocol::Operation::Idle,"main menu stops all wake commands");
 p.receiveData(3);p.tick(3);p.ingest("N00001 S35 T10 P1\nEnd of da",3.1);p.ingest("ta.",3.2);p.tick(3.46);require(p.downloadComplete&&p.download.find("N00001")!=std::string::npos,"legacy completion and capture");
 // Every possible menu split, including a pause >250 ms before the final line.
 for(size_t split=1;split<main.size();split++){Protocol q;std::vector<std::string> sent;q.send=[&](const std::string& v){sent.push_back(v);};q.connected();q.wake(0);q.ingest(main.substr(0,split),.1);q.tick(.4);q.ingest(main.substr(split),.5);q.tick(.751);require(sent.empty()&&q.mainMenu,"partial main menu must never trigger I/M");}
 p.connected();tx.clear();p.ingest(main,0);p.tick(.3);p.wake(.4);p.tick(.4);require(tx.empty()&&p.mainMenu,"already in main menu: no writes");
 p.connected();tx.clear();p.wake(0);p.tick(1.2);require(tx==std::vector<std::string>{"G"},"unknown state checks G before waking");p.ingest("Unknown instrument text",1.3);p.tick(2.5);require(tx.size()==1,"unrecognised response suppresses wake commands");
 require(identify("SAIV110 Surface logger SN321, Ver: 1.0\n").surface,"surface identity");
 p.connected();tx.clear();p.ingest("partial menu",.1);require(p.typeCharacters("I",.2)&&p.typeCharacters("S",.21),"terminal input queues every character");p.tick(.34);require(tx.empty(),"terminal input respects RX quiet time");p.tick(.36);require(tx==std::vector<std::string>{"IS"},"terminal input is not overwritten or given an extra line ending");
 std::cout<<"PASS "<<checks<<" checks\n";return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}}
