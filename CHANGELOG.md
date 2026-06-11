### Added:
- Nothing

### Updated:
- Nothing

### Fixed:
- Don't draw continuously while focused unless necessary (by @WillyJL)
- Fix symbolic links in auto update (by @WillyJL)
- Pick correct macOS update file if on x64 (by @WillyJL)

### Removed:
- Removed "Interface > Render if unfocused" setting:
  - Doesn't make sense anymore
  - Previously it would always draw when focused, and always draw when unfocused if this setting was on
  - Now, both when focused and unfocused, it will draw only if necessary, eg mouse moved, GIF is playing...

### Known Issues:
- The new notification-daemon process on Linux can sometimes get stuck spinning and cause the app to crash
