# Xdcheckin
WIP.
Python based Chaoxing checkin tool for XDU.

# Supported Checkin types
1. Location (with or without designated place enabled). <br>
2. Qrcode (with or without designated place enabled).

# Usage
For average users: <br>
&nbsp;1. Installed dependencies if any unmet. <br>
&emsp;&emsp;2. Modify ```xdcheckin.py``` <br>
          i. Fill ```config.json``` with your Chaoxing username and password. <br>
         ii. Modify location according to your need. Defaulted to ```chaoxing.locations["B"]```. <br>
        iii. Use ```qr()``` for qrcode checkins, otherwise ```loc()```. Defaulted to ```qr()```. <br>

For devs:
    Check ```chaoxing/chaoxing.py``` for APIs.

# Credits
[w964522982/xxtSign](https://github.com/w964522982/xxtSign) <br>
[YangRucheng/Chaoxing-AutoSign](https://github.com/YangRucheng/Chaoxing-AutoSign)
