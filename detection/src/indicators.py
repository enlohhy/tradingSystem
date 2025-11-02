# -*- coding: utf-8 -*-
"""
技术指标计算模块
包含：MA、MACD、KDJ、BOLL、VOL等技术指标
"""

import numpy as np
from typing import List, Dict, Tuple


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(prices: List[float], periods: List[int] = [5, 10, 20, 30, 60]) -> Dict[int, List[float]]:
        """
        计算移动平均线（MA）
        
        Args:
            prices: 价格列表
            periods: 周期列表
            
        Returns:
            各周期的MA值
        """
        result = {}
        prices_array = np.array(prices)
        
        for period in periods:
            if len(prices) >= period:
                ma = []
                for i in range(len(prices)):
                    if i >= period - 1:
                        ma_value = np.mean(prices_array[i - period + 1:i + 1])
                        ma.append(ma_value)
                    else:
                        ma.append(None)
                result[period] = ma
        
        return result
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线（EMA）
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            EMA值列表
        """
        ema = []
        multiplier = 2 / (period + 1)
        
        # 第一个EMA值使用SMA
        sma = np.mean(prices[:period])
        ema.append(sma)
        
        # 后续使用EMA公式
        for i in range(period, len(prices)):
            ema_value = (prices[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)
        
        return ema
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """
        计算MACD指标
        
        Args:
            prices: 价格列表
            fast: 快线周期（默认12）
            slow: 慢线周期（默认26）
            signal: 信号线周期（默认9）
            
        Returns:
            包含DIF、DEA、MACD的字典
        """
        if len(prices) < slow:
            return {"DIF": [], "DEA": [], "MACD": []}
        
        # 计算EMA
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow)
        
        # 计算DIF（快线-慢线）
        dif = []
        for i in range(len(ema_slow)):
            dif.append(ema_fast[i + (slow - fast)] - ema_slow[i])
        
        # 计算DEA（DIF的EMA）
        dea = TechnicalIndicators.calculate_ema(dif, signal)
        
        # 计算MACD柱（(DIF - DEA) * 2）
        macd = []
        for i in range(len(dea)):
            macd.append((dif[i + (signal - 1)] - dea[i]) * 2)
        
        return {
            "DIF": dif,
            "DEA": dea,
            "MACD": macd
        }
    
    @staticmethod
    def calculate_kdj(high: List[float], low: List[float], close: List[float], 
                      n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, List[float]]:
        """
        计算KDJ指标
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            n: RSV周期（默认9）
            m1: K值平滑周期（默认3）
            m2: D值平滑周期（默认3）
            
        Returns:
            包含K、D、J的字典
        """
        if len(close) < n:
            return {"K": [], "D": [], "J": []}
        
        k_values = []
        d_values = []
        j_values = []
        
        k = 50.0  # 初始K值
        d = 50.0  # 初始D值
        
        for i in range(n - 1, len(close)):
            # 计算RSV
            highest = max(high[i - n + 1:i + 1])
            lowest = min(low[i - n + 1:i + 1])
            
            if highest == lowest:
                rsv = 50
            else:
                rsv = (close[i] - lowest) / (highest - lowest) * 100
            
            # 计算K、D、J
            k = (rsv + (m1 - 1) * k) / m1
            d = (k + (m2 - 1) * d) / m2
            j = 3 * k - 2 * d
            
            k_values.append(k)
            d_values.append(d)
            j_values.append(j)
        
        return {
            "K": k_values,
            "D": d_values,
            "J": j_values
        }
    
    @staticmethod
    def calculate_boll(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        计算布林带（BOLL）
        
        Args:
            prices: 价格列表
            period: 周期（默认20）
            std_dev: 标准差倍数（默认2）
            
        Returns:
            包含上轨、中轨、下轨的字典
        """
        if len(prices) < period:
            return {"UPPER": [], "MIDDLE": [], "LOWER": []}
        
        upper = []
        middle = []
        lower = []
        
        prices_array = np.array(prices)
        
        for i in range(period - 1, len(prices)):
            window = prices_array[i - period + 1:i + 1]
            ma = np.mean(window)
            std = np.std(window)
            
            middle.append(ma)
            upper.append(ma + std_dev * std)
            lower.append(ma - std_dev * std)
        
        return {
            "UPPER": upper,
            "MIDDLE": middle,
            "LOWER": lower
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        计算RSI指标
        
        Args:
            prices: 价格列表
            period: 周期（默认14）
            
        Returns:
            RSI值列表
        """
        if len(prices) < period + 1:
            return []
        
        rsi_values = []
        gains = []
        losses = []
        
        # 计算价格变化
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))
        
        # 计算RSI
        for i in range(period - 1, len(gains)):
            avg_gain = np.mean(gains[i - period + 1:i + 1])
            avg_loss = np.mean(losses[i - period + 1:i + 1])
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """
        计算ATR（平均真实波幅）
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            period: 周期（默认14）
            
        Returns:
            ATR值列表
        """
        if len(close) < period + 1:
            return []
        
        tr_values = []
        
        # 计算真实波幅
        for i in range(1, len(close)):
            tr1 = high[i] - low[i]
            tr2 = abs(high[i] - close[i - 1])
            tr3 = abs(low[i] - close[i - 1])
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)
        
        # 计算ATR
        atr_values = []
        for i in range(period - 1, len(tr_values)):
            atr = np.mean(tr_values[i - period + 1:i + 1])
            atr_values.append(atr)
        
        return atr_values


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113, 115, 117, 116, 118, 120]
    
    indicators = TechnicalIndicators()
    
    print("测试MA指标:")
    ma = indicators.calculate_ma(test_prices, [5, 10])
    print(f"MA5最后值: {ma[5][-1]:.2f}")
    print(f"MA10最后值: {ma[10][-1]:.2f}")
    
    print("\n测试MACD指标:")
    macd = indicators.calculate_macd(test_prices)
    if macd["DIF"]:
        print(f"DIF最后值: {macd['DIF'][-1]:.4f}")
        print(f"DEA最后值: {macd['DEA'][-1]:.4f}")
        print(f"MACD最后值: {macd['MACD'][-1]:.4f}")
    
    print("\n测试完成！")

