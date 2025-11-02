# -*- coding: utf-8 -*-
"""
加密货币实时监测应用 - WebSocket版本
使用币安WebSocket接收实时价格推送
"""

import sys
import os
import time
import io
import threading
from datetime import datetime
from colorama import init, Fore, Back, Style

# Windows编码兼容性设置
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 初始化colorama（Windows下需要）
init(autoreset=True)

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.binance_websocket import BinanceWebSocket
from src.config_loader import ConfigLoader


# 全局变量存储最新数据
latest_data = {}
data_lock = threading.Lock()


def clear_screen():
    """清空屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """打印标题"""
    print("\n" + Fore.CYAN + "=" * 80)
    print(Fore.YELLOW + Style.BRIGHT + " " * 22 + ">>> 加密货币实时监测系统 <<<")
    print(Fore.CYAN + "=" * 80 + "\n" + Style.RESET_ALL)


def format_price(price):
    """格式化价格显示"""
    if price < 1:
        return f"${price:.6f}"
    else:
        return f"${price:,.2f}"


def print_crypto_info(coin_data):
    """
    打印单个币种的详细信息（带颜色）
    
    Args:
        coin_data: 币种数据字典
    """
    symbol = coin_data["symbol"]
    price = coin_data["price"]
    change_24h = coin_data["change_24h"]
    volume_24h = coin_data.get("volume_24h", 0)
    high_24h = coin_data.get("high_24h", 0)
    low_24h = coin_data.get("low_24h", 0)
    
    # 价格变化方向指示和颜色
    if change_24h > 0:
        change_indicator = "▲"
        change_text = "涨"
        change_color = Fore.GREEN
    elif change_24h < 0:
        change_indicator = "▼"
        change_text = "跌"
        change_color = Fore.RED
    else:
        change_indicator = "="
        change_text = "平"
        change_color = Fore.YELLOW
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}【{symbol}】{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}当前价格:      {Fore.YELLOW}{format_price(price)}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}24小时涨跌:    {change_color}{change_indicator} {change_24h:+.2f}% ({change_text}){Style.RESET_ALL}")
    
    if volume_24h > 0:
        print(f"  {Fore.WHITE}24小时交易量:  {Fore.MAGENTA}${volume_24h:,.0f}{Style.RESET_ALL}")
    
    if high_24h > 0:
        print(f"  {Fore.WHITE}24小时最高:    {Fore.GREEN}{format_price(high_24h)}{Style.RESET_ALL}")
    
    if low_24h > 0:
        print(f"  {Fore.WHITE}24小时最低:    {Fore.RED}{format_price(low_24h)}{Style.RESET_ALL}")
    
    print(Fore.CYAN + "-" * 80 + Style.RESET_ALL)


def get_simple_summary(price_data_list):
    """获取简洁摘要"""
    if not price_data_list:
        return "暂无数据"
    
    result = []
    for coin in price_data_list:
        symbol = coin["symbol"]
        price = coin["price"]
        change_24h = coin["change_24h"]
        
        change_indicator = "+" if change_24h > 0 else "-" if change_24h < 0 else "="
        
        if price < 1:
            result.append(f"{symbol}: ${price:.6f} ({change_indicator}{abs(change_24h):.2f}%)")
        else:
            result.append(f"{symbol}: ${price:,.2f} ({change_indicator}{abs(change_24h):.2f}%)")
    
    return " | ".join(result)


def on_price_update(symbol, data):
    """
    价格更新回调函数
    
    Args:
        symbol: 交易对符号（小写）
        data: 格式化的价格数据
    """
    global latest_data
    with data_lock:
        latest_data[symbol] = data


def display_loop(ws_client, config):
    """显示循环"""
    global latest_data
    
    print(f"\n{Fore.GREEN}WebSocket已连接，正在接收实时数据...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}数据将实时更新显示（每3秒刷新屏幕）{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}按 Ctrl+C 退出{Style.RESET_ALL}\n")
    time.sleep(3)
    
    try:
        while True:
            # 清空屏幕
            clear_screen()
            
            # 打印标题
            print_header()
            
            # 显示更新时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Fore.GREEN}更新时间: {Fore.YELLOW}{current_time}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}数据源: {Fore.YELLOW}币安WebSocket (实时推送){Style.RESET_ALL}\n")
            print(Fore.CYAN + "=" * 80 + Style.RESET_ALL)
            
            # 获取当前数据
            with data_lock:
                current_data = list(latest_data.values())
            
            if current_data:
                # 按币种排序
                current_data.sort(key=lambda x: x["symbol"])
                
                # 显示每个币种的信息
                for coin in current_data:
                    print_crypto_info(coin)
                
                # 显示简洁摘要
                print("\n" + Fore.CYAN + "=" * 80)
                print(Fore.GREEN + Style.BRIGHT + "简洁概览:" + Style.RESET_ALL)
                print(Fore.WHITE + get_simple_summary(current_data) + Style.RESET_ALL)
                print(Fore.CYAN + "=" * 80 + Style.RESET_ALL)
            else:
                print(f"\n{Fore.YELLOW}正在等待数据...{Style.RESET_ALL}")
            
            # 每3秒刷新一次显示
            time.sleep(3)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}感谢使用加密货币监测系统！{Style.RESET_ALL}\n")
        ws_client.close()
        sys.exit(0)


def main():
    """主函数"""
    # 让全局变量在函数中可用
    global data_lock
    data_lock = threading.Lock()
    
    # 加载配置
    config = ConfigLoader()
    
    # 获取监测币种
    symbols = config.get_cryptocurrencies()
    
    print(f"\n{Fore.GREEN}>>> 正在启动加密货币实时监测系统...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}数据源: {Fore.YELLOW}币安WebSocket{Style.RESET_ALL}")
    print(f"{Fore.CYAN}监测币种: {Fore.YELLOW}{', '.join(symbols)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}推送模式: {Fore.YELLOW}实时推送（无延迟）{Style.RESET_ALL}")
    
    # 创建WebSocket客户端
    ws_client = BinanceWebSocket()
    
    # 连接到WebSocket
    ws_client.connect(symbols, on_price_update)
    
    # 等待初始数据
    time.sleep(2)
    
    # 开始显示循环
    display_loop(ws_client, config)


if __name__ == "__main__":
    main()
