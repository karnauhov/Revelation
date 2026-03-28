#include "flutter_window.h"

#include <mmsystem.h>
#include <optional>
#include <vector>

#include <flutter/standard_method_codec.h>
#include "flutter/generated_plugin_registrant.h"
#include "utils.h"

namespace {

constexpr wchar_t kUiSoundAlias[] = L"revelation_ui_sound";

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

std::wstring GetExecutableDirectory() {
  std::vector<wchar_t> buffer(MAX_PATH, L'\0');
  DWORD path_length = ::GetModuleFileNameW(
      nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));
  if (path_length == 0 || path_length >= buffer.size()) {
    return std::wstring();
  }

  std::wstring executable_path(buffer.data(), path_length);
  const size_t separator = executable_path.find_last_of(L"\\/");
  if (separator == std::wstring::npos) {
    return std::wstring();
  }

  return executable_path.substr(0, separator);
}

std::wstring NormalizeAssetPath(std::wstring asset_key) {
  for (wchar_t& symbol : asset_key) {
    if (symbol == L'/') {
      symbol = L'\\';
    }
  }

  return asset_key;
}

std::wstring GetFlutterAssetPath(const std::string& asset_key) {
  const std::wstring executable_directory = GetExecutableDirectory();
  const std::wstring asset_key_utf16 = Utf16FromUtf8(asset_key);
  if (executable_directory.empty() || asset_key_utf16.empty()) {
    return std::wstring();
  }

  return executable_directory + L"\\data\\flutter_assets\\" +
         NormalizeAssetPath(asset_key_utf16);
}

void CloseUiSound() {
  const std::wstring close_command = L"close " + std::wstring(kUiSoundAlias);
  ::mciSendStringW(close_command.c_str(), nullptr, 0, nullptr);
}

std::string GetMciErrorMessage(MCIERROR error_code) {
  std::vector<wchar_t> buffer(256, L'\0');
  if (::mciGetErrorStringW(error_code, buffer.data(),
                           static_cast<UINT>(buffer.size()))) {
    return Utf8FromUtf16(buffer.data());
  }

  return "MCI error " + std::to_string(error_code);
}

std::optional<std::string> PlayUiSoundAsset(const std::string& asset_key) {
  const std::wstring asset_path = GetFlutterAssetPath(asset_key);
  if (asset_path.empty()) {
    return std::string("Unable to resolve Flutter asset path.");
  }

  CloseUiSound();

  const std::wstring open_command =
      L"open \"" + asset_path + L"\" type mpegvideo alias " + kUiSoundAlias;
  const MCIERROR open_result =
      ::mciSendStringW(open_command.c_str(), nullptr, 0, nullptr);
  if (open_result != 0) {
    return GetMciErrorMessage(open_result);
  }

  const std::wstring play_command =
      L"play " + std::wstring(kUiSoundAlias) + L" from 0";
  const MCIERROR play_result =
      ::mciSendStringW(play_command.c_str(), nullptr, 0, nullptr);
  if (play_result != 0) {
    CloseUiSound();
    return GetMciErrorMessage(play_result);
  }

  return std::nullopt;
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

  audio_channel_ = std::make_unique<
      flutter::MethodChannel<flutter::EncodableValue>>(
      flutter_controller_->engine()->messenger(), "revelation/audio",
      &flutter::StandardMethodCodec::GetInstance());
  audio_channel_->SetMethodCallHandler(
      [](const flutter::MethodCall<flutter::EncodableValue>& method_call,
         std::unique_ptr<flutter::MethodResult<flutter::EncodableValue>>
             result) {
        const std::string& method_name = method_call.method_name();

        if (method_name == "playAsset") {
          const auto* args =
              std::get_if<flutter::EncodableMap>(method_call.arguments());
          if (args == nullptr) {
            result->Error("bad_args", "Expected map arguments.");
            return;
          }

          const auto asset_key_it =
              args->find(flutter::EncodableValue("assetKey"));
          if (asset_key_it == args->end()) {
            result->Error("bad_args", "Missing assetKey argument.");
            return;
          }

          const auto* asset_key =
              std::get_if<std::string>(&asset_key_it->second);
          if (asset_key == nullptr || asset_key->empty()) {
            result->Error("bad_args", "assetKey must be a non-empty string.");
            return;
          }

          const std::optional<std::string> play_error =
              PlayUiSoundAsset(*asset_key);
          if (play_error.has_value()) {
            result->Error("play_failed", *play_error);
            return;
          }

          result->Success();
          return;
        }

        if (method_name == "stop") {
          CloseUiSound();
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
  CloseUiSound();

  if (audio_channel_) {
    audio_channel_ = nullptr;
  }

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
