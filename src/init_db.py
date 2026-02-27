# -*- coding: utf-8 -*-
"""
数据库初始化脚本

创建数据库(如果不存在)并初始化所有表

运行：python src/init_db.py
"""
import os
import sys
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def create_database():
    """创建数据库(如果不存在)"""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
    }
    db_name = os.getenv('DB_NAME', 'quant_trade')

    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.close()
    conn.close()
    print(f"数据库 '{db_name}' 已就绪")


def init_tables():
    """初始化所有表"""
    # 导入表定义
    from models import get_create_sql_list

    # 连接数据库
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    tables = get_create_sql_list()
    print(f"\n开始创建 {len(tables)} 张表...\n")

    for sql, table_name in tables:
        try:
            cursor.execute(sql)
            print(f"  [OK] {table_name}")
        except Exception as e:
            print(f"  [FAIL] {table_name}: {e}")

    conn.commit()
    cursor.close()
    conn.close()


def show_tables():
    """显示所有表"""
    from db import execute_query
    rows = execute_query("SHOW TABLES")
    print(f"\n当前数据库共有 {len(rows)} 张表:")
    for row in rows:
        table_name = list(row.values())[0]
        print(f"  - {table_name}")


def main():
    print("=" * 60)
    print("数据库初始化")
    print("=" * 60)

    # 显示配置
    print(f"\n连接配置:")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('DB_PORT', '3306')}")
    print(f"  User: {os.getenv('DB_USER', 'root')}")
    print(f"  Database: {os.getenv('DB_NAME', 'quant_trade')}")

    # 测试连接
    print("\n测试连接...")
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
        )
        conn.close()
        print("  连接成功!")
    except Exception as e:
        print(f"  连接失败: {e}")
        return

    # 创建数据库
    print("\n步骤1: 创建数据库...")
    create_database()

    # 创建表
    print("\n步骤2: 创建表...")
    init_tables()

    # 显示结果
    print("\n步骤3: 验证...")
    show_tables()

    print("\n" + "=" * 60)
    print("初始化完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
