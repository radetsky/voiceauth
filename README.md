# Simple Voice Authenticator 

## Why 
To validate user with the telephone by check CallerID of incoming call 

## Install 
### Ubuntu 

```
sudo apt-get update
sudp apt-get install asterisk 
sudo apt-get install build-essential
sudo apt-get install postgresql  
git clone ...
cd voiceauth 
python3 -m pip install -r ./requirements.txt 
```

Add these configuration files as /etc/asterisk/manager.d/voiceauth.conf:
```
[voiceauth]
secret=voiceauth
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.255
read=all
write=all
``` 

Create text file callerids.txt in current directory with each callerid per line 
Example: 
```
0440123456
0440123987
0440124032
```



## Run 
Setup environment variables in the voiceauth.sh and run it. 
```
vim ./voiceauth.sh 
./voiceauth.sh
```

DB_* variables is simple and do not need to make a description 
AUTH_TOKEN is a string that http_api expect in X-Auth-Token HTTP header in POST request 
WEBHOOK is URL to POST JSON data with the result of every call that made by voiceauth.py
AMI_* parameters is an asterisk manager access parameters that configured in /etc/asterisk/manager.conf 


