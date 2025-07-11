import re
import time
from typing import Optional
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
async def share_url_parse_tool(url: str) -> dict:
    """解析视频分享链接，获取视频信息"""
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    video_share_url = url_reg.search(url).group()

    try:
        video_info = await parse_video_share_url(video_share_url)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


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
async def video_id_parse_tool(source: str, video_id: str) -> dict:
    """根据视频来源和ID解析视频信息"""
    try:
        video_source = VideoSource(source)
        video_info = await parse_video_id(video_source, video_id)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


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
) -> dict:
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
    api_key = None
    try:
        # 尝试从 HTTP 请求中获取 API 密钥
        try:
            # 获取所有请求头（安全方法，不会抛出异常）
            headers = get_http_headers(include_all=True)
            # 打印当前时间
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 当前请求的headers: {headers}"
            )
            # 从请求头中获取 API 密钥
            if "apikey" in headers:
                api_key = headers["apikey"]
                ctx.info(f"使用请求头中的 API 密钥: {api_key}")
                print(f"使用请求头中的 API 密钥: {api_key}")

            # 尝试获取 HTTP 请求对象
            request = get_http_request()
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 当前请求的query_params: {request.query_params}"
            )
            # 从查询参数中获取 API 密钥
            query_api_key = request.query_params.get("apikey")
            if not api_key and query_api_key:
                api_key = query_api_key
                ctx.info(f"使用 URL 查询参数中的 API 密钥: {api_key}")
                print(f"使用 URL 查询参数中的 API 密钥: {api_key}")
        except RuntimeError:
            # 不在 HTTP 请求上下文中，忽略错误
            print("非 HTTP 请求上下文，无法获取请求信息")

        # 如果没有就抛出异常
        if not api_key:
            raise ValueError(
                "没有传递apikey，请通过参数传入apikey或请求头传入apikey，否则无法使用视频内容提取功能！"
            )

        processor = VideoProcessor(api_key, api_base_url, model)

        # 解析视频链接
        url_reg = re.compile(
            r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*"
        )
        match = url_reg.search(text)
        if not match:
            raise ValueError(f"无法从文本中提取视频链接: {text}")

        video_share_url = match.group()
        video_obj = await parse_video_share_url(video_share_url)
        video_info = {"code": 200, "msg": "解析成功", "data": video_obj.__dict__}

        # 下载视频
        # 组装视频信息
        download_video_info = {
            "url": video_info["data"]["video_url"],
            "title": video_info["data"]["title"],
            "video_id": str(int(time.time())),  # 使用时间戳作为视频ID
        }
        video_path = await processor.download_video(download_video_info)
        ctx.info(f"视频下载地址: {video_path}")
        # 提取音频
        audio_path = processor.extract_audio(video_path)
        ctx.info(f"音频提取地址: {audio_path}")
        # 提取文本
        text_content = processor.extract_text_from_audio(audio_path)
        ctx.info(f"文本提取地址: {text_content}")
        # 清理临时文件
        processor.cleanup_files(video_path, audio_path)
        ctx.info(f"临时文件清理: {video_path}, {audio_path}")
        # 组装返回数据
        return {
            "code": 200,
            "msg": "解析成功",
            "data": video_info["data"],
            "text_content": text_content,
        }
    except Exception as err:
        ctx.error(f"解析失败: {str(err)}")
        return {
            "code": 500,
            "msg": str(err),
        }


def main():
    """作为Python包入口点的主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="视频解析MCP服务器")
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


if __name__ == "__main__":
    main()
