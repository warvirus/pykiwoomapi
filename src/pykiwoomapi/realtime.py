"""Real-time WebSocket client for PyKiwoom."""

import asyncio
import inspect
import json
import logging
import threading
from typing import Any, Callable, List, Optional

import websockets

from .auth import Auth


class WebSocketClient:
    """WebSocket client for real-time market data streaming.

    Args:
        auth: Auth object with valid token.
        callback: Callback function to handle received messages.
    """
    RECV_TIMEOUT = 3.0  # seconds

    def __init__(self, auth: Auth, callback: Optional[Callable] = None) -> None:
        self._auth = auth
        self.logger = auth.logger
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
        self._thread_loop: Optional[asyncio.AbstractEventLoop] = None
        if callback:
            self.message_handlers.append(callback)

    async def connect(self) -> None:
        # 기존 연결이 남아있으면 먼저 정리
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            self.websocket = None
        self.connected = False
        self.is_login = False

        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            self.logger.debug("Connected to real-time server.")
            param = {
                "trnm": "LOGIN",
                "token": self._auth.token,
            }
            self.logger.debug("Sending login packet to real-time server.")
            await self.send_message(param, True)
        except websockets.exceptions.ConnectionClosedError as e:
            self.logger.error("[Realtime] Connection error: %s", e)
            self.connected = False
        except Exception as e:
            self.logger.error("[Realtime] Unexpected error: %s", e)
            self.connected = False
            self.is_login = False
            await self.recv_message(
                {"trnm": "[Realtime] ERROR", "error_type": "CONNECTION_FAILED", "message": str(e)}
            )

    async def send_message(self, message: Any, force: bool = False) -> None:
        if self.keep_running and self.connected and (self.is_login or force):
            if not isinstance(message, str):
                message = json.dumps(message)
            try:
                await self.websocket.send(message) # type: ignore
                self.logger.debug("Message sent: %s", message)
            except websockets.exceptions.ConnectionClosedOK:
                self.logger.error("[Realtime] Connection already closed.")
                self.connected = False
            except Exception as e:
                self.logger.error("[Realtime] Send error: %s", e)
                self.connected = False
        else:
            self.logger.error("[Realtime] Not connected to server.")

    async def disconnected_message(self, return_code = 0, return_msg = "") -> None:
        message = {
            'trnm': 'DISCONNECTED',
            'return_code': return_code,
            'return_msg': return_msg,   
        }
        for handler in self.message_handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)

    async def recv_message(self, message: Any) -> None:
        for handler in self.message_handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)

    async def receive_messages(self) -> None:
        while self.keep_running:
            response_str = ""
            try:
                # 연결이 끊긴 경우 재연결 시도
                if not self.connected or self.websocket is None:
                    if not self.keep_running:   # 추가
                        break
                    
                    self.logger.debug("[Realtime] Reconnecting in 3 seconds...")
                    await asyncio.sleep(3)
                    await self.connect()
                else:
                    # timeout을 두어 주기적으로 keep_running을 확인
                    response_str = await asyncio.wait_for(self.websocket.recv(), timeout=self.RECV_TIMEOUT)
                    response = json.loads(response_str)

                    trnm = response.get("trnm", "")
                    if trnm == "LOGIN":
                        return_code = response.get("return_code", -1)
                        if return_code != 0:
                            self.logger.error(
                                f"[Realtime] Login failed: return_code : {return_code}, {response.get('return_msg', '')}", 
                            )
                            await self.disconnect()
                        else:
                            self.logger.info("Real-time login successful.")
                            self.is_login = True
                            await self.recv_message(response)  # 로그인 응답도 핸들러로 전달
                    elif trnm == "PING":
                        await self.send_message(response)
                    else:
                        self.logger.debug(
                            "Real-time server response: %s",
                            json.dumps(response, indent=4, ensure_ascii=False),
                        )
                        await self.recv_message(response)  # 일반 메시지도 핸들러로 전달
            # self.websocket.recv()에서 발생할 수 있는 다양한 예외 처리 
            except AttributeError as e:
                self.logger.error("[Realtime] Attribute error: %s", e)
                continue

            except asyncio.TimeoutError:
                # 주기적으로 연결 상태를 확인하기 위해 타임아웃 설정
                continue

            except websockets.ConnectionClosed:
                if self.keep_running:
                    self.logger.warning("[Realtime] Connection closed, will reconnect...")
                self.connected = False
                self.is_login = False
                self.websocket = None
                await self.disconnected_message(-1)  # 연결 끊김 메시지 핸들러로 전달

            except json.JSONDecodeError:
                self.logger.error("[Realtime] JSON parse error: %s...", response_str[:100])
            except RuntimeError as e:
                if "asyncio" in str(e).lower() or "loop" in str(e).lower():
                    self.logger.warning("[Realtime] Loop issue, stopping.")
                    break
                else:
                    self.logger.error("[Realtime] Runtime error: %s", e)
            except Exception as e:
                err_str = str(e)
                if "Future" in err_str and "loop" in err_str:
                    self.logger.warning("[Realtime] Loop issue, stopping.")
                    break
                else:
                    self.logger.error(f"[Realtime] Receive error: : {err_str} : '{response_str}'", )

        # while 루프 종료 후 연결이 남아있다면 정리        
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass

        self.websocket = None
        await self.disconnected_message(0)  # 연결 끊김 메시지 핸들러로 전달
        self.logger.info("Real-time closed : successful.")

    async def run(self) -> None:
        await self.connect()
        await self.receive_messages()

    async def disconnect(self) -> None:
        self.keep_running = False
        self.is_login = False

        if self.connected and self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False
            self.logger.debug("Real-time disconnected.")

    def add_message_handler(self, handler: Callable) -> None:
        if inspect.iscoroutinefunction(handler):
            self.message_handlers.append(handler)
        else:
            self.logger.warning("[Realtime] Handler must be an async function.")

    def start_thread(self, callback: Optional[Callable] = None) -> None:
        self.keep_running = True
        
        self._thread = threading.Thread(
            target=self.run_worker_in_thread, args=(callback,), daemon=True
        )
        self._thread.start()

    def close_thread(self) -> None:
        self.keep_running = False
        self.connected = False

        # websocket.close()를 예약하고 완료를 기다림
        if self._thread_loop and not self._thread_loop.is_closed() and self.websocket:
            future = asyncio.run_coroutine_threadsafe(
                self.websocket.close(), self._thread_loop
            )
            try:
                future.result(timeout=(self.RECV_TIMEOUT*2))   # 최대 RECV_TIMEOUT*2 대기
            except Exception:
                pass

        self.websocket = None

        # 스레드 참조를 보관하고 있다면 join으로 완전 종료 확인
        if hasattr(self, '_thread') and self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.RECV_TIMEOUT*2)  # 최대 RECV_TIMEOUT*2 대기

        self.logger.debug("[Realtime] Thread closed.")

    def run_worker_in_thread(self, callback: Optional[Callable] = None) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._thread_loop = loop
        try:
            loop.run_until_complete(self.run())
        except Exception as e:
            self.logger.error(f"[Realtime] Thread error: {e}")
        finally:
            loop.close()
            self._thread_loop = None

    def send_data(self, data: Any) -> None:
        # worker thread의 이벤트 루프에 코루틴을 예약 (fire-and-forget)
        # future.result()로 대기하면 worker thread 내부에서 호출 시 데드락 발생
        if self._thread_loop and not self._thread_loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.send_message(data), self._thread_loop)
        else:
            self.logger.error("[Realtime] Cannot send data: worker thread loop is not available.")

