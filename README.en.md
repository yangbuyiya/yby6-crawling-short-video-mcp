# Video Watermark Removal & Link Extraction MCP Service

## Project Introduction

This project is a FastMCP-based service for parsing short video sharing links from multiple platforms. It automatically extracts the original video URL and related information without watermarks.  
Suitable for scenarios requiring batch parsing, watermark removal, and short video collection. The project also supports video content text extraction through speech recognition.

[![PyPI version](https://img.shields.io/pypi/v/yby6-video-mcp-server.svg)](https://pypi.org/project/yby6-video-mcp-server/)

## Main Features

- Supports 20+ short video platforms (Douyin, Kuaishou, Xiaohongshu, Weibo, Xigua Video, etc.)
- One-click parsing of video sharing links to obtain watermark-free video URLs
- Supports multiple transport methods (stdio, SSE, HTTP)
- Supports video content text extraction (requires FFmpeg and API Key, uses SiliconFlow by default: https://cloud.siliconflow.cn/i/tbvUltCF)
- Supports Docker containerized deployment
- Clear code structure, easy to extend

## Demo
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/8501c118-4ab2-471e-b4f6-683ac58902f0" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/c649c0e0-309d-4cf7-9c6b-5581f9ae4383" />

## Supported Platforms

Currently supports parsing from the following short video platforms:

- Douyin
- Kuaishou
- Xiaohongshu (RED)
- Weibo
- Pipixia
- Weishi
- Lvzhou
- Zuiyou
- Quanmin Video
- Xigua Video
- Lishipin
- Pipigaoxiao
- Huya
- AcFun
- Doupai
- Meipai
- Quanmin K Song
- Sixroom
- Xinpianchang
- Haokan Video

## Directory Structure

```
crawling-short-video-mcp/
├── yby6_video_mcp_server/
│   ├── server.py                # Main service entry
│   ├── functionality/           # Platform-specific parsing modules
│   │   ├── base.py             # Base classes and enum definitions
│   │   ├── douyin.py           # Douyin implementation
│   │   ├── kuaishou.py         # Kuaishou implementation
│   │   ├── ...                 # Other platform implementations
│   │   └── video_processor.py  # Video processing and text extraction
│   └── utils/                   # Utility functions
├── Dockerfile.base              # Base image build file
├── Dockerfile.mcp               # MCP service image build file
├── requirements.txt             # Dependencies list
├── pyproject.toml              # Project configuration and metadata
└── README.md                    # Project documentation
```

## Installation

### Prerequisites

#### FFmpeg Installation (Required for video text content extraction)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download FFmpeg: https://ffmpeg.org/download.html#build-windows
2. Extract to a directory, e.g., `C:\ffmpeg`
3. Add to system PATH: `C:\ffmpeg\bin`
4. Restart command line or system for environment variables to take effect

Verify installation:
```bash
ffmpeg -version
```

### Method 1: Install via pip from PyPI (may not have the latest version)
Current latest version: [![PyPI version](https://img.shields.io/pypi/v/yby6-video-mcp-server.svg)](https://pypi.org/project/yby6-video-mcp-server/)

```bash
# Install latest version
pip install -i https://pypi.org/simple yby6-video-mcp-server

# Or install specific version
pip install -i https://pypi.org/simple yby6-video-mcp-server==1.0.1
```

After installation, verify with:

```bash
yby6_video_mcp_server --version
```

## MCP Configuration

```json
"yby6_video_mcp_server": {
  "command": "uv",
  "args": ["yby6_video_mcp_server"],
  "env": {
    "API_KEY": "Get your free API key at: https://cloud.siliconflow.cn/i/tbvUltCF"
  }
}
```

### Method 2: Install from source (recommended for latest version)

1. Clone this project

   ```bash
   git clone https://github.com/yangbuyiya/yby6-crawling-short-video-mcp.git
   cd yby6-crawling-short-video-mcp
   ```

2. Install dependencies

   Recommended to use Python 3.10+ with a virtual environment:
   
   **macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Method 3: Deploy with Docker

This project provides Docker support for quick deployment

1. Run container with SSE mode
   
   ```bash
   docker run -d -p 8637:8637 registry.cn-hangzhou.aliyuncs.com/yby6/yby6_video_mcp_server:1.0.0
   ```

You can also quickly build and deploy with:

1. Build base image (with FFmpeg and Python environment)

   ```bash
   docker build -t ffmpeg-python-base:1.0.0 -f Dockerfile.base .
   ```

2. Build MCP service image

   ```bash
   docker build -t yby6-video-mcp:latest -f Dockerfile.mcp .
   ```

3. Run container

   ```bash
   docker run -d -p 8637:8637 yby6-video-mcp:latest
   ```

## Usage

### stdio MCP Service Start

```json
// Run from PyPI
"yby6_video_mcp_server": {
  "command": "uv",
  "args": ["yby6_video_mcp_server"],
  "env": {
    "API_KEY": "sk-xcazqbgbnoagddpyaorhqhioxazvqdtednppksiqaotjsboe"
  }
},

// Run from source
"yby6_video_mcp_server": {
  "command": "uv",
  "args": [
    "--directory",
    "to/path/yby6-crawling-short-video-mcp/yby6_video_mcp_server",
    "run",
    "-m",
    "yby6_video_mcp_server.server"
  ],
  "env": {
    "API_KEY": "sk-xcazqbgbnoagddpyaorhqhioxazvqdtednppksiqaotjsboe"
  }
},
```

### SSE or HTTP MCP Service Address

- Supports API key configuration in request headers
- Supports API key configuration in request parameters

```json
"yby6_video_mcp_server": {
  "url": "http://127.0.0.1:8637/sse?apikey=xxxxxx",
}
```

### Starting the Service

```bash
# After pip installation
yby6_video_mcp_server --transport http --host 0.0.0.0 --port 8637

# Or run from source
python -m yby6_video_mcp_server.server --transport http --host 0.0.0.0 --port 8637
```

Parameters:
- `--transport`: Transport method, options: `stdio`, `sse`, `http` (recommended)
- `--host`: Host address, default `0.0.0.0`
- `--port`: Port number, default `8000`
- `--path`: Custom MCP request path (optional)

### API Documentation

#### 1. Parse Video Share Link

**Endpoint:** `share_url_parse_tool`

**Parameters:**

| Parameter | Type   | Required | Description     |
|-----------|--------|----------|-----------------|
| url       | string | Yes      | Video share URL |

**Response Example:**

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "video_url": "https://xxx.com/xxx.mp4",
    "cover_url": "https://xxx.com/cover.jpg",
    "title": "Video Title",
    "music_url": "https://xxx.com/music.mp3",
    "images": [],
    "author": {
      "uid": "User ID",
      "name": "Username",
      "avatar": "Avatar URL"
    }
  }
}
```

#### 2. Parse by Video ID

**Endpoint:** `video_id_parse_tool`

**Parameters:**

| Parameter | Type   | Required | Description                               |
|-----------|--------|----------|-------------------------------------------|
| source    | string | Yes      | Video source, e.g., douyin, kuaishou, etc.|
| video_id  | string | Yes      | Video ID                                  |

**Response Example:** Same as above

#### 3. Video Content Text Extraction

**Endpoint:** `share_text_parse_tool`

**Parameters:**

| Parameter    | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| share_link   | string | Yes      | Douyin share link or text containing the link    |
| api_base_url | string | No       | API base URL, defaults to SiliconFlow            |
| model        | string | No       | Speech recognition model, defaults to SenseVoiceSmall |

> For SSE and Streamable HTTP modes, just include the apikey in the request parameters: http://127.0.0.1:8637/sse?apikey=xxxxxx
> The LLM used is SiliconFlow, get your apikey at: https://cloud.siliconflow.cn/i/tbvUltCF

**Response Example:**

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "video_url": "https://xxx.com/xxx.mp4",
    "cover_url": "https://xxx.com/cover.jpg",
    "title": "Video Title",
    "author": {
      "uid": "User ID",
      "name": "Username",
      "avatar": "Avatar URL"
    }
  },
  "text_content": "Transcribed speech content from the video"
}
```

## Dependencies

Main dependencies include:

- fastmcp: MCP service framework
- httpx: Asynchronous HTTP client
- ffmpeg-python: Video processing
- lxml & parsel: HTML parsing
- fake-useragent: Browser request simulation
- pydantic: Data validation

## Docker Deployment

The project provides two Dockerfiles:
- `Dockerfile.base`: Builds base image with Python environment and FFmpeg
- `Dockerfile.mcp`: Builds MCP service image

Quick deployment scripts:
```bash
# Windows
.\script\deployBase.bat
.\script\deployMcp.bat

# Linux/macOS
bash script/deployBase.sh
bash script/deployMcp.sh
```

Run container with SSE mode:
```bash
docker run -d -p 8637:8637 registry.cn-hangzhou.aliyuncs.com/yby6/yby6_video_mcp_server:1.0.0
```

## Contributions and Feedback

Issues and PRs are welcome to improve the project!

- Project URL: https://github.com/yangbuyiya/yby6-crawling-short-video-mcp
- Author Email: yangbuyiya@duck.com

---

This project is built upon the shoulders of giants. Thanks to:

- [parse-video-py](https://github.com/wujunwei928/parse-video-py)
- [fastmcp](https://github.com/jlowin/fastmcp)

# ⚠️ Disclaimer

1. This project is an open-source tool for learning and research purposes only. Users assume all risks, losses, or legal liabilities arising from the use of this project. The author and contributors bear no direct or indirect responsibility.
2. The functionality and code of this project are implemented based on existing technologies. The author does not guarantee its complete correctness, flawlessness, or continuous availability. The author is not responsible for any consequences resulting from project defects or unavailability.
3. Third-party libraries, plugins, or services used by this project follow their original agreements. Users should consult and comply with relevant agreements. Users are responsible for any liability arising from violations of third-party agreements.
4. Users should ensure their usage is legal and compliant, and should not use this project for any illegal, non-compliant activities, or activities that infringe on others' rights. Users bear all consequences arising from illegal or non-compliant use.
5. It is strictly prohibited to use this project for purposes such as intellectual property infringement, dissemination of illegal information, commercial cracking, or data scraping. The author firmly opposes and does not support any illegal use.
6. When processing data, users should ensure compliance with relevant laws and regulations (such as data compliance and privacy protection). Users are responsible for any liability arising from non-compliant operations.
7. The author and contributors are not related to specific user behaviors and bear no joint liability. Secondary development, modification, distribution, and other behaviors based on this project are unrelated to the author, and the relevant responsibilities are borne by the actors themselves.
8. This project does not grant any patent licenses. Users bear the risks arising from patent disputes or infringements. Without written authorization from the author, it is prohibited to use this project for commercial promotion, re-authorization, or other commercial purposes.
9. The author reserves the right to terminate services to non-compliant users at any time and require them to delete relevant code and data.
10. The author reserves the right to update this disclaimer at any time. Continued use is deemed acceptance of the latest terms. If you do not agree with this statement, please stop using this project immediately. 