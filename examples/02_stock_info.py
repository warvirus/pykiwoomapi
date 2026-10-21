"""Example 02: Stock Basic Information Query."""

import json
import os

from dotenv import load_dotenv

from pykiwoomapi import Auth, KiwoomClient

# 1. .env 파일의 내용을 로드합니다.
load_dotenv()

def main():
    mock = True if os.getenv("KIWOOM_APP_MOCK", "1") == "1" or os.getenv("KIWOOM_APP_MOCK", "True").lower() == "true" else False
    app_key = os.getenv("KIWOOM_APP_KEY", "your_app_key")
    secret_key = os.getenv("KIWOOM_SECRET_KEY", "your_secret_key")
    print(f"mock: {mock}, app key : {app_key}, secret_key : {secret_key}")

    auth = Auth()
    if not auth.login(app_key, secret_key, mock=mock):
        print("Login failed")
        return

    client = KiwoomClient(auth)

    result = client.read("주식기본정보요청", stk_cd="005930")
    print("Response:", json.dumps(result, indent=4))



    tr_cmd = {
        "rqname": "주식기본정보요청",
        "stk_cd": "005930"
    }
    result = client.read(tr_cmd)
    print("res:", json.dumps(result, indent=4))

    auth.logout()


if __name__ == "__main__":
    main()
