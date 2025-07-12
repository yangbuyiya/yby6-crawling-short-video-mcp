# 全网短视频去水印链接提取 MCP服务

## 项目简介

本项目是一个基于 FastMCP 的全网短视频去水印解析服务，支持多平台视频分享链接的解析，自动提取视频真实地址及相关信息。  
适用于需要批量解析、去水印、采集短视频的场景。本项目还支持视频内容文本提取功能，可以通过语音识别将视频内容转为文本。

[![PyPI version](https://img.shields.io/pypi/v/yby6-video-mcp-server.svg)](https://pypi.org/project/yby6-video-mcp-server/)

## 主要特性

- 支持20+种短视频平台（抖音、快手、小红书、微博、西瓜视频等）
- 一键解析视频分享链接，获取无水印视频地址
- 支持多种传输方式（stdio、SSE、HTTP）
- 支持视频内容文本提取功能（需要FFmpeg和API Key、默认使用硅基流动：https://cloud.siliconflow.cn/i/tbvUltCF ）
- 支持Docker容器化部署
- 代码结构清晰，易于扩展


## 演示
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/8501c118-4ab2-471e-b4f6-683ac58902f0" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/c649c0e0-309d-4cf7-9c6b-5581f9ae4383" />


## 支持平台

目前支持以下短视频平台的解析：

- 抖音（DouYin）
- 快手（KuaiShou）
- 小红书（RedBook）
- 微博（WeiBo）
- 皮皮虾（PiPiXia）
- 微视（WeiShi）
- 绿洲（LvZhou）
- 最右（ZuiYou）
- 度小视/全民小视频（QuanMin）
- 西瓜视频（XiGua）
- 梨视频（LiShiPin）
- 皮皮搞笑（PiPiGaoXiao）
- 虎牙（HuYa）
- AcFun（AcFun）
- 逗拍（DouPai）
- 美拍（MeiPai）
- 全民K歌（QuanMinKGe）
- 六间房（SixRoom）
- 新片场（XinPianChang）
- 好看视频（HaoKan）


## 目录结构

```
crawling-short-video-mcp/
├── yby6_video_mcp_server/
│   ├── server.py                # 主服务入口
│   ├── functionality/           # 各平台解析功能模块
│   │   ├── base.py             # 基础类和枚举定义
│   │   ├── douyin.py           # 抖音解析实现
│   │   ├── kuaishou.py         # 快手解析实现
│   │   ├── ...                 # 其他平台实现
│   │   └── video_processor.py  # 视频处理和文本提取
│   └── utils/                   # 工具函数
├── Dockerfile.base              # 基础镜像构建文件
├── Dockerfile.mcp               # MCP服务镜像构建文件
├── requirements.txt             # 依赖包列表
├── pyproject.toml              # 项目配置和元数据
└── README.md                    # 项目说明
```

## 安装方法

### 前置依赖

#### FFmpeg 安装（视频文本内容提取必需）

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
1. 下载 FFmpeg: https://ffmpeg.org/download.html#build-windows
2. 解压到指定目录，如 `C:\ffmpeg`
3. 添加到系统环境变量 PATH: `C:\ffmpeg\bin`
4. 重启命令行或系统以使环境变量生效

验证安装:
```bash
ffmpeg -version
```

### 方法一：pypi 使用 pip 安装 (可能版本落后,没有及时更新)

```bash
# 安装最新版本
pip install yby6-video-mcp-server

# 或指定版本安装
pip install yby6-video-mcp-server==1.0.0
```

安装完成后，可以通过以下命令验证安装：

```bash
yby6_video_mcp_server --version
```

### 方法二：从源码安装 (推荐 最新版本)

1. 克隆本项目

   ```bash
   git clone https://github.com/yangbuyiya/yby6-crawling-short-video-mcp.git
   cd yby6-crawling-short-video-mcp
   ```

2. 安装依赖

   推荐使用 Python 3.10+，并建议使用虚拟环境：
   
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

### 方法三：使用 Docker 部署

本项目提供了 Docker 支持，可以通过以下命令快速部署：

1. 构建基础镜像（包含 FFmpeg 和 Python 环境）

   ```bash
   docker build -t ffmpeg-python-base:1.0.0 -f Dockerfile.base .
   ```

2. 构建 MCP 服务镜像

   ```bash
   docker build -t yby6-video-mcp:latest -f Dockerfile.mcp .
   ```

3. 运行容器

   ```bash
   docker run -d -p 8637:8637 yby6-video-mcp:latest
   ```

## 使用方法

### stdio MCP启动服务

```json
//  pypi 拉取运行 
"yby6_video_mcp_server": {
  "command": "uv",
  "args": ["yby6_video_mcp_server"],
  "env": {
    "API_KEY": "sk-xcazqbgbnoagddpyaorhqhioxazvqdtednppksiqaotjsboe"
  }
},

// 从源码运行
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

### SSE or HTTP MCP服务地址

- 支持请求头配置apikey
- 支持请求参数配置apikey

```json

"yby6_video_mcp_server": {
  "url": "http://127.0.0.1:8637/sse?apikey=xxxxxx",
}

```

### 启动服务

```bash
# 使用pip安装后
yby6_video_mcp_server --transport http --host 0.0.0.0 --port 8637

# 或从源码运行
python -m yby6_video_mcp_server.server --transport http --host 0.0.0.0 --port 8637
```

参数说明：
- `--transport` 传输方式，可选：`stdio`、`sse`、`http`（推荐 http）
- `--host` 主机地址，默认 `0.0.0.0`
- `--port` 端口号，默认 `8000`
- `--path` 自定义MCP请求路径（可选）

### API 接口说明

#### 1. 解析视频分享链接

**接口名称:** `share_url_parse_tool`

**请求参数:**

| 参数名 | 类型   | 必填 | 说明             |
|--------|--------|------|------------------|
| url    | string | 是   | 视频分享链接     |

**返回示例:**

```json
{
  "code": 200,
  "msg": "解析成功",
  "data": {
    "video_url": "https://xxx.com/xxx.mp4",
    "cover_url": "https://xxx.com/cover.jpg",
    "title": "视频标题",
    "music_url": "https://xxx.com/music.mp3",
    "images": [],
    "author": {
      "uid": "用户ID",
      "name": "用户名",
      "avatar": "头像URL"
    }
  }
}
```

#### 2. 根据视频ID解析

**接口名称:** `video_id_parse_tool`

**请求参数:**

| 参数名    | 类型   | 必填 | 说明                                 |
|-----------|--------|------|--------------------------------------|
| source    | string | 是   | 视频来源，如 douyin、kuaishou 等     |
| video_id  | string | 是   | 视频ID                               |

**返回示例:** 同上

#### 3. 视频内容文本提取

**接口名称:** `share_text_parse_tool`

**请求参数:**

| 参数名       | 类型   | 必填 | 说明                                       |
|--------------|--------|------|------------------------------------------|
| share_link   | string | 是   | 抖音分享链接或包含链接的文本                |
| api_base_url | string | 否   | API基础URL，默认使用SiliconFlow           |
| model        | string | 否   | 语音识别模型，默认使用SenseVoiceSmall     |

> 链接 sse、Streamable HTTP模式的时候只需要将 apikey 带入请求参数当中： http://127.0.0.1:8637/sse?apikey=xxxxxx
> 使用的大模型是硅基流动前往获取apikey即可：https://cloud.siliconflow.cn/i/tbvUltCF

**返回示例:**

```json
{
  "code": 200,
  "msg": "解析成功",
  "data": {
    "video_url": "https://xxx.com/xxx.mp4",
    "cover_url": "https://xxx.com/cover.jpg",
    "title": "视频标题",
    "author": {
      "uid": "用户ID",
      "name": "用户名",
      "avatar": "头像URL"
    }
  },
  "text_content": "视频中的语音文本内容"
}
```

## 依赖说明

主要依赖包括：

- fastmcp: MCP服务框架
- httpx: 异步HTTP客户端
- ffmpeg-python: 视频处理
- lxml & parsel: HTML解析
- fake-useragent: 模拟浏览器请求
- pydantic: 数据验证

## Docker 部署

项目提供了两个Dockerfile:
- `Dockerfile.base`: 构建基础镜像，包含Python环境和FFmpeg
- `Dockerfile.mcp`: 构建MCP服务镜像

使用脚本快速部署:
```bash
# Windows
.\script\deployBase.bat
.\script\deployMcp.bat

# Linux/macOS
bash script/deployBase.sh
bash script/deployMcp.sh
```

运行容器
```bash
docker run -d -p 8637:8637 -e yby6-video-mcp:latest
```

## 贡献与反馈

欢迎提交 issue 或 PR 参与项目改进！

- 项目地址: https://github.com/yangbuyiya/yby6-crawling-short-video-mcp
- 作者邮箱: yangbuyiya@duck.com

---

本项目站在巨人的肩膀上二次开发，感谢以下项目：

- [parse-video-py](https://github.com/wujunwei928/parse-video-py)
- [fastmcp](https://github.com/jlowin/fastmcp)
