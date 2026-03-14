#include "flutter_window.h"

#include <optional>
#include <vector>

#include <flutter/standard_method_codec.h>
#include "flutter/generated_plugin_registrant.h"

namespace {

std::wstring Utf16FromUtf8(const std::string& utf8_string) {
  if (utf8_string.empty()) {
    return std::wstring();
  }

  int utf16_length = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
                                         utf8_string.c_str(), -1, nullptr, 0);
  if (utf16_length <= 0) {
    return std::wstring();
  }

  std::vector<wchar_t> utf16_buffer(static_cast<size_t>(utf16_length), L'\0');
  int converted = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS,
                                      utf8_string.c_str(), -1,
                                      utf16_buffer.data(), utf16_length);
  if (converted <= 0) {
    return std::wstring();
  }

  return std::wstring(utf16_buffer.data());
}

}  // namespace

FlutterWindow::FlutterWindow(const flutter::DartProject& project)
    : project_(project) {}

FlutterWindow::~FlutterWindow() {}

bool FlutterWindow::OnCreate() {
  if (!Win32Window::OnCreate()) {
    return false;
  }

  RECT frame = GetClientArea();

  // The size here must match the window dimensions to avoid unnecessary surface
  // creation / destruction in the startup path.
  flutter_controller_ = std::make_unique<flutter::FlutterViewController>(
      frame.right - frame.left, frame.bottom - frame.top, project_);
  // Ensure that basic setup of the controller was successful.
  if (!flutter_controller_->engine() || !flutter_controller_->view()) {
    return false;
  }
  RegisterPlugins(flutter_controller_->engine());
  SetChildContent(flutter_controller_->view()->GetNativeWindow());

  window_channel_ = std::make_unique<
      flutter::MethodChannel<flutter::EncodableValue>>(
      flutter_controller_->engine()->messenger(), "revelation/window",
      &flutter::StandardMethodCodec::GetInstance());
  window_channel_->SetMethodCallHandler(
      [this](const flutter::MethodCall<flutter::EncodableValue>& method_call,
             std::unique_ptr<flutter::MethodResult<flutter::EncodableValue>>
                 result) {
        const std::string& method_name = method_call.method_name();

        if (method_name == "setWindowTitle") {
          const auto* args =
              std::get_if<flutter::EncodableMap>(method_call.arguments());
          if (args == nullptr) {
            result->Error("bad_args", "Expected map arguments.");
            return;
          }

          const auto title_it = args->find(flutter::EncodableValue("title"));
          if (title_it == args->end()) {
            result->Error("bad_args", "Missing title argument.");
            return;
          }

          const auto* title = std::get_if<std::string>(&title_it->second);
          if (title == nullptr) {
            result->Error("bad_args", "Title must be a string.");
            return;
          }

          const std::wstring wide_title = Utf16FromUtf8(*title);
          if (title->empty() || !wide_title.empty()) {
            ::SetWindowTextW(GetHandle(), wide_title.c_str());
          }

          result->Success();
          return;
        }

        if (method_name == "closeWindow") {
          ::PostMessage(GetHandle(), WM_CLOSE, 0, 0);
          result->Success();
          return;
        }

        result->NotImplemented();
      });

  flutter_controller_->engine()->SetNextFrameCallback([&]() {
    this->Show();
  });

  // Flutter can complete the first frame before the "show window" callback is
  // registered. The following call ensures a frame is pending to ensure the
  // window is shown. It is a no-op if the first frame hasn't completed yet.
  flutter_controller_->ForceRedraw();

  return true;
}

void FlutterWindow::OnDestroy() {
  if (window_channel_) {
    window_channel_ = nullptr;
  }

  if (flutter_controller_) {
    flutter_controller_ = nullptr;
  }

  Win32Window::OnDestroy();
}

LRESULT
FlutterWindow::MessageHandler(HWND hwnd, UINT const message,
                              WPARAM const wparam,
                              LPARAM const lparam) noexcept {
  // Some top-level window delegates may intercept WM_GETMINMAXINFO and return
  // early. Apply runner-level min-size constraints first so they are honored.
  if (message == WM_GETMINMAXINFO) {
    const LRESULT base_result =
        Win32Window::MessageHandler(hwnd, message, wparam, lparam);
    if (flutter_controller_) {
      std::optional<LRESULT> result =
          flutter_controller_->HandleTopLevelWindowProc(hwnd, message, wparam,
                                                        lparam);
      if (result) {
        return *result;
      }
    }
    return base_result;
  }

  // Give Flutter, including plugins, an opportunity to handle window messages.
  if (flutter_controller_) {
    std::optional<LRESULT> result =
        flutter_controller_->HandleTopLevelWindowProc(hwnd, message, wparam,
                                                      lparam);
    if (result) {
      return *result;
    }
  }

  switch (message) {
    case WM_FONTCHANGE:
      flutter_controller_->engine()->ReloadSystemFonts();
      break;
  }

  return Win32Window::MessageHandler(hwnd, message, wparam, lparam);
}
