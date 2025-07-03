#!/usr/bin/env bash
set -euo pipefail
rm -rf build
flutter clean
flutter pub get
flutter run -d linux --debug --dart-define-from-file=api-keys.json
snapcraft clean
snapcraft
echo "Build complete"
