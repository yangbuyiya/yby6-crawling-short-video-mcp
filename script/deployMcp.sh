#!/bin/bash

# 设置编码为 UTF-8
export LANG=UTF-8

# 设置颜色代码
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BLUE='\033[94m'
MAGENTA='\033[95m'
CYAN='\033[96m'
WHITE='\033[97m'
RESET='\033[0m'

# 打印标题
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║${RESET} ${CYAN}              Docker 部署工具 v1.0.0              ${BLUE}║${RESET}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ==================== 配置变量区域 ====================
# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo -e "${WHITE}[信息]${RESET} ${CYAN}切换到项目根目录: $(pwd)${RESET}"

# 设置代理
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890

# Docker镜像相关配置
DOCKER_IMAGE_NAME="yby6/yby6_video_mcp_server"
DOCKER_IMAGE_TAG="1.0.2"
DOCKER_PLATFORM="linux/amd64,linux/arm64"
DOCKERFILE_PATH="Dockerfile.mcp"

# 阿里云配置
ALIYUN_REGISTRY="registry.cn-hangzhou.aliyuncs.com"
NAMESPACE="yby6"
IMAGE_NAME="yby6_video_mcp_server"
IMAGE_TAG="1.0.2"

# Docker构建参数
BUILD_ARGS="--platform $DOCKER_PLATFORM --load --progress plain"

# ==================== 执行区域 ====================
# 检查 Docker 环境
echo -e "${WHITE}[1/6]${RESET} ${YELLOW}检查 Docker 环境...${RESET}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}  ✗ Docker 未安装或未添加到环境变量中${RESET}"
    echo -e "${RED}  请先安装 Docker 并确保添加到环境变量中${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ Docker 环境检查通过${RESET}"
echo ""

# 检查 Docker 服务
echo -e "${WHITE}[2/6]${RESET} ${YELLOW}检查 Docker 服务...${RESET}"
if ! docker info &> /dev/null; then
    echo -e "${RED}  ✗ Docker 服务未运行，请启动 Docker${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ Docker 服务检查通过${RESET}"
echo ""

# 检查配置文件
echo -e "${WHITE}[3/6]${RESET} ${YELLOW}检查配置文件...${RESET}"
CONFIG_FILE="$SCRIPT_DIR/.local-config"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}  ✗ 配置文件不存在${RESET}"
    echo -e "${YELLOW}  请创建 script/.local-config 文件并填写以下内容：${RESET}"
    echo -e "${WHITE}  ALIYUN_USERNAME=你的阿里云账号${RESET}"
    echo -e "${WHITE}  ALIYUN_PASSWORD=你的阿里云密码${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ 配置文件检查通过${RESET}"
echo ""

# 读取认证信息
echo -e "${WHITE}[4/6]${RESET} ${YELLOW}读取认证信息...${RESET}"

# 读取配置文件
while IFS='=' read -r key value; do
    # 跳过注释和空行
    [[ $key =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    
    # 移除前后空格和引号
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs | sed 's/^["'\'']*//;s/["'\'']*$//')
    
    case "$key" in
        "ALIYUN_USERNAME")
            ALIYUN_USERNAME="$value"
            ;;
        "ALIYUN_PASSWORD")
            ALIYUN_PASSWORD="$value"
            ;;
    esac
done < "$CONFIG_FILE"

if [ -z "$ALIYUN_USERNAME" ]; then
    echo -e "${RED}  ✗ ALIYUN_USERNAME 未设置${RESET}"
    exit 1
fi
if [ -z "$ALIYUN_PASSWORD" ]; then
    echo -e "${RED}  ✗ ALIYUN_PASSWORD 未设置${RESET}"
    exit 1
fi

echo -e "${GREEN}  ✓ 认证信息读取成功${RESET}"
echo ""

# 构建 Docker 镜像
echo -e "${WHITE}[5/6]${RESET} ${YELLOW}开始构建 Docker 镜像...${RESET}"
echo -e "${WHITE}  镜像名称: ${RESET}${CYAN}$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG${RESET}"
echo -e "${WHITE}  构建平台: ${RESET}${CYAN}$DOCKER_PLATFORM${RESET}"

if [ ! -f "$DOCKERFILE_PATH" ]; then
    echo -e "${RED}  ✗ Dockerfile不存在: $DOCKERFILE_PATH${RESET}"
    echo -e "${RED}  当前目录: $(pwd)${RESET}"
    exit 1
fi

if ! docker buildx build -f "$DOCKERFILE_PATH" $BUILD_ARGS -t "$DOCKER_IMAGE_NAME:$DOCKER_IMAGE_TAG" .; then
    echo -e "${RED}  ✗ Docker构建失败！错误代码: $?${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ 构建完成${RESET}"
echo ""

# 推送 Docker 镜像到阿里云
echo -e "${WHITE}[6/6]${RESET} ${YELLOW}推送 Docker 镜像到阿里云...${RESET}"

# 登录到阿里云容器镜像服务
echo -e "${WHITE}  登录阿里云容器镜像服务...${RESET}"
if ! echo "$ALIYUN_PASSWORD" | docker login --username="$ALIYUN_USERNAME" --password-stdin "$ALIYUN_REGISTRY" &> /dev/null; then
    echo -e "${RED}  ✗ 登录失败${RESET}"
    echo -e "${RED}  请检查用户名和密码是否正确${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ 登录成功${RESET}"

# 为 Docker 镜像打标签
echo -e "${WHITE}  为 Docker 镜像打标签...${RESET}"
if ! docker tag "$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG" "$ALIYUN_REGISTRY/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG" &> /dev/null; then
    echo -e "${RED}  ✗ 打标签失败${RESET}"
    echo -e "${RED}  请检查本地镜像是否存在：${RESET}"
    echo -e "${WHITE}  docker images | grep $IMAGE_NAME${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ 标签设置成功${RESET}"

# 推送镜像
echo -e "${WHITE}  推送 Docker 镜像...${RESET}"
if ! docker push "$ALIYUN_REGISTRY/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG"; then
    echo -e "${RED}  ✗ 推送失败${RESET}"
    echo -e "${RED}  请检查权限和网络连接${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ 推送完成${RESET}"

# 登出阿里云容器镜像服务
echo -e "${WHITE}  登出阿里云容器镜像服务...${RESET}"
docker logout "$ALIYUN_REGISTRY" &> /dev/null
echo -e "${GREEN}  ✓ 已安全登出${RESET}"
echo ""

# 打印完成信息
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║${RESET} ${CYAN}                   部署完成！                    ${GREEN}║${RESET}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# 显示镜像信息
echo -e "${MAGENTA}镜像信息：${RESET}"
echo -e "${WHITE}  仓库地址：${RESET}${CYAN}$ALIYUN_REGISTRY/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG${RESET}"
echo -e "${WHITE}  检出命令：${RESET}${CYAN}docker pull $ALIYUN_REGISTRY/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG${RESET}"
echo -e "${WHITE}  标签设置：${RESET}${CYAN}docker tag $ALIYUN_REGISTRY/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG $NAMESPACE/$IMAGE_NAME:$IMAGE_TAG${RESET}"
echo ""

echo "按回车键继续..."
read -r 