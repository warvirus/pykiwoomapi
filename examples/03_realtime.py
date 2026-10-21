"""Example 03: Real-time WebSocket Data Streaming."""

import asyncio
import os

from dotenv import load_dotenv

from pykiwoomapi import Auth, WebSocketClient

# 1. .env 파일의 내용을 로드합니다.
load_dotenv()

def on_message(message):
    print(f"Received: {message}")


async def main():
    mock = True if os.getenv("KIWOOM_APP_MOCK", "1") == "1" or os.getenv("KIWOOM_APP_MOCK", "True").lower() == "true" else False
    app_key = os.getenv("KIWOOM_APP_KEY", "your_app_key")
    secret_key = os.getenv("KIWOOM_SECRET_KEY", "your_secret_key")
    print(f"mock: {mock}, app key : {app_key}, secret_key : {secret_key}")

    auth = Auth(mock=True)
    if not auth.login(app_key, secret_key, mock=mock):
        print("Login failed")
        return

    try:
        ws = WebSocketClient(auth, callback=on_message)

        print("Starting WebSocket connection...")
        await ws.connect()

        if ws.connected:
            print("Connected! Waiting for messages...")
            await asyncio.sleep(30)
            await ws.disconnect()

    except KeyboardInterrupt:
        print("keyboard interrupt!")

    finally:
        auth.logout()


if __name__ == "__main__":
    asyncio.run(main())
