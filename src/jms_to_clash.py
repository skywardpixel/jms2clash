#!/usr/bin/env python3
"""
JMS to Clash Converter
Converts JMS subscription strings to Clash configuration files optimized for Chinese users.

Usage:
    python3 jms_to_clash.py [options]
    echo "subscription" | python3 jms_to_clash.py
    python3 jms_to_clash.py < input.txt > output.yaml

Options:
    --help, -h      Show this help message
    --version       Show version information
"""

import sys
import json
import base64
import binascii
import urllib.parse
import re
import yaml
import argparse
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs

VERSION = "0.1.1"

def decode_vmess(vmess_url: str) -> Optional[Dict[str, Any]]:
    """Decode VMess URL to proxy config"""
    try:
        # Remove vmess:// prefix
        encoded = vmess_url[8:]
        # Decode base64 with error handling
        try:
            decoded_bytes = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4))
            decoded = decoded_bytes.decode('utf-8')
        except (UnicodeDecodeError, binascii.Error):
            # Try latin-1 encoding as fallback
            try:
                decoded_bytes = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4))
                decoded = decoded_bytes.decode('latin-1')
            except (UnicodeDecodeError, binascii.Error):
                return None
        config = json.loads(decoded)

        return {
            'name': config.get('ps', 'VMess'),
            'type': 'vmess',
            'server': config.get('add', ''),
            'port': int(config.get('port', 443)),
            'uuid': config.get('id', ''),
            'alterId': int(config.get('aid', 0)),
            'cipher': config.get('scy', 'auto'),
            'network': config.get('net', 'tcp'),
            'tls': config.get('tls') == 'tls',
            'skip-cert-verify': True,
            'servername': config.get('sni', ''),
            'ws-opts': {
                'path': config.get('path', '/'),
                'headers': {'Host': config.get('host', '')} if config.get('host') else {}
            } if config.get('net') == 'ws' else None,
            'h2-opts': {
                'host': [config.get('host', '')],
                'path': config.get('path', '/')
            } if config.get('net') == 'h2' else None,
            'grpc-opts': {
                'grpc-service-name': config.get('path', '')
            } if config.get('net') == 'grpc' else None
        }
    except Exception as e:
        print(f"Warning: Skipping malformed VMess URL (encoding error)", file=sys.stderr)
        return None

def decode_vless(vless_url: str) -> Optional[Dict[str, Any]]:
    """Decode VLESS URL to proxy config"""
    try:
        parsed = urlparse(vless_url)
        params = parse_qs(parsed.query)

        config = {
            'name': urllib.parse.unquote(parsed.fragment) or 'VLESS',
            'type': 'vless',
            'server': parsed.hostname,
            'port': parsed.port or 443,
            'uuid': parsed.username,
            'network': params.get('type', ['tcp'])[0],
            'tls': params.get('security', [''])[0] == 'tls',
            'skip-cert-verify': True,
            'servername': params.get('sni', [''])[0],
            'flow': params.get('flow', [''])[0]
        }

        if config['network'] == 'ws':
            config['ws-opts'] = {
                'path': params.get('path', ['/'])[0],
                'headers': {'Host': params.get('host', [''])[0]} if params.get('host') else {}
            }
        elif config['network'] == 'grpc':
            config['grpc-opts'] = {
                'grpc-service-name': params.get('serviceName', [''])[0]
            }

        return config
    except Exception as e:
        print(f"Error decoding VLESS: {e}", file=sys.stderr)
        return None

def decode_ss(ss_url: str) -> Optional[Dict[str, Any]]:
    """Decode Shadowsocks URL to proxy config"""
    try:
        # Handle ss://method:password@server:port#name format
        if '@' in ss_url:
            parts = ss_url[5:].split('@')
            if len(parts) != 2:
                return None

            # Decode method:password with error handling
            try:
                decoded_bytes = base64.b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4))
                method_pass = decoded_bytes.decode('utf-8')
            except (UnicodeDecodeError, binascii.Error):
                # Try latin-1 encoding as fallback
                try:
                    decoded_bytes = base64.b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4))
                    method_pass = decoded_bytes.decode('latin-1')
                except (UnicodeDecodeError, binascii.Error):
                    return None
            method, password = method_pass.split(':', 1)

            # Parse server:port#name
            server_part = parts[1]
            if '#' in server_part:
                server_port, name = server_part.split('#', 1)
                name = urllib.parse.unquote(name)
            else:
                server_port = server_part
                name = 'SS'

            server, port = server_port.rsplit(':', 1)
        else:
            # Handle ss://base64encoded#name format
            url_parts = ss_url[5:].split('#')
            encoded = url_parts[0]
            name = urllib.parse.unquote(url_parts[1]) if len(url_parts) > 1 else 'SS'

            try:
                decoded_bytes = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4))
                decoded = decoded_bytes.decode('utf-8')
            except (UnicodeDecodeError, binascii.Error):
                # Try latin-1 encoding as fallback
                try:
                    decoded_bytes = base64.b64decode(encoded + '=' * (4 - len(encoded) % 4))
                    decoded = decoded_bytes.decode('latin-1')
                except (UnicodeDecodeError, binascii.Error):
                    return None
            method, rest = decoded.split(':', 1)
            password, server_port = rest.rsplit('@', 1)
            server, port = server_port.rsplit(':', 1)

        return {
            'name': name,
            'type': 'ss',
            'server': server,
            'port': int(port),
            'cipher': method,
            'password': password,
            'plugin': None,
            'plugin-opts': {}
        }
    except Exception as e:
        print(f"Warning: Skipping malformed SS URL (encoding error)", file=sys.stderr)
        return None

def decode_trojan(trojan_url: str) -> Optional[Dict[str, Any]]:
    """Decode Trojan URL to proxy config"""
    try:
        parsed = urlparse(trojan_url)
        params = parse_qs(parsed.query)

        config = {
            'name': urllib.parse.unquote(parsed.fragment) or 'Trojan',
            'type': 'trojan',
            'server': parsed.hostname,
            'port': parsed.port or 443,
            'password': parsed.username,
            'skip-cert-verify': True,
            'sni': params.get('sni', [''])[0] or parsed.hostname
        }

        if params.get('type', [''])[0] == 'ws':
            config['network'] = 'ws'
            config['ws-opts'] = {
                'path': params.get('path', ['/'])[0],
                'headers': {'Host': params.get('host', [''])[0]} if params.get('host') else {}
            }

        return config
    except Exception as e:
        print(f"Error decoding Trojan: {e}", file=sys.stderr)
        return None

def parse_subscription(content: str) -> List[Dict[str, Any]]:
    """Parse subscription content and extract proxy configs"""
    proxies = []

    # Try to decode as base64 first
    try:
        decoded_bytes = base64.b64decode(content + '=' * (4 - len(content) % 4))
        try:
            decoded_content = decoded_bytes.decode('utf-8')
        except UnicodeDecodeError:
            decoded_content = decoded_bytes.decode('latin-1', errors='ignore')
        content = decoded_content
    except (binascii.Error, Exception):
        pass

    # Split by lines and process each URL
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        try:
            if line.startswith('vmess://'):
                proxy = decode_vmess(line)
            elif line.startswith('vless://'):
                proxy = decode_vless(line)
            elif line.startswith('ss://'):
                proxy = decode_ss(line)
            elif line.startswith('trojan://'):
                proxy = decode_trojan(line)
            else:
                continue

            if proxy:
                # Clean up None values
                proxy = {k: v for k, v in proxy.items() if v is not None}
                proxies.append(proxy)

        except Exception as e:
            print(f"Error parsing line: {line[:50]}... - {e}", file=sys.stderr)
            continue

    return proxies

def generate_clash_config(proxies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate complete Clash configuration for Chinese users"""
    proxy_names = [proxy['name'] for proxy in proxies]

    config = {
        'port': 7890,
        'socks-port': 7891,
        'allow-lan': False,
        'mode': 'rule',
        'log-level': 'info',
        'external-controller': '127.0.0.1:9090',
        'dns': {
            'enable': True,
            'listen': '0.0.0.0:53',
            'ipv6': False,
            'default-nameserver': [
                '114.114.114.114',
                '223.5.5.5'
            ],
            'enhanced-mode': 'fake-ip',
            'fake-ip-range': '198.18.0.1/16',
            'fake-ip-filter': [
                '*.lan', '*.localdomain', '*.example', '*.invalid',
                '*.localhost', '*.test', '*.local', '*.home.arpa',
                '+.msftconnecttest.com', '+.msftncsi.com',
                'localhost.ptlogin2.qq.com', '+.srv.nintendo.net',
                '+.stun.playstation.net', 'xbox.*.microsoft.com',
                '+.battlenet.com.cn', '+.wotgame.cn', '+.wggames.cn',
                '+.wowsgame.cn', '+.wargaming.net', 'music.163.com',
                '*.music.163.com', '*.126.net', 'musicapi.taihe.com',
                'music.taihe.com', 'songsearch.kugou.com',
                'trackercdn.kugou.com', '*.kuwo.cn', 'api-jooxtt.sanook.com',
                'api.joox.com', 'joox.com', 'y.qq.com', '*.y.qq.com',
                'streamoc.music.tc.qq.com', 'mobileoc.music.tc.qq.com',
                'isure.stream.qqmusic.qq.com', 'dl.stream.qqmusic.qq.com',
                'aqqmusic.tc.qq.com', 'amobile.music.tc.qq.com',
                '*.xiami.com', '*.music.migu.cn', 'music.migu.cn'
            ],
            'nameserver': [
                '119.29.29.29',
                '223.5.5.5',
                '114.114.114.114',
                '8.8.8.8'
            ],
            'fallback': [
                'https://dns.cloudflare.com/dns-query',
                'https://dns.google/dns-query',
                'tls://dns.google'
            ],
            'fallback-filter': {
                'geoip': True,
                'geoip-code': 'CN',
                'ipcidr': ['240.0.0.0/4']
            }
        },
        'proxies': proxies,
        'proxy-groups': [
            {
                'name': '🚀 节点选择',
                'type': 'select',
                'proxies': ['♻️ 自动选择', '🎯 全球直连'] + proxy_names
            },
            {
                'name': '♻️ 自动选择',
                'type': 'url-test',
                'proxies': proxy_names,
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300,
                'tolerance': 50
            },
            {
                'name': '🎯 全球直连',
                'type': 'select',
                'proxies': ['DIRECT']
            },
            {
                'name': '🛑 广告拦截',
                'type': 'select',
                'proxies': ['REJECT', 'DIRECT']
            },
            {
                'name': '📺 哔哩哔哩',
                'type': 'select',
                'proxies': ['🎯 全球直连'] + proxy_names
            },
            {
                'name': '🎵 网易云音乐',
                'type': 'select',
                'proxies': ['🎯 全球直连'] + proxy_names
            },
            {
                'name': '📹 YouTube',
                'type': 'select',
                'proxies': ['🚀 节点选择'] + proxy_names
            },
            {
                'name': '🎬 Netflix',
                'type': 'select',
                'proxies': ['🚀 节点选择'] + proxy_names
            },
            {
                'name': '📱 Telegram',
                'type': 'select',
                'proxies': ['🚀 节点选择'] + proxy_names
            },
            {
                'name': '🔍 Google',
                'type': 'select',
                'proxies': ['🚀 节点选择'] + proxy_names
            },
            {
                'name': '🍎 苹果服务',
                'type': 'select',
                'proxies': ['🎯 全球直连', '🚀 节点选择'] + proxy_names
            },
            {
                'name': 'Ⓜ️ 微软服务',
                'type': 'select',
                'proxies': ['🎯 全球直连', '🚀 节点选择'] + proxy_names
            },
            {
                'name': '📢 谷歌FCM',
                'type': 'select',
                'proxies': ['🚀 节点选择', '🎯 全球直连'] + proxy_names
            },
            {
                'name': '🐟 漏网之鱼',
                'type': 'select',
                'proxies': ['🚀 节点选择', '🎯 全球直连'] + proxy_names
            }
        ],
        'rules': [
            # Local network
            'DOMAIN-SUFFIX,local,DIRECT',
            'IP-CIDR,127.0.0.0/8,DIRECT',
            'IP-CIDR,172.16.0.0/12,DIRECT',
            'IP-CIDR,192.168.0.0/16,DIRECT',
            'IP-CIDR,10.0.0.0/8,DIRECT',
            'IP-CIDR,17.0.0.0/8,DIRECT',
            'IP-CIDR,100.64.0.0/10,DIRECT',

            # Ad blocking
            'DOMAIN-KEYWORD,googleads,🛑 广告拦截',
            'DOMAIN-KEYWORD,googlesyndication,🛑 广告拦截',
            'DOMAIN-KEYWORD,googletagmanager,🛑 广告拦截',
            'DOMAIN,pagead2.googlesyndication.com,🛑 广告拦截',

            # Chinese services
            'DOMAIN,clash.razord.top,🎯 全球直连',
            'DOMAIN,yacd.haishan.me,🎯 全球直连',

            # Specific services
            'DOMAIN-KEYWORD,youtube,📹 YouTube',
            'DOMAIN,youtubei.googleapis.com,📹 YouTube',
            'DOMAIN-SUFFIX,googlevideo.com,📹 YouTube',
            'DOMAIN-SUFFIX,youtube.com,📹 YouTube',
            'DOMAIN-SUFFIX,ytimg.com,📹 YouTube',

            'DOMAIN-KEYWORD,netflix,🎬 Netflix',
            'DOMAIN-SUFFIX,netflix.com,🎬 Netflix',
            'DOMAIN-SUFFIX,netflix.net,🎬 Netflix',
            'DOMAIN-SUFFIX,nflximg.net,🎬 Netflix',
            'DOMAIN-SUFFIX,nflxext.com,🎬 Netflix',
            'DOMAIN-SUFFIX,nflxso.net,🎬 Netflix',
            'DOMAIN-SUFFIX,nflxvideo.net,🎬 Netflix',

            'DOMAIN-KEYWORD,telegram,📱 Telegram',
            'DOMAIN-SUFFIX,t.me,📱 Telegram',
            'DOMAIN-SUFFIX,tdesktop.com,📱 Telegram',
            'DOMAIN-SUFFIX,telegram.me,📱 Telegram',
            'DOMAIN-SUFFIX,telegram.org,📱 Telegram',
            'DOMAIN-SUFFIX,telesco.pe,📱 Telegram',

            'DOMAIN-KEYWORD,bilibili,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,acg.tv,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,acgvideo.com,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,b23.tv,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,bilibili.com,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,bilivideo.com,📺 哔哩哔哩',
            'DOMAIN-SUFFIX,hdslb.com,📺 哔哩哔哩',

            'DOMAIN,music.163.com,🎵 网易云音乐',
            'DOMAIN-SUFFIX,music.163.com,🎵 网易云音乐',
            'DOMAIN-SUFFIX,163yun.com,🎵 网易云音乐',
            'DOMAIN-SUFFIX,126.net,🎵 网易云音乐',
            'DOMAIN-SUFFIX,163.com,🎵 网易云音乐',

            'DOMAIN-KEYWORD,microsoft,Ⓜ️ 微软服务',
            'DOMAIN-SUFFIX,bing.com,Ⓜ️ 微软服务',
            'DOMAIN-SUFFIX,microsoft.com,Ⓜ️ 微软服务',
            'DOMAIN-SUFFIX,office.com,Ⓜ️ 微软服务',
            'DOMAIN-SUFFIX,outlook.com,Ⓜ️ 微软服务',
            'DOMAIN-SUFFIX,xbox.com,Ⓜ️ 微软服务',

            'DOMAIN,mtalk.google.com,📢 谷歌FCM',
            'DOMAIN,alt1-mtalk.google.com,📢 谷歌FCM',
            'DOMAIN,alt2-mtalk.google.com,📢 谷歌FCM',
            'DOMAIN,alt3-mtalk.google.com,📢 谷歌FCM',
            'DOMAIN,alt4-mtalk.google.com,📢 谷歌FCM',

            # GeoIP rules
            'GEOIP,LAN,🎯 全球直连',
            'GEOIP,CN,🎯 全球直连',
            'MATCH,🐟 漏网之鱼'
        ]
    }
    return config

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert JMS subscription strings to Clash configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 jms_to_clash.py < subscription.txt > config.yaml
  echo "vmess://..." | python3 jms_to_clash.py
  cat subscription.txt | python3 jms_to_clash.py > clash_config.yaml

Supported proxy formats:
  - VMess: vmess://...
  - VLESS: vless://...
  - Shadowsocks: ss://...
  - Trojan: trojan://...
  - Base64 encoded subscriptions
        """
    )

    parser.add_argument('--version', action='version', version=f'jms2clash {VERSION}')

    args = parser.parse_args()

    # Main conversion logic
    try:
        # Read from stdin
        content = sys.stdin.read().strip()

        if not content:
            print("Error: No input provided. Use --help for usage information.", file=sys.stderr)
            sys.exit(1)

        # Parse subscription
        proxies = parse_subscription(content)

        if not proxies:
            print("Error: No valid proxies found in input", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(proxies)} proxies", file=sys.stderr)

        # Generate Clash config
        clash_config = generate_clash_config(proxies)

        # Output YAML
        yaml_output = yaml.dump(clash_config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(yaml_output)

    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
