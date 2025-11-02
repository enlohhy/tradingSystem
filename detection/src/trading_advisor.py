# -*- coding: utf-8 -*-
"""
交易顾问模块
综合技术指标和交易理论，给出交易建议和止盈止损位
"""

import numpy as np
from typing import List, Dict, Tuple
from src.indicators import TechnicalIndicators
from src.trading_theory import FibonacciAnalysis, ElliottWaveAnalysis, ChanTheoryAnalysis, WyckoffAnalysis


class TradingAdvisor:
    """交易顾问"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.fibonacci = FibonacciAnalysis()
        self.elliott = ElliottWaveAnalysis()
        self.chan = ChanTheoryAnalysis()
        self.wyckoff = WyckoffAnalysis()
    
    def analyze_comprehensive(self, klines: List[Dict]) -> Dict:
        """
        综合分析
        
        Args:
            klines: K线数据列表
            
        Returns:
            综合分析结果
        """
        if len(klines) < 30:
            return {"error": "数据不足，至少需要30根K线"}
        
        # 提取数据
        closes = [k['close'] for k in klines]
        highs = [k['high'] for k in klines]
        lows = [k['low'] for k in klines]
        volumes = [k['volume'] for k in klines]
        
        current_price = closes[-1]
        
        # 1. 技术指标分析
        indicators_analysis = self._analyze_indicators(closes, highs, lows, volumes)
        
        # 2. 斐波那契分析
        fib_analysis = self._analyze_fibonacci(closes, highs, lows, current_price)
        
        # 3. 波浪理论分析
        elliott_analysis = self._analyze_elliott(closes)
        
        # 4. 缠论分析
        chan_analysis = self._analyze_chan(highs, lows, closes)
        
        # 5. 威科夫分析
        wyckoff_analysis = self._analyze_wyckoff(closes, volumes)
        
        # 6. 综合评分
        score = self._calculate_score(indicators_analysis, fib_analysis, elliott_analysis, 
                                      chan_analysis, wyckoff_analysis)
        
        # 7. 生成交易建议
        recommendations = self._generate_recommendations(
            current_price, score, indicators_analysis, fib_analysis
        )
        
        return {
            "current_price": current_price,
            "indicators": indicators_analysis,
            "fibonacci": fib_analysis,
            "elliott_wave": elliott_analysis,
            "chan_theory": chan_analysis,
            "wyckoff": wyckoff_analysis,
            "score": score,
            "recommendations": recommendations
        }
    
    def _analyze_indicators(self, closes: List[float], highs: List[float], 
                           lows: List[float], volumes: List[float]) -> Dict:
        """分析技术指标"""
        current_price = closes[-1]
        
        # MA均线
        ma_dict = self.indicators.calculate_ma(closes, [5, 10, 20, 30, 60])
        ma_signal = self._analyze_ma_signal(current_price, ma_dict)
        
        # MACD
        macd = self.indicators.calculate_macd(closes)
        macd_signal = self._analyze_macd_signal(macd)
        
        # KDJ
        kdj = self.indicators.calculate_kdj(highs, lows, closes)
        kdj_signal = self._analyze_kdj_signal(kdj)
        
        # BOLL
        boll = self.indicators.calculate_boll(closes)
        boll_signal = self._analyze_boll_signal(current_price, boll)
        
        # RSI
        rsi = self.indicators.calculate_rsi(closes)
        rsi_signal = self._analyze_rsi_signal(rsi)
        
        # ATR（波动率）
        atr = self.indicators.calculate_atr(highs, lows, closes)
        volatility = atr[-1] if atr else 0
        
        return {
            "MA": ma_signal,
            "MACD": macd_signal,
            "KDJ": kdj_signal,
            "BOLL": boll_signal,
            "RSI": rsi_signal,
            "volatility": volatility,
            "ma_values": {k: v[-1] if v else None for k, v in ma_dict.items()},
            "macd_values": {k: v[-1] if v else None for k, v in macd.items()},
            "kdj_values": {k: v[-1] if v else None for k, v in kdj.items()},
            "boll_values": {k: v[-1] if v else None for k, v in boll.items()},
            "rsi_value": rsi[-1] if rsi else None
        }
    
    def _analyze_ma_signal(self, current_price: float, ma_dict: Dict) -> Dict:
        """分析均线信号"""
        signals = []
        score = 0
        
        # 检查价格与各均线关系
        for period, values in ma_dict.items():
            if values and values[-1] is not None:
                ma_value = values[-1]
                if current_price > ma_value:
                    signals.append(f"价格在MA{period}上方")
                    score += 1
                else:
                    signals.append(f"价格在MA{period}下方")
                    score -= 1
        
        # 检查均线排列
        ma_values = [v[-1] for v in ma_dict.values() if v and v[-1] is not None]
        if ma_values == sorted(ma_values, reverse=True):
            signals.append("多头排列")
            score += 2
        elif ma_values == sorted(ma_values):
            signals.append("空头排列")
            score -= 2
        
        if score > 3:
            trend = "强烈看多"
        elif score > 0:
            trend = "看多"
        elif score < -3:
            trend = "强烈看空"
        elif score < 0:
            trend = "看空"
        else:
            trend = "中性"
        
        return {"trend": trend, "score": score, "signals": signals}
    
    def _analyze_macd_signal(self, macd: Dict) -> Dict:
        """分析MACD信号"""
        if not macd["DIF"] or not macd["DEA"]:
            return {"signal": "数据不足", "score": 0}
        
        dif = macd["DIF"][-1]
        dea = macd["DEA"][-1]
        macd_bar = macd["MACD"][-1]
        
        signals = []
        score = 0
        
        # 金叉死叉
        if len(macd["DIF"]) >= 2:
            if dif > dea and macd["DIF"][-2] <= macd["DEA"][-2]:
                signals.append("金叉（买入信号）")
                score += 2
            elif dif < dea and macd["DIF"][-2] >= macd["DEA"][-2]:
                signals.append("死叉（卖出信号）")
                score -= 2
        
        # DIF和DEA位置
        if dif > 0 and dea > 0:
            signals.append("零轴上方（多头市场）")
            score += 1
        elif dif < 0 and dea < 0:
            signals.append("零轴下方（空头市场）")
            score -= 1
        
        # MACD柱状图
        if macd_bar > 0:
            signals.append("柱状图为正（动能增强）")
            score += 0.5
        else:
            signals.append("柱状图为负（动能减弱）")
            score -= 0.5
        
        if score > 2:
            signal = "强烈买入"
        elif score > 0:
            signal = "买入"
        elif score < -2:
            signal = "强烈卖出"
        elif score < 0:
            signal = "卖出"
        else:
            signal = "观望"
        
        return {"signal": signal, "score": score, "details": signals}
    
    def _analyze_kdj_signal(self, kdj: Dict) -> Dict:
        """分析KDJ信号"""
        if not kdj["K"]:
            return {"signal": "数据不足", "score": 0}
        
        k = kdj["K"][-1]
        d = kdj["D"][-1]
        j = kdj["J"][-1]
        
        signals = []
        score = 0
        
        # 超买超卖
        if k > 80 and d > 80:
            signals.append("超买区域（可能回调）")
            score -= 1
        elif k < 20 and d < 20:
            signals.append("超卖区域（可能反弹）")
            score += 1
        
        # 金叉死叉
        if len(kdj["K"]) >= 2:
            if k > d and kdj["K"][-2] <= kdj["D"][-2]:
                signals.append("KDJ金叉（买入）")
                score += 1.5
            elif k < d and kdj["K"][-2] >= kdj["D"][-2]:
                signals.append("KDJ死叉（卖出）")
                score -= 1.5
        
        # J值判断
        if j > 100:
            signals.append("J值超买")
            score -= 0.5
        elif j < 0:
            signals.append("J值超卖")
            score += 0.5
        
        if score > 1.5:
            signal = "买入"
        elif score < -1.5:
            signal = "卖出"
        else:
            signal = "观望"
        
        return {"signal": signal, "score": score, "details": signals, "values": {"K": k, "D": d, "J": j}}
    
    def _analyze_boll_signal(self, current_price: float, boll: Dict) -> Dict:
        """分析布林带信号"""
        if not boll["MIDDLE"]:
            return {"signal": "数据不足", "score": 0}
        
        upper = boll["UPPER"][-1]
        middle = boll["MIDDLE"][-1]
        lower = boll["LOWER"][-1]
        
        signals = []
        score = 0
        
        # 价格位置
        if current_price > upper:
            signals.append("价格突破上轨（超买）")
            score -= 1
        elif current_price < lower:
            signals.append("价格突破下轨（超卖）")
            score += 1
        elif current_price > middle:
            signals.append("价格在中轨上方（偏多）")
            score += 0.5
        else:
            signals.append("价格在中轨下方（偏空）")
            score -= 0.5
        
        # 带宽分析
        bandwidth = (upper - lower) / middle
        if bandwidth > 0.1:
            signals.append("布林带宽度较大（波动性高）")
        else:
            signals.append("布林带收窄（可能突破）")
        
        if score > 0.5:
            signal = "偏多"
        elif score < -0.5:
            signal = "偏空"
        else:
            signal = "中性"
        
        return {"signal": signal, "score": score, "details": signals}
    
    def _analyze_rsi_signal(self, rsi: List[float]) -> Dict:
        """分析RSI信号"""
        if not rsi:
            return {"signal": "数据不足", "score": 0}
        
        rsi_value = rsi[-1]
        
        signals = []
        score = 0
        
        if rsi_value > 70:
            signals.append("RSI超买（>70）")
            score -= 1
        elif rsi_value < 30:
            signals.append("RSI超卖（<30）")
            score += 1
        elif rsi_value > 50:
            signals.append("RSI偏强（>50）")
            score += 0.5
        else:
            signals.append("RSI偏弱（<50）")
            score -= 0.5
        
        if score > 0.5:
            signal = "偏多"
        elif score < -0.5:
            signal = "偏空"
        else:
            signal = "中性"
        
        return {"signal": signal, "score": score, "details": signals, "value": rsi_value}
    
    def _analyze_fibonacci(self, closes: List[float], highs: List[float], 
                          lows: List[float], current_price: float) -> Dict:
        """斐波那契分析"""
        # 找出最近的高低点
        high = max(highs[-20:])
        low = min(lows[-20:])
        
        # 计算回调位和支撑阻力
        retracement = self.fibonacci.calculate_retracement(high, low)
        support_resistance = self.fibonacci.find_support_resistance(current_price, high, low)
        
        return {
            "high": high,
            "low": low,
            "retracement_levels": retracement,
            "support": support_resistance["support"],
            "resistance": support_resistance["resistance"]
        }
    
    def _analyze_elliott(self, closes: List[float]) -> Dict:
        """波浪理论分析"""
        wave_pattern = self.elliott.identify_wave_pattern(closes)
        prediction = self.elliott.predict_next_move(closes)
        
        return {
            "pattern": wave_pattern,
            "prediction": prediction
        }
    
    def _analyze_chan(self, highs: List[float], lows: List[float], closes: List[float]) -> Dict:
        """缠论分析"""
        bi_list = self.chan.identify_bi(highs, lows, closes)
        trend = self.chan.analyze_trend(bi_list)
        
        return {
            "bi_count": len(bi_list),
            "trend": trend
        }
    
    def _analyze_wyckoff(self, closes: List[float], volumes: List[float]) -> Dict:
        """威科夫分析"""
        phase = self.wyckoff.identify_phase(closes, volumes)
        supply_demand = self.wyckoff.analyze_supply_demand(closes, volumes)
        
        return {
            "phase": phase,
            "supply_demand": supply_demand
        }
    
    def _calculate_score(self, indicators: Dict, fib: Dict, elliott: Dict, 
                        chan: Dict, wyckoff: Dict) -> Dict:
        """计算综合评分"""
        # 技术指标评分
        indicator_score = (
            indicators["MA"]["score"] * 0.25 +
            indicators["MACD"]["score"] * 0.25 +
            indicators["KDJ"]["score"] * 0.2 +
            indicators["BOLL"]["score"] * 0.15 +
            indicators["RSI"]["score"] * 0.15
        )
        
        # 波浪理论评分
        elliott_score = elliott["prediction"]["confidence"] * 2 - 1
        if elliott["prediction"]["prediction"].find("上涨") >= 0:
            elliott_score = abs(elliott_score)
        else:
            elliott_score = -abs(elliott_score)
        
        # 缠论评分
        chan_score = chan["trend"]["strength"] * 2 - 1
        if chan["trend"]["trend"].find("上涨") >= 0:
            chan_score = abs(chan_score)
        else:
            chan_score = -abs(chan_score)
        
        # 威科夫评分
        wyckoff_score = wyckoff["supply_demand"]["strength"] * 2 - 1
        if wyckoff["supply_demand"]["trend"] == "上涨":
            wyckoff_score = abs(wyckoff_score)
        else:
            wyckoff_score = -abs(wyckoff_score)
        
        # 总分
        total_score = (
            indicator_score * 0.4 +
            elliott_score * 0.2 +
            chan_score * 0.2 +
            wyckoff_score * 0.2
        )
        
        # 归一化到0-100
        normalized_score = (total_score + 5) / 10 * 100
        normalized_score = max(0, min(100, normalized_score))
        
        return {
            "total": round(normalized_score, 2),
            "indicator_score": round(indicator_score, 2),
            "elliott_score": round(elliott_score, 2),
            "chan_score": round(chan_score, 2),
            "wyckoff_score": round(wyckoff_score, 2)
        }
    
    def _generate_recommendations(self, current_price: float, score: Dict, 
                                 indicators: Dict, fib: Dict) -> Dict:
        """生成交易建议"""
        total_score = score["total"]
        
        # 判断交易方向
        if total_score > 65:
            direction = "做多（买入）"
            confidence = "高"
        elif total_score > 55:
            direction = "做多（买入）"
            confidence = "中"
        elif total_score < 35:
            direction = "做空（卖出）"
            confidence = "高"
        elif total_score < 45:
            direction = "做空（卖出）"
            confidence = "中"
        else:
            direction = "观望"
            confidence = "不建议交易"
        
        # 计算止盈止损位（基于ATR和斐波那契）
        atr = indicators["volatility"]
        
        if direction.startswith("做多"):
            # 做多止损止盈
            stop_loss = self._calculate_stop_loss_long(current_price, atr, fib)
            take_profit = self._calculate_take_profit_long(current_price, atr, fib)
        elif direction.startswith("做空"):
            # 做空止损止盈
            stop_loss = self._calculate_stop_loss_short(current_price, atr, fib)
            take_profit = self._calculate_take_profit_short(current_price, atr, fib)
        else:
            stop_loss = {"15min": None, "1h": None, "4h": None, "24h": None}
            take_profit = {"15min": None, "1h": None, "4h": None, "24h": None}
        
        # 时间周期预测
        predictions = self._predict_timeframes(total_score, direction)
        
        return {
            "direction": direction,
            "confidence": confidence,
            "score": total_score,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "predictions": predictions,
            "risk_reward_ratio": self._calculate_risk_reward(current_price, stop_loss, take_profit)
        }
    
    def _calculate_stop_loss_long(self, price: float, atr: float, fib: Dict) -> Dict:
        """计算做多止损位"""
        # 使用ATR和斐波那契支撑位
        support = fib["support"][0] if fib["support"] else price * 0.95
        
        return {
            "15min": round(price - atr * 1, 2),
            "1h": round(max(price - atr * 2, support), 2),
            "4h": round(max(price - atr * 3, support), 2),
            "24h": round(max(price - atr * 5, fib["low"]), 2)
        }
    
    def _calculate_take_profit_long(self, price: float, atr: float, fib: Dict) -> Dict:
        """计算做多止盈位"""
        # 使用ATR和斐波那契阻力位
        resistance = fib["resistance"][0] if fib["resistance"] else price * 1.05
        
        return {
            "15min": round(price + atr * 1.5, 2),
            "1h": round(min(price + atr * 3, resistance), 2),
            "4h": round(min(price + atr * 5, resistance), 2),
            "24h": round(min(price + atr * 8, fib["high"]), 2)
        }
    
    def _calculate_stop_loss_short(self, price: float, atr: float, fib: Dict) -> Dict:
        """计算做空止损位"""
        resistance = fib["resistance"][0] if fib["resistance"] else price * 1.05
        
        return {
            "15min": round(price + atr * 1, 2),
            "1h": round(min(price + atr * 2, resistance), 2),
            "4h": round(min(price + atr * 3, resistance), 2),
            "24h": round(min(price + atr * 5, fib["high"]), 2)
        }
    
    def _calculate_take_profit_short(self, price: float, atr: float, fib: Dict) -> Dict:
        """计算做空止盈位"""
        support = fib["support"][0] if fib["support"] else price * 0.95
        
        return {
            "15min": round(price - atr * 1.5, 2),
            "1h": round(max(price - atr * 3, support), 2),
            "4h": round(max(price - atr * 5, support), 2),
            "24h": round(max(price - atr * 8, fib["low"]), 2)
        }
    
    def _predict_timeframes(self, score: float, direction: str) -> Dict:
        """预测不同时间周期"""
        if direction.startswith("做多"):
            return {
                "15min": "上涨" if score > 55 else "震荡",
                "1h": "上涨" if score > 60 else "震荡",
                "4h": "上涨" if score > 65 else "震荡上涨",
                "24h": "上涨" if score > 70 else "震荡"
            }
        elif direction.startswith("做空"):
            return {
                "15min": "下跌" if score < 45 else "震荡",
                "1h": "下跌" if score < 40 else "震荡",
                "4h": "下跌" if score < 35 else "震荡下跌",
                "24h": "下跌" if score < 30 else "震荡"
            }
        else:
            return {
                "15min": "震荡",
                "1h": "震荡",
                "4h": "震荡",
                "24h": "震荡"
            }
    
    def _calculate_risk_reward(self, price: float, stop_loss: Dict, take_profit: Dict) -> Dict:
        """计算风险收益比"""
        result = {}
        
        for timeframe in ["15min", "1h", "4h", "24h"]:
            sl = stop_loss.get(timeframe)
            tp = take_profit.get(timeframe)
            
            if sl and tp:
                risk = abs(price - sl)
                reward = abs(tp - price)
                ratio = reward / risk if risk > 0 else 0
                result[timeframe] = round(ratio, 2)
            else:
                result[timeframe] = None
        
        return result


# 测试代码
if __name__ == "__main__":
    print("交易顾问模块加载成功！")
    print("请在主程序中调用进行综合分析。")

