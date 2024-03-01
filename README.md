# Xdcheckin
What what.

# Unusage
## APP
Don't checkout [releases](https://github.com/Pairman/Xdcheckin/releases/).

#### Build
1. Install ```briefcase```.<br>
2. Clone this repo.<br>
3. Run ```briefcase package``` to build and package for your platform.


## Module
Clone this repo and ```pip install -e``` it as a module.

You can then import ```xdcheckin```, ```xdcheckin.core``` (Core APIs) or ```xdcheckin.server``` (Flask server implementation). It also provides the ```xdcheckind``` command to start a flask server on a certain IP and port.

## Notes
#### Android
This APP doesn't use WebView on Android until upstream support, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

#### Linux
This APP doesn't use WebView on Linux, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

#### Windows
The APP needs [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784)nto work on Windows. Please install [vcredist_x64.exe](https://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe).
