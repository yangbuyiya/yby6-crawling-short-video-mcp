import re
import time
import httpx
import tempfile
from pathlib import Path
from typing import Optional
import ffmpeg

# 请求头，模拟移动端访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1'
}

# 默认 API 配置
DEFAULT_API_BASE_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
DEFAULT_MODEL = "FunAudioLLM/SenseVoiceSmall"


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, api_key: str, api_base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.api_base_url = api_base_url or DEFAULT_API_BASE_URL
        self.model = model or DEFAULT_MODEL
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def __del__(self):
        """清理临时目录"""
        import shutil
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def download_video(self, video_info: dict) -> Path:
        """异步下载视频到临时目录"""
        print(f"下载视频信息: {video_info}")
        # 如果 video_info['video_id'] 是空, 则使用当前时间戳作为视频ID
        if not video_info['video_id']:
            video_info['video_id'] = str(int(time.time()))
        filename = f"{video_info['video_id']}.mp4"
        filepath = self.temp_dir / filename
        
        with httpx.Client() as client:
            response = client.get(video_info['url'], headers=HEADERS, follow_redirects=True)
            response.raise_for_status()
        
        # 下载文件
        with open(filepath, 'wb') as f:
            for chunk in response.iter_bytes(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return filepath
    
    def extract_audio(self, video_path: Path) -> Path:
        """从视频文件中提取音频"""
        print(f"准备提取的视频文件: {video_path}")
        audio_path = video_path.with_suffix('.mp3')
        
        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='libmp3lame', q=0)
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            return audio_path
        except Exception as e:
            raise Exception(f"提取音频时出错: {str(e)}")
    
    def extract_text_from_audio(self, audio_path: Path) -> str:
        """从音频文件中提取文字"""
        print(f"准备提取的音频文件: {audio_path}")
        files = {
            'file': (audio_path.name, open(audio_path, 'rb'), 'audio/mpeg'),
            'model': (None, self.model)
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # 设置较长的超时时间，单位为秒
            timeout = httpx.Timeout(300.0)  # 5分钟超时
            with httpx.Client(timeout=timeout) as client:
                response = client.post(self.api_base_url, files=files, headers=headers)
                response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if 'text' in result:
                return result['text']
            else:
                return response.text
                
        except Exception as e:
            raise Exception(f"提取文字时出错: {str(e)}")
        finally:
            files['file'][1].close()
    
    def cleanup_files(self, *file_paths: Path):
        """清理指定的文件"""
        for file_path in file_paths:
            if file_path.exists():
                file_path.unlink() 