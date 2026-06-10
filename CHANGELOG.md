### Added:
- Right click option on Refresh button to manually check app updates (by @WillyJL)
- Add Cmd+W shortcut to close window on macOS (#268 by @cantunborn)

### Updated:
- Show download size and speed in Donor DDL progress bar (#271 by @FaceCrap & @WillyJL)

### Fixed:
- Fix updating on Windows when the app closes faster than Powershell starts (by @WillyJL)
- Detect unsupported configurations with app data and app install locations overlapping (by @WillyJL)
- Fix horizontal scrolling in more info popup (by @WillyJL)
- Fix webview blank page on macOS (#269 by @cantunborn)
- Fix bundled compressonator on Linux (by @WillyJL)

### Removed:
- Nothing

### Known Issues:
- The new notification-daemon process on Linux can sometimes get stuck spinning and cause the app to crash
