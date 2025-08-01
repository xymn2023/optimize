# Linux服务器优化工具

一个专为Linux系统设计的智能服务器优化脚本，能够自动检测服务器IP地址，判断地理位置（国内/国外），并应用相应的优化策略。
主要解决无法访问Github、Gitee、Docker的问题。

## 🌟 主要功能

### 自动检测功能
- 🔍 **IP地址检测**: 自动获取服务器公网IP地址
- 🌍 **地理位置检测**: 智能判断服务器是否位于中国大陆
- 💻 **系统检测**: 自动识别Linux操作系统

### 优化功能
- 🌐 **DNS优化**: 根据地理位置配置最优DNS服务器
- 🐙 **GitHub优化**: 配置GitHub访问加速
- 🐉 **Gitee优化**: 解决Gitee访问问题，配置Git使用Gitee作为备用源
- 🐳 **Docker优化**: 配置Docker镜像源加速
- ⚡ **网络优化**: 应用TCP/IP网络参数优化

## 📋 系统要求

- Linux操作系统
- Python 3.7+
- root权限（推荐）
- 网络连接

## 🚀 快速开始

## 推荐 


一键运行


```
git clone https://github.com/xymn2023/optimize.git && cd optimize && sudo chmod +x run_optimizer.sh && sudo ./run_optimizer.sh
```

## 使用说明


1. **下载文件**
   ```bash
   # 确保所有文件在同一目录下
   server_optimizer.py
   requirements.txt
   run_optimizer.sh
   ```

2. **添加执行权限并运行**
   ```bash
   chmod +x run_optimizer.sh
   sudo ./run_optimizer.sh
   ```

**就这么简单！** 脚本会自动：
- 🔍 检测系统环境
- 📦 安装Python3和pip3（如果需要）
- 🔧 安装所有必要的依赖包
- 🚀 执行服务器优化
- ✅ 提供验证选项

## 🔧 优化详情

### 国内服务器优化策略

#### DNS优化
- 阿里DNS: `223.5.5.5`
- 腾讯DNS: `119.29.29.29`
- 114DNS: `114.114.114.114`
- Google DNS备用: `8.8.8.8`

#### GitHub优化
- 配置GitHub相关域名的hosts文件
- 使用优化的IP地址访问GitHub服务

#### Gitee优化
- 动态检测Gitee的IP地址
- 配置Gitee相关域名的hosts文件
- 设置Git使用Gitee作为GitHub的备用源
- 智能容错：如果域名访问失败，自动尝试IP地址访问
- 重试机制：验证时最多重试10次，每次间隔1秒
- 故障排除：连接失败后自动诊断并提供7种备选方案
- 自动修复：尝试刷新DNS缓存和更新IP地址

#### Docker优化
- 中科大镜像源: `https://docker.mirrors.ustc.edu.cn`
- 网易镜像源: `https://hub-mirror.c.163.com`
- 百度云镜像源: `https://mirror.baidubce.com`
- Docker中国镜像源: `https://registry.docker-cn.com`

#### 网络优化
- TCP/IP参数优化
- BBR拥塞控制算法
- 连接池优化

### 海外服务器优化策略

#### DNS优化
- Google DNS: `8.8.8.8`, `8.8.4.4`
- Cloudflare DNS: `1.1.1.1`, `1.0.0.1`

#### GitHub优化
- 使用GitHub官方IP地址
- 配置hosts文件优化访问

#### Gitee优化
- 配置Gitee相关域名的hosts文件
- 确保Gitee访问正常

#### Docker优化
- Docker官方镜像源: `https://registry-1.docker.io`
- Docker Hub: `https://docker.io`

#### 网络优化
- TCP/IP参数优化
- BBR拥塞控制算法
- 连接池优化

## 📊 优化报告

脚本运行完成后会生成详细的优化报告，包括：

- 🌍 服务器位置信息
- 🏳️ 国家/地区代码
- 🏙️ 城市信息
- 🌐 ISP提供商
- 💻 操作系统信息
- ✅ 已应用的优化策略列表

## 🔍 验证优化效果

脚本完成后会提供验证选项，可以测试：

1. **DNS解析测试**: 验证DNS服务器配置
2. **网站访问测试**: 验证GitHub和Gitee访问
3. **Docker配置检查**: 验证镜像源设置
4. **网络参数检查**: 验证TCP/IP优化参数

也可以手动验证：
```bash
# 测试DNS解析
nslookup github.com
nslookup gitee.com

# 测试网站访问
curl -I https://github.com
curl -I https://gitee.com

# 检查Docker配置
docker info | grep Registry

# 检查网络参数
sysctl net.ipv4.tcp_congestion_control
```

## ⏰ 优化生效时间

### 🚀 立即生效的功能
- **hosts文件修改**: 立即生效，无需重启
- **Git配置**: 立即生效
- **DNS优化**: 重启服务后立即生效

### 🔄 需要重启服务生效的功能
- **Docker优化**: 需要重启Docker服务
- **网络参数优化**: 部分参数需要重启网络服务

### 💾 持久性说明

#### ✅ 永久生效的配置
- **hosts文件**: 永久生效，重启后仍然有效
- **Docker配置**: 永久生效，重启后仍然有效
- **网络参数**: 永久生效，重启后仍然有效
- **Git配置**: 永久生效，重启后仍然有效
- **DNS配置**: 通过网络管理器配置，确保永久生效

#### 🔒 安全备份
脚本会自动备份重要配置文件：
- `/etc/hosts.backup.*`
- `/etc/docker/daemon.json.backup.*`

## ⚠️ 注意事项

1. **权限要求**: 某些优化需要root权限
2. **备份文件**: 脚本会自动备份重要配置文件
3. **重启建议**: 建议优化完成后重启服务器以确保所有设置生效
4. **网络连接**: 确保服务器能够访问外网
5. **DNS持久性**: 脚本会配置网络管理器确保DNS设置不被覆盖

## 🔄 恢复设置

如果需要恢复原始设置：

```bash
# 恢复hosts文件
sudo cp /etc/hosts.backup.* /etc/hosts

# 恢复DNS设置
sudo systemctl restart systemd-resolved

# 恢复Docker配置
sudo rm /etc/docker/daemon.json
sudo systemctl restart docker

# 恢复网络参数
sudo sysctl -p
```

## 🐛 故障排除

### 常见问题

1. **无法获取IP地址**
   - 检查网络连接
   - 确认防火墙设置
   - 尝试使用VPN

2. **地理位置检测失败**
   - 检查网络连接
   - 脚本会自动按海外处理

3. **权限不足**
   - 以管理员/root权限运行
   - 检查文件权限

4. **Docker配置失败**
   - 确认Docker已安装
   - 检查Docker服务状态

### Gitee连接问题

如果Gitee连接失败，脚本会自动启动故障排除流程：

#### 🔧 自动诊断
1. **网络连接测试**：ping测试外网和DNS服务器
2. **DNS解析检查**：使用nslookup和dig检查解析（工具不可用时跳过）
3. **防火墙检查**：检查iptables和UFW规则（工具不可用时跳过）
4. **代理设置检查**：检查环境变量和系统代理
5. **服务器位置检测**：识别国内/海外服务器，提供针对性方案

#### 🔄 自动修复
1. **工具安装**：自动安装必要的DNS和网络工具
2. **DNS缓存刷新**：重启DNS服务和刷新缓存
3. **IP地址更新**：使用多种方法获取最新Gitee IP
   - 本地DNS查询（dig/nslookup/ping）
   - 在线DNS服务查询（Google DNS, Cloudflare DNS）
4. **hosts文件更新**：自动备份并更新hosts文件
5. **修复效果测试**：验证修复是否成功

#### 🎯 智能重试机制
- **重试次数**：最多重试5次
- **重试间隔**：每次重试间隔1秒
- **双重测试**：域名访问失败后自动尝试IP地址访问
- **渐进式修复**：本地方法失败后尝试在线服务

#### 💡 备选方案
如果所有自动修复方法都失败，脚本会提供7种手动解决方案：

1. **镜像站点**：使用Gitee备用域名
2. **代理配置**：设置HTTP/SOCKS5代理
3. **Git代理**：为Git配置代理服务器
4. **SSH访问**：使用SSH密钥方式访问
5. **GitHub备选**：使用GitHub作为替代
6. **手动修复**：手动更新hosts文件
7. **CDN加速**：配置CDN服务

#### 🌍 海外服务器特殊处理
- **智能识别**：自动检测服务器位置
- **针对性方案**：为海外服务器提供7种临时解决方案
- **工具兼容**：自动检测系统工具可用性，跳过不可用的检查
- **推荐方案**：优先推荐使用GitHub作为替代或配置代理

#### 🔧 工具兼容性
- **多重备选**：nslookup → dig → ping，自动选择可用工具
- **智能降级**：工具不可用时自动使用替代方法
- **安装建议**：提供针对不同系统的工具安装命令
- **容错处理**：确保在任何环境下都能正常运行

## 📝 更新日志

### v1.3.0
- 🔧 新增自动工具安装功能，自动安装dnsutils、net-tools、curl、wget
- 🌐 新增在线DNS服务查询功能，支持Google DNS、Cloudflare DNS等
- 📝 新增自动hosts文件更新功能，自动获取最新Gitee IP并更新
- 🎯 优化重试机制，将重试次数调整为5次
- 🔄 增强自动修复流程，支持渐进式修复策略
- 📋 完善故障排除文档，详细说明自动修复步骤

### v1.2.0
- 🔧 增强工具兼容性，支持缺少nslookup/dig的系统
- 🌍 完善海外服务器Gitee访问解决方案
- 🛠️ 添加工具安装建议和智能降级功能
- 📝 优化故障排除流程

### v1.1.0
- 🔄 移除Windows系统支持，专注Linux优化
- 🐉 新增Gitee访问优化功能
- 🌐 优化网络参数配置
- 📝 更新文档说明

### v1.0.0
- ✨ 初始版本发布
- 🌍 支持IP地理位置检测
- 🐙 支持GitHub优化
- 🐳 支持Docker优化
- 🌐 支持DNS和网络优化
- 💻 支持Linux系统

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如果遇到问题，请提交Issue或联系开发者。 
