#ifndef RUNNER_SOUND_ENGINE_H_
#define RUNNER_SOUND_ENGINE_H_

#include <memory>
#include <string>
#include <unordered_map>

class SoundEngine {
 public:
  SoundEngine();
  ~SoundEngine();

  SoundEngine(const SoundEngine&) = delete;
  SoundEngine& operator=(const SoundEngine&) = delete;

  void PrepareAssets(const std::unordered_map<std::string, std::string>& assets);
  void Play(const std::string& sound_name);
  void Stop();

 private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

#endif  // RUNNER_SOUND_ENGINE_H_
