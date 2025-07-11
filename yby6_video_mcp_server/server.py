import re
import time
import httpx
import tempfile
from pathlib import Path
from typing import Optional
import ffmpeg
from .functionality import VideoSource, parse_video_id, parse_video_share_url
from fastmcp.server.context import Context
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request, get_http_headers

# 创建FastMCP实例
mcp = FastMCP("全网短视频去水印链接提取 MCP服务")

""" 
解析视频分享链接，获取视频信息
@param url: 视频分享链接
@return: 视频信息
"""
@mcp.tool()
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

def main():
    """作为Python包入口点的主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频解析MCP服务器")
    parser.add_argument("--transport", type=str, default="stdio", 
                        choices=["stdio", "sse", "http"], 
                        help="传输方式: stdio, sse, http")
    parser.add_argument("--host", type=str, default="0.0.0.0", 
                        help="主机地址")
    parser.add_argument("--port", type=int, default=8000, 
                        help="端口号")
    parser.add_argument("--path", type=str, default=None, 
                        help="自定义请求路径")
    
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