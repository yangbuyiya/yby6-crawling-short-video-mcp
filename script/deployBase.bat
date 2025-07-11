@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 设置颜色代码
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "MAGENTA=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

:: 打印标题
echo.
echo %BLUE%╔════════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║%RESET% %CYAN%              Docker 部署工具 v1.0.0              %BLUE%║%RESET%
echo %BLUE%╚════════════════════════════════════════════════════════════╝%RESET%
echo.

:: ==================== 配置变量区域 ====================
:: 切换到项目根目录
cd /d "%~dp0.."
echo %WHITE%[信息]%RESET% %CYAN%切换到项目根目录: %CD%%RESET%

:: 设置代理
set http_proxy=http://127.0.0.1:7890
set https_proxy=http://127.0.0.1:7890

:: Docker镜像相关配置
set DOCKER_IMAGE_NAME=yby6/ffmpeg-python-base
set DOCKER_IMAGE_TAG=1.0.0
set DOCKER_PLATFORM=linux/amd64
set DOCKERFILE_PATH=Dockerfile.base


:: 阿里云配置
set ALIYUN_REGISTRY=registry.cn-hangzhou.aliyuncs.com
set NAMESPACE=yby6
set IMAGE_NAME=ffmpeg-python-base
set IMAGE_TAG=1.0.0

:: Docker构建参数
set BUILD_ARGS=--platform %DOCKER_PLATFORM% --load --progress plain

:: ==================== 执行区域 ====================
:: 检查 Docker 环境
echo %WHITE%[1/6]%RESET% %YELLOW%检查 Docker 环境...%RESET%
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%  ✗ Docker 未安装或未添加到环境变量中%RESET%
    echo %RED%  请先安装 Docker 并确保添加到环境变量中%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ Docker 环境检查通过%RESET%
echo.

:: 检查 Docker 服务
echo %WHITE%[2/6]%RESET% %YELLOW%检查 Docker 服务...%RESET%
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED%  ✗ Docker 服务未运行，请启动 Docker Desktop%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ Docker 服务检查通过%RESET%
echo.

:: 检查配置文件
echo %WHITE%[3/6]%RESET% %YELLOW%检查配置文件...%RESET%
if not exist "%~dp0.local-config" (
    echo %RED%  ✗ 配置文件不存在%RESET%
    echo %YELLOW%  请创建 script/.local-config 文件并填写以下内容：%RESET%
    echo %WHITE%  ALIYUN_USERNAME=你的阿里云账号%RESET%
    echo %WHITE%  ALIYUN_PASSWORD=你的阿里云密码%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ 配置文件检查通过%RESET%
echo.

:: 读取认证信息
echo %WHITE%[4/6]%RESET% %YELLOW%读取认证信息...%RESET%
for /f "tokens=1,2 delims==" %%a in (%~dp0.local-config) do (
    if "%%a"=="ALIYUN_USERNAME" set ALIYUN_USERNAME=%%b
    if "%%a"=="ALIYUN_PASSWORD" set ALIYUN_PASSWORD=%%b
)

if "%ALIYUN_USERNAME%"=="" (
    echo %RED%  ✗ ALIYUN_USERNAME 未设置%RESET%
    pause
    exit /b 1
)
if "%ALIYUN_PASSWORD%"=="" (
    echo %RED%  ✗ ALIYUN_PASSWORD 未设置%RESET%
    pause
    exit /b 1
)

:: 移除引号
set ALIYUN_USERNAME=%ALIYUN_USERNAME:"=%
set ALIYUN_PASSWORD=%ALIYUN_PASSWORD:"=%
echo %GREEN%  ✓ 认证信息读取成功%RESET%
echo.

:: 构建 Docker 镜像
echo %WHITE%[5/6]%RESET% %YELLOW%开始构建 Docker 镜像...%RESET%
echo %WHITE%  镜像名称: %RESET%%CYAN%%DOCKER_IMAGE_NAME%:%DOCKER_IMAGE_TAG%%RESET%
echo %WHITE%  构建平台: %RESET%%CYAN%%DOCKER_PLATFORM%%RESET%

if not exist "%DOCKERFILE_PATH%" (
    echo %RED%  ✗ Dockerfile不存在: %DOCKERFILE_PATH%%RESET%
    echo %RED%  当前目录: %CD%%RESET%
    pause
    exit /b 1
)

docker buildx build -f "%DOCKERFILE_PATH%" %BUILD_ARGS% -t %DOCKER_IMAGE_NAME%:%DOCKER_IMAGE_TAG% .
if %errorlevel% neq 0 (
    echo %RED%  ✗ Docker构建失败！错误代码: %errorlevel%%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ 构建完成%RESET%
echo.

:: 推送 Docker 镜像到阿里云
echo %WHITE%[6/6]%RESET% %YELLOW%推送 Docker 镜像到阿里云...%RESET%

:: 登录到阿里云容器镜像服务
echo %WHITE%  登录阿里云容器镜像服务...%RESET%
docker login --username="%ALIYUN_USERNAME%" --password="%ALIYUN_PASSWORD%" %ALIYUN_REGISTRY% >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%  ✗ 登录失败%RESET%
    echo %RED%  请检查用户名和密码是否正确%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ 登录成功%RESET%

:: 为 Docker 镜像打标签
echo %WHITE%  为 Docker 镜像打标签...%RESET%
docker tag %NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG% %ALIYUN_REGISTRY%/%NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG% >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%  ✗ 打标签失败%RESET%
    echo %RED%  请检查本地镜像是否存在：%RESET%
    echo %WHITE%  docker images ^| findstr %IMAGE_NAME%%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ 标签设置成功%RESET%

:: 推送镜像
echo %WHITE%  推送 Docker 镜像...%RESET%
docker push %ALIYUN_REGISTRY%/%NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG%
if %errorlevel% neq 0 (
    echo %RED%  ✗ 推送失败%RESET%
    echo %RED%  请检查权限和网络连接%RESET%
    pause
    exit /b 1
)
echo %GREEN%  ✓ 推送完成%RESET%

:: 登出阿里云容器镜像服务
echo %WHITE%  登出阿里云容器镜像服务...%RESET%
docker logout %ALIYUN_REGISTRY% >nul 2>&1
echo %GREEN%  ✓ 已安全登出%RESET%
echo.

:: 打印完成信息
echo %GREEN%╔════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║%RESET% %CYAN%                   部署完成！                    %GREEN%║%RESET%
echo %GREEN%╚════════════════════════════════════════════════════════════╝%RESET%
echo.

:: 显示镜像信息
echo %MAGENTA%镜像信息：%RESET%
echo %WHITE%  仓库地址：%RESET%%CYAN%%ALIYUN_REGISTRY%/%NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG%%RESET%
echo %WHITE%  检出命令：%RESET%%CYAN%docker pull %ALIYUN_REGISTRY%/%NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG%%RESET%
echo %WHITE%  标签设置：%RESET%%CYAN%docker tag %ALIYUN_REGISTRY%/%NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG% %NAMESPACE%/%IMAGE_NAME%:%IMAGE_TAG%%RESET%
echo.

pause 