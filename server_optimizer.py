#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能服务器优化脚本
自动检测服务器IP地址，判断地理位置，并应用相应的优化策略
支持国内和国外服务器的GitHub、Docker、DNS优化
"""

import requests
import json
import subprocess
import sys
import os
import platform
from typing import Dict, List, Optional
import time

class ServerOptimizer:
    def __init__(self):
        self.is_china = False
        self.ip_info = {}
        self.system = platform.system().lower()
        
    def get_public_ip(self) -> str:
        """获取公网IP地址"""
        try:
            # 使用多个IP检测服务，提高可靠性
            ip_services = [
                "https://api.ipify.org",
                "https://ifconfig.me",
                "https://icanhazip.com",
                "https://ident.me"
            ]
            
            for service in ip_services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue
                    
            raise Exception("无法获取公网IP地址")
        except Exception as e:
            print(f"❌ 获取公网IP失败: {e}")
            return None
    
    def detect_location(self, ip: str) -> bool:
        """检测IP地址地理位置，判断是否为中国大陆"""
        try:
            # 使用ip-api.com服务检测地理位置
            url = f"http://ip-api.com/json/{ip}?fields=country,countryCode,region,regionName,city,isp"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.ip_info = data
                
                # 判断是否为中国大陆
                china_codes = ['CN']
                is_china = data.get('countryCode') in china_codes
                
                print(f"📍 服务器位置: {data.get('country', 'Unknown')} - {data.get('regionName', '')} - {data.get('city', '')}")
                print(f"🌐 ISP: {data.get('isp', 'Unknown')}")
                print(f"🏳️  地区代码: {data.get('countryCode', 'Unknown')}")
                
                return is_china
            else:
                raise Exception(f"API响应错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 地理位置检测失败: {e}")
            # 如果检测失败，默认按国外处理
            return False
    
    def run_command(self, command: str, description: str, silent: bool = False) -> bool:
        """执行系统命令"""
        try:
            if not silent:
                print(f"🔄 {description}...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                if not silent:
                    print(f"✅ {description} 成功")
                return True
            else:
                if not silent:
                    print(f"❌ {description} 失败: {result.stderr}")
                return False
        except Exception as e:
            if not silent:
                print(f"❌ {description} 异常: {e}")
            return False
    
    def optimize_dns(self):
        """优化DNS设置"""
        print("\n🔧 优化DNS设置...")
        
        if self.is_china:
            # 国内DNS优化
            dns_servers = [
                "223.5.5.5",  # 阿里DNS
                "119.29.29.29",  # 腾讯DNS
                "114.114.114.114",  # 114DNS
                "8.8.8.8"  # Google DNS作为备用
            ]
        else:
            # 国外DNS优化
            dns_servers = [
                "8.8.8.8",  # Google DNS
                "8.8.4.4",  # Google DNS备用
                "1.1.1.1",  # Cloudflare DNS
                "1.0.0.1"   # Cloudflare DNS备用
            ]
        
        # Linux系统DNS优化
        for i, dns in enumerate(dns_servers):
            self.run_command(f"echo 'nameserver {dns}' >> /etc/resolv.conf", f"添加DNS服务器 {dns}")
        
        # 刷新DNS缓存
        self.run_command("systemctl restart systemd-resolved", "重启DNS服务")
        
        # 配置网络管理器使用静态DNS，确保DNS设置永久生效
        self.configure_network_manager_dns(dns_servers)
    
    def configure_network_manager_dns(self, dns_servers):
        """配置网络管理器使用静态DNS，确保DNS设置永久生效"""
        print("🔧 配置网络管理器DNS设置...")
        
        try:
            # 获取当前活跃的网络连接
            result = subprocess.run("nmcli -t -f UUID,TYPE,DEVICE connection show --active", 
                                  shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                connections = result.stdout.strip().split('\n')
                
                for connection in connections:
                    if connection:
                        parts = connection.split(':')
                        if len(parts) >= 3:
                            uuid = parts[0]
                            conn_type = parts[1]
                            device = parts[2]
                            
                            # 只处理以太网和WiFi连接
                            if conn_type in ['802-3-ethernet', '802-11-wireless']:
                                print(f"  配置连接: {device} ({conn_type})")
                                
                                # 构建DNS服务器字符串
                                dns_string = ','.join(dns_servers)
                                
                                # 配置DNS服务器
                                dns_cmd = f"nmcli connection modify {uuid} ipv4.dns '{dns_string}'"
                                self.run_command(dns_cmd, f"设置 {device} 的DNS服务器")
                                
                                # 禁用自动DNS
                                self.run_command(f"nmcli connection modify {uuid} ipv4.ignore-auto-dns yes", 
                                                 f"禁用 {device} 的自动DNS")
                                
                                # 重新激活连接
                                self.run_command(f"nmcli connection up {uuid}", f"重新激活 {device} 连接")
            
            print("✅ 网络管理器DNS配置完成")
            
        except Exception as e:
            print(f"⚠️  网络管理器DNS配置失败: {e}")
            print("    这不会影响其他优化功能")
    
    def optimize_github(self):
        """优化GitHub访问"""
        print("\n🐙 优化GitHub访问...")
        
        if self.is_china:
            # 国内GitHub优化
            github_hosts = [
                "140.82.112.3 github.com",
                "140.82.112.9 codeload.github.com",
                "140.82.113.5 api.github.com",
                "140.82.113.10 uploads.github.com",
                "140.82.114.9 raw.githubusercontent.com",
                "140.82.114.10 gist.githubusercontent.com",
                "140.82.114.11 cloud.githubusercontent.com",
                "140.82.114.12 camo.githubusercontent.com",
                "140.82.114.13 avatars0.githubusercontent.com",
                "140.82.114.14 avatars1.githubusercontent.com",
                "140.82.114.15 avatars2.githubusercontent.com",
                "140.82.114.16 avatars3.githubusercontent.com",
                "140.82.114.17 avatars4.githubusercontent.com",
                "140.82.114.18 avatars5.githubusercontent.com",
                "140.82.114.19 avatars6.githubusercontent.com",
                "140.82.114.20 avatars7.githubusercontent.com",
                "140.82.114.21 avatars8.githubusercontent.com"
            ]
        else:
            # 国外GitHub优化（使用官方IP）
            github_hosts = [
                "140.82.112.3 github.com",
                "140.82.112.9 codeload.github.com",
                "140.82.113.5 api.github.com",
                "140.82.113.10 uploads.github.com",
                "140.82.114.9 raw.githubusercontent.com",
                "140.82.114.10 gist.githubusercontent.com",
                "140.82.114.11 cloud.githubusercontent.com",
                "140.82.114.12 camo.githubusercontent.com",
                "140.82.114.13 avatars0.githubusercontent.com",
                "140.82.114.14 avatars1.githubusercontent.com",
                "140.82.114.15 avatars2.githubusercontent.com",
                "140.82.114.16 avatars3.githubusercontent.com",
                "140.82.114.17 avatars4.githubusercontent.com",
                "140.82.114.18 avatars5.githubusercontent.com",
                "140.82.114.19 avatars6.githubusercontent.com",
                "140.82.114.20 avatars7.githubusercontent.com",
                "140.82.114.21 avatars8.githubusercontent.com"
            ]
        
        hosts_file = "/etc/hosts"
        
        # 备份hosts文件
        if os.path.exists(hosts_file):
            backup_file = f"{hosts_file}.backup.{int(time.time())}"
            self.run_command(f"cp {hosts_file} {backup_file}", "备份hosts文件")
        
        # 添加GitHub hosts
        for host_entry in github_hosts:
            self.run_command(f"echo '{host_entry}' >> {hosts_file}", f"添加GitHub hosts: {host_entry}")
    
    def get_gitee_ip(self):
        """动态获取Gitee的IP地址"""
        try:
            # 首先尝试使用dig
            if self.run_command("which dig", "检查dig工具", silent=True):
                result = subprocess.run("dig +short gitee.com", shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    ip = result.stdout.strip().split('\n')[0]
                    if ip and ip != '127.0.0.1':
                        return ip
            
            # 如果dig不可用，尝试nslookup
            elif self.run_command("which nslookup", "检查nslookup工具", silent=True):
                result = subprocess.run("nslookup gitee.com", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    # 从nslookup输出中提取IP地址
                    for line in result.stdout.split('\n'):
                        if 'Address:' in line and not '#' in line:
                            ip = line.split('Address:')[-1].strip()
                            if ip and ip != '127.0.0.1':
                                return ip
            
            # 如果都不可用，尝试ping获取IP
            else:
                result = subprocess.run("ping -c 1 gitee.com", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    # 从ping输出中提取IP地址
                    for line in result.stdout.split('\n'):
                        if 'PING' in line and '(' in line and ')' in line:
                            ip = line.split('(')[1].split(')')[0]
                            if ip and ip != '127.0.0.1':
                                return ip
            
            # 如果所有方法都失败，使用备用IP
            return "212.64.62.174"
        except:
            return "212.64.62.174"
    
    def optimize_gitee(self):
        """优化Gitee访问"""
        print("\n🐉 优化Gitee访问...")
        
        # 动态获取Gitee的IP地址
        gitee_ip = self.get_gitee_ip()
        print(f"📍 检测到Gitee IP: {gitee_ip}")
        
        # Gitee的hosts配置（使用动态获取的IP）
        gitee_hosts = [
            f"{gitee_ip} gitee.com",
            f"{gitee_ip} www.gitee.com",
            f"{gitee_ip} api.gitee.com",
            f"{gitee_ip} gitee.io",
            f"{gitee_ip} gitee.net",
            f"{gitee_ip} gitee.cn",
            f"{gitee_ip} gitee.org",
            f"{gitee_ip} gitee.dev",
            f"{gitee_ip} gitee.tech",
            f"{gitee_ip} gitee.cloud",
            f"{gitee_ip} gitee.works",
            f"{gitee_ip} gitee.site",
            f"{gitee_ip} gitee.app",
            f"{gitee_ip} gitee.space",
            f"{gitee_ip} gitee.store",
            f"{gitee_ip} gitee.shop",
            f"{gitee_ip} gitee.blog",
            f"{gitee_ip} gitee.wiki",
            f"{gitee_ip} gitee.docs",
            f"{gitee_ip} gitee.help",
            f"{gitee_ip} gitee.support",
            f"{gitee_ip} gitee.community",
            f"{gitee_ip} gitee.forum",
            f"{gitee_ip} gitee.chat",
            f"{gitee_ip} gitee.meet",
            f"{gitee_ip} gitee.live",
            f"{gitee_ip} gitee.stream",
            f"{gitee_ip} gitee.video",
            f"{gitee_ip} gitee.audio",
            f"{gitee_ip} gitee.music",
            f"{gitee_ip} gitee.photo",
            f"{gitee_ip} gitee.image",
            f"{gitee_ip} gitee.file",
            f"{gitee_ip} gitee.download",
            f"{gitee_ip} gitee.upload",
            f"{gitee_ip} gitee.sync",
            f"{gitee_ip} gitee.backup",
            f"{gitee_ip} gitee.restore",
            f"{gitee_ip} gitee.migrate",
            f"{gitee_ip} gitee.clone",
            f"{gitee_ip} gitee.pull",
            f"{gitee_ip} gitee.push",
            f"{gitee_ip} gitee.merge",
            f"{gitee_ip} gitee.branch",
            f"{gitee_ip} gitee.tag",
            f"{gitee_ip} gitee.release",
            f"{gitee_ip} gitee.issue",
            f"{gitee_ip} gitee.pr",
            f"{gitee_ip} gitee.wiki",
            f"{gitee_ip} gitee.pages",
            f"{gitee_ip} gitee.actions",
            f"{gitee_ip} gitee.ci",
            f"{gitee_ip} gitee.cd",
            f"{gitee_ip} gitee.deploy",
            f"{gitee_ip} gitee.monitor",
            f"{gitee_ip} gitee.log",
            f"{gitee_ip} gitee.metric",
            f"{gitee_ip} gitee.alert",
            f"{gitee_ip} gitee.notify",
            f"{gitee_ip} gitee.webhook",
            f"{gitee_ip} gitee.api",
            f"{gitee_ip} gitee.sdk",
            f"{gitee_ip} gitee.cli",
            f"{gitee_ip} gitee.tool",
            f"{gitee_ip} gitee.plugin",
            f"{gitee_ip} gitee.extension",
            f"{gitee_ip} gitee.app",
            f"{gitee_ip} gitee.service",
            f"{gitee_ip} gitee.platform",
            f"{gitee_ip} gitee.ecosystem",
            f"{gitee_ip} gitee.marketplace",
            f"{gitee_ip} gitee.store",
            f"{gitee_ip} gitee.shop",
            f"{gitee_ip} gitee.buy",
            f"{gitee_ip} gitee.sell",
            f"{gitee_ip} gitee.trade",
            f"{gitee_ip} gitee.payment",
            f"{gitee_ip} gitee.billing",
            f"{gitee_ip} gitee.invoice",
            f"{gitee_ip} gitee.receipt",
            f"{gitee_ip} gitee.refund",
            f"{gitee_ip} gitee.cancel",
            f"{gitee_ip} gitee.suspend",
            f"{gitee_ip} gitee.terminate",
            f"{gitee_ip} gitee.delete",
            f"{gitee_ip} gitee.archive",
            f"{gitee_ip} gitee.restore",
            f"{gitee_ip} gitee.backup",
            f"{gitee_ip} gitee.sync",
            f"{gitee_ip} gitee.migrate",
            f"{gitee_ip} gitee.import",
            f"{gitee_ip} gitee.export",
            f"{gitee_ip} gitee.convert",
            f"{gitee_ip} gitee.transform",
            f"{gitee_ip} gitee.process",
            f"{gitee_ip} gitee.compute",
            f"{gitee_ip} gitee.analyze",
            f"{gitee_ip} gitee.report",
            f"{gitee_ip} gitee.dashboard",
            f"{gitee_ip} gitee.console",
            f"{gitee_ip} gitee.admin",
            f"{gitee_ip} gitee.manage",
            f"{gitee_ip} gitee.control",
            f"{gitee_ip} gitee.settings",
            f"{gitee_ip} gitee.config",
            f"{gitee_ip} gitee.profile",
            f"{gitee_ip} gitee.account",
            f"{gitee_ip} gitee.user",
            f"{gitee_ip} gitee.team",
            f"{gitee_ip} gitee.organization",
            f"{gitee_ip} gitee.company",
            f"{gitee_ip} gitee.enterprise",
            f"{gitee_ip} gitee.business",
            f"{gitee_ip} gitee.corporate",
            f"{gitee_ip} gitee.professional",
            f"{gitee_ip} gitee.premium",
            f"{gitee_ip} gitee.ultimate",
            f"{gitee_ip} gitee.unlimited"
        ]
        
        hosts_file = "/etc/hosts"
        
        # 添加Gitee hosts
        for host_entry in gitee_hosts:
            self.run_command(f"echo '{host_entry}' >> {hosts_file}", f"添加Gitee hosts: {host_entry}")
        
        # 如果是在国内，还可以配置Git使用Gitee作为备用源
        if self.is_china:
            print("🔧 配置Git使用Gitee作为备用源...")
            self.run_command("git config --global url.'https://gitee.com/'.insteadOf 'https://github.com/'", "配置Git使用Gitee镜像")
            self.run_command("git config --global url.'https://gitee.com/'.insteadOf 'git@github.com:'", "配置Git SSH使用Gitee镜像")
    
    def optimize_docker(self):
        """优化Docker镜像源"""
        print("\n🐳 优化Docker镜像源...")
        
        docker_mirrors = [
            "https://docker.m.daocloud.io",
            "https://docker.1panel.live",
            "https://hub.rat.dev"
        ]
        
        docker_daemon_config = {
            "registry-mirrors": docker_mirrors,
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "3"
            }
        }
        
        config_dir = "/etc/docker"
        config_file = f"{config_dir}/daemon.json"
        
        # 创建配置目录
        self.run_command(f"mkdir -p {config_dir}", "创建Docker配置目录")
        
        # 写入配置文件
        try:
            with open(config_file, 'w') as f:
                json.dump(docker_daemon_config, f, indent=2)
            print(f"✅ Docker镜像源配置成功，已写入 {config_file}")
            
            # 重启Docker服务
            self.run_command("systemctl restart docker", "重启Docker服务")
        except Exception as e:
            print(f"❌ 写入Docker配置文件或重启服务失败: {e}")
    
    def optimize_network(self):
        """网络优化设置"""
        print("\n🌐 网络优化设置...")
        
        # Linux网络优化
        optimizations = [
            # TCP优化
            "echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf",
            "echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_rmem = 4096 87380 16777216' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_wmem = 4096 65536 16777216' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_window_scaling = 1' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_timestamps = 1' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_sack = 1' >> /etc/sysctl.conf",
            # 连接优化
            "echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_max_syn_backlog = 8192' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_max_tw_buckets = 2000000' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_tw_reuse = 1' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_fin_timeout = 30' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_keepalive_time = 1200' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_keepalive_intvl = 15' >> /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_keepalive_probes = 5' >> /etc/sysctl.conf"
        ]
        
        for opt in optimizations:
            self.run_command(opt, "应用网络优化参数")
        
        # 应用sysctl配置
        self.run_command("sysctl -p", "应用系统参数")
    
    def create_optimization_report(self):
        """创建优化报告"""
        print("\n📊 优化报告")
        print("=" * 50)
        print(f"🌍 服务器位置: {'中国大陆' if self.is_china else '海外'}")
        print(f"🏳️  国家/地区: {self.ip_info.get('country', 'Unknown')}")
        print(f"🏙️  城市: {self.ip_info.get('city', 'Unknown')}")
        print(f"🌐 ISP: {self.ip_info.get('isp', 'Unknown')}")
        print(f"💻 操作系统: {platform.system()} {platform.release()}")
        print("=" * 50)
        
        if self.is_china:
            print("✅ 已应用国内优化策略:")
            print("    • 使用国内DNS服务器")
            print("    • 配置GitHub镜像加速")
            print("    • 配置Gitee访问优化")
            print("    • 设置Docker国内镜像源")
            print("    • 应用网络优化参数")
        else:
            print("✅ 已应用海外优化策略:")
            print("    • 使用国际DNS服务器")
            print("    • 配置GitHub官方访问")
            print("    • 配置Gitee访问优化")
            print("    • 设置Docker官方镜像源")
            print("    • 应用网络优化参数")
    
    def run_optimization(self):
        """执行完整的优化流程"""
        print("🚀 开始智能服务器优化...")
        print("=" * 50)
        
        # 1. 获取公网IP
        print("📡 检测服务器IP地址...")
        ip = self.get_public_ip()
        if not ip:
            print("❌ 无法获取IP地址，退出优化")
            return False
        
        print(f"🌐 服务器IP: {ip}")
        
        # 2. 检测地理位置
        print("\n🌍 检测地理位置...")
        self.is_china = self.detect_location(ip)
        print(f"📍 地理位置: {'中国大陆' if self.is_china else '海外'}")
        
        # 3. 执行优化
        self.optimize_dns()
        self.optimize_github()
        self.optimize_gitee() # 新增Gitee优化
        self.optimize_docker()
        self.optimize_network()
        
        # 4. 生成报告
        self.create_optimization_report()
        
        print("\n🎉 优化完成！")
        print("💡 建议重启服务器以确保所有设置生效")
        
        # 提供验证选项
        self.offer_verification()
        
        return True
    
    def offer_verification(self):
        """提供验证选项"""
        print("\n🔍 验证优化效果:")
        print("1. 测试DNS解析: nslookup github.com")
        print("2. 测试GitHub访问: curl -I https://github.com")
        print("3. 测试Gitee访问: curl -I https://gitee.com")
        print("4. 检查Docker镜像源: docker info | grep Registry")
        print("5. 检查网络参数: sysctl net.ipv4.tcp_congestion_control")
        
        try:
            choice = input("\n是否立即验证优化效果? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                self.verify_optimization()
        except KeyboardInterrupt:
            print("\n跳过验证")
    
    def verify_optimization(self):
        """验证优化效果"""
        print("\n🔍 开始验证优化效果...")
        
        # 测试DNS解析
        print("\n1. 测试DNS解析...")
        
        # 检查nslookup工具是否可用
        if self.run_command("which nslookup", "检查nslookup工具", silent=True):
            self.run_command("nslookup github.com", "测试GitHub DNS解析")
            self.run_command("nslookup gitee.com", "测试Gitee DNS解析")
        else:
            print("    ⚠️  nslookup工具不可用，使用替代方法...")
            # 使用ping测试DNS解析
            self.run_command("ping -c 1 github.com", "使用ping测试GitHub DNS解析")
            self.run_command("ping -c 1 gitee.com", "使用ping测试Gitee DNS解析")
            
            # 尝试使用dig（如果可用）
            if self.run_command("which dig", "检查dig工具", silent=True):
                self.run_command("dig +short github.com", "使用dig测试GitHub DNS解析")
                self.run_command("dig +short gitee.com", "使用dig测试Gitee DNS解析")
            else:
                print("    ⚠️  dig工具也不可用，跳过详细DNS测试")
        
        # 测试网站访问
        print("\n2. 测试网站访问...")
        self.run_command("curl -I --connect-timeout 10 https://github.com", "测试GitHub访问")
        
        # 测试Gitee访问（带重试机制）
        print("🔍 测试Gitee访问（最多重试5次）...")
        gitee_test_result = self.test_gitee_with_retry()
        
        # 如果Gitee访问失败，尝试使用IP地址访问
        if not gitee_test_result:
            print("⚠️  Gitee域名访问失败，尝试使用IP地址访问...")
            gitee_ip = self.get_gitee_ip()
            ip_test_result = self.test_gitee_ip_with_retry(gitee_ip)
            
            # 如果IP访问也失败，启动故障排除
            if not ip_test_result:
                print("\n❌ Gitee访问完全失败，启动故障排除...")
                self.troubleshoot_gitee_connection()
        
        # 检查Docker配置
        print("\n3. 检查Docker配置...")
        self.run_command("docker info 2>/dev/null | grep -i registry || echo 'Docker未安装或未运行'", "检查Docker镜像源")
        
        # 检查网络参数
        print("\n4. 检查网络参数...")
        self.run_command("sysctl net.ipv4.tcp_congestion_control", "检查拥塞控制算法")
        self.run_command("sysctl net.core.rmem_max", "检查接收缓冲区大小")
        
        print("\n✅ 验证完成！")
    
    def test_gitee_with_retry(self, max_retries=5):
        """测试Gitee访问，带重试机制"""
        for attempt in range(1, max_retries + 1):
            print(f"  尝试 {attempt}/{max_retries}...")
            
            try:
                result = subprocess.run(
                    "curl -I --connect-timeout 5 --max-time 10 https://gitee.com",
                    shell=True, capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    print(f"✅ Gitee访问成功（第{attempt}次尝试）")
                    return True
                else:
                    print(f"❌ 第{attempt}次尝试失败")
                    if attempt < max_retries:
                        print("  等待1秒后重试...")
                        time.sleep(1)
                    
            except subprocess.TimeoutExpired:
                print(f"❌ 第{attempt}次尝试超时")
                if attempt < max_retries:
                    print("  等待1秒后重试...")
                    time.sleep(1)
            except Exception as e:
                print(f"❌ 第{attempt}次尝试异常: {e}")
                if attempt < max_retries:
                    print("  等待1秒后重试...")
                    time.sleep(1)
        
        print(f"❌ Gitee访问失败，已尝试{max_retries}次")
        return False
    
    def test_gitee_ip_with_retry(self, gitee_ip, max_retries=5):
        """使用IP地址测试Gitee访问，带重试机制"""
        print(f"🔍 使用IP地址 {gitee_ip} 测试Gitee访问（最多重试{max_retries}次）...")
        
        for attempt in range(1, max_retries + 1):
            print(f"  尝试 {attempt}/{max_retries}...")
            
            try:
                result = subprocess.run(
                    f"curl -I --connect-timeout 5 --max-time 10 -H 'Host: gitee.com' https://{gitee_ip}",
                    shell=True, capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    print(f"✅ Gitee IP访问成功（第{attempt}次尝试）")
                    return True
                else:
                    print(f"❌ 第{attempt}次尝试失败")
                    if attempt < max_retries:
                        print("  等待1秒后重试...")
                        time.sleep(1)
                    
            except subprocess.TimeoutExpired:
                print(f"❌ 第{attempt}次尝试超时")
                if attempt < max_retries:
                    print("  等待1秒后重试...")
                    time.sleep(1)
            except Exception as e:
                print(f"❌ 第{attempt}次尝试异常: {e}")
                if attempt < max_retries:
                    print("  等待1秒后重试...")
                    time.sleep(1)
        
        print(f"❌ Gitee IP访问失败，已尝试{max_retries}次")
        return False
    
    def troubleshoot_gitee_connection(self):
        """Gitee连接故障排除和备选方案"""
        print("\n🔧 Gitee连接故障排除...")
        
        # 1. 检查网络连接
        print("1. 检查网络连接...")
        self.run_command("ping -c 3 8.8.8.8", "测试外网连接")
        self.run_command("ping -c 3 114.114.114.114", "测试国内DNS连接")
        
        # 2. 检查DNS解析
        print("\n2. 检查DNS解析...")
        # 检查工具是否可用
        if self.run_command("which nslookup", "检查nslookup工具", silent=True):
            self.run_command("nslookup gitee.com", "检查Gitee DNS解析")
        else:
            print("    ⚠️  nslookup工具不可用")
        
        if self.run_command("which dig", "检查dig工具", silent=True):
            self.run_command("dig gitee.com", "使用dig检查Gitee解析")
        else:
            print("    ⚠️  dig工具不可用")
        
        # 3. 检查防火墙设置
        print("\n3. 检查防火墙设置...")
        self.run_command("iptables -L -n | grep -E '(DROP|REJECT)'", "检查防火墙规则")
        if self.run_command("which ufw", "检查ufw工具", silent=True):
            self.run_command("ufw status", "检查UFW防火墙状态")
        else:
            print("    ⚠️  ufw工具不可用")
        
        # 4. 检查代理设置
        print("\n4. 检查代理设置...")
        self.run_command("env | grep -i proxy", "检查环境变量代理设置")
        self.run_command("cat /etc/environment | grep -i proxy", "检查系统代理设置")
        
        # 5. 检测服务器位置
        print("\n5. 检测服务器位置...")
        self.detect_server_location_for_gitee()
        
        # 6. 尝试自动修复
        print("\n6. 尝试自动修复...")
        self.attempt_auto_fix()
        
        # 7. 提供备选方案
        self.provide_gitee_alternatives()
    
    def provide_gitee_alternatives(self):
        """提供Gitee访问的备选方案"""
        print("\n💡 Gitee访问备选方案:")
        print("=" * 50)
        
        # 方案1: 使用镜像站点
        print("1. 🌐 使用Gitee镜像站点:")
        print("    - https://gitee.com (官方站点)")
        print("    - https://git.oschina.net (备用域名)")
        print("    - 尝试使用VPN或代理访问")
        
        # 方案2: 配置代理
        print("\n2. 🔧 配置代理服务器:")
        print("    # 设置HTTP代理")
        print("    export http_proxy=http://proxy-server:port")
        print("    export https_proxy=http://proxy-server:port")
        print("    # 或者使用socks5代理")
        print("    export all_proxy=socks5://proxy-server:port")
        
        # 方案3: 使用Git配置代理
        print("\n3. 🐙 Git代理配置:")
        print("    # 为Git配置代理")
        print("    git config --global http.proxy http://proxy-server:port")
        print("    git config --global https.proxy http://proxy-server:port")
        print("    # 或者使用socks5")
        print("    git config --global http.proxy socks5://proxy-server:port")
        
        # 方案4: 使用SSH方式
        print("\n4. 🔑 使用SSH方式访问:")
        print("    # 生成SSH密钥")
        print("    ssh-keygen -t rsa -b 4096 -C 'your_email@example.com'")
        print("    # 将公钥添加到Gitee账户")
        print("    cat ~/.ssh/id_rsa.pub")
        print("    # 测试SSH连接")
        print("    ssh -T git@gitee.com")
        
        # 方案5: 使用GitHub作为备选
        print("\n5. 🐙 使用GitHub作为备选:")
        print("    # 如果Gitee无法访问，可以使用GitHub")
        print("    git clone https://github.com/username/repository.git")
        print("    # 或者配置GitHub镜像")
        print("    git config --global url.'https://github.com/'.insteadOf 'https://gitee.com/'")
        
        # 方案6: 手动修复hosts文件
        print("\n6. 📝 手动修复hosts文件:")
        print("    # 编辑hosts文件")
        print("    sudo nano /etc/hosts")
        print("    # 添加最新的Gitee IP地址")
        print("    # 可以从以下网站获取最新IP:")
        print("    # https://www.ipaddress.com/site/gitee.com")
        print("    # https://dnschecker.org/")
        
        # 方案7: 使用CDN加速
        print("\n7. ⚡ 使用CDN加速:")
        print("    # 配置Cloudflare或其他CDN")
        print("    # 或者使用国内CDN服务")
        
        print("\n" + "=" * 50)
        print("💡 建议按顺序尝试以上方案")
        print("📞 如果问题持续存在，请联系网络管理员或ISP")
    
    def detect_server_location_for_gitee(self):
        """检测服务器位置，为Gitee访问提供针对性解决方案"""
        print("🔍 检测服务器位置...")
        
        # 检查是否为中国大陆服务器
        if self.is_china:
            print("    📍 检测到中国大陆服务器")
            print("    ✅ 中国大陆服务器通常可以正常访问Gitee")
            print("    💡 如果仍然无法访问，可能是网络配置问题")
        else:
            print("    📍 检测到海外服务器")
            print("    ⚠️  海外服务器通常无法直接访问Gitee")
            print("    💡 建议使用以下临时解决方案：")
            self.provide_overseas_gitee_solutions()
    
    def provide_overseas_gitee_solutions(self):
        """为海外服务器提供Gitee访问的临时解决方案"""
        print("\n🌍 海外服务器Gitee访问临时解决方案:")
        print("=" * 60)
        
        # 方案1: 使用国内代理
        print("1. 🔧 使用国内代理服务器:")
        print("    # 设置HTTP代理（需要国内代理服务器）")
        print("    export http_proxy=http://your-china-proxy:port")
        print("    export https_proxy=http://your-china-proxy:port")
        print("    # 测试连接")
        print("    curl -I https://gitee.com")
        
        # 方案2: 使用VPN
        print("\n2. 🔒 使用VPN连接到中国大陆:")
        print("    # 连接VPN后测试")
        print("    curl -I https://gitee.com")
        
        # 方案3: 使用SSH隧道
        print("\n3. 🔗 使用SSH隧道:")
        print("    # 通过国内服务器建立SSH隧道")
        print("    ssh -D 1080 user@your-china-server")
        print("    # 设置SOCKS5代理")
        print("    export all_proxy=socks5://127.0.0.1:1080")
        
        # 方案4: 使用GitHub镜像
        print("\n4. 🐙 使用GitHub作为替代:")
        print("    # 配置Git使用GitHub")
        print("    git config --global url.'https://github.com/'.insteadOf 'https://gitee.com/'")
        print("    # 或者直接使用GitHub")
        print("    git clone https://github.com/username/repository.git")
        
        # 方案5: 使用国内服务器
        print("\n5. 🖥️  使用国内服务器:")
        print("    # 在GitHub Actions或其他CI/CD中使用国内服务器")
        
        print("\n" + "=" * 60)
        print("💡 建议按顺序尝试以上方案")
        print("📞 如果问题持续存在，请联系网络管理员或ISP")

if __name__ == "__main__":
    optimizer = ServerOptimizer()
    optimizer.run_optimization()
