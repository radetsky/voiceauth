#!/bin/bash 

export DB_HOST=127.0.0.1 
export DB_NAME=voiceauth 
export DB_USER=voiceauth
export DB_PASS=voiceauth
export DB_TABLE=voiceauth 
export AUTH_TOKEN=test123 
export WEBHOOK=http://localhost:8081/ 

export AMI_HOST=143.244.144.230
export AMI_PORT=5038 
export AMI_USER=voiceauth
export AMI_PASS=voiceauth
export AMI_CHANNEL=SIP/provider
export AMI_CONTEXT=voiceauth
python3 ./voiceauth.py 



