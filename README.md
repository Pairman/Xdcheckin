# Xdcheckin
WIP.
Python based Chaoxing checkin tool for XDU.

## Supported Checkin types
1. Location (with or without designated place enabled). <br>
2. Qrcode (with or without designated place enabled).

## Usage
For average users: <br>
&emsp;&emsp;1. Installed dependencies if any unmet. <br>
&emsp;&emsp;2. Modify ```xdcheckin.py``` <br>
&emsp;&emsp;&emsp;&emsp;i.   Fill ```config.json``` with your Chaoxing username and password. <br>
&emsp;&emsp;&emsp;&emsp;ii.  Modify location according to your need. Defaulted to ```locations["B"]```. <br>
&emsp;&emsp;&emsp;&emsp;iii. Use ```qr()``` for qrcode checkins, otherwise ```loc()```. Defaulted to ```qr()```.

For devs: <br>
&emsp;&emsp;Check ```chaoxing/chaoxing.py``` for APIs.

## Credits
[w964522982/xxtSign](https://github.com/w964522982/xxtSign) <br>
[YangRucheng/Chaoxing-AutoSign](https://github.com/YangRucheng/Chaoxing-AutoSign)
