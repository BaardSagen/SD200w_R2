#include "imgui.h"
#include "imgui_impl_win32.h"
#include "imgui_impl_dx11.h"
#include "app.hpp"
#include <windows.h>
#include <d3d11.h>
#include <shellapi.h>
#include <filesystem>
#include <fstream>
#include <memory>
#include <algorithm>
static ID3D11Device* device=nullptr;
static ID3D11DeviceContext* context=nullptr;
static IDXGISwapChain* swapchain=nullptr;
static ID3D11RenderTargetView* target=nullptr;
static saiv::App* activeApp=nullptr;
static UINT resizeW=0,resizeH=0;
// File-transport GUI tests enqueue pointer input after the OS backend refresh.
// These messages are ignored in normal instrument sessions.
static bool testInputEnabled=false;
struct TestPointer {int action,x,y;};
static std::vector<TestPointer> testPointers;
static void destroyTarget(){if(target){target->Release();target=nullptr;}}
static bool makeTarget(){ID3D11Texture2D* buffer=nullptr;if(FAILED(swapchain->GetBuffer(0,IID_PPV_ARGS(&buffer))))return false;HRESULT hr=device->CreateRenderTargetView(buffer,nullptr,&target);buffer->Release();return SUCCEEDED(hr);}
static void cleanup(){destroyTarget();if(swapchain){swapchain->Release();swapchain=nullptr;}if(context){context->Release();context=nullptr;}if(device){device->Release();device=nullptr;}}
static bool createDevice(HWND h){DXGI_SWAP_CHAIN_DESC d{};d.BufferCount=2;d.BufferDesc.Format=DXGI_FORMAT_R8G8B8A8_UNORM;d.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;d.OutputWindow=h;d.SampleDesc.Count=1;d.Windowed=TRUE;d.SwapEffect=DXGI_SWAP_EFFECT_DISCARD;D3D_FEATURE_LEVEL level;const D3D_FEATURE_LEVEL levels[]={D3D_FEATURE_LEVEL_11_0,D3D_FEATURE_LEVEL_10_0};HRESULT hr=D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,levels,2,D3D11_SDK_VERSION,&d,&swapchain,&device,&level,&context);if(FAILED(hr))hr=D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,levels,2,D3D11_SDK_VERSION,&d,&swapchain,&device,&level,&context);return SUCCEEDED(hr)&&makeTarget();}
extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND,UINT,WPARAM,LPARAM);
static LRESULT WINAPI proc(HWND h,UINT msg,WPARAM w,LPARAM l){if(testInputEnabled&&msg==WM_APP+17){testPointers.push_back({int(w),int(short(LOWORD(l))),int(short(HIWORD(l)))});return 1;}if(activeApp&&msg==WM_CHAR&&(w==15||w==16)&&(GetKeyState(VK_CONTROL)&0x8000))return 0;if(activeApp&&msg==WM_CHAR&&activeApp->terminalCharacter(static_cast<unsigned>(w)))return 0;if(activeApp&&msg==WM_KEYDOWN&&w==VK_DELETE&&activeApp->terminalCharacter(127))return 0;if(ImGui_ImplWin32_WndProcHandler(h,msg,w,l))return 1;switch(msg){case WM_SIZE:if(w!=SIZE_MINIMIZED){resizeW=LOWORD(l);resizeH=HIWORD(l);}return 0;case WM_SYSCOMMAND:if((w&0xfff0)==SC_KEYMENU)return 0;break;case WM_GETMINMAXINFO:{auto* m=reinterpret_cast<MINMAXINFO*>(l);m->ptMinTrackSize={920,600};return 0;}case WM_DESTROY:PostQuitMessage(0);return 0;}return DefWindowProcW(h,msg,w,l);}
int WINAPI wWinMain(HINSTANCE instance,HINSTANCE,PWSTR,int){
 ImGui_ImplWin32_EnableDpiAwareness();CoInitializeEx(nullptr,COINIT_APARTMENTTHREADED);
 bool demo=false,smoke=false;std::filesystem::path openPath,testWire;int count=0;LPWSTR* args=CommandLineToArgvW(GetCommandLineW(),&count);for(int i=1;i<count;i++){std::wstring a=args[i];if(a==L"--demo")demo=true;else if(a==L"--smoke-test"){smoke=true;demo=true;}else if(a==L"--terminal-test"&&i+1<count)testWire=args[++i];else if(a==L"--open"&&i+1<count)openPath=args[++i];}LocalFree(args);testInputEnabled=!testWire.empty();
 WNDCLASSEXW wc{sizeof(WNDCLASSEXW)};wc.style=CS_CLASSDC;wc.lpfnWndProc=proc;wc.hInstance=instance;wc.lpszClassName=L"SAIVInstrumentStudio";wc.hCursor=LoadCursor(nullptr,IDC_ARROW);wc.hIcon=static_cast<HICON>(LoadImageW(instance,MAKEINTRESOURCEW(1),IMAGE_ICON,32,32,0));wc.hIconSm=static_cast<HICON>(LoadImageW(instance,MAKEINTRESOURCEW(1),IMAGE_ICON,16,16,0));RegisterClassExW(&wc);
 RECT work{};SystemParametersInfoW(SPI_GETWORKAREA,0,&work,0);int width=std::min(1180L,work.right-work.left-40),height=std::min(780L,work.bottom-work.top-40);HWND window=CreateWindowW(wc.lpszClassName,L"SAIV Instrument Studio 0.3.0",WS_OVERLAPPEDWINDOW,work.left+(work.right-work.left-width)/2,work.top+(work.bottom-work.top-height)/2,width,height,nullptr,nullptr,instance,nullptr);
 if(!window||!createDevice(window)){MessageBoxW(nullptr,L"Unable to initialise DirectX 11.",L"SAIV Instrument Studio",MB_ICONERROR);cleanup();return 1;}
 IMGUI_CHECKVERSION();ImGui::CreateContext();auto& io=ImGui::GetIO();io.IniFilename=nullptr;
 ImGui::StyleColorsLight();auto& style=ImGui::GetStyle();style.WindowPadding={16,14};style.FramePadding={12,8};style.ItemSpacing={10,9};style.WindowRounding=10;style.ChildRounding=8;style.FrameRounding=6;style.PopupRounding=8;style.ScrollbarSize=13;style.ScrollbarRounding=7;style.FrameBorderSize=0;style.WindowBorderSize=1;
 style.Colors[ImGuiCol_MenuBarBg]={.94f,.96f,.98f,1};style.Colors[ImGuiCol_WindowBg]={.96f,.97f,.98f,1};style.Colors[ImGuiCol_ChildBg]={1,1,1,1};style.Colors[ImGuiCol_Text]={.10f,.15f,.21f,1};style.Colors[ImGuiCol_TextDisabled]={.42f,.47f,.53f,1};style.Colors[ImGuiCol_Button]={.88f,.92f,.95f,1};style.Colors[ImGuiCol_ButtonHovered]={.75f,.86f,.94f,1};style.Colors[ImGuiCol_ButtonActive]={.58f,.76f,.90f,1};style.Colors[ImGuiCol_FrameBg]={.91f,.94f,.96f,1};style.Colors[ImGuiCol_Header]={.82f,.9f,.96f,1};style.Colors[ImGuiCol_Border]={.80f,.85f,.89f,1};
 float scale=ImGui_ImplWin32_GetDpiScaleForHwnd(window);style.ScaleAllSizes(scale);auto fonts=std::filesystem::path(L"C:/Windows/Fonts");auto font=(fonts/L"segoeui.ttf").string();ImFont* normal=nullptr;if(std::filesystem::exists(font))normal=io.Fonts->AddFontFromFileTTF(font.c_str(),16*scale);if(!normal)normal=io.Fonts->AddFontDefault();auto bold=(fonts/L"segoeuib.ttf").string();ImFont* heading=std::filesystem::exists(bold)?io.Fonts->AddFontFromFileTTF(bold.c_str(),24*scale):normal;auto monoPath=(fonts/L"consola.ttf").string();ImFont* mono=std::filesystem::exists(monoPath)?io.Fonts->AddFontFromFileTTF(monoPath.c_str(),15*scale):normal;
 ImGui_ImplWin32_Init(window);ImGui_ImplDX11_Init(device,context);ShowWindow(window,SW_SHOWDEFAULT);UpdateWindow(window);
 int exitCode=0;
 try{saiv::App app(window,heading,mono,demo,testWire);activeApp=&app;if(!openPath.empty())app.open(openPath);bool done=false;int frames=0;while(!done){MSG m;while(PeekMessageW(&m,nullptr,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageW(&m);if(m.message==WM_QUIT)done=true;}if(done)break;if(IsIconic(window)){Sleep(50);continue;}if(resizeW&&resizeH){destroyTarget();HRESULT hr=swapchain->ResizeBuffers(0,resizeW,resizeH,DXGI_FORMAT_UNKNOWN,0);resizeW=resizeH=0;if(FAILED(hr)||!makeTarget())throw std::runtime_error("Graphics resize failed.");}
 ImGui_ImplDX11_NewFrame();ImGui_ImplWin32_NewFrame();for(auto&e:testPointers){io.AddMousePosEvent(float(e.x),float(e.y));if(e.action<2)io.AddMouseButtonEvent(0,e.action==1);}testPointers.clear();ImGui::NewFrame();if(smoke)app.setPage(1+(frames/120)%5);app.render();ImGui::Render();float clear[]={.04f,.06f,.09f,1};context->OMSetRenderTargets(1,&target,nullptr);context->ClearRenderTargetView(target,clear);ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());HRESULT hr=swapchain->Present(1,0);if(hr==DXGI_ERROR_DEVICE_REMOVED||hr==DXGI_ERROR_DEVICE_RESET)throw std::runtime_error("Graphics device reset. Restart the application.");if(hr==DXGI_STATUS_OCCLUDED)Sleep(50);frames++;if(smoke&&frames>=720)done=true;}
 activeApp=nullptr;}catch(const std::exception& e){activeApp=nullptr;MessageBoxA(window,e.what(),"SAIV Instrument Studio",MB_ICONERROR);exitCode=2;}
 ImGui_ImplDX11_Shutdown();ImGui_ImplWin32_Shutdown();ImGui::DestroyContext();cleanup();DestroyWindow(window);UnregisterClassW(wc.lpszClassName,instance);CoUninitialize();return exitCode;
}
