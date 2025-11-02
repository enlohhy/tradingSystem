# -*- coding: utf-8 -*-
"""
币安K线历史数据获取模块
用于获取历史市场数据进行技术分析
参考: https://developers.binance.com/docs/binance-spot-api-docs/rest-api#klinecandlestick-data
"""

import requests
from typing import List, Dict
from datetime import datetime, timedelta


class BinanceKlineData:
    """币安K线数据获取器"""
    
    def __init__(self, api_url: str = "https://api.binance.com"):
        """
        初始化K线数据获取器
        
        Args:
            api_url: API基础URL
        """
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对，如 "BTCUSDT"
            interval: K线间隔，可选: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            limit: 获取数量，默认100，最大1000
            
        Returns:
            K线数据列表
        """
        try:
            url = f"{self.api_url}/api/v3/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            klines = response.json()
            
            # 格式化K线数据
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    "open_time": kline[0],  # 开盘时间
                    "open": float(kline[1]),  # 开盘价
                    "high": float(kline[2]),  # 最高价
                    "low": float(kline[3]),  # 最低价
                    "close": float(kline[4]),  # 收盘价
                    "volume": float(kline[5]),  # 成交量
                    "close_time": kline[6],  # 收盘时间
                    "quote_volume": float(kline[7]),  # 成交额
                    "trades": int(kline[8]),  # 成交笔数
                    "taker_buy_base": float(kline[9]),  # 主动买入成交量
                    "taker_buy_quote": float(kline[10])  # 主动买入成交额
                })
            
            return formatted_klines
            
        except requests.exceptions.RequestException as e:
            print(f"获取K线数据失败: {e}")
            return []
        except Exception as e:
            print(f"处理K线数据时出错: {e}")
            return []
    
    def get_klines_for_multiple_symbols(self, symbols: List[str], interval: str = "1h", limit: int = 100) -> Dict[str, List[Dict]]:
        """
        批量获取多个币种的K线数据
        
        Args:
            symbols: 交易对列表，如 ["BTCUSDT", "ETHUSDT"]
            interval: K线间隔
            limit: 每个币种获取的K线数量
            
        Returns:
            字典，key为交易对，value为K线数据列表
        """
        result = {}
        for symbol in symbols:
            klines = self.get_klines(symbol, interval, limit)
            if klines:
                result[symbol] = klines
        return result
    
    def format_klines_summary(self, symbol: str, klines: List[Dict]) -> str:
        """
        格式化K线数据摘要
        
        Args:
            symbol: 交易对
            klines: K线数据列表
            
        Returns:
            格式化后的文字摘要
        """
        if not klines:
            return f"{symbol}: 无K线数据"
        
        latest = klines[-1]
        first = klines[0]
        
        # 计算统计数据
        high_price = max(k["high"] for k in klines)
        low_price = min(k["low"] for k in klines)
        total_volume = sum(k["volume"] for k in klines)
        
        # 价格变化
        price_change = ((latest["close"] - first["open"]) / first["open"]) * 100
        
        result = []
        result.append(f"\n【{symbol} K线数据摘要】")
        result.append(f"  数据周期: {len(klines)} 根K线")
        result.append(f"  最新价格: ${latest['close']:,.2f}")
        result.append(f"  期间最高: ${high_price:,.2f}")
        result.append(f"  期间最低: ${low_price:,.2f}")
        result.append(f"  价格变化: {price_change:+.2f}%")
        result.append(f"  总成交量: {total_volume:,.2f}")
        result.append(f"  总成交笔数: {sum(k['trades'] for k in klines):,}")
        
        return "\n".join(result)
    
    def get_current_price(self, symbol: str) -> Dict:
        """
        获取当前最新价格（24小时ticker）
        
        Args:
            symbol: 交易对
            
        Returns:
            价格数据字典
        """
        try:
            url = f"{self.api_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol.upper()}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "symbol": symbol,
                "price": float(data.get("lastPrice", 0)),
                "change_24h": float(data.get("priceChangePercent", 0)),
                "volume_24h": float(data.get("quoteVolume", 0)),
                "high_24h": float(data.get("highPrice", 0)),
                "low_24h": float(data.get("lowPrice", 0))
            }
            
        except Exception as e:
            print(f"获取当前价格失败: {e}")
            return {}


# 测试代码
if __name__ == "__main__":
    kline_client = BinanceKlineData()
    
    # 测试获取K线数据
    print("正在获取BTC K线数据...")
    klines = kline_client.get_klines("BTCUSDT", "1h", 24)
    
    if klines:
        print(f"成功获取 {len(klines)} 根K线")
        print(kline_client.format_klines_summary("BTCUSDT", klines))
    else:
        print("获取失败")

