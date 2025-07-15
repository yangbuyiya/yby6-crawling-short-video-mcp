# 辅助函数模块

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse
from .constants import URL_REGEX_PATTERN


def extract_url_from_text(text: str) -> Optional[str]:
    """从文本中提取URL"""
    url_reg = re.compile(URL_REGEX_PATTERN)
    match = url_reg.search(text)
    return match.group() if match else None


def get_val_from_url_by_query_key(url: str, query_key: str) -> str:
    """
    从url的query参数中解析出query_key对应的值
    :param url: url地址
    :param query_key: query参数的key
    :return:
    """
    url_res = urlparse(url)
    url_query = parse_qs(url_res.query, keep_blank_values=True)

    try:
        query_val = url_query[query_key][0]
    except KeyError:
        raise KeyError(f"url中不存在query参数: {query_key}")

    if len(query_val) == 0:
        raise ValueError(f"url中query参数值长度为0: {query_key}")

    return url_query[query_key][0] 