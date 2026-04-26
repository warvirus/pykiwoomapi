"""Real-time WebSocket client for PyKiwoom."""

import asyncio
import json
import logging
import threading
import time
from typing import Any, Callable, List, Optional

import websockets

from .auth import Auth


class WebSocketClient:
    """WebSocket client for real-time market data streaming.

    Args:
        auth: Auth object with valid token.
        callback: Callback function to handle received messages.
    """

    def __init__(self, auth: Auth, callback: Optional[Callable] = None) -> None:
        self._auth = auth
        self.uri = (
            "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"
            if self._auth.mock
            else "wss://api.kiwoom.com:10000/api/dostk/websocket"
        )
        self.websocket: Optional[Any] = None
        self.connected = False
        self.is_login = False
        self.keep_running = True
        self.message_handlers: List[Callable] = []
        if callback:
            self.message_handlers.append(callback)

    async def connect(self) -> None:
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            logging.debug("Attempting to connect to server...")

            param = {
                "trnm": "LOGIN",
                "token": self._auth.token,
            }
            logging.debug("Sending login packet to real-time server.")
            await self.send_message(param, True)
        except websockets.exceptions.ConnectionClosedError as e:
            logging.error("[Realtime] Connection error: %s", e)
        except Exception as e:
            logging.error("[Realtime] Unexpected error: %s", e)
            self.connected = False
            self.is_login = False
            await self.recv_message(
                {"trnm": "[Realtime] ERROR", "error_type": "CONNECTION_FAILED", "message": str(e)}
            )

    async def recv_message(self, message: Any) -> None:
        for handler in self.message_handlers:
            handler(message)

    async def send_message(self, message: Any, force: bool = False) -> None:
        if self.keep_running and self.connected and (self.is_login or force):
            if not isinstance(message, str):
                message = json.dumps(message)
            try:
                await self.websocket.send(message)
                logging.debug("Message sent: %s", message)
            except websockets.exceptions.ConnectionClosedOK:
                logging.error("[Realtime] Connection already closed.")
                self.connected = False
            except Exception as e:
                logging.error("[Realtime] Send error: %s", e)
                self.connected = False
        else:
            logging.error("[Realtime] Not connected to server.")

    async def receive_messages(self) -> None:
        retry_cnt = 0
        while self.keep_running:
            if self.connected:
                response_str = ""
                try:
                    response_str = await self.websocket.recv()
                    response = json.loads(response_str)

                    if response.get("trnm") == "LOGIN":
                        if response.get("return_code") != 0:
                            logging.error(
                                "[Realtime] Login failed: %s", response.get("return_msg")
                            )
                            await self.disconnect()
                        else:
                            logging.info("Real-time login successful.")
                            self.is_login = True
                            for handler in self.message_handlers:
                                handler(response)
                    else:
                        if response.get("trnm") == "PING":
                            await self.send_message(response)
                        else:
                            logging.debug(
                                "Real-time server response: %s",
                                json.dumps(response, indent=4, ensure_ascii=False),
                            )
                            for handler in self.message_handlers:
                                handler(response)

                except websockets.ConnectionClosed:
                    logging.error("[Realtime] Connection closed by server.")
                    self.connected = False
                    self.is_login = False
                    if self.websocket:
                        await self.websocket.close()
                except json.JSONDecodeError:
                    logging.error("[Realtime] JSON parse error: %s...", response_str[:100])
                except Exception as e:
                    logging.error("[Realtime] Receive error: %s", e)
            else:
                await self.connect()
                if self.connected:
                    retry_cnt = 0
                else:
                    retry_cnt = retry_cnt + (1 if retry_cnt < 10 else 0)
                    delay_sec = 5 * retry_cnt
                    while self.keep_running:
                        if delay_sec > 0:
                            await asyncio.sleep(1)
                            delay_sec -= 1
                        else:
                            break

        if self.websocket:
            await self.websocket.close()
        self.websocket = None

    async def run(self) -> None:
        await self.receive_messages()

    async def disconnect(self) -> None:
        self.keep_running = False
        self.is_login = False

        if self.connected and self.websocket:
            while self.websocket is not None:
                time.sleep(0.01)
            self.connected = False
            logging.info("Real-time logout complete.")

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.stop()
        except RuntimeError:
            pass

    def add_message_handler(self, handler: Callable) -> None:
        if asyncio.iscoroutinefunction(handler):
            self.message_handlers.append(handler)
        else:
            logging.warning("[Realtime] Handler must be an async function.")

    def start_thread(self, callback: Optional[Callable] = None) -> None:
        thread = threading.Thread(target=self.run_worker_in_thread, args=(callback,))
        thread.start()

    def close_thread(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.disconnect())
        loop.close()

    def run_worker_in_thread(self, callback: Optional[Callable] = None) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())
        loop.close()

    def send_data(self, data: Any) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.send_message(data))
        loop.close()