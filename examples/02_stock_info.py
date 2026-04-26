"""Example 02: Stock Basic Information Query."""

import os
from pykiwoomapi import Auth, KiwoomClient
from dotenv import load_dotenv

# 1. .env 파일의 내용을 로드합니다.
load_dotenv()

def main():
    app_key = os.getenv("KIWOOM_APP_KEY", "your_app_key")
    secret_key = os.getenv("KIWOOM_SECRET_KEY", "your_secret_key")

    auth = Auth()
    if not auth.login(app_key, secret_key, mock=True):
        print("Login failed")
        return

    client = KiwoomClient(auth)

    result = client.read("주식기본정보요청", stk_cd="005930")
    print("Response:", result)



    tr_cmd = {
        "rqname": "주식기본정보요청", 
        "stk_cd": "005930"
    }
    result = client.read(tr_cmd)
    print("res:", result)

    auth.logout()


if __name__ == "__main__":
    main()