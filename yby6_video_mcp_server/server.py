import logging
from typing import Optional, Dict, Any
from .utils import (
    share_url_parse_tool,
    video_id_parse_tool,
    share_text_parse_tool
)
from fastmcp import FastMCP, Context

# 直接导入版本号，避免循环导入
from . import __version__

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
async def share_url_parse_tool_wrapper(url: str) -> Dict[str, Any]:
    """解析视频分享链接，获取视频信息"""
    return await share_url_parse_tool(url)


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
async def video_id_parse_tool_wrapper(source: str, video_id: str) -> Dict[str, Any]:
    """根据视频来源和ID解析视频信息"""
    return await video_id_parse_tool(source, video_id)


@mcp.tool(
    description="""
          提取视频内容，需要传递apikey，否则无法使用视频内容提取功能！
          参数:
          - text: 抖音分享文本，包含分享链接
          - api_base_url: API基础URL，默认使用siliconflow.cn
          - model: 语音识别模型，默认使用FunAudioLLM/SenseVoiceSmall
          """
)
async def share_text_parse_tool_wrapper(
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
    return await share_text_parse_tool(text, api_base_url, model, ctx)


def main():
    """作为Python包入口点的主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="视频解析MCP服务器 @yangbuyiya")
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


if __name__ == "__main__":
    main()
