#pragma once
#include <windows.h>
#include "core.hpp"
namespace saiv {
bool convertDialog(HWND owner,Table& data);
void mergeDialog(HWND owner);
}
