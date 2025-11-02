# -*- coding: utf-8 -*-
"""
币安WebSocket数据流模块
实时接收币安推送的价格数据
参考文档: https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams
"""

import json
import threading
import time
from typing import Dict, Callable, List
import websocket
import requests


class BinanceWebSocket:
    """币安WebSocket客户端"""
    
    def __init__(self):
        """初始化WebSocket客户端"""
        self.ws = None
        self.base_url = "wss://stream.binance.com:9443"
        self.api_base = "https://api.binance.com"
        
        # 存储最新价格数据
        self.price_data = {}
        self.ticker_data = {}
        
        # 回调函数
        self.on_update_callback = None
        
        # 运行标志
        self.running = False
        
        # 币种符号映射
        self.symbol_map = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "DOGE": "DOGEUSDT",
            "BNB": "BNBUSDT"
        }
    
    def get_initial_ticker_data(self, symbols: List[str]) -> Dict:
        """
        获取初始的24小时ticker数据
        
        Args:
            symbols: 币种符号列表
            
        Returns:
            初始ticker数据
        """
        ticker_data = {}
        try:
            for symbol in symbols:
                trading_pair = self.symbol_map.get(symbol, f"{symbol}USDT")
                url = f"{self.api_base}/api/v3/ticker/24hr"
                params = {"symbol": trading_pair}
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    ticker_data[trading_pair.lower()] = {
                        "high": float(data.get("highPrice", 0)),
                        "low": float(data.get("lowPrice", 0)),
                        "volume": float(data.get("quoteVolume", 0)),
                        "change": float(data.get("priceChangePercent", 0))
                    }
        except Exception as e:
            print(f"获取初始ticker数据失败: {e}")
        
        return ticker_data
    
    def connect(self, symbols: List[str], on_update: Callable = None):
        """
        连接到币安WebSocket并订阅价格流
        
        Args:
            symbols: 要监测的币种符号列表，如 ["BTC", "ETH"]
            on_update: 价格更新时的回调函数
        """
        self.on_update_callback = on_update
        self.running = True
        
        # 获取初始ticker数据
        print("正在获取初始数据...")
        self.ticker_data = self.get_initial_ticker_data(symbols)
        
        # 构建流名称列表
        streams = []
        for symbol in symbols:
            trading_pair = self.symbol_map.get(symbol, f"{symbol}USDT")
            # 订阅ticker流（24小时滚动统计）
            streams.append(f"{trading_pair.lower()}@ticker")
        
        # 构建WebSocket URL（组合流）
        stream_names = "/".join(streams)
        ws_url = f"{self.base_url}/stream?streams={stream_names}"
        
        print(f"正在连接到币安WebSocket...")
        print(f"订阅的交易对: {', '.join([self.symbol_map.get(s, f'{s}USDT') for s in symbols])}")
        
        # 创建WebSocket连接
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # 在新线程中运行WebSocket
        ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
        ws_thread.start()
    
    def _run_websocket(self):
        """在后台线程中运行WebSocket"""
        while self.running:
            try:
                self.ws.run_forever(
                    ping_interval=20,
                    ping_timeout=10
                )
            except Exception as e:
                print(f"WebSocket运行错误: {e}")
                if self.running:
                    print("5秒后重新连接...")
                    time.sleep(5)
    
    def _on_open(self, ws):
        """WebSocket连接打开时的回调"""
        print("✓ WebSocket连接成功，开始接收实时数据...")
        print(f"连接URL: {ws.url}")
    
    def _on_message(self, ws, message):
        """接收到消息时的回调"""
        try:
            data = json.loads(message)
            
            # 处理ticker数据
            if "data" in data:
                ticker = data["data"]
                if ticker.get("e") == "24hrTicker":
                    symbol = ticker["s"].lower()  # 如 "btcusdt"
                    
                    # 更新ticker数据
                    self.ticker_data[symbol] = {
                        "high": float(ticker.get("h", 0)),
                        "low": float(ticker.get("l", 0)),
                        "volume": float(ticker.get("q", 0)),
                        "change": float(ticker.get("P", 0))
                    }
                    
                    # 更新价格数据
                    self.price_data[symbol] = {
                        "price": float(ticker.get("c", 0)),
                        "time": ticker.get("E", 0) / 1000  # 转换为秒
                    }
                    
                    # 调用更新回调
                    if self.on_update_callback:
                        self.on_update_callback(symbol, self.get_formatted_data(symbol))
            else:
                # 直接ticker数据（非stream格式）
                if data.get("e") == "24hrTicker":
                    symbol = data["s"].lower()
                    
                    self.ticker_data[symbol] = {
                        "high": float(data.get("h", 0)),
                        "low": float(data.get("l", 0)),
                        "volume": float(data.get("q", 0)),
                        "change": float(data.get("P", 0))
                    }
                    
                    self.price_data[symbol] = {
                        "price": float(data.get("c", 0)),
                        "time": data.get("E", 0) / 1000
                    }
                    
                    if self.on_update_callback:
                        self.on_update_callback(symbol, self.get_formatted_data(symbol))
                        
        except Exception as e:
            print(f"处理消息错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_error(self, ws, error):
        """WebSocket错误时的回调"""
        print(f"WebSocket错误: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭时的回调"""
        print(f"WebSocket连接已关闭")
        if self.running:
            print("正在尝试重新连接...")
    
    def get_formatted_data(self, symbol: str) -> Dict:
        """
        获取格式化的价格数据
        
        Args:
            symbol: 交易对符号（小写），如 "btcusdt"
            
        Returns:
            格式化的数据字典
        """
        price_info = self.price_data.get(symbol, {})
        ticker_info = self.ticker_data.get(symbol, {})
        
        # 提取币种符号（去掉USDT）
        coin_symbol = symbol.replace("usdt", "").upper()
        
        return {
            "symbol": coin_symbol,
            "price": price_info.get("price", 0),
            "change_24h": ticker_info.get("change", 0),
            "volume_24h": ticker_info.get("volume", 0),
            "high_24h": ticker_info.get("high", 0),
            "low_24h": ticker_info.get("low", 0),
            "last_updated": price_info.get("time", 0)
        }
    
    def get_all_data(self) -> List[Dict]:
        """
        获取所有币种的格式化数据
        
        Returns:
            所有币种的数据列表
        """
        result = []
        for symbol in self.price_data.keys():
            result.append(self.get_formatted_data(symbol))
        return result
    
    def pause(self):
        """暂停WebSocket连接（停止自动重连）"""
        self.running = False
        if self.ws:
            self.ws.close()
        print("WebSocket已暂停，停止自动重连")
    
    def resume(self, symbols: List[str], on_update: Callable = None):
        """恢复WebSocket连接"""
        if not self.running:
            print("正在恢复WebSocket连接...")
            self.connect(symbols, on_update)
    
    def close(self):
        """关闭WebSocket连接"""
        self.running = False
        if self.ws:
            self.ws.close()
        print("WebSocket连接已断开")


# 测试代码
if __name__ == "__main__":
    import time
    from colorama import init, Fore, Style
    
    init(autoreset=True)
    
    def on_price_update(symbol, data):
        """价格更新回调"""
        price = data['price']
        change = data['change_24h']
        
        if change > 0:
            color = Fore.GREEN
            indicator = "▲"
        elif change < 0:
            color = Fore.RED
            indicator = "▼"
        else:
            color = Fore.YELLOW
            indicator = "="
        
        print(f"{Fore.CYAN}{data['symbol']}{Style.RESET_ALL}: "
              f"${price:,.2f} "
              f"{color}{indicator} {change:+.2f}%{Style.RESET_ALL}")
    
    # 创建WebSocket客户端
    ws_client = BinanceWebSocket()
    
    # 连接并订阅
    symbols = ["BTC", "ETH", "SOL", "DOGE"]
    ws_client.connect(symbols, on_price_update)
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭...")
        ws_client.close()

