# -*- coding: utf-8 -*-
"""快速测试K线数据获取"""
import sys
import os
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.binance_kline import BinanceKlineData
from colorama import init, Fore, Style

init(autoreset=True)

print(Fore.CYAN + "=" * 80)
print(Fore.YELLOW + Style.BRIGHT + ">>> 测试K线数据获取 <<<")
print(Fore.CYAN + "=" * 80 + "\n")

kline_client = BinanceKlineData()

# 测试获取BTC的1小时K线数据
print(f"{Fore.GREEN}正在获取BTC最近24小时K线数据...{Style.RESET_ALL}\n")

klines = kline_client.get_klines("BTCUSDT", "1h", 24)

if klines:
    print(f"{Fore.GREEN}✓ 成功获取 {len(klines)} 根K线{Style.RESET_ALL}")
    print(kline_client.format_klines_summary("BTCUSDT", klines))
    
    # 显示前3根K线详情
    print(f"\n{Fore.CYAN}前3根K线详情:{Style.RESET_ALL}")
    for i, kline in enumerate(klines[:3], 1):
        print(f"\nK线 {i}:")
        print(f"  开盘: ${kline['open']:,.2f}")
        print(f"  最高: ${kline['high']:,.2f}")
        print(f"  最低: ${kline['low']:,.2f}")
        print(f"  收盘: ${kline['close']:,.2f}")
        print(f"  成交量: {kline['volume']:,.4f}")
    
    print(f"\n{Fore.GREEN}✓ K线数据获取测试通过！{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}✗ 获取失败{Style.RESET_ALL}")

# 测试获取当前价格
print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
print(f"{Fore.GREEN}正在获取当前价格...{Style.RESET_ALL}\n")

price = kline_client.get_current_price("BTCUSDT")

if price:
    print(f"{Fore.GREEN}✓ 当前价格获取成功{Style.RESET_ALL}")
    print(f"  价格: ${price['price']:,.2f}")
    print(f"  24h涨跌: {price['change_24h']:+.2f}%")
    print(f"  24h最高: ${price['high_24h']:,.2f}")
    print(f"  24h最低: ${price['low_24h']:,.2f}")
else:
    print(f"{Fore.RED}✗ 获取失败{Style.RESET_ALL}")

print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
print(f"{Fore.GREEN}测试完成！{Style.RESET_ALL}\n")

