#!/bin/bash

# 智能服务器优化工具启动脚本

echo "========================================"
echo "           智能服务器优化工具"
echo "========================================"
echo

# 获取脚本所在的目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# 检测系统类型
echo "🔍 检测系统环境..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    echo "📋 检测到系统: $OS $VER"
else
    echo "⚠️  无法检测操作系统类型，继续执行..."
fi

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  警告: 建议以root权限运行此脚本以获得最佳效果"
    echo "某些优化可能需要root权限"
    echo "请使用: sudo $0"
    echo
    read -p "是否继续运行? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查并安装Python3
echo "🔧 检查Python3..."
if ! command -v python3 &> /dev/null; then
    echo "📦 安装Python3..."
    if command -v apt &> /dev/null; then
        # Debian/Ubuntu系统
        echo "使用apt包管理器安装Python3..."
        apt update
        apt install -y python3 python3-pip curl
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL系统
        echo "使用yum包管理器安装Python3..."
        yum install -y python3 python3-pip curl
    elif command -v dnf &> /dev/null; then
        # Fedora系统
        echo "使用dnf包管理器安装Python3..."
        dnf install -y python3 python3-pip curl
    else
        echo "❌ 无法自动安装Python3，请手动安装后重试"
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        exit 1
    fi
else
    echo "✅ Python3已安装: $(python3 --version)"
fi

# 检查并安装pip3
echo "🔧 检查pip3..."
if ! command -v pip3 &> /dev/null; then
    echo "📦 安装pip3..."
    if command -v apt &> /dev/null; then
        apt install -y python3-pip
    elif command -v yum &> /dev/null; then
        yum install -y python3-pip
    elif command -v dnf &> /dev/null; then
        dnf install -y python3-pip
    else
        echo "❌ 无法自动安装pip3"
        exit 1
    fi
else
    echo "✅ pip3已安装: $(pip3 --version)"
fi

# 检查并安装requests模块
echo "🔧 检查Python依赖..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 安装requests模块..."
    
    # 尝试使用pip3安装
    if pip3 install requests; then
        echo "✅ requests模块安装成功"
    else
        echo "⚠️  pip3安装失败，尝试使用系统包管理器..."
        
        # 尝试使用系统包管理器安装
        if command -v apt &> /dev/null; then
            apt install -y python3-requests
        elif command -v yum &> /dev/null; then
            yum install -y python3-requests
        elif command -v dnf &> /dev/null; then
            dnf install -y python3-requests
        else
            echo "❌ 无法安装requests模块"
            echo "请手动安装: pip3 install requests"
            exit 1
        fi
    fi
else
    echo "✅ requests模块已安装"
fi

# 检查并安装dig和nslookup
echo "🔧 检查网络工具..."
if ! command -v dig &> /dev/null || ! command -v nslookup &> /dev/null; then
    echo "📦 安装dig和nslookup..."
    if command -v apt &> /dev/null; then
        apt install -y dnsutils
    elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
        yum install -y bind-utils
    else
        echo "❌ 无法自动安装dig和nslookup，请手动安装"
        exit 1
    fi
else
    echo "✅ dig和nslookup已安装"
fi


# 最终验证
echo "🔍 最终验证..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ requests模块验证失败"
    exit 1
fi
if ! command -v dig &> /dev/null || ! command -v nslookup &> /dev/null; then
    echo "❌ dig或nslookup验证失败"
    exit 1
fi

echo "✅ 所有依赖检查完成"

# 运行优化脚本
echo
echo "🚀 开始执行优化..."
python3 "$SCRIPT_DIR/server_optimizer.py"

echo
echo "优化完成！"