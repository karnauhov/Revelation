#include "sound_engine.h"

#include <mfapi.h>
#include <mfidl.h>
#include <mfobjects.h>
#include <mfreadwrite.h>
#include <mmreg.h>
#include <xaudio2.h>
#include <windows.h>
#include <wrl/client.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <iostream>
#include <limits>
#include <mutex>
#include <queue>
#include <thread>
#include <utility>
#include <vector>

namespace {

using Microsoft::WRL::ComPtr;

constexpr DWORD kFirstAudioStream =
    static_cast<DWORD>(MF_SOURCE_READER_FIRST_AUDIO_STREAM);

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

std::string HResultMessage(HRESULT hr) {
  char* buffer = nullptr;
  const DWORD flags = FORMAT_MESSAGE_ALLOCATE_BUFFER |
                      FORMAT_MESSAGE_FROM_SYSTEM |
                      FORMAT_MESSAGE_IGNORE_INSERTS;
  const DWORD length =
      ::FormatMessageA(flags, nullptr, static_cast<DWORD>(hr), 0,
                       reinterpret_cast<LPSTR>(&buffer), 0, nullptr);
  if (length == 0 || buffer == nullptr) {
    return "HRESULT 0x" + std::to_string(static_cast<unsigned long>(hr));
  }

  std::string message(buffer, length);
  ::LocalFree(buffer);
  while (!message.empty() &&
         (message.back() == '\r' || message.back() == '\n')) {
    message.pop_back();
  }
  return message;
}

void LogAudioMessage(const std::string& message) {
  std::cerr << "[revelation/audio] " << message << std::endl;
}

}  // namespace

class SoundEngine::Impl {
 public:
  Impl() : worker_(&Impl::WorkerMain, this) {}

  ~Impl() {
    Enqueue(Command::Shutdown());
    if (worker_.joinable()) {
      worker_.join();
    }
  }

  void PrepareAssets(const std::unordered_map<std::string, std::string>& assets) {
    Enqueue(Command::PrepareAssets(assets));
  }

  void Play(const std::string& sound_name) { Enqueue(Command::Play(sound_name)); }

  void Stop() { Enqueue(Command::Stop()); }

 private:
  struct Command {
    enum class Type { kPrepareAssets, kPlay, kStop, kShutdown };

    static Command PrepareAssets(
        const std::unordered_map<std::string, std::string>& assets) {
      Command command;
      command.type = Type::kPrepareAssets;
      command.assets = assets;
      return command;
    }

    static Command Play(const std::string& sound_name) {
      Command command;
      command.type = Type::kPlay;
      command.sound_name = sound_name;
      return command;
    }

    static Command Stop() {
      Command command;
      command.type = Type::kStop;
      return command;
    }

    static Command Shutdown() {
      Command command;
      command.type = Type::kShutdown;
      return command;
    }

    Type type = Type::kStop;
    std::unordered_map<std::string, std::string> assets;
    std::string sound_name;
  };

  struct DecodedSound {
    std::vector<uint8_t> wave_format;
    std::vector<uint8_t> pcm_data;
  };

  class VoiceCallback : public IXAudio2VoiceCallback {
   public:
    VoiceCallback() = default;

    void STDMETHODCALLTYPE OnVoiceProcessingPassStart(UINT32) override {}
    void STDMETHODCALLTYPE OnVoiceProcessingPassEnd() override {}
    void STDMETHODCALLTYPE OnStreamEnd() override { finished.store(true); }
    void STDMETHODCALLTYPE OnBufferStart(void*) override {}
    void STDMETHODCALLTYPE OnBufferEnd(void*) override { finished.store(true); }
    void STDMETHODCALLTYPE OnLoopEnd(void*) override {}
    void STDMETHODCALLTYPE OnVoiceError(void*, HRESULT) override {
      finished.store(true);
    }

    std::atomic<bool> finished{false};
  };

  struct ActiveVoice {
    IXAudio2SourceVoice* voice = nullptr;
    std::shared_ptr<VoiceCallback> callback;
  };

  void Enqueue(Command command) {
    {
      std::lock_guard<std::mutex> lock(queue_mutex_);
      commands_.push(std::move(command));
    }
    queue_cv_.notify_one();
  }

  void WorkerMain() {
    const HRESULT co_init_result =
        ::CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    const bool should_uninitialize_com =
        SUCCEEDED(co_init_result) || co_init_result == S_FALSE;
    if (FAILED(co_init_result) && co_init_result != RPC_E_CHANGED_MODE) {
      LogAudioMessage("CoInitializeEx failed: " +
                      HResultMessage(co_init_result));
    }

    const HRESULT mf_startup_result = ::MFStartup(MF_VERSION, MFSTARTUP_FULL);
    const bool media_foundation_started = SUCCEEDED(mf_startup_result);
    if (!media_foundation_started) {
      LogAudioMessage("MFStartup failed: " + HResultMessage(mf_startup_result));
    }

    for (;;) {
      CleanupFinishedVoices();

      Command command;
      bool has_command = false;
      {
        std::unique_lock<std::mutex> lock(queue_mutex_);
        queue_cv_.wait_for(lock, std::chrono::milliseconds(25), [this]() {
          return !commands_.empty();
        });
        if (!commands_.empty()) {
          command = std::move(commands_.front());
          commands_.pop();
          has_command = true;
        }
      }

      if (!has_command) {
        continue;
      }

      if (command.type == Command::Type::kShutdown) {
        break;
      }

      switch (command.type) {
        case Command::Type::kPrepareAssets:
          PrepareAssetsOnWorker(command.assets, media_foundation_started);
          break;
        case Command::Type::kPlay:
          PlayOnWorker(command.sound_name);
          break;
        case Command::Type::kStop:
          StopOnWorker();
          break;
        case Command::Type::kShutdown:
          break;
      }
    }

    StopOnWorker();
    sounds_.clear();

    if (mastering_voice_ != nullptr) {
      mastering_voice_->DestroyVoice();
      mastering_voice_ = nullptr;
    }
    xaudio2_.Reset();

    if (media_foundation_started) {
      ::MFShutdown();
    }
    if (should_uninitialize_com) {
      ::CoUninitialize();
    }
  }

  bool EnsureAudioClient() {
    if (xaudio2_ != nullptr && mastering_voice_ != nullptr) {
      return true;
    }

    HRESULT result =
        ::XAudio2Create(xaudio2_.ReleaseAndGetAddressOf(), 0,
                        XAUDIO2_DEFAULT_PROCESSOR);
    if (FAILED(result)) {
      LogAudioMessage("XAudio2Create failed: " + HResultMessage(result));
      xaudio2_.Reset();
      return false;
    }

    result = xaudio2_->CreateMasteringVoice(&mastering_voice_);
    if (FAILED(result)) {
      LogAudioMessage("CreateMasteringVoice failed: " +
                      HResultMessage(result));
      mastering_voice_ = nullptr;
      xaudio2_.Reset();
      return false;
    }

    return true;
  }

  void PrepareAssetsOnWorker(
      const std::unordered_map<std::string, std::string>& assets,
      bool media_foundation_started) {
    StopOnWorker();
    sounds_.clear();

    if (!media_foundation_started) {
      return;
    }

    std::unordered_map<std::string, DecodedSound> decoded_sounds;
    decoded_sounds.reserve(assets.size());

    for (const auto& entry : assets) {
      DecodedSound sound;
      if (DecodeAsset(entry.second, &sound)) {
        decoded_sounds.emplace(entry.first, std::move(sound));
      }
    }

    sounds_ = std::move(decoded_sounds);
  }

  void PlayOnWorker(const std::string& sound_name) {
    CleanupFinishedVoices();

    const auto sound_it = sounds_.find(sound_name);
    if (sound_it == sounds_.end()) {
      return;
    }

    const DecodedSound& sound = sound_it->second;
    if (sound.wave_format.empty() || sound.pcm_data.empty()) {
      return;
    }

    if (!EnsureAudioClient()) {
      return;
    }

    if (sound.pcm_data.size() >
        static_cast<size_t>(std::numeric_limits<UINT32>::max())) {
      LogAudioMessage("Audio buffer is too large for '" + sound_name + "'.");
      return;
    }

    const WAVEFORMATEX* wave_format =
        reinterpret_cast<const WAVEFORMATEX*>(sound.wave_format.data());

    auto callback = std::make_shared<VoiceCallback>();
    IXAudio2SourceVoice* source_voice = nullptr;
    HRESULT result = xaudio2_->CreateSourceVoice(
        &source_voice, wave_format, 0, XAUDIO2_DEFAULT_FREQ_RATIO,
        callback.get(), nullptr, nullptr);
    if (FAILED(result) || source_voice == nullptr) {
      LogAudioMessage("CreateSourceVoice failed: " + HResultMessage(result));
      return;
    }

    XAUDIO2_BUFFER buffer = {};
    buffer.AudioBytes = static_cast<UINT32>(sound.pcm_data.size());
    buffer.pAudioData = sound.pcm_data.data();
    buffer.Flags = XAUDIO2_END_OF_STREAM;

    result = source_voice->SubmitSourceBuffer(&buffer, nullptr);
    if (FAILED(result)) {
      LogAudioMessage("SubmitSourceBuffer failed: " + HResultMessage(result));
      source_voice->DestroyVoice();
      return;
    }

    result = source_voice->Start(0);
    if (FAILED(result)) {
      LogAudioMessage("SourceVoice Start failed: " + HResultMessage(result));
      source_voice->DestroyVoice();
      return;
    }

    active_voices_.push_back(
        ActiveVoice{source_voice, std::move(callback)});
  }

  void StopOnWorker() {
    for (ActiveVoice& active_voice : active_voices_) {
      if (active_voice.voice == nullptr) {
        continue;
      }

      active_voice.voice->Stop(0);
      active_voice.voice->FlushSourceBuffers();
      active_voice.voice->DestroyVoice();
      active_voice.voice = nullptr;
    }

    active_voices_.clear();
  }

  void CleanupFinishedVoices() {
    active_voices_.erase(
        std::remove_if(active_voices_.begin(), active_voices_.end(),
                       [](ActiveVoice& active_voice) {
                         if (active_voice.voice == nullptr) {
                           return true;
                         }

                         if (active_voice.callback == nullptr ||
                             !active_voice.callback->finished.load()) {
                           return false;
                         }

                         active_voice.voice->DestroyVoice();
                         active_voice.voice = nullptr;
                         return true;
                       }),
        active_voices_.end());
  }

  bool DecodeAsset(const std::string& asset_key, DecodedSound* sound) {
    if (sound == nullptr) {
      return false;
    }

    const std::wstring asset_path = GetFlutterAssetPath(asset_key);
    if (asset_path.empty()) {
      LogAudioMessage("Unable to resolve asset path for '" + asset_key + "'.");
      return false;
    }

    ComPtr<IMFSourceReader> reader;
    HRESULT result =
        ::MFCreateSourceReaderFromURL(asset_path.c_str(), nullptr,
                                      reader.GetAddressOf());
    if (FAILED(result)) {
      LogAudioMessage("MFCreateSourceReaderFromURL failed for '" + asset_key +
                      "': " + HResultMessage(result));
      return false;
    }

    ComPtr<IMFMediaType> pcm_media_type;
    result = ::MFCreateMediaType(pcm_media_type.GetAddressOf());
    if (FAILED(result)) {
      LogAudioMessage("MFCreateMediaType failed for '" + asset_key +
                      "': " + HResultMessage(result));
      return false;
    }

    result =
        pcm_media_type->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Audio);
    if (SUCCEEDED(result)) {
      result = pcm_media_type->SetGUID(MF_MT_SUBTYPE, MFAudioFormat_PCM);
    }
    if (FAILED(result)) {
      LogAudioMessage("Failed to configure PCM media type for '" + asset_key +
                      "': " + HResultMessage(result));
      return false;
    }

    result =
        reader->SetCurrentMediaType(kFirstAudioStream, nullptr,
                                    pcm_media_type.Get());
    if (FAILED(result)) {
      LogAudioMessage("SetCurrentMediaType failed for '" + asset_key +
                      "': " + HResultMessage(result));
      return false;
    }

    if (!ExtractWaveFormat(reader.Get(), asset_key, sound)) {
      return false;
    }

    sound->pcm_data.clear();

    while (true) {
      DWORD stream_flags = 0;
      ComPtr<IMFSample> sample;
      result = reader->ReadSample(kFirstAudioStream, 0, nullptr, &stream_flags,
                                  nullptr, sample.GetAddressOf());
      if (FAILED(result)) {
        LogAudioMessage("ReadSample failed for '" + asset_key +
                        "': " + HResultMessage(result));
        return false;
      }

      if ((stream_flags & MF_SOURCE_READERF_CURRENTMEDIATYPECHANGED) != 0 &&
          !ExtractWaveFormat(reader.Get(), asset_key, sound)) {
        return false;
      }

      if (sample != nullptr) {
        ComPtr<IMFMediaBuffer> media_buffer;
        result = sample->ConvertToContiguousBuffer(media_buffer.GetAddressOf());
        if (FAILED(result)) {
          LogAudioMessage("ConvertToContiguousBuffer failed for '" + asset_key +
                          "': " + HResultMessage(result));
          return false;
        }

        BYTE* audio_bytes = nullptr;
        DWORD current_length = 0;
        result = media_buffer->Lock(&audio_bytes, nullptr, &current_length);
        if (FAILED(result)) {
          LogAudioMessage("Media buffer lock failed for '" + asset_key +
                          "': " + HResultMessage(result));
          return false;
        }

        sound->pcm_data.insert(sound->pcm_data.end(), audio_bytes,
                               audio_bytes + current_length);
        media_buffer->Unlock();
      }

      if ((stream_flags & MF_SOURCE_READERF_ENDOFSTREAM) != 0) {
        break;
      }
    }

    if (sound->pcm_data.empty()) {
      LogAudioMessage("Decoded audio is empty for '" + asset_key + "'.");
      return false;
    }

    return true;
  }

  bool ExtractWaveFormat(IMFSourceReader* reader, const std::string& asset_key,
                         DecodedSound* sound) {
    if (reader == nullptr || sound == nullptr) {
      return false;
    }

    ComPtr<IMFMediaType> current_media_type;
    HRESULT result =
        reader->GetCurrentMediaType(kFirstAudioStream,
                                    current_media_type.GetAddressOf());
    if (FAILED(result)) {
      LogAudioMessage("GetCurrentMediaType failed for '" + asset_key +
                      "': " + HResultMessage(result));
      return false;
    }

    WAVEFORMATEX* wave_format = nullptr;
    UINT32 wave_format_size = 0;
    result = ::MFCreateWaveFormatExFromMFMediaType(
        current_media_type.Get(), &wave_format, &wave_format_size);
    if (FAILED(result) || wave_format == nullptr || wave_format_size == 0) {
      LogAudioMessage("MFCreateWaveFormatExFromMFMediaType failed for '" +
                      asset_key + "': " + HResultMessage(result));
      if (wave_format != nullptr) {
        ::CoTaskMemFree(wave_format);
      }
      return false;
    }

    const uint8_t* begin = reinterpret_cast<const uint8_t*>(wave_format);
    sound->wave_format.assign(begin, begin + wave_format_size);
    ::CoTaskMemFree(wave_format);
    return true;
  }

  std::mutex queue_mutex_;
  std::condition_variable queue_cv_;
  std::queue<Command> commands_;
  std::thread worker_;
  std::unordered_map<std::string, DecodedSound> sounds_;
  std::vector<ActiveVoice> active_voices_;
  ComPtr<IXAudio2> xaudio2_;
  IXAudio2MasteringVoice* mastering_voice_ = nullptr;
};

SoundEngine::SoundEngine() : impl_(std::make_unique<Impl>()) {}

SoundEngine::~SoundEngine() = default;

void SoundEngine::PrepareAssets(
    const std::unordered_map<std::string, std::string>& assets) {
  impl_->PrepareAssets(assets);
}

void SoundEngine::Play(const std::string& sound_name) { impl_->Play(sound_name); }

void SoundEngine::Stop() { impl_->Stop(); }
