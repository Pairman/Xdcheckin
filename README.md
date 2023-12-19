# Xdcheckin-toga-flask
[Xdcheckin-py](https://github.com/Pairman/Xdcheckin/tree/py) with flask as backend interface and toga frontend for multiplatform support.

# Usage
Checkout [Releases](https://github.com/Pairman/Xdcheckin/releases/).
## Notes
### Android
Currently, APP webview is broken on Android and awaits upstream fix. Hence do not try to use this app directly. You must open the app as an backend server and visit ```http://127.0.0.1:5001/``` in your browser.

# Build
1. Install beeware build tool and framework with ```pip install briefcase toga```. <br>
2. Clone recursively with ```git clone -b toga-flask --recursive https://github.com/Pairman/Xdcheckin```. <br>
3. Cd into the cloned repo. <br>
4. Run ```breifcase create``` to create project skeleton. <br>
5. Run ```briefcase update -r && briefcase build && briefcase package <platform>``` to build and generate packages, where ```<platform>``` can be ```windows```, ```android``` or etc.
