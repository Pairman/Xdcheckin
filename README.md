# Xdcheckin-flask
Xdcheckin with flask frontend integrated with [Xdclassroom](https://github.com/Pairman/Xdclassroom) for qrcode checkin via classroom livestreams.

## Usage
1. Clone this repo **RECURSIVELY** with ```git clone --recursive -b flask https://github.com/Pairman/Xdcheckin```, otherwise folder ```xdcheckin_py``` will be empty. <br>
2. Install dependencies with ```pip install requests flask flask-session gunicorn```
3. Go to the cloned directory. Run ```gunicorn --bind="127.0.0.1:5000" main:app```
4. Go to ```127.0.0.1:5000``` in your browser.
