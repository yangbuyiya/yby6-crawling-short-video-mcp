import re
import os
import time
import logging
from typing import Optional, Dict, Any
from .functionality import (
    VideoSource,
    parse_video_id,
    parse_video_share_url,
    VideoProcessor
)
from fastmcp.server.context import Context
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request, get_http_headers

# 直接导入版本号，避免循环导入
from . import __version__

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 常量定义
URL_REGEX_PATTERN = r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*"
DEFAULT_RESPONSE_CODES = {
    'SUCCESS': 200,
    'ERROR': 500
}

# 创建FastMCP实例
mcp = FastMCP(f"全网短视频去水印链接提取 MCP服务 V{__version__}")


@mcp.tool(
    description="""
          解析视频分享链接，获取视频信息
          参数:
          - url: 视频分享链接
          返回:
          - code: 状态码
          - msg: 状态信息
          - data: 视频信息
          """
)
async def share_url_parse_tool(url: str) -> Dict[str, Any]:
    """解析视频分享链接，获取视频信息"""
    if not url or not isinstance(url, str):
        return _create_error_response("URL参数无效")
    
    try:
        video_share_url = _extract_url_from_text(url)
        if not video_share_url:
            return _create_error_response("无法从输入文本中提取有效的URL")
            
        video_info = await parse_video_share_url(video_share_url)
        logger.info(f"成功解析视频URL: {video_share_url}")
        return _create_success_response("解析成功", video_info.__dict__)
    except ValueError as err:
        logger.error(f"URL解析失败: {err}")
        return _create_error_response(str(err))
    except Exception as err:
        logger.error(f"未知错误: {err}")
        return _create_error_response(f"解析失败: {str(err)}")


@mcp.tool(
    description="""
          根据视频来源和ID解析视频信息
          参数:
          - source: 视频来源
          - video_id: 视频ID
          返回:
          - code: 状态码
          - msg: 状态信息
          - data: 视频信息
          """
)
async def video_id_parse_tool(source: str, video_id: str) -> Dict[str, Any]:
    """根据视频来源和ID解析视频信息"""
    if not source or not video_id:
        return _create_error_response("视频来源和ID参数不能为空")
    
    try:
        video_source = VideoSource(source)
        video_info = await parse_video_id(video_source, video_id)
        logger.info(f"成功解析视频 - 来源: {source}, ID: {video_id}")
        return _create_success_response("解析成功", video_info.__dict__)
    except ValueError as err:
        logger.error(f"视频ID解析失败: {err}")
        return _create_error_response(f"无效的视频来源或ID: {str(err)}")
    except Exception as err:
        logger.error(f"未知错误: {err}")
        return _create_error_response(f"解析失败: {str(err)}")


@mcp.tool(
    description="""
          提取视频内容，需要传递apikey，否则无法使用视频内容提取功能！
          参数:
          - text: 抖音分享文本，包含分享链接
          - api_base_url: API基础URL，默认使用siliconflow.cn
          - model: 语音识别模型，默认使用FunAudioLLM/SenseVoiceSmall
          """
)
async def share_text_parse_tool(
    text: str,
    api_base_url: Optional[str] = None,
    model: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """
    解析抖音分享链接，提取无水印视频地址
    下载无水印视频
    提取音频
    转换音频为文本
    清理临时文件

    参数:
    - text: 抖音分享文本，包含分享链接
    - api_base_url: API基础URL，默认使用SiliconFlow
    - model: 语音识别模型，默认使用SenseVoiceSmall
    """
    if not text or not isinstance(text, str):
        return _create_error_response("文本参数不能为空")
    
    try:
        # 获取配置参数
        api_key, api_base_url, model = _get_api_configuration(ctx, api_base_url, model)
        
        if not api_key:
            error_msg = "没有传递apikey，请通过参数传入apikey或请求头传入apikey，或者设置环境变量API_KEY，否则无法使用视频内容提取功能！"
            logger.error(error_msg)
            return _create_error_response(error_msg)

        processor = VideoProcessor(api_key, api_base_url, model)

        # 解析视频链接
        video_share_url = _extract_url_from_text(text)
        if not video_share_url:
            error_msg = f"无法从文本中提取视频链接: {text}"
            logger.error(error_msg)
            return _create_error_response(error_msg)

        video_obj = await parse_video_share_url(video_share_url)
        video_info = _create_success_response("解析成功", video_obj.__dict__)

        # 处理视频下载和文本提取
        try:
            download_video_info = {
                "url": video_info["data"]["video_url"],
                "title": video_info["data"]["title"],
                "video_id": str(int(time.time())),
            }
            
            logger.info(f"开始下载视频: {download_video_info['title']}")
            video_path = await processor.download_video(download_video_info)
            ctx.info(f"视频下载地址: {video_path}")
            
            logger.info("开始提取音频")
            audio_path = processor.extract_audio(video_path)
            ctx.info(f"音频提取地址: {audio_path}")
            
            logger.info("开始转换音频为文本")
            text_content = processor.extract_text_from_audio(audio_path)
            ctx.info(f"文本提取内容: {text_content}")
            
            logger.info("清理临时文件")
            processor.cleanup_files(video_path, audio_path)
            ctx.info(f"临时文件清理: {video_path}, {audio_path}")
            
            return {
                "code": DEFAULT_RESPONSE_CODES['SUCCESS'],
                "msg": "解析成功",
                "data": video_info["data"],
                "text_content": text_content,
            }
        except Exception as processing_err:
            logger.error(f"视频处理失败: {processing_err}")
            # 确保清理可能存在的临时文件
            try:
                if 'video_path' in locals() and 'audio_path' in locals():
                    processor.cleanup_files(video_path, audio_path)
            except Exception:
                pass
            raise processing_err
    except ValueError as err:
        logger.error(f"参数错误: {err}")
        if ctx:
            ctx.error(f"参数错误: {str(err)}")
        return _create_error_response(str(err))
    except Exception as err:
        logger.error(f"未知错误: {err}")
        if ctx:
            ctx.error(f"解析失败: {str(err)}")
        return _create_error_response(f"解析失败: {str(err)}")


def main():
    """作为Python包入口点的主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="视频解析MCP服务器")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse", "http"],
        help="传输方式: stdio, sse, http",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=8637, help="端口号")
    parser.add_argument("--path", type=str, default=None, help="自定义请求路径")

    args = parser.parse_args()

    print("启动视频解析MCP服务器...")

    # 根据命令行参数选择传输方式
    if args.transport == "http":
        path = args.path if args.path else "/mcp"
        print(f"使用 Streamable HTTP 传输方式: http://{args.host}:{args.port}{path}")
        mcp.run(transport="http", host=args.host, port=args.port, path=path)
    elif args.transport == "sse":
        path = args.path if args.path else "/sse/"
        print(f"使用 SSE 传输方式: http://{args.host}:{args.port}{path}")
        mcp.run(transport="sse", host=args.host, port=args.port, path=path)
    else:
        print("使用 STDIO 传输方式")
        mcp.run(transport="stdio")

def _extract_url_from_text(text: str) -> Optional[str]:
    """从文本中提取URL"""
    url_reg = re.compile(URL_REGEX_PATTERN)
    match = url_reg.search(text)
    return match.group() if match else None


def _create_success_response(msg: str, data: Any) -> Dict[str, Any]:
    """创建成功响应"""
    return {
        "code": DEFAULT_RESPONSE_CODES['SUCCESS'],
        "msg": msg,
        "data": data
    }


def _create_error_response(msg: str) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "code": DEFAULT_RESPONSE_CODES['ERROR'],
        "msg": msg
    }


def _get_api_configuration(ctx: Optional[Context], api_base_url: Optional[str], model: Optional[str]) -> tuple:
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


if __name__ == "__main__":
    main()
