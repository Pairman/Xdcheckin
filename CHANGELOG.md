# Changelog

Changelog for Xdcheckin.

## [Unreleased]

## [1.3.7] - 2023-03-18

### New
- (Module) Add xdcheckin.core.chaoxing.Chaoxing.checkin_format_location() to format checkin location based on config. Called automatically in xdcheckin.core.chaoxing.Chaoxing.checkin_get_location().

### Fixed

- Fix webpage title not properly displayed for non-XDUers.

### Changed

- Revert location fetching logic for location checkin due to Chaoxing API restabilization. This should provide more accuracy for location checkin.
- (Module) xdcheckin.core.chaoxing.Chaoxing.checkin_do_presign() now returns checkin location on success. You should call xdcheckin.core.chaoxing.Chaoxing.checkin_format_location() manually then.

## [1.3.6] - 2023-03-15

### Fixed

- Fix hidden camera on normal devices.

### Changed

- Checkin location address override now only affects addresses shorter than 13.

## [1.3.5] - 2023-03-15

### Added

- Automatically hide camera if device is unavailable.
- Properly formatted changelog.

## [1.3.4] - 2024-03-14

### Added

- Introduce randomness to checkin location coordinates for anti-detection.
- User-given location address is now passed through for checking-in for anti-detection.

## [1.3.3] - 2024-03-13

### Fixed

- (Android) version 1.3.2 crashes on start.
- (Module) ```xdcheckin.app``` is now properly unimportable.

### Changed

- (Android) APP signature is changed. Please uninstall before upgrading from earlier versions.

## [1.3.2] - 2024-03-10

### Fixed

- Fix false alert on logout failure.

### Changed

- IDS captcha has been changed to a floating image instead of a red line.
- Change text of activity buttons.

## [1.3.1] - 2024-03-09

### Added

- IDS login support.
- Automatic login support.

### Changed

- Optimize curriculum loading speed.

### Fixed

- PPTVideo image is now uncompressed in case of qrcode not detected errors.
- Various other fixes.

## [1.2.11] - 2024-03-04

### Fixed

- Fix multiuser dysfunctionality and security issues related to session data.

### Changed

- Optimize curriculum text and layout.
- (Module) Newesxidian has been splitted to xdcheckin.core.xidian.Newesxidian.

## [1.2.10] - 2024-03-02

### Added

- Classroom "Load" and "Extract" buttons are now moved to classroom list.

### Fixed

- (Module) Fix missing data files.

## [1.2.9] - 2024-03-02

### Added

- Video players are now automatically resized.

### Changed

- Further simplify button text.
- Webpage is now displayed bigger for easier usage.

### Removed

- Remove the "Resize All" button.

## [1.2.8] - 2024-03-01

### Added

- Other video players will now be muted automatically when unmuting one.
- Confirmation dialog before logging out.
- (Module) Xdcheckin is now an importable module with ```xdcheckin-server``` cli tool.

## [1.2.7] - 2024-02-28

### Added

- Added functionalities for logging out and logging in again.

### Fixed

- Fix login failure after preceding failure.
- Fix curriculum loading failure after preceding failure.
- APP version will now properly show up in the page footer.
- Login error messages are now properly generated.
- Fix video players, locations and classrooms list failures.

### Changed

- Move "Input Location" and "I'm Feeling Lucky" under their corresponding list.

### Removed

- Remove the "Unmute All" and "Mute All" buttons.

## [1.2.6] - 2024-02-26

### Added

- Page footer will now display APP version.

### Fixed

- Fix zero-sized video players.
- Fix a bug causing login failure.
- Login error message will now be properly displayed.
- (Windows/macOS) Fix APP crash failure.

## [1.2.5] - 2024-02-26

### Changed

- Optimized login and curriculum loading logic.

## [1.2.4] - 2024-02-25

### Fixed

- Fix location checkin failure.

## [1.2.3] - 2024-02-25

### Added

- Curriculum info will now be displayed.

### Fixed

- Current location info will now be properly displayed.

### Changed

- Optimized data usage and responsiveness of qrcode checkin.

## [1.2.2] - 2024-02-24

### Added

- Livestream URLs with blank or missing perspectives are now supported.

### Changed

- Fully updated livestream URLs list.

### Fixed

- Fix classroom switching failure.

## [1.2.1] - 2024-02-22

### Added

- Lesson time is now displayed in curriculum.


### Fixed

- Wrong curriculum year due to Chaoxing's broken API.

## [1.2.0] - 2024-02-22

### Added

- Livestream info is now displayed in curriculum.

## [1.1.8] - 2024-02-09

### Fixed

- (Android) Text will now wrap properly.

## [1.1.7] - 2024-02-08

### Fixed

- APP will now properly stop the backend server on exit.

### Removed

- (Linux) Remove APP WebView to fix crashes with unmet dependencies. Thus this is the first usable version.
- (Android) Remove APP WebView since it's useless.

## [1.1.6] - 2024-01-19

### Added

- (Android) APP will now automatically open the webpage.

## [1.1.5] - 2024-01-17

### Added

- Checking-in is now multithreaded for speed.
- Several responses are now cached for reusage and speed.

### Changed

- Activities fetching will now be cached for 60 seconds. Please wait before fetching again.

## [1.1.4] - 2024-01-13

### Fixed

- Activities fetching is now multithreaded for speed.
- Fix non-ranged location or qrcode checkin failure due to further Chaoxing's API changes.

### Changed

- Optimized webpage loading speed.
- Activities fetching is now limited to 48 courses.

## [1.1.3] - 2024-01-09

### Added

- Display more details in checkin result and alert.

### Fixed

- Fix non-ranged location checkin failure due to Chaoxing's API changes.

## [1.1.2] - 2024-01-07

### Fixed

- Fix qrcode checkin failure due to Chaoxing's API changes.

## [1.1.1] - 2024-01-06

### Added

- Added camera section which is also available for qrcode scanning.

### Fixed

- (Android) Fix a bug causing newly installed APP to crash.

## [1.0.4] - 2024-01-06

### Changed

- Backend restructure.

## [1.0.3] - 2024-01-05

### Added

- Cooldown for location checkin buttons to avoid spamming.
- Replace cookies with local storage for security.

## [1.0.2] - 2024-01-04

### Added

- Cooldown for scan button to avoid spamming.

## [1.0.1] - 2024-01-01

### Fixed

- Fix scan button not properly hidden before logged in.

### Changed

- Pyzbar now replaces OpenCV for qrcode processing.
- (Windows) [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784) must be installed to use Pyzbar.

## [1.0.0] - 2024-01-01

### Changed

- OpenCV is now used for processing qrcode with accuracy and responsiveness.

## [0.0.18] - 2023-12-31

### Added

- Activities checking is now multithreaded for quicker responses.

[unreleased]: https://github.com/Pairman/Xdcheckin/compare/1.3.7...main
[1.3.7]: https://github.com/Pairman/Xdcheckin/compare/1.3.6...1.3.7
[1.3.6]: https://github.com/Pairman/Xdcheckin/compare/1.3.5...1.3.6
[1.3.5]: https://github.com/Pairman/Xdcheckin/compare/1.3.4...1.3.5
[1.3.4]: https://github.com/Pairman/Xdcheckin/compare/1.3.3...1.3.4
[1.3.3]: https://github.com/Pairman/Xdcheckin/compare/1.3.2...1.3.3
[1.3.2]: https://github.com/Pairman/Xdcheckin/compare/1.3.1...1.3.2
[1.3.1]: https://github.com/Pairman/Xdcheckin/compare/1.2.11...1.3.1
[1.2.11]: https://github.com/Pairman/Xdcheckin/compare/1.2.10...1.2.11
[1.2.10]: https://github.com/Pairman/Xdcheckin/compare/1.2.9...1.2.10
[1.2.9]: https://github.com/Pairman/Xdcheckin/compare/1.2.8...1.2.9
[1.2.8]: https://github.com/Pairman/Xdcheckin/compare/1.2.7...1.2.8
[1.2.7]: https://github.com/Pairman/Xdcheckin/compare/1.2.6...1.2.7
[1.2.6]: https://github.com/Pairman/Xdcheckin/compare/1.2.5...1.2.6
[1.2.5]: https://github.com/Pairman/Xdcheckin/compare/1.2.4...1.2.5
[1.2.4]: https://github.com/Pairman/Xdcheckin/compare/1.2.3...1.2.4
[1.2.3]: https://github.com/Pairman/Xdcheckin/compare/1.2.2...1.2.3
[1.2.2]: https://github.com/Pairman/Xdcheckin/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/Pairman/Xdcheckin/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/Pairman/Xdcheckin/compare/1.1.8...1.2.0
[1.1.8]: https://github.com/Pairman/Xdcheckin/compare/1.1.7...1.1.8
[1.1.7]: https://github.com/Pairman/Xdcheckin/compare/1.1.6...1.1.7
[1.1.6]: https://github.com/Pairman/Xdcheckin/compare/1.1.5...1.1.6
[1.1.5]: https://github.com/Pairman/Xdcheckin/compare/1.1.4...1.1.5
[1.1.4]: https://github.com/Pairman/Xdcheckin/compare/1.1.3...1.1.4
[1.1.3]: https://github.com/Pairman/Xdcheckin/compare/1.1.2...1.1.3
[1.1.2]: https://github.com/Pairman/Xdcheckin/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/Pairman/Xdcheckin/compare/1.0.4...1.1.1
[1.0.4]: https://github.com/Pairman/Xdcheckin/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/Pairman/Xdcheckin/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/Pairman/Xdcheckin/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/Pairman/Xdcheckin/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/Pairman/Xdcheckin/compare/0.0.18...1.0.0
[0.0.18]: https://github.com/Pairman/Xdcheckin/tree/0.0.18
