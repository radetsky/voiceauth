# Simple Voice Authenticator 

## Why 
To validate user with the telephone by check CallerID of incoming call 

## Install 
### Ubuntu 

```
sudo apt-get update
sudo apt-get install asterisk build-essential postgresql python3-pip postgresql-client-common
git clone https://github.com/radetsky/voiceauth.git
cd voiceauth 
python3 -m pip install -r ./requirements.txt 
```

### Setup PostgreSQL 
```
sudo -i -u postgres psql
```
Copy-paste content of bootstrap.sql file 

### Asterisk setup 

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

### Asterisk 16 (Ubuntu 20.04 LTS default asterisk)

Edit /etc/asterisk/sip.conf. 

First of all uncomment 'allowguest=no' string IMMEDIATELY! 

In section general find the regisrations examples and add line that looks like:
```
register => LOGIN:password@IP.AD.DR.ES:PORT
```


Find the 'authentication' section and add something like these bottom lines to the bottom of the file:
```
[provider]
type=peer
host=IP.AD.DR.ES
fromuser=LOGIN
context=voiceauth
call-limit=HOWMUCHLINESYOUVEGOT
disallow=all
allow=ulaw
allow=alaw
```
Replace IP.AD.DR.ES, PORT, HOWMUCHLINESYOUVEGOT with given values from provider

Add these lines to /etc/asterisk/extensions.ael:
```
context voiceauth {
    _X! => {
        Hangup(16);
    }
}
context va_call {
    _X! => {
        Set(CALLERID(all)="${ORIGCID}");
        Dial(SIP/provider/${EXTEN},120);
        NoOp(${DIALSTATUS});
        Hangup(16);
    }
}

context va_answer {
    _X! => {
       Answer();
       Wait(1);
       Hangup(16);
    }
}
```

Restart asterisk: 
```
systemctl restart asterisk
```

### Zadarma properties 
Zadarma wants to setup IP based authorization before you can set your own CallerID. 
Please follow the instructions https://zadarma.com/en/support/instructions/asterisk/trunk/
And do not forget to call 8888 to confirm IP address settings. Use any softphone to connect. 

## Firewall setup 
I prefer to use whitelist firewall settings because of any asterisk installation turns into a target. This is example of firewall setup for Zadarma service. 
Add here your IP address to allow API calls.

```
sudo ufw default deny incoming
sudo ufw allow ssh 
sudo ufw allow from 185.45.152.0/24
sudo ufw allow from 185.45.155.0/24
sudo ufw allow from 37.139.38.0/24
sudo ufw allow from 195.122.19.0/27
sudo ufw allow from 103.109.103.64/28
sudo ufw allow from 31.31.222.192/27
sudo ufw allow from 89.185.0.75 
sudo ufw enable 
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

## Initiate call 
```
curl -d "0501231231" http://localhost:8000 -H "X-Auth-Token: test123"
```

## Webhook 
After any call to user voiceauth will do POST request to WEBHOOK with the body in JSON format
```
{"dst": "0501231231", "callerid": "+380919876543", "status": "BUSY"}
```

