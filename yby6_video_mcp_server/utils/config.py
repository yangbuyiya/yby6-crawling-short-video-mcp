# 配置处理模块

import os
import logging
from typing import Optional

from fastmcp.server.context import Context
from fastmcp.server.dependencies import get_http_request, get_http_headers

logger = logging.getLogger(__name__)


def get_api_configuration(ctx: Optional[Context], api_base_url: Optional[str], model: Optional[str]) -> tuple:
    """获取API配置信息"""
    api_key = None
    
    try:
        # 尝试从HTTP请求中获取API密钥
        headers = get_http_headers(include_all=True)
        logger.debug(f"请求头信息: {headers}")
        
        if "apikey" in headers:
            api_key = headers["apikey"]
            if ctx:
                ctx.info(f"使用请求头中的 API 密钥")
            logger.info("使用请求头中的 API 密钥")

        # 尝试从查询参数获取API密钥
        if not api_key:
            request = get_http_request()
            logger.debug(f"查询参数: {request.query_params}")
            query_api_key = request.query_params.get("apikey")
            if query_api_key:
                api_key = query_api_key
                if ctx:
                    ctx.info(f"使用 URL 查询参数中的 API 密钥")
                logger.info("使用 URL 查询参数中的 API 密钥")
                
    except RuntimeError:
        logger.debug("非 HTTP 请求上下文，无法获取请求信息")
    
    # 从环境变量获取配置
    if not api_key:
        api_key = os.getenv("API_KEY")
        if api_key and ctx:
            ctx.info(f"使用环境变量中的 API 密钥")
        if api_key:
            logger.info("使用环境变量中的 API 密钥")
            
    if not api_base_url:
        api_base_url = os.getenv("API_BASE_URL")
        if api_base_url and ctx:
            ctx.info(f"使用环境变量中的 API 基础 URL: {api_base_url}")
        if api_base_url:
            logger.info(f"使用环境变量中的 API 基础 URL: {api_base_url}")
            
    if not model:
        model = os.getenv("MODEL")
        if model and ctx:
            ctx.info(f"使用环境变量中的模型: {model}")
        if model:
            logger.info(f"使用环境变量中的模型: {model}")
    
    return api_key, api_base_url, model 