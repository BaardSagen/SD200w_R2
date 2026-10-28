// Inert test process. It never opens a COM port or starts SIT.
// A close request marks that the actual installer passed extraction/version checks.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
static LRESULT CALLBACK proc(HWND h,UINT m,WPARAM w,LPARAM l) {
    if(m==WM_CLOSE){SetWindowTextW(h,L"SIT installer preflight verified");return 0;}
    return DefWindowProcW(h,m,w,l);
}
int WINAPI WinMain(HINSTANCE instance,HINSTANCE,LPSTR,int) {
    WNDCLASSW wc={};wc.hInstance=instance;wc.lpfnWndProc=proc;
    wc.lpszClassName=L"SITPackageTestHost";RegisterClassW(&wc);
    HWND h=CreateWindowW(wc.lpszClassName,L"SIT installer test host",WS_OVERLAPPEDWINDOW,
                         0,0,400,150,0,0,instance,0);
    ShowWindow(h,SW_SHOW);MSG msg;
    while(GetMessageW(&msg,0,0,0)>0){TranslateMessage(&msg);DispatchMessageW(&msg);}
    return 0;
}
