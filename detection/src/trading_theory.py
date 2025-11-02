# -*- coding: utf-8 -*-
"""
交易理论分析模块
包含：斐波那契、波浪理论、缠论、威科夫交易法
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class FibonacciAnalysis:
    """斐波那契分析"""
    
    # 斐波那契回调比例
    RETRACEMENT_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
    # 斐波那契扩展比例
    EXTENSION_LEVELS = [1.272, 1.414, 1.618, 2.0, 2.618]
    
    @staticmethod
    def calculate_retracement(high: float, low: float) -> Dict[float, float]:
        """
        计算斐波那契回调位
        
        Args:
            high: 高点
            low: 低点
            
        Returns:
            各回调位的价格
        """
        diff = high - low
        levels = {}
        
        for ratio in FibonacciAnalysis.RETRACEMENT_LEVELS:
            levels[ratio] = high - (diff * ratio)
        
        return levels
    
    @staticmethod
    def calculate_extension(start: float, end: float, retrace: float) -> Dict[float, float]:
        """
        计算斐波那契扩展位
        
        Args:
            start: 起始点
            end: 结束点
            retrace: 回调点
            
        Returns:
            各扩展位的价格
        """
        diff = end - start
        levels = {}
        
        for ratio in FibonacciAnalysis.EXTENSION_LEVELS:
            levels[ratio] = retrace + (diff * ratio)
        
        return levels
    
    @staticmethod
    def find_support_resistance(current_price: float, high: float, low: float) -> Dict[str, List[float]]:
        """
        找出支撑位和阻力位
        
        Args:
            current_price: 当前价格
            high: 高点
            low: 低点
            
        Returns:
            支撑位和阻力位
        """
        retracement = FibonacciAnalysis.calculate_retracement(high, low)
        
        support = []
        resistance = []
        
        for ratio, price in retracement.items():
            if price < current_price:
                support.append(price)
            else:
                resistance.append(price)
        
        return {
            "support": sorted(support, reverse=True),
            "resistance": sorted(resistance)
        }


class ElliottWaveAnalysis:
    """艾略特波浪理论分析"""
    
    @staticmethod
    def identify_wave_pattern(prices: List[float]) -> Dict[str, any]:
        """
        识别波浪形态
        
        Args:
            prices: 价格列表
            
        Returns:
            波浪形态信息
        """
        if len(prices) < 8:
            return {"pattern": "数据不足", "phase": "未知"}
        
        # 简化的波浪识别（实际应用需要更复杂的算法）
        peaks = []
        troughs = []
        
        # 找出峰值和谷值
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i - 1] and prices[i] > prices[i + 1]:
                peaks.append((i, prices[i]))
            elif prices[i] < prices[i - 1] and prices[i] < prices[i + 1]:
                troughs.append((i, prices[i]))
        
        # 判断趋势
        if len(peaks) >= 2 and len(troughs) >= 2:
            if peaks[-1][1] > peaks[-2][1] and troughs[-1][1] > troughs[-2][1]:
                trend = "上升趋势"
                phase = "推动浪"
            elif peaks[-1][1] < peaks[-2][1] and troughs[-1][1] < troughs[-2][1]:
                trend = "下降趋势"
                phase = "调整浪"
            else:
                trend = "震荡"
                phase = "盘整"
        else:
            trend = "不确定"
            phase = "观察中"
        
        return {
            "pattern": trend,
            "phase": phase,
            "peaks": len(peaks),
            "troughs": len(troughs)
        }
    
    @staticmethod
    def predict_next_move(prices: List[float]) -> Dict[str, any]:
        """
        预测下一步走势
        
        Args:
            prices: 价格列表
            
        Returns:
            预测信息
        """
        wave_info = ElliottWaveAnalysis.identify_wave_pattern(prices)
        
        if wave_info["pattern"] == "上升趋势":
            if wave_info["phase"] == "推动浪":
                prediction = "继续上涨概率高"
                confidence = 0.7
            else:
                prediction = "可能回调"
                confidence = 0.6
        elif wave_info["pattern"] == "下降趋势":
            if wave_info["phase"] == "推动浪":
                prediction = "继续下跌概率高"
                confidence = 0.7
            else:
                prediction = "可能反弹"
                confidence = 0.6
        else:
            prediction = "震荡为主，等待突破"
            confidence = 0.5
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "wave_info": wave_info
        }


class ChanTheoryAnalysis:
    """缠论分析"""
    
    @staticmethod
    def identify_bi(high: List[float], low: List[float], close: List[float]) -> List[Dict]:
        """
        识别笔（缠论基本单位）
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            
        Returns:
            笔的列表
        """
        if len(close) < 5:
            return []
        
        bi_list = []
        direction = None  # 'up' or 'down'
        start_idx = 0
        start_price = close[0]
        
        for i in range(1, len(close)):
            if direction is None:
                if close[i] > close[i - 1]:
                    direction = 'up'
                elif close[i] < close[i - 1]:
                    direction = 'down'
            elif direction == 'up':
                if close[i] < close[i - 1]:
                    # 上升笔结束
                    bi_list.append({
                        'type': 'up',
                        'start': start_idx,
                        'end': i - 1,
                        'start_price': start_price,
                        'end_price': close[i - 1]
                    })
                    direction = 'down'
                    start_idx = i - 1
                    start_price = close[i - 1]
            elif direction == 'down':
                if close[i] > close[i - 1]:
                    # 下降笔结束
                    bi_list.append({
                        'type': 'down',
                        'start': start_idx,
                        'end': i - 1,
                        'start_price': start_price,
                        'end_price': close[i - 1]
                    })
                    direction = 'up'
                    start_idx = i - 1
                    start_price = close[i - 1]
        
        return bi_list
    
    @staticmethod
    def identify_center(bi_list: List[Dict]) -> List[Dict]:
        """
        识别中枢
        
        Args:
            bi_list: 笔的列表
            
        Returns:
            中枢列表
        """
        if len(bi_list) < 3:
            return []
        
        centers = []
        
        for i in range(len(bi_list) - 2):
            # 简化的中枢识别：三笔重叠区域
            prices = [
                bi_list[i]['start_price'],
                bi_list[i]['end_price'],
                bi_list[i + 1]['start_price'],
                bi_list[i + 1]['end_price'],
                bi_list[i + 2]['start_price'],
                bi_list[i + 2]['end_price']
            ]
            
            upper = max(min(bi_list[i]['end_price'], bi_list[i]['start_price']),
                       min(bi_list[i + 1]['end_price'], bi_list[i + 1]['start_price']))
            lower = min(max(bi_list[i]['end_price'], bi_list[i]['start_price']),
                       max(bi_list[i + 1]['end_price'], bi_list[i + 1]['start_price']))
            
            if upper > lower:
                centers.append({
                    'upper': upper,
                    'lower': lower,
                    'middle': (upper + lower) / 2
                })
        
        return centers
    
    @staticmethod
    def analyze_trend(bi_list: List[Dict]) -> Dict[str, any]:
        """
        分析趋势（缠论）
        
        Args:
            bi_list: 笔的列表
            
        Returns:
            趋势分析结果
        """
        if len(bi_list) < 3:
            return {"trend": "数据不足", "strength": 0}
        
        # 分析最近三笔的走势
        recent_bi = bi_list[-3:]
        
        if all(bi['type'] == 'up' for bi in recent_bi[::2]):
            trend = "强势上涨"
            strength = 0.8
        elif all(bi['type'] == 'down' for bi in recent_bi[::2]):
            trend = "强势下跌"
            strength = 0.8
        else:
            trend = "震荡"
            strength = 0.5
        
        return {
            "trend": trend,
            "strength": strength,
            "bi_count": len(bi_list)
        }


class WyckoffAnalysis:
    """威科夫交易法分析"""
    
    @staticmethod
    def identify_phase(prices: List[float], volumes: List[float]) -> Dict[str, any]:
        """
        识别威科夫阶段
        
        Args:
            prices: 价格列表
            volumes: 成交量列表
            
        Returns:
            威科夫阶段信息
        """
        if len(prices) < 10 or len(volumes) < 10:
            return {"phase": "数据不足", "action": "观察"}
        
        # 计算价格和成交量变化
        price_change = (prices[-1] - prices[0]) / prices[0]
        avg_volume_early = np.mean(volumes[:len(volumes)//2])
        avg_volume_late = np.mean(volumes[len(volumes)//2:])
        volume_change = (avg_volume_late - avg_volume_early) / avg_volume_early
        
        # 威科夫四个阶段判断
        if abs(price_change) < 0.02 and volume_change > 0.3:
            # 成交量增加但价格横盘
            if prices[-1] > prices[-5]:
                phase = "吸筹阶段（Accumulation）"
                action = "准备做多"
            else:
                phase = "派发阶段（Distribution）"
                action = "准备做空"
        elif price_change > 0.05 and volume_change > 0:
            phase = "上涨阶段（Markup）"
            action = "持有多单"
        elif price_change < -0.05 and volume_change > 0:
            phase = "下跌阶段（Markdown）"
            action = "持有空单或离场"
        else:
            phase = "观察阶段"
            action = "等待信号"
        
        return {
            "phase": phase,
            "action": action,
            "price_change": price_change,
            "volume_change": volume_change
        }
    
    @staticmethod
    def analyze_supply_demand(prices: List[float], volumes: List[float]) -> Dict[str, any]:
        """
        分析供需关系
        
        Args:
            prices: 价格列表
            volumes: 成交量列表
            
        Returns:
            供需分析结果
        """
        if len(prices) < 5:
            return {"balance": "未知", "strength": 0}
        
        # 分析最近的价格和成交量关系
        recent_prices = prices[-5:]
        recent_volumes = volumes[-5:]
        
        price_trend = recent_prices[-1] - recent_prices[0]
        volume_avg = np.mean(recent_volumes)
        
        if price_trend > 0 and recent_volumes[-1] > volume_avg:
            balance = "需求大于供给"
            strength = 0.7
        elif price_trend < 0 and recent_volumes[-1] > volume_avg:
            balance = "供给大于需求"
            strength = 0.7
        elif price_trend > 0 and recent_volumes[-1] < volume_avg:
            balance = "需求减弱"
            strength = 0.4
        elif price_trend < 0 and recent_volumes[-1] < volume_avg:
            balance = "供给减弱"
            strength = 0.4
        else:
            balance = "供需平衡"
            strength = 0.5
        
        return {
            "balance": balance,
            "strength": strength,
            "trend": "上涨" if price_trend > 0 else "下跌"
        }


# 测试代码
if __name__ == "__main__":
    # 测试斐波那契
    print("=== 斐波那契分析测试 ===")
    fib = FibonacciAnalysis()
    retracement = fib.calculate_retracement(120, 100)
    print("回调位:", retracement)
    
    support_resistance = fib.find_support_resistance(110, 120, 100)
    print("支撑位:", support_resistance["support"])
    print("阻力位:", support_resistance["resistance"])
    
    # 测试波浪理论
    print("\n=== 波浪理论测试 ===")
    test_prices = [100, 105, 103, 108, 106, 112, 109, 115, 113, 118]
    elliott = ElliottWaveAnalysis()
    wave_pattern = elliott.identify_wave_pattern(test_prices)
    print("波浪形态:", wave_pattern)
    
    prediction = elliott.predict_next_move(test_prices)
    print("预测:", prediction)
    
    print("\n测试完成！")

