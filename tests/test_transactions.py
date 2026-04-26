"""Tests for the transactions module."""

import pytest
from pykiwoomapi.transactions import (
    APPID,
    _Elements,
    _ElementsRealtime,
    Element,
    ElementReal,
)


class TestAPPID:
    def test_appid_keys_are_strings(self):
        for key in APPID.keys():
            assert isinstance(key, str)

    def test_appid_values_are_lists(self):
        for value in APPID.values():
            assert isinstance(value, list)
            assert len(value) == 2

    def test_stock_commands_exist(self):
        assert "주식기본정보요청" in APPID
        assert "주식거래원요청" in APPID

    def test_account_commands_exist(self):
        assert "예수금상세현황요청" in APPID
        assert "계좌평가잔고내역요청" in APPID

    def test_order_commands_exist(self):
        assert "주식 매수주문" in APPID
        assert "주식 매도주문" in APPID


class TestElements:
    def test_element_lookup(self):
        result = Element("stk_cd")
        assert result == "종목코드"

    def test_element_not_found(self):
        result = Element("unknown_field")
        assert result == "unknown_field"

    def test_element_real_lookup(self):
        result = ElementReal("10")
        assert result == "현재가"

    def test_element_real_not_found(self):
        result = ElementReal("99999")
        assert result == "99999"