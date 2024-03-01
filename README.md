# Xdcheckin
Don't use.

# Unusage
## APP
Don't checkout [releases](https://github.com/Pairman/Xdcheckin/releases/).

### Build
1. Install build tool via ```pip install briefcase```.<br>
2. Clone this repo with ```git clone https://github.com/Pairman/Xdcheckin```.<br>
3. Run ```briefcase package``` to build and package for your platform.


## Module
Install the module via ```pip install Xdcheckin```.

The module provides ```xdcheckin```, ```xdcheckin.core``` (core APIs) or ```xdcheckin.server``` (server implementation) for importing. It also provides the ```xdcheckin-server``` commandline tool to start a server at the given IP and port.

## Notes
### For Android
The APP doesn't use WebView on Android until upstream support, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

### For Linux
The APP doesn't use WebView on Linux, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

### For Windows
The APP needs [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784)nto work on Windows. Please install [vcredist_x64.exe](https://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe).
