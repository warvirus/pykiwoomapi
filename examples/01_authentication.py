"""Example 01: Authentication with Kiwoom API."""

import logging
import os
from pykiwoomapi import Auth, KiwoomClient
from dotenv import load_dotenv

# 1. .env 파일의 내용을 로드합니다.
load_dotenv()

APP_KEY = os.getenv("KIWOOM_APP_KEY", "your_app_key")
SECRET_KEY = os.getenv("KIWOOM_SECRET_KEY", "your_secret_key")

print("Using APP_KEY:", APP_KEY)
print("Using SECRET_KEY:", SECRET_KEY)


def main():
    # Custom logger example
    my_logger = logging.getLogger("my_app")
    my_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
    my_logger.addHandler(handler)

    my_logger.info("Starting authentication...")

    results = []

    # Usage 1: Create Auth with custom logger
    auth = Auth(
        mock=False,
        appkey=APP_KEY,
        secretkey=SECRET_KEY,
        logger=my_logger
    )
    print(f"Auth URL: {auth.url}")
    print(f"Is authenticated before login: {auth.is_auth}")

    success = auth.login(mock=True, results=results)
    print(f"Login success: {success}")
    print(f"Auth URL (after mock=True): {auth.url}")
    print(f"Results: {results}")

    if success:
        print(f"Is authenticated after login: {auth.is_auth}")
        print(f"Token: {auth.token[:20]}...")  # type: ignore
        client = KiwoomClient(auth)
        print("KiwoomClient created successfully")
        print(f"Client is authenticated: {client.is_auth}")

    auth.logout()
    print("Logged out successfully")


def main2():
    # Usage 2: Default logger
    results = []
    auth = Auth(mock=False)
    success = auth.login(APP_KEY, SECRET_KEY, mock=True, results=results)
    print(f"Login success: {success}, Results: {results}")


if __name__ == "__main__":
    main()
    print("\n--- main2 (default logger) ---")
    main2()