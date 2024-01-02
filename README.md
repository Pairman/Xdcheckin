# Xdcheckin_toga-flask
[Xdcheckin_py](https://github.com/Pairman/Xdcheckin/tree/py) with flask backend and toga frontend for multiplatform support.

# Usage
Checkout [Releases](https://github.com/Pairman/Xdcheckin/releases/).
### Notes
#### Android
Currently, APP webview is broken on Android and awaits upstream fix. Hence do not try to use this app directly. You must open the app as an backend server and visit ```http://127.0.0.1:5001/``` in your browser.

#### Windows
For Xdcheckin 1.0.1+, Pyzbar on Windows needs [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784). If you encounter any ```ImportError``` about Pyzbar, please install ``vcredist_x64.exe`` if using 64-bit Python, ``vcredist_x86.exe`` if using 32-bit Python.

# Build
1. Install beeware build tool and framework with ```pip install briefcase toga```. <br>
2. Clone recursively with ```git clone -b toga-flask --recursive https://github.com/Pairman/Xdcheckin```. <br>
3. Cd into the cloned repo. <br>
4. Run ```breifcase create``` to create project skeleton. <br>
5. Run ```briefcase update -r && briefcase package <platform>``` to build and generate packages, where ```<platform>``` can be ```windows```, ```android``` or etc.
