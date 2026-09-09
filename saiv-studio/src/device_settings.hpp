#pragma once
#include "serial.hpp"
#include <filesystem>
namespace saiv {
struct SettingResult { std::string message,received,error; };
SettingResult changeDeviceSetting(Serial&,SerialSettings,Identity,const std::string& context,bool clock,int interval,bool utc,const std::filesystem::path& config);
}
