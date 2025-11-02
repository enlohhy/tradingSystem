# -*- coding: utf-8 -*-
"""
配置加载模块
负责加载和管理配置文件
"""

import yaml
import os
from typing import Dict, List


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"配置文件未找到: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "cryptocurrencies": ["BTC", "ETH", "SOL", "DOGE"],
            "binance": {
                "ws_url": "wss://stream.binance.com:9443",
                "api_url": "https://api.binance.com",
                "symbol_map": {
                    "BTC": "BTCUSDT",
                    "ETH": "ETHUSDT",
                    "SOL": "SOLUSDT",
                    "DOGE": "DOGEUSDT"
                }
            }
        }
    
    def get_cryptocurrencies(self) -> List[str]:
        """获取监测的币种列表"""
        return self.config.get("cryptocurrencies", [])
    
    def get_binance_config(self) -> Dict:
        """获取币安配置"""
        return self.config.get("binance", {})
    
    def get_ws_url(self) -> str:
        """获取WebSocket URL"""
        return self.get_binance_config().get("ws_url", "wss://stream.binance.com:9443")
    
    def get_api_url(self) -> str:
        """获取REST API URL"""
        return self.get_binance_config().get("api_url", "https://api.binance.com")
    
    def get_symbol_map(self) -> Dict[str, str]:
        """获取币种交易对映射"""
        return self.get_binance_config().get("symbol_map", {})

