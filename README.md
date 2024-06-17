# Xdcheckin
Don't use.

## APP
### Install
Checkout [releases](https://github.com/Pairman/Xdcheckin/releases/).

### Build
1. Install build tool:
```
pip install briefcase
```

2. Clone this repo:
```
git clone https://github.com/Pairman/Xdcheckin
```

3. Build and package for your platform:
```
briefcase package
```

## Module
### Install
Install the module:
```
pip install Xdcheckin
```

### Usage
The module provides ```xdcheckin```, ```xdcheckin.core``` (core APIs) and ```xdcheckin.server``` (server implementation) for importing. It also provides the ```xdcheckin-server``` commandline tool to start a server at the given IP and port.

## Notes
### For Android
The APP doesn't use WebView on Android until upstream support, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

Due to signature change, if you upgrade from version 1.3.2 (or older) to 1.3.3 (or newer), please uninstall before upgrading.

### For Linux
The APP doesn't use WebView on Linux, therefore it will open ```http://127.0.0.1:5001``` in your browser automatically.

### For Windows
The APP needs [Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-US/download/details.aspx?id=40784) to work on Windows. Please install [vcredist_x64.exe](https://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe).

## Credits
[BenderBlog/traintime_pda](https://github.com/BenderBlog/traintime_pda) <br>
[cxOrz/chaoxing-sign-cli](https://github.com/cxOrz/chaoxing-sign-cli) <br>
[Reclu3e/xd_learning_live_publish](https://github.com/Reclu3e/xd_learning_live_publish) <br>
[runoob09/xxt_library_seat](https://github.com/runoob09/xxt_library_seat) <br>
[w964522982/xxtSign](https://github.com/w964522982/xxtSign) <br>
[xdlinux/libxduauth](https://github.com/xdlinux/libxduauth) <br>
[YangRucheng/Chaoxing-AutoSign](https://github.com/YangRucheng/Chaoxing-AutoSign)
