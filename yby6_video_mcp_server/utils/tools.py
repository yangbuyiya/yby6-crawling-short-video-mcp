# MCP工具函数模块

import time
import logging
from typing import Optional, Dict, Any

from fastmcp.server.context import Context
from ..functionality import (
    VideoSource,
    parse_video_id,
    parse_video_share_url,
    VideoProcessor
)
from .responses import create_success_response, create_error_response
from .helpers import extract_url_from_text
from .config import get_api_configuration
from .constants import DEFAULT_RESPONSE_CODES

logger = logging.getLogger(__name__)


async def share_url_parse_tool(url: str) -> Dict[str, Any]:
    """解析视频分享链接，获取视频信息"""
    if not url or not isinstance(url, str):
        return create_error_response("URL参数无效")
    
    try:
        video_share_url = extract_url_from_text(url)
        if not video_share_url:
            return create_error_response("无法从输入文本中提取有效的URL")
            
        video_info = await parse_video_share_url(video_share_url)
        logger.info(f"成功解析视频URL: {video_share_url}")
        return create_success_response("解析成功", video_info.__dict__)
    except ValueError as err:
        logger.error(f"URL解析失败: {err}")
        return create_error_response(str(err))
    except Exception as err:
        logger.error(f"未知错误: {err}")
        return create_error_response(f"解析失败: {str(err)}")


async def video_id_parse_tool(source: str, video_id: str) -> Dict[str, Any]:
    """根据视频来源和ID解析视频信息"""
    if not source or not video_id:
        return create_error_response("视频来源和ID参数不能为空")
    
    try:
        video_source = VideoSource(source)
        video_info = await parse_video_id(video_source, video_id)
        logger.info(f"成功解析视频 - 来源: {source}, ID: {video_id}")
        return create_success_response("解析成功", video_info.__dict__)
    except ValueError as err:
        logger.error(f"视频ID解析失败: {err}")
        return create_error_response(f"无效的视频来源或ID: {str(err)}")
    except Exception as err:
        logger.error(f"未知错误: {err}")
        return create_error_response(f"解析失败: {str(err)}")


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
        return create_error_response("文本参数不能为空")
    
    try:
        # 获取配置参数
        api_key, api_base_url, model = get_api_configuration(ctx, api_base_url, model)
        
        if not api_key:
            error_msg = "没有传递apikey，请通过参数传入apikey或请求头传入apikey，或者设置环境变量API_KEY，否则无法使用视频内容提取功能！"
            logger.error(error_msg)
            return create_error_response(error_msg)

        processor = VideoProcessor(api_key, api_base_url, model)

        # 解析视频链接
        video_share_url = extract_url_from_text(text)
        if not video_share_url:
            error_msg = f"无法从文本中提取视频链接: {text}"
            logger.error(error_msg)
            return create_error_response(error_msg)

        video_obj = await parse_video_share_url(video_share_url)
        video_info = create_success_response("解析成功", video_obj.__dict__)

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
        return create_error_response(str(err))
    except Exception as err:
        logger.error(f"未知错误: {err}")
        if ctx:
            ctx.error(f"解析失败: {str(err)}")
        return create_error_response(f"解析失败: {str(err)}") 