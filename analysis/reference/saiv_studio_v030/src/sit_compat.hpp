#pragma once
#include "core.hpp"
#include "sit/native_data.h"
#include <filesystem>

namespace saiv {
// Formula order: C/T/P, P/T/S, P/T/S, latitude/P.
double sitFormula(int kind,double a,double b,double c);
// The established SIT conversion callback 0 instead takes P,C,T.
double sitConversionFormula(int kind,double a,double b,double c);
double sitConductivity(double salinity,double temperature,double pressure);
sit::Data toSit(const Table&);
Table fromSit(const sit::Data&);
Table loadDataset(const std::filesystem::path&);
Table parseCsvDataset(const std::string&,const std::string& source);
Table enrichSit(Table);
void saveNativeDataset(const Table&,const std::filesystem::path&);
std::vector<double> measurementSeconds(const Table&);
std::string fieldsText(const Table&);
std::string readDatasetBytes(const std::filesystem::path&);
void writeNewFile(const std::filesystem::path&,const std::string&);
}
