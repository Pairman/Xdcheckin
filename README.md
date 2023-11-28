# Xdcheckin-flask
Xdcheckin with flask frontend integrated with [Xdclassroom](https://github.com/Pairman/Xdclassroom) for qrcode checkin via classroom livestreams.

## Usage
1. Clone this repo **RECURSIVELY** with ```git clone -r https://github.com/Pairman/Xdcheckin```. <br>
2. Install dependencies with ```pip install requests flask flask-session gunicorn```
3. Go to the cloned folder. Run with ```gunicorn --bind="127.0.0.1:5000" main:app```
4. Go to "127.0.0.1:5000" in your browser.

## Credits
[w964522982/xxtSign](https://github.com/w964522982/xxtSign) <br>
[YangRucheng/Chaoxing-AutoSign](https://github.com/YangRucheng/Chaoxing-AutoSign)
