# 响应处理模块

from typing import Dict, Any
from .constants import DEFAULT_RESPONSE_CODES


def create_success_response(msg: str, data: Any) -> Dict[str, Any]:
    """创建成功响应"""
    return {
        "code": DEFAULT_RESPONSE_CODES['SUCCESS'],
        "msg": msg,
        "data": data
    }


def create_error_response(msg: str) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "code": DEFAULT_RESPONSE_CODES['ERROR'],
        "msg": msg
    } 