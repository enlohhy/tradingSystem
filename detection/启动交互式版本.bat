@echo off
chcp 65001 >nul
echo ========================================
echo  加密货币智能监测系统 - 交互式版本
echo ========================================
echo.
echo 功能说明:
echo  [空格] 切换实时/暂停模式
echo  [R]     手动刷新数据
echo  [A]     技术分析（获取历史数据）
echo  [Q]     退出程序
echo.
echo ========================================
echo.
python cli_app_interactive.py
pause

