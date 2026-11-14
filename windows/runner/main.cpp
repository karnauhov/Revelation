#include <flutter/dart_project.h>
#include <flutter/flutter_view_controller.h>
#include <flutter_inappwebview_windows/flutter_inappwebview_windows_plugin_c_api.h>
#include <windows.h>

#include "flutter_window.h"
#include "utils.h"

int APIENTRY wWinMain(_In_ HINSTANCE instance, _In_opt_ HINSTANCE prev,
                      _In_ wchar_t *command_line, _In_ int show_command) {
  // Attach to console when present (e.g., 'flutter run') or create a
  // new console when running with a debugger.
  if (!::AttachConsole(ATTACH_PARENT_PROCESS) && ::IsDebuggerPresent()) {
    CreateAndAttachConsole();
  }

  // Initialize COM, so that it is available for use in the library and/or
  // plugins.
  const HRESULT com_result = ::CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
  if (FAILED(com_result)) {
    return EXIT_FAILURE;
  }

  int exit_code = EXIT_FAILURE;
  {
    flutter::DartProject project(L"data");
    project.set_dart_entrypoint_arguments(GetCommandLineArguments());

    FlutterWindow window(project);
    Win32Window::Point origin(10, 10);
    Win32Window::Size size(800, 650);
    window.SetMinSize(800, 650);
    // Startup title is replaced by localized Flutter title after first frame.
    if (window.Create(L"Revelation", origin, size)) {
      window.SetQuitOnClose(true);

      ::MSG msg;
      BOOL result;
      while ((result = ::GetMessage(&msg, nullptr, 0, 0)) > 0) {
        ::TranslateMessage(&msg);
        ::DispatchMessage(&msg);
      }
      if (result == 0) {
        exit_code = EXIT_SUCCESS;
      }
    }
    window.Destroy();
  }

  if (!FlutterInappwebviewWindowsPluginCApiShutdownGraphics()) {
    exit_code = EXIT_FAILURE;
  }
  ::CoUninitialize();
  return exit_code;
}
