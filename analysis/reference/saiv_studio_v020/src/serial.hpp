#pragma once
#include <atomic>
#include <mutex>
#include <thread>
#include <deque>
#include <vector>
#include <string>
#include "core.hpp"
namespace saiv {
struct PortInfo { std::string name,description; };
std::vector<PortInfo> enumeratePorts();
struct SerialSettings { std::string port; unsigned baud=9600; int parity=0,bits=8; bool dtr=true,rts=true; };
struct SerialEvent { enum Kind { Connected,Received,Transmitted,Error,Closed } kind; std::string text; };
class Serial {
 std::thread worker_;
 std::atomic<bool> stop_{false};
 std::mutex mutex_;
 std::deque<std::string> outgoing_;
 std::deque<SerialEvent> events_;
 size_t queuedBytes_=0;
 void event(SerialEvent::Kind,const std::string&);
 void run(SerialSettings);
public:
 std::atomic<bool> connected{false};
 ~Serial(){disconnect();}
 void connect(const SerialSettings&);
 void disconnect();
 void write(const std::string&);
 std::vector<SerialEvent> poll();
};
struct Detection { PortInfo port; Identity identity; std::string status; SerialSettings settings; };
class Detector {
 std::thread worker_;
 std::mutex mutex_;
 std::vector<Detection> results_;
 std::atomic<bool> stop_{false};
public:
 std::atomic<bool> busy{false};
 ~Detector(){stop_=true;if(worker_.joinable())worker_.join();}
 void start();
 void cancel(){stop_=true;}
 std::vector<Detection> results();
};
std::string windowsError(unsigned code);
}
