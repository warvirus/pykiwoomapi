"""Main API client for PyKiwoom."""

import logging
from typing import Any, Dict, List, Optional, Union

from .auth import Auth
from .common import api_request
from .transactions import APPID


class KiwoomClient:
    """Kiwoom Open API+ client.

    Args:
        auth: Auth object with valid token.
    """

    def __init__(self, auth: Auth) -> None:
        self._auth = auth

    @property
    def is_auth(self) -> bool:
        return self._auth.is_auth

    @property
    def auth(self) -> Auth:
        return self._auth

    def read(
        self,
        cmd: Union[str, Dict[str, Any]],
        cont_yn: str = "N",
        next_key: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute an API command.

        Usage patterns:

        1. Simple command (string):
            client.read("주식기본정보요청", stk_cd="005930")

        2. Structured request (dict):
            tr_cmd = {
                "rqname": "주식기본정보요청",
                "stk_cd": "005930",
                "next": "0",
                "screen": "1000",
                "input": {"종목코드": "005930"},
                "output": ["종목코드", "종목명", "PER", "PBR"]
            }
            client.read(tr_cmd)

        Args:
            cmd: Command name (str) or structured request (dict).
            cont_yn: Continuation flag ('Y' or 'N').
            next_key: Pagination key for subsequent requests.
            **kwargs: Request parameters (for string command mode).

        Returns:
            API response dictionary.
        """
        if isinstance(cmd, dict):
            return self._read_structured(cmd)
        else:
            return self._read_simple(cmd, cont_yn, next_key, **kwargs)

    def _read_structured(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structured request format."""
        rqname = req.get("rqname")
        if not rqname:
            logging.error("Missing 'rqname' in request")
            return {"return_code": -1, "return_msg": "Missing 'rqname'"}

        if rqname not in APPID:
            logging.error("Unknown command: %s", rqname)
            return {"return_code": -1, "return_msg": f"Unknown command: {rqname}"}

        api_id = APPID[rqname][0]
        fn_name = APPID[rqname][1]

        cont_yn = req.get("next", "N")
        next_key = req.get("next_key", "")

        input_data = req.get("input", {})
        if not input_data:
            for k, v in req.items():
                if k not in ("rqname", "next", "next_key", "screen", "input", "output"):
                    input_data[k] = v

        if isinstance(fn_name, str):
            return api_request(
                self._auth.mock,
                self._auth.token,
                api_id,
                fn_name,
                cont_yn,
                next_key,
                data=input_data,
            )
        elif callable(fn_name):
            return fn_name(
                self._auth.mock,
                self._auth.token,
                api_id,
                cont_yn,
                next_key,
                data=input_data,
            )
        else:
            logging.error("Internal function error: fn_name is '%s'", fn_name)
            return {"return_code": -1, "return_msg": "Internal error"}

    def _read_simple(
        self,
        cmd: str,
        cont_yn: str = "N",
        next_key: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Handle simple command string format."""
        if cmd not in APPID:
            logging.error("Unknown command: %s", cmd)
            return {"return_code": -1, "return_msg": "Unknown command"}

        api_id = APPID[cmd][0]
        fn_name = APPID[cmd][1]

        if isinstance(fn_name, str):
            return api_request(
                self._auth.mock,
                self._auth.token,
                api_id,
                fn_name,
                cont_yn,
                next_key,
                **kwargs,
            )
        elif callable(fn_name):
            return fn_name(
                self._auth.mock,
                self._auth.token,
                api_id,
                cont_yn,
                next_key,
                **kwargs,
            )
        else:
            logging.error("Internal function error: fn_name is '%s'", fn_name)
            return {"return_code": -1, "return_msg": "Internal error"}