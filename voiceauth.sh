#!/bin/bash 

export DB_HOST=127.0.0.1 
export DB_NAME=voiceauth 
export DB_USER=voiceauth
export DB_PASS=voiceauth
export DB_TABLE=voiceauth 
export AUTH_TOKEN=test123 
export WEBHOOK=http://localhost:8001/ 

export AMI_HOST=178.62.222.78
export AMI_PORT=5038 
export AMI_USER=voiceauth
export AMI_PASS=voiceauth
export AMI_CHANNEL=va_call # outgoing context to call the user
export AMI_CONTEXT=va_answer  # answering context to call the user 
export VA_PROCESS_COUNT=3
python3 ./http_api.py -l 0.0.0.0 -p 8000 &
python3 ./voiceauth.py 

