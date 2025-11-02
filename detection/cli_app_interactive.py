# -*- coding: utf-8 -*-
"""
加密货币实时监测应用 - 交互式版本
支持实时推送和手动获取两种模式
支持技术分析（获取历史数据）
"""

import sys
import os
import time
import io
import threading
from datetime import datetime
from colorama import init, Fore, Back, Style

# Windows专用模块
if sys.platform == 'win32':
    import msvcrt

# Windows编码兼容性设置
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# 初始化colorama
init(autoreset=True)

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.binance_websocket import BinanceWebSocket
from src.binance_kline import BinanceKlineData
from src.config_loader import ConfigLoader
from src.trading_advisor import TradingAdvisor
from typing import Dict, Any


# 全局变量
latest_data = {}
data_lock = threading.Lock()
realtime_mode = True  # 实时模式开关
ws_client = None
running = True
need_refresh = False  # 需要刷新标志


def clear_screen():
    """清空屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """打印标题"""
    print("\n" + Fore.CYAN + "=" * 80)
    print(Fore.YELLOW + Style.BRIGHT + " " * 20 + ">>> 加密货币智能监测系统 <<<")
    print(Fore.CYAN + "=" * 80 + "\n" + Style.RESET_ALL)


def print_controls():
    """打印控制说明"""
    mode_status = f"{Fore.GREEN}实时推送中" if realtime_mode else f"{Fore.YELLOW}已暂停"
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}控制面板:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[空格]{Style.RESET_ALL} 切换实时/暂停模式  {mode_status}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[R]{Style.RESET_ALL}     手动刷新数据")
    print(f"  {Fore.GREEN}[A]{Style.RESET_ALL}     技术分析（获取历史数据）")
    print(f"  {Fore.GREEN}[Q]{Style.RESET_ALL}     退出程序")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")


def format_price(price):
    """格式化价格显示"""
    if price < 1:
        return f"${price:.6f}"
    else:
        return f"${price:,.2f}"


def print_crypto_info(coin_data):
    """打印单个币种的详细信息"""
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
    """价格更新回调函数"""
    global latest_data
    if realtime_mode:
        with data_lock:
            latest_data[symbol] = data


def manual_refresh(config):
    """手动刷新数据"""
    global latest_data, need_refresh
    
    print(f"\n{Fore.YELLOW}正在手动获取最新数据...{Style.RESET_ALL}")
    
    kline_client = BinanceKlineData()
    symbols = config.get_cryptocurrencies()
    symbol_map = config.get_symbol_map()
    
    with data_lock:
        for symbol in symbols:
            trading_pair = symbol_map.get(symbol, f"{symbol}USDT")
            price_data = kline_client.get_current_price(trading_pair)
            
            if price_data:
                latest_data[trading_pair.lower()] = {
                    "symbol": symbol,
                    "price": price_data["price"],
                    "change_24h": price_data["change_24h"],
                    "volume_24h": price_data["volume_24h"],
                    "high_24h": price_data["high_24h"],
                    "low_24h": price_data["low_24h"]
                }
    
    need_refresh = True  # 标记需要刷新显示
    print(f"{Fore.GREEN}✓ 数据刷新完成{Style.RESET_ALL}")
    time.sleep(0.5)


def perform_technical_analysis(config):
    """执行技术分析（获取历史数据并进行专业分析）"""
    clear_screen()
    print_header()
    
    print(f"{Fore.YELLOW}{Style.BRIGHT}>>> 专业技术分析系统 <<<{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}分析理论：斐波那契、波浪理论、缠论、威科夫交易法{Style.RESET_ALL}")
    print(f"{Fore.WHITE}技术指标：MA、MACD、KDJ、BOLL、RSI、ATR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    kline_client = BinanceKlineData()
    advisor = TradingAdvisor()
    symbols = config.get_cryptocurrencies()
    symbol_map = config.get_symbol_map()
    
    for symbol in symbols:
        trading_pair = symbol_map.get(symbol, f"{symbol}USDT")
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}{'█' * 80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}正在分析 {symbol} ({trading_pair})...{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}{'█' * 80}{Style.RESET_ALL}\n")
        
        # 获取足够的K线数据用于分析（100根1小时K线）
        print(f"{Fore.CYAN}[1/5] 获取K线数据...{Style.RESET_ALL}")
        klines = kline_client.get_klines(trading_pair, "1h", 100)
        
        if not klines or len(klines) < 30:
            print(f"{Fore.RED}✗ K线数据不足，跳过{Style.RESET_ALL}\n")
            continue
        
        print(f"{Fore.GREEN}✓ 成功获取 {len(klines)} 根K线{Style.RESET_ALL}")
        
        # 进行综合分析
        print(f"{Fore.CYAN}[2/5] 计算技术指标...{Style.RESET_ALL}")
        try:
            analysis = advisor.analyze_comprehensive(klines)
            
            if "error" in analysis:
                print(f"{Fore.RED}✗ {analysis['error']}{Style.RESET_ALL}\n")
                continue
            
            print(f"{Fore.GREEN}✓ 指标计算完成{Style.RESET_ALL}")
            
            # 显示分析结果
            print(f"\n{Fore.CYAN}[3/5] 技术指标分析{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-' * 80}{Style.RESET_ALL}")
            display_indicator_analysis(analysis)
            
            print(f"\n{Fore.CYAN}[4/5] 交易理论分析{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-' * 80}{Style.RESET_ALL}")
            display_theory_analysis(analysis)
            
            print(f"\n{Fore.CYAN}[5/5] 交易建议{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-' * 80}{Style.RESET_ALL}")
            display_trading_recommendations(symbol, analysis)
            
        except Exception as e:
            print(f"{Fore.RED}✗ 分析出错: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}所有币种分析完成！{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}按任意键返回主界面...{Style.RESET_ALL}")
    
    # 等待按键
    if sys.platform == 'win32':
        msvcrt.getch()
    else:
        input()


def display_indicator_analysis(analysis: Dict):
    """显示技术指标分析结果"""
    indicators = analysis["indicators"]
    
    # MA均线
    ma = indicators["MA"]
    print(f"\n{Fore.WHITE}【MA均线】{Style.RESET_ALL}")
    print(f"  趋势: {Fore.YELLOW}{ma['trend']}{Style.RESET_ALL} (评分: {ma['score']})")
    for signal in ma['signals'][:3]:
        print(f"  • {signal}")
    
    # MACD
    macd = indicators["MACD"]
    print(f"\n{Fore.WHITE}【MACD】{Style.RESET_ALL}")
    print(f"  信号: {Fore.YELLOW}{macd['signal']}{Style.RESET_ALL} (评分: {macd['score']:.1f})")
    for detail in macd['details']:
        print(f"  • {detail}")
    
    # KDJ
    kdj = indicators["KDJ"]
    print(f"\n{Fore.WHITE}【KDJ】{Style.RESET_ALL}")
    print(f"  信号: {Fore.YELLOW}{kdj['signal']}{Style.RESET_ALL} (K:{kdj['values']['K']:.2f} D:{kdj['values']['D']:.2f} J:{kdj['values']['J']:.2f})")
    for detail in kdj['details']:
        print(f"  • {detail}")
    
    # BOLL
    boll = indicators["BOLL"]
    print(f"\n{Fore.WHITE}【BOLL布林带】{Style.RESET_ALL}")
    print(f"  信号: {Fore.YELLOW}{boll['signal']}{Style.RESET_ALL}")
    for detail in boll['details']:
        print(f"  • {detail}")
    
    # RSI
    rsi = indicators["RSI"]
    print(f"\n{Fore.WHITE}【RSI】{Style.RESET_ALL}")
    print(f"  信号: {Fore.YELLOW}{rsi['signal']}{Style.RESET_ALL} (RSI: {rsi['value']:.2f})")


def display_theory_analysis(analysis: Dict):
    """显示交易理论分析结果"""
    # 斐波那契
    fib = analysis["fibonacci"]
    print(f"\n{Fore.WHITE}【斐波那契】{Style.RESET_ALL}")
    print(f"  区间: ${fib['low']:.2f} - ${fib['high']:.2f}")
    if fib['support']:
        print(f"  支撑位: {', '.join([f'${s:.2f}' for s in fib['support'][:3]])}")
    if fib['resistance']:
        print(f"  阻力位: {', '.join([f'${r:.2f}' for r in fib['resistance'][:3]])}")
    
    # 波浪理论
    elliott = analysis["elliott_wave"]
    print(f"\n{Fore.WHITE}【波浪理论】{Style.RESET_ALL}")
    print(f"  形态: {elliott['pattern']['pattern']}")
    print(f"  预测: {elliott['prediction']['prediction']}")
    print(f"  可信度: {elliott['prediction']['confidence']*100:.0f}%")
    
    # 缠论
    chan = analysis["chan_theory"]
    print(f"\n{Fore.WHITE}【缠论】{Style.RESET_ALL}")
    print(f"  趋势: {chan['trend']['trend']}")
    print(f"  强度: {chan['trend']['strength']*100:.0f}%")
    
    # 威科夫
    wyckoff = analysis["wyckoff"]
    print(f"\n{Fore.WHITE}【威科夫交易法】{Style.RESET_ALL}")
    print(f"  阶段: {wyckoff['phase']['phase']}")
    print(f"  操作建议: {wyckoff['phase']['action']}")
    print(f"  供需关系: {wyckoff['supply_demand']['balance']}")


def display_trading_recommendations(symbol: str, analysis: Dict):
    """显示交易建议"""
    rec = analysis["recommendations"]
    score = analysis["score"]
    
    # 综合评分
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}【综合评分】{Style.RESET_ALL}")
    score_color = Fore.GREEN if score['total'] > 60 else Fore.RED if score['total'] < 40 else Fore.YELLOW
    print(f"  总分: {score_color}{Style.BRIGHT}{score['total']}/100{Style.RESET_ALL}")
    print(f"  • 技术指标: {score['indicator_score']:.2f}")
    print(f"  • 波浪理论: {score['elliott_score']:.2f}")
    print(f"  • 缠论: {score['chan_score']:.2f}")
    print(f"  • 威科夫: {score['wyckoff_score']:.2f}")
    
    # 交易方向
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}【交易建议】{Style.RESET_ALL}")
    direction_color = Fore.GREEN if rec['direction'].startswith("做多") else Fore.RED if rec['direction'].startswith("做空") else Fore.WHITE
    print(f"  方向: {direction_color}{Style.BRIGHT}{rec['direction']}{Style.RESET_ALL}")
    print(f"  可信度: {rec['confidence']}")
    
    # 时间周期预测
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}【走势预测】{Style.RESET_ALL}")
    predictions = rec['predictions']
    print(f"  15分钟: {predictions['15min']}")
    print(f"  1小时: {predictions['1h']}")
    print(f"  4小时: {predictions['4h']}")
    print(f"  24小时: {predictions['24h']}")
    
    # 止损止盈位
    if rec['stop_loss']['15min'] is not None:
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}【止损位】{Style.RESET_ALL}")
        for timeframe, price in rec['stop_loss'].items():
            if price:
                print(f"  {timeframe}: ${price:.2f}")
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}【止盈位】{Style.RESET_ALL}")
        for timeframe, price in rec['take_profit'].items():
            if price:
                print(f"  {timeframe}: ${price:.2f}")
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}【风险收益比】{Style.RESET_ALL}")
        for timeframe, ratio in rec['risk_reward_ratio'].items():
            if ratio:
                ratio_color = Fore.GREEN if ratio >= 2 else Fore.YELLOW if ratio >= 1 else Fore.RED
                print(f"  {timeframe}: {ratio_color}{ratio:.2f}:1{Style.RESET_ALL}")
    
    # 风险提示
    print(f"\n{Fore.RED}{Style.BRIGHT}【风险提示】{Style.RESET_ALL}")
    print(f"{Fore.RED}  • 本分析仅供参考，不构成投资建议{Style.RESET_ALL}")
    print(f"{Fore.RED}  • 请根据自身情况设置止损，控制风险{Style.RESET_ALL}")
    print(f"{Fore.RED}  • 市场有风险，投资需谨慎{Style.RESET_ALL}")


def keyboard_listener():
    """键盘监听线程（Windows）"""
    global realtime_mode, running, need_refresh, ws_client
    
    if sys.platform != 'win32':
        return
    
    # 保存配置用于WebSocket重连
    config = ConfigLoader()
    symbols = config.get_cryptocurrencies()
    
    while running:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            # 空格键 - 切换实时/暂停
            if key == b' ':
                realtime_mode = not realtime_mode
                need_refresh = True  # 切换模式后立即刷新显示
                
                # 控制WebSocket连接
                if realtime_mode:
                    # 恢复实时模式 - 重新连接WebSocket
                    status = "实时推送"
                    print(f"\n{Fore.YELLOW}>>> 正在切换到: {status} 模式{Style.RESET_ALL}")
                    if ws_client:
                        ws_client.resume(symbols, on_price_update)
                else:
                    # 暂停模式 - 断开WebSocket
                    status = "暂停"
                    print(f"\n{Fore.YELLOW}>>> 正在切换到: {status} 模式{Style.RESET_ALL}")
                    if ws_client:
                        ws_client.pause()
                
                print(f"{Fore.GREEN}✓ 已切换到: {status} 模式{Style.RESET_ALL}")
                time.sleep(0.5)
            
            # R键 - 手动刷新
            elif key.lower() == b'r':
                config = ConfigLoader()
                manual_refresh(config)
            
            # A键 - 技术分析
            elif key.lower() == b'a':
                config = ConfigLoader()
                perform_technical_analysis(config)
                need_refresh = True  # 分析后刷新显示
            
            # Q键 - 退出
            elif key.lower() == b'q':
                running = False
        
        time.sleep(0.1)


def display_loop(config):
    """显示循环"""
    global latest_data, running, need_refresh, realtime_mode
    
    last_refresh_time = time.time()
    
    while running:
        current_time_sec = time.time()
        
        # 刷新条件：
        # 1. 实时模式：每3秒刷新
        # 2. 暂停模式：只在需要时刷新（手动刷新或模式切换）
        should_refresh = False
        
        if realtime_mode:
            # 实时模式：每3秒刷新
            if current_time_sec - last_refresh_time >= 3:
                should_refresh = True
        else:
            # 暂停模式：只在标志为True时刷新
            if need_refresh:
                should_refresh = True
                need_refresh = False  # 重置标志
        
        if should_refresh:
            # 清空屏幕
            clear_screen()
            
            # 打印标题
            print_header()
            
            # 显示更新时间和状态
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mode_text = f"{Fore.GREEN}实时推送中" if realtime_mode else f"{Fore.YELLOW}已暂停（按R手动刷新）"
            
            print(f"{Fore.GREEN}更新时间: {Fore.YELLOW}{current_time}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}数据源: {Fore.YELLOW}币安WebSocket{Style.RESET_ALL}")
            print(f"{Fore.GREEN}模式: {mode_text}{Style.RESET_ALL}\n")
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
            
            # 显示控制说明
            print_controls()
            
            last_refresh_time = current_time_sec
        
        # 短暂休眠，避免CPU占用过高
        time.sleep(0.5)


def main():
    """主函数"""
    global data_lock, ws_client, running
    
    data_lock = threading.Lock()
    
    # 加载配置
    config = ConfigLoader()
    symbols = config.get_cryptocurrencies()
    
    print(f"\n{Fore.GREEN}>>> 正在启动加密货币智能监测系统...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}数据源: {Fore.YELLOW}币安WebSocket + REST API{Style.RESET_ALL}")
    print(f"{Fore.CYAN}监测币种: {Fore.YELLOW}{', '.join(symbols)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}功能: {Fore.YELLOW}实时推送 + 手动刷新 + 技术分析{Style.RESET_ALL}")
    
    # 创建WebSocket客户端
    ws_client = BinanceWebSocket()
    
    # 启动WebSocket
    print(f"\n{Fore.YELLOW}正在连接WebSocket...{Style.RESET_ALL}")
    ws_client.connect(symbols, on_price_update)
    
    # 等待初始数据
    time.sleep(2)
    
    # 启动键盘监听线程（Windows）
    if sys.platform == 'win32':
        keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
        keyboard_thread.start()
        print(f"{Fore.GREEN}✓ 键盘控制已启用{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}! 非Windows系统，键盘控制不可用{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}系统启动完成！{Style.RESET_ALL}")
    time.sleep(2)
    
    try:
        # 开始显示循环
        display_loop(config)
    except KeyboardInterrupt:
        pass
    finally:
        running = False
        if ws_client:
            ws_client.close()
        print(f"\n\n{Fore.GREEN}感谢使用加密货币监测系统！{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()

