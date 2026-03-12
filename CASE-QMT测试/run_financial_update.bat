@echo off
chcp 65001 >nul
set WUCAI_SQL_PASSWORD=Hao1023@zb
cd /d "C:\Users\wenwen\quant\CASE-QMT测试"
"C:\Users\wenwen\AppData\Local\Programs\Python\Python39\python.exe" financial_daily_update.py
