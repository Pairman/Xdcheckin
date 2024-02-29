# Xdcheckin_toga-flask
What what.

# Unusage
Don't checkout [releases](https://github.com/Pairman/Xdcheckin/releases/).
### Notes
#### Android
Currently, APP webview is broken on Android and awaits upstream fix. This APP will automatically open ```http://127.0.0.1:5001``` in your browser.

#### Linux
We don't use WebView on Linux, therefore you should visit ```http://127.0.0.1:5001``` in your browser manually.

#### Windows
For Xdcheckin 1.0.1+, Pyzbar on Windows needs [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784). If you encounter any ```ImportError```, install [vcredist_x64.exe](https://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe).

# Build
1. Install ```briefcase```.<br>
2. Clone branch ```toga-flask```.<br>
3. Run ```briefcase package``` to build and package for your platform.
