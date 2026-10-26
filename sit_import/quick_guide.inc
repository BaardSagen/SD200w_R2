// Offline help for the original SIT menus and terminal workflow.
static const UINT guideMenuId=0x7e44;
struct GuideTopic {const wchar_t* title;const wchar_t* text;};
static const GuideTopic guideTopics[]={
 {L"Start here",
  L"SAIV Instrument Terminal (SIT)\r\n\r\n"
  L"The terminal is the starting point for working with an instrument. The buttons on the right give direct access to the most common tasks.\r\n\r\n"
  L"WITH AN INSTRUMENT\r\nConnect the instrument, choose Detect and accept the correct result. Then use Download, Interval or TIME/DATE as needed.\r\n\r\n"
  L"WITH SAVED DATA\r\nUse File > Open for an existing SD2 dataset. For CSV/TXT files, use File > Import CSV/TXT or Convert. No instrument is needed to work with saved files.\r\n\r\n"
  L"BACK TO THE TERMINAL\r\nChoose View > Instrument.\r\n\r\n"
  L"CHOOSING CALCULATION METHODS\r\nStart with System evaluation for a short recommendation. Select a measurement topic for its method and an example.\r\n\r\n"
  L"Select a topic on the left for a short explanation. Close this guide to return to SIT. The guide is included in the program and works offline."},
 {L"Detect and terminal",
  L"1. Connect the instrument and its communication cable.\r\n\r\n"
  L"2. Click Detect. Wait for the search to finish, check the instrument shown and accept the correct result.\r\n\r\n"
  L"3. The terminal shows the instrument's replies and menus. Click in the terminal to type the commands shown by the instrument. Wait for its reply before sending the next command.\r\n\r\n"
  L"If no instrument is found, check the cable and power, and check Setup > Serial port. Close other programs that may be using the same COM port, then try Detect again.\r\n\r\n"
  L"SIT remembers the last accepted COM port. Run Detect again after changing instruments or ports.\r\n\r\n"
  L"A grey button is currently unavailable. Instrument controls depend on the detected instrument and its connection."},
 {L"Download and save text",
  L"Click Download after Detect has found and accepted the instrument. Follow the prompts for that instrument and wait for the operation to finish.\r\n\r\n"
  L"SD200 INSTRUMENTS\r\nDownload transfers the measurements through the serial connection. Follow SIT's prompts for the data file.\r\n\r\n"
  L"OSU107 / SAIV110 LOGGERS\r\nDownload uses the logger's disk-refresh workflow. After the refresh, use the files on the logger's USB disk. Copy the required CSV/TXT files to a working folder, then use Import CSV/TXT or Convert in SIT.\r\n\r\n"
  L"SAVE TEXT\r\nThe Save text button saves the terminal text. Use the data-file and export commands when you want measurement data for later analysis.\r\n\r\n"
  L"Keep the original downloaded files so you can return to them later."},
 {L"Open and import files",
  L"EXISTING SIT DATA\r\nChoose File > Open and select the SD2 file. Keep its companion files with the same name in the same folder (RF2, OX2, OP2 and SF2, where present). They hold associated data and settings.\r\n\r\n"
  L"CSV/TXT DATA\r\nChoose File > Import CSV/TXT, select the source file and choose a new name for the SD2 dataset. SIT opens the imported data for viewing.\r\n\r\n"
  L"Imported logger fields are retained with the dataset in its SF2 companion file. When copying the dataset, include all its companion files.\r\n\r\n"
  L"If you want to choose units or calculate additional fields first, use Convert instead. In its result window, choose Import to SD2 to open the converted dataset in SIT.\r\n\r\n"
  L"Use File > Close file to close the current dataset."},
 {L"Convert and export",
  L"1. Click Convert, or choose File > Convert CSV/TXT. Select one file, or hold Ctrl/Shift to select several files.\r\n\r\n"
  L"2. Work through the available fields. Choose the required units and calculations, and whether to retain each original field. The choices depend on the file's columns.\r\n\r\n"
  L"3. Supply any requested position or supporting values. Read the units shown on each page.\r\n\r\n"
  L"4. Review the resulting table and curve. Export all fields saves the logger result, including its additional fields. Import to SD2 creates a dataset for use in SIT.\r\n\r\n"
  L"MULTIPLE FILES\r\nChoose an output folder. Conversion choices are reused for files with the same instrument type and column layout. Different layouts need their own choices. GPS and missing temperature, salinity or air pressure are requested separately when needed. Each result is saved as a separate _SIT.txt file. Existing files are kept; a numbered filename is used if needed. The progress window lists saved files and any failures. Cancel remaining stops after the current file; completed files are kept.\r\n\r\n"
  L"SIT remembers successful conversion choices for matching instrument types and column layouts. When offered previous choices, select Yes to reuse them, No to choose again, or Cancel to stop.\r\n\r\n"
  L"For an opened SIT dataset, File > Export offers the available list, standard-depth and other export formats. These formats depend on the dataset; use Export all fields in the logger result window when you need every logger field."},
 {L"Merge files",
  L"Merge combines measurements from separate files by their timestamps.\r\n\r\n"
  L"1. Click Merge and select the main measurement file.\r\n\r\n"
  L"2. Choose the folder containing the additional files and set the time tolerance (0.0 to 10.0 seconds).\r\n\r\n"
  L"3. Scan the folder, check the reported matches and select one or two additional files. Measurements outside the tolerance are not matched. If you change the file, folder or tolerance, scan again.\r\n\r\n"
  L"4. Choose whether to include the separate date/time columns from M1 and M2, then save the merged result under a new name.\r\n\r\n"
  L"Use the Convert button in the Merge window if the result needs unit conversion or calculated fields.\r\n\r\n"
  L"Check that the source clocks use the same time basis. A larger tolerance does not correct an incorrectly set clock."},
 {L"Lists, graphs and print",
  L"Open or import a dataset first. Available views depend on the data.\r\n\r\n"
  L"View > List shows the measurements. View > Tables offers standard-depth and standard-temperature tables.\r\n\r\n"
  L"View > Graph offers the available channel pairs against time or depth. Multigraph opens a separate graph window; imported data has field selectors for up to ten visible channels.\r\n\r\n"
  L"Use File > Set range and File > Set scaling to adjust the relevant data range or scale. Display contains options for legends, units, depth calculation and graph colours.\r\n\r\n"
  L"For paper output, check File > Page setup and then use Print or File > Print. Use File > Export when you need a data file.\r\n\r\n"
  L"View > Instrument returns to the terminal."},
 {L"Interval and TIME/DATE",
  L"Run Detect and accept the connected instrument before using these buttons.\r\n\r\n"
  L"INTERVAL\r\nClick Interval, choose an available sampling interval and confirm. Follow the instrument-specific prompts. For SAIV110 Surface logger, SIT may ask you to select config/system.ini on the connected USB disk.\r\n\r\n"
  L"TIME/DATE\r\nClick TIME/DATE to set the instrument clock from the PC. Check the PC clock and choose the intended time basis: local time (LT) or GMT. Follow the confirmation shown in the dialog.\r\n\r\n"
  L"Changing these settings may stop logging. Read the result and check the instrument's status before starting the next measurement session.\r\n\r\n"
  L"If the connection has changed or a setting fails, run Detect again and check the terminal response."},
 {L"Setup and Help",
  L"SETUP\r\nThe Setup button opens six tabs: Serial port, CU901 files, Modem, e-mail, Options and Calc values. Use Serial port for connection settings and the other tabs for the corresponding SIT functions.\r\n\r\n"
  L"HELP\r\nHelp > Quick guide opens this guide. Help > About shows the installed version.\r\n\r\n"
  L"Help > Update software opens the update dialog. No internet connection is made until you choose Check now. You can read the release notes before deciding whether to install an available update.\r\n\r\n"
  L"Later closes the update dialog. The Do not check for updates at startup checkbox hides the startup reminder; Help > Update software remains available.\r\n\r\n"
  L"Save your work and finish instrument operations before installing an update."},
#include "formula_guide.inc"
};
static void guideSelect(HWND h){
 int selected=int(SendDlgItemMessageW(h,401,LB_GETCURSEL,0,0));
 if(selected<0||size_t(selected)>=sizeof(guideTopics)/sizeof(guideTopics[0]))return;
 SetDlgItemTextW(h,402,guideTopics[selected].title);
 SetDlgItemTextW(h,403,guideTopics[selected].text);
 SendDlgItemMessageW(h,403,EM_SETSEL,0,0);
 SendDlgItemMessageW(h,403,EM_SCROLLCARET,0,0);
}
static void guideLayout(HWND h){
 RECT r;GetClientRect(h,&r);int width=r.right,height=r.bottom;
 MoveWindow(GetDlgItem(h,400),14,12,244,20,TRUE);
 MoveWindow(GetDlgItem(h,401),14,36,244,height-96,TRUE);
 MoveWindow(GetDlgItem(h,402),274,12,width-288,20,TRUE);
 MoveWindow(GetDlgItem(h,403),274,36,width-288,height-96,TRUE);
 MoveWindow(GetDlgItem(h,404),14,height-43,width-138,26,TRUE);
 MoveWindow(GetDlgItem(h,IDOK),width-112,height-46,98,28,TRUE);
}
static LRESULT CALLBACK guideProc(HWND h,UINT m,WPARAM w,LPARAM l){
 switch(m){
 case WM_SIZE:guideLayout(h);return 0;
 case WM_GETMINMAXINFO:reinterpret_cast<MINMAXINFO*>(l)->ptMinTrackSize={800,480};return 0;
 case WM_COMMAND:
  if(LOWORD(w)==401&&HIWORD(w)==LBN_SELCHANGE){guideSelect(h);return 0;}
  if(LOWORD(w)==IDOK||LOWORD(w)==IDCANCEL){DestroyWindow(h);return 0;}break;
 case WM_CLOSE:DestroyWindow(h);return 0;
 }
 return DefWindowProcW(h,m,w,l);
}
static void guideShow(HWND owner,const wchar_t* topic){
 WNDCLASSW wc={};wc.hInstance=instance;wc.lpfnWndProc=guideProc;
 wc.hCursor=LoadCursor(0,IDC_ARROW);wc.hbrBackground=HBRUSH(COLOR_BTNFACE+1);
 wc.lpszClassName=L"SITQuickGuide";RegisterClassW(&wc);
 RECT r;GetWindowRect(owner,&r);
 HWND h=CreateWindowExW(WS_EX_CONTROLPARENT,wc.lpszClassName,L"SAIV IT - Quick guide",
  WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_THICKFRAME,r.left+24,r.top+24,1000,720,owner,0,instance,0);
 if(!h){error(owner,"Could not open the quick guide.");return;}
 SendMessageW(h,WM_SETICON,ICON_SMALL,SendMessageW(owner,WM_GETICON,ICON_SMALL,0));
 control(h,L"STATIC",L"&Topics",0,0,0,0,0,400);
 HWND list=control(h,L"LISTBOX",L"",LBS_NOTIFY|LBS_NOINTEGRALHEIGHT|WS_VSCROLL|WS_BORDER|WS_TABSTOP,0,0,0,0,401);
 control(h,L"STATIC",L"",0,0,0,0,0,402);
 control(h,L"EDIT",L"",ES_MULTILINE|ES_READONLY|ES_AUTOVSCROLL|WS_VSCROLL|WS_BORDER|WS_TABSTOP,0,0,0,0,403);
 control(h,L"STATIC",L"Scroll to read more. Select text and Ctrl+C to copy formulas or source links. Esc closes.",0,0,0,0,0,404);
 control(h,L"BUTTON",L"&Close",BS_DEFPUSHBUTTON|WS_TABSTOP,0,0,0,0,IDOK);
 for(const auto&topic:guideTopics)SendMessageW(list,LB_ADDSTRING,0,LPARAM(topic.title));
 int initial=0;if(topic)for(size_t i=0;i<sizeof(guideTopics)/sizeof(guideTopics[0]);++i)if(!lstrcmpW(topic,guideTopics[i].title)){initial=int(i);break;}
 SendMessageW(list,LB_SETCURSEL,initial,0);guideSelect(h);guideLayout(h);
 EnableWindow(owner,FALSE);ShowWindow(h,SW_SHOW);SetFocus(list);
 MSG msg;int result=1;
 while(IsWindow(h)&&(result=GetMessageW(&msg,0,0,0))>0)
  if(!IsDialogMessageW(h,&msg)){TranslateMessage(&msg);DispatchMessageW(&msg);}
 if(IsWindow(h))DestroyWindow(h);
 EnableWindow(owner,TRUE);SetActiveWindow(owner);
 if(result==0)PostQuitMessage(int(msg.wParam));
}
