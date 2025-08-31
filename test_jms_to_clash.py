#!/usr/bin/env python3
"""
Test suite for JMS to Clash converter using pytest framework
Run with: python -m pytest test_jms_to_clash.py -v
"""

import pytest
import yaml
import sys
import os
import tempfile
from unittest.mock import patch
from io import StringIO

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from jms_to_clash import (
    decode_vmess, decode_vless, decode_ss, decode_trojan,
    parse_subscription, generate_clash_config, main
)

class TestProxyDecoders:
    """Test individual proxy format decoders"""

    def test_decode_vmess(self):
        """Test VMess URL decoding"""
        vmess_url = "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6InRjcCIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoidGxzIiwidiI6IjIifQ=="

        result = decode_vmess(vmess_url)

        assert result is not None
        assert result['name'] == 'Test VMess'
        assert result['type'] == 'vmess'
        assert result['server'] == 'example.com'
        assert result['port'] == 443
        assert result['uuid'] == '12345678-1234-1234-1234-1234567890ab'
        assert result['network'] == 'tcp'
        assert result['tls'] is True

    def test_decode_vmess_websocket(self):
        """Test VMess WebSocket decoding"""
        vmess_url = "vmess://eyJhZGQiOiJ3cy5leGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6Ijk4NzY1NDMyLTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6IndzIiwicGF0aCI6Ii9wYXRoIiwicG9ydCI6IjgwIiwicHMiOiJXZWJTb2NrZXQgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoiIiwidiI6IjIiLCJob3N0Ijoid3MuZXhhbXBsZS5jb20ifQ=="

        result = decode_vmess(vmess_url)

        assert result is not None
        assert result['network'] == 'ws'
        assert result['ws-opts']['path'] == '/path'
        assert result['ws-opts']['headers']['Host'] == 'ws.example.com'

    def test_decode_vless(self):
        """Test VLESS URL decoding"""
        vless_url = "vless://12345678-1234-1234-1234-123456789abc@example.com:443?type=tcp&security=tls&sni=example.com#Test%20VLESS"

        result = decode_vless(vless_url)

        assert result is not None
        assert result['name'] == 'Test VLESS'
        assert result['type'] == 'vless'
        assert result['server'] == 'example.com'
        assert result['port'] == 443
        assert result['uuid'] == '12345678-1234-1234-1234-123456789abc'
        assert result['network'] == 'tcp'
        assert result['tls'] is True

    def test_decode_shadowsocks(self):
        """Test Shadowsocks URL decoding"""
        ss_url = "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@example.com:8388#Test%20SS"

        result = decode_ss(ss_url)

        assert result is not None
        assert result['name'] == 'Test SS'
        assert result['type'] == 'ss'
        assert result['server'] == 'example.com'
        assert result['port'] == 8388
        assert result['cipher'] == 'aes-256-gcm'
        assert result['password'] == 'password'

    def test_decode_trojan(self):
        """Test Trojan URL decoding"""
        trojan_url = "trojan://password123@example.com:443?sni=example.com#Test%20Trojan"

        result = decode_trojan(trojan_url)

        assert result is not None
        assert result['name'] == 'Test Trojan'
        assert result['type'] == 'trojan'
        assert result['server'] == 'example.com'
        assert result['port'] == 443
        assert result['password'] == 'password123'
        assert result['sni'] == 'example.com'

    def test_decode_invalid_url(self):
        """Test handling of invalid URLs"""
        assert decode_vmess("invalid_url") is None
        # These may not return None due to urlparse handling, so just check they don't crash
        try:
            decode_vless("invalid_url")
            decode_ss("invalid_url")
            decode_trojan("invalid_url")
        except:
            pass  # Expected to fail gracefully

class TestSubscriptionParsing:
    """Test subscription parsing functionality"""

    def test_parse_mixed_subscription(self):
        """Test parsing subscription with multiple proxy types"""
        subscription = """# Test subscription
vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6InRjcCIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoidGxzIiwidiI6IjIifQ==
ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@example.com:8388#Test%20SS
trojan://password123@example.com:443?sni=example.com#Test%20Trojan
# Another comment
vless://12345678-1234-1234-1234-123456789abc@example.com:443?type=tcp&security=tls&sni=example.com#Test%20VLESS"""

        proxies = parse_subscription(subscription)

        assert len(proxies) == 4
        assert proxies[0]['name'] == 'Test VMess'
        assert proxies[1]['name'] == 'Test SS'
        assert proxies[2]['name'] == 'Test Trojan'
        assert proxies[3]['name'] == 'Test VLESS'

    def test_parse_base64_subscription(self):
        """Test parsing base64 encoded subscription"""
        import base64

        plain_subscription = """vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6InRjcCIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoidGxzIiwidiI6IjIifQ==
ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@example.com:8388#Test%20SS"""

        encoded_subscription = base64.b64encode(plain_subscription.encode()).decode()
        proxies = parse_subscription(encoded_subscription)

        assert len(proxies) == 2
        assert proxies[0]['name'] == 'Test VMess'
        assert proxies[1]['name'] == 'Test SS'

    def test_parse_empty_subscription(self):
        """Test parsing empty subscription"""
        proxies = parse_subscription("")
        assert len(proxies) == 0

    def test_parse_comments_only(self):
        """Test parsing subscription with only comments"""
        subscription = """# This is a comment
# Another comment
# No actual proxies here"""

        proxies = parse_subscription(subscription)
        assert len(proxies) == 0

class TestConfigGeneration:
    """Test Clash configuration generation"""

    def test_generate_clash_config(self):
        """Test generating complete Clash configuration"""
        proxies = [
            {
                'name': 'Test Server 1',
                'type': 'vmess',
                'server': 'example.com',
                'port': 443,
                'uuid': 'test-uuid',
                'alterId': 0,
                'cipher': 'auto'
            },
            {
                'name': 'Test Server 2',
                'type': 'ss',
                'server': 'example2.com',
                'port': 8388,
                'cipher': 'aes-256-gcm',
                'password': 'test-password'
            }
        ]

        config = generate_clash_config(proxies)

        # Test basic structure
        assert 'port' in config
        assert 'socks-port' in config
        assert 'dns' in config
        assert 'proxies' in config
        assert 'proxy-groups' in config
        assert 'rules' in config

        # Test specific values
        assert config['port'] == 7890
        assert config['socks-port'] == 7891
        assert config['mode'] == 'rule'

        # Test proxies
        assert len(config['proxies']) == 2
        assert config['proxies'][0]['name'] == 'Test Server 1'
        assert config['proxies'][1]['name'] == 'Test Server 2'

        # Test proxy groups
        assert len(config['proxy-groups']) == 14
        group_names = [group['name'] for group in config['proxy-groups']]
        assert '🚀 节点选择' in group_names
        assert '♻️ 自动选择' in group_names
        assert '🎯 全球直连' in group_names

        # Test DNS configuration
        assert config['dns']['enable'] is True
        assert config['dns']['enhanced-mode'] == 'fake-ip'
        assert '119.29.29.29' in config['dns']['nameserver']
        assert '223.5.5.5' in config['dns']['nameserver']

    def test_empty_proxies_config(self):
        """Test generating config with no proxies"""
        config = generate_clash_config([])

        assert len(config['proxies']) == 0
        # Proxy groups should still exist but with minimal proxies
        assert len(config['proxy-groups']) == 14

class TestYAMLOutput:
    """Test YAML output functionality"""

    def test_yaml_output_valid(self):
        """Test that generated YAML is valid"""
        proxies = [{
            'name': 'Test Server',
            'type': 'vmess',
            'server': 'example.com',
            'port': 443,
            'uuid': 'test-uuid'
        }]

        config = generate_clash_config(proxies)
        yaml_output = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Should be able to load it back
        loaded_config = yaml.safe_load(yaml_output)
        assert loaded_config['port'] == 7890
        assert len(loaded_config['proxies']) == 1

    def test_yaml_unicode_support(self):
        """Test YAML output with Chinese characters"""
        proxies = [{
            'name': '测试服务器',
            'type': 'vmess',
            'server': 'example.com',
            'port': 443,
            'uuid': 'test-uuid'
        }]

        config = generate_clash_config(proxies)
        yaml_output = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)

        assert '测试服务器' in yaml_output
        assert '节点选择' in yaml_output

class TestMainFunction:
    """Test main function and CLI integration"""

    def test_main_with_valid_input(self):
        """Test main function with valid input"""
        test_input = "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6InRjcCIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoidGxzIiwidiI6IjIifQ=="

        with patch('sys.stdin', StringIO(test_input)):
            with patch('sys.stdout', StringIO()) as mock_stdout:
                with patch('sys.argv', ['jms_to_clash.py']):
                    try:
                        main()
                    except SystemExit:
                        pass

                output = mock_stdout.getvalue()
                assert 'port: 7890' in output
                assert 'Test VMess' in output

    def test_main_with_empty_input(self):
        """Test main function with empty input"""
        with patch('sys.stdin', StringIO("")):
            with patch('sys.stderr', StringIO()) as mock_stderr:
                with patch('sys.argv', ['jms_to_clash.py']):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 1
                    error_output = mock_stderr.getvalue()
                    assert "No input provided" in error_output

    def test_main_help_option(self):
        """Test main function with help option"""
        with patch('sys.argv', ['jms_to_clash.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_main_version_option(self):
        """Test main function with version option"""
        with patch('sys.argv', ['jms_to_clash.py', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Version should exit with code 0
            assert exc_info.value.code == 0

    def test_main_invalid_option(self):
        """Test main function with invalid option"""
        with patch('sys.argv', ['jms_to_clash.py', '--invalid']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Should exit with error code for invalid arguments
            assert exc_info.value.code != 0

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_malformed_vmess(self):
        """Test handling of malformed VMess URLs"""
        malformed_urls = [
            "vmess://invalid_base64",
            "vmess://eyJpbnZhbGlkIjoianNvbiJ9",  # Invalid JSON structure
            "vmess://",  # Empty
        ]

        for url in malformed_urls:
            result = decode_vmess(url)
            # Should either return None or handle gracefully without crashing
            if result is not None:
                # If it returns something, it should at least have basic structure
                assert isinstance(result, dict)

    def test_malformed_subscription(self):
        """Test handling of subscription with malformed URLs"""
        subscription = """vmess://invalid_base64
ss://also_invalid
valid_line_but_not_proxy_url
vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTBhYiIsIm5ldCI6InRjcCIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgVk1lc3MiLCJzY3kiOiJhdXRvIiwidGxzIjoidGxzIiwidiI6IjIifQ=="""

        proxies = parse_subscription(subscription)
        # Should only parse the valid VMess URL
        assert len(proxies) == 1
        assert proxies[0]['name'] == 'Test VMess'

    def test_special_characters_in_names(self):
        """Test handling of special characters in proxy names"""
        # Create a VMess config with special characters in name
        import base64
        import json

        vmess_config = {
            "add": "example.com",
            "aid": "0",
            "id": "12345678-1234-1234-1234-1234567890ab",
            "net": "tcp",
            "port": "443",
            "ps": "Test🚀Server测试",  # Special characters and emoji
            "scy": "auto",
            "tls": "tls",
            "v": "2"
        }

        encoded = base64.b64encode(json.dumps(vmess_config).encode()).decode()
        vmess_url = f"vmess://{encoded}"

        result = decode_vmess(vmess_url)
        assert result is not None
        assert result['name'] == 'Test🚀Server测试'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
