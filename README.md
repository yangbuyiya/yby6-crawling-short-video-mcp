# 全网短视频去水印链接提取 MCP服务

## 项目简介

本项目是一个基于 FastMCP 的全网短视频去水印解析服务，支持多平台视频分享链接的解析，自动提取视频真实地址及相关信息。  
适用于需要批量解析、去水印、采集短视频的场景。

本项目基于 parse-video-py 项目二次开发，感谢作者的贡献。

## 主要特性

- 支持多种短视频平台（如抖音、快手、微博、皮皮虾等）
- 一键解析视频分享链接，获取无水印视频地址
- 支持多种传输方式（stdio、SSE、HTTP）
- 代码结构清晰，易于扩展

## 目录结构

```
crawling-short-video-mcp/
├── video_mcp_server/
│   ├── server.py                # 主服务入口
│   ├── functionality/           # 各平台解析功能模块
│   └── utils/                   # 工具函数
├── requirements.txt             # 依赖包列表
└── README.md                    # 项目说明
```

## 安装方法

1. 克隆本项目

   ```bash
   git clone <your-repo-url>
   cd crawling-short-video-mcp
   ```

2. 安装依赖

   推荐使用 Python 3.10+，并建议使用虚拟环境：

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 使用方法

### 启动服务

在项目根目录下，使用如下命令启动服务：

```bash
python3 -m video_mcp_server.server --transport http --host 0.0.0.0 --port 8000
```

- `--transport` 传输方式，可选：`stdio`、`sse`、`http`（推荐 http）
- `--host` 主机地址，默认 `0.0.0.0`
- `--port` 端口号，默认 `8000`
- `--path` 自定义MCP请求路径（可选）

### 示例：解析视频链接

你可以通过 HTTP 接口或其他方式调用 `share_url_parse_tool` 工具，传入短视频分享链接，返回解析结果。

**返回示例：**

```json
{
  "code": 200,
  "msg": "解析成功",
  "data": {
    "video_url": "https://xxx.com/xxx.mp4",
    "cover_url": "...",
    "author": "..."
  }
}
```

## 功能模块说明

- `video_mcp_server/functionality/` 目录下包含各大短视频平台的解析实现，便于扩展和维护。
- 工具函数统一放在 `video_mcp_server/utils/`。

## 依赖说明

详见 `requirements.txt`，主要依赖包括：

- fastmcp
- httpx
- ffmpeg-python
- lxml
- parsel
- 以及常用的解析、工具库

## 贡献与反馈

欢迎提交 issue 或 PR 参与项目改进！

---

如需更详细的接口文档或二次开发指导，请补充说明。

本项目站在巨人的肩膀上，感谢以下项目：

- [parse-video-py](https://github.com/wujunwei928/parse-video-py)
- [fastmcp](https://github.com/jlowin/fastmcp)