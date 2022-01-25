# Simple Voice Authenticator 

## Why 
To validate user with the telephone by check CallerID of incoming call 

## Install 
### Ubuntu 

```
sudo apt-get update
sudo apt-get install build-essential
sudo apt-get install postgresql postgresql-server 
git clone ...
cd voiceauth 
python3 -m pip install -r ./requirements.txt 
```

## Run 
Setup environment variables as shown in example for fish shell:
```
set -gx DB_HOST 127.0.0.1 
set -gx DB_NAME voiceauth 
set -gx DB_USER voiceauth
set -gx DB_PASS voiceauth
set -gx DB_TABLE voiceauth 
set -gx AUTH_TOKEN test123 
set -gx WEBHOOK http://localhost:8081/ 
```

DB_* variables is simple and do not need to make a description 
AUTH_TOKEN is a string that http_api expect in X-Auth-Token HTTP header in POST request 
WEBHOOK is URL to POST JSON data with the result of every call that made by asterisk_callman.py 

