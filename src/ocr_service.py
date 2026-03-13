# -*- coding: utf-8 -*-
"""
OCR识别服务

使用百度OCR API识别持仓截图
"""
import os
import base64
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
import re
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import execute_update, execute_query, get_connection
from dotenv import load_dotenv

load_dotenv()


class BaiduOCRService:
    """百度OCR服务"""

    def __init__(self):
        self.api_key = os.getenv('BAIDU_OCR_API_KEY')
        self.secret_key = os.getenv('BAIDU_OCR_SECRET_KEY')
        self.access_token = None

    def get_access_token(self) -> Optional[str]:
        """获取百度OCR access token"""
        if self.access_token:
            return self.access_token

        if not self.api_key or not self.secret_key:
            print("警告: 未配置百度OCR API密钥")
            return None

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        try:
            response = requests.post(url, params=params)
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                return self.access_token
            else:
                print(f"获取access token失败: {result}")
                return None
        except Exception as e:
            print(f"获取access token异常: {e}")
            return None

    def recognize_image(self, image_path: str) -> Optional[Dict]:
        """
        识别图片中的文字

        Args:
            image_path: 图片路径

        Returns:
            识别结果字典
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode()

        # 调用通用文字识别API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'image': image_base64}

        try:
            response = requests.post(url, headers=headers, data=data)
            result = response.json()

            if 'words_result' in result:
                return result
            else:
                print(f"OCR识别失败: {result}")
                return None
        except Exception as e:
            print(f"OCR识别异常: {e}")
            return None

    def recognize_table(self, image_path: str) -> Optional[Dict]:
        """
        识别图片中的表格

        Args:
            image_path: 图片路径

        Returns:
            识别结果字典
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode()

        # 调用表格文字识别API
        url = f"https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/v2/recognize_tables?access_token={access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'image': image_base64,
            'language_kind': 'CHN_ENG'
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            result = response.json()

            if 'tables_result' in result:
                return result
            else:
                print(f"表格识别失败: {result}")
                return None
        except Exception as e:
            print(f"表格识别异常: {e}")
            return None

    def parse_position_text(self, ocr_result: Dict) -> List[Dict]:
        """
        解析持仓识别结果

        Args:
            ocr_result: OCR识别结果

        Returns:
            持仓信息列表
        """
        positions = []

        if 'words_result' not in ocr_result:
            return positions

        lines = [item['words'] for item in ocr_result['words_result']]

        # 尝试解析持仓信息
        # 假设格式为：股票代码 股票名称 持仓数量 成本价
        for line in lines:
            # 尝试匹配股票代码格式（6位数字.SH或.SZ）
            code_pattern = r'(\d{6}\.(SH|SZ))'
            match = re.search(code_pattern, line)

            if match:
                # 提取股票代码
                stock_code = match.group(1)

                # 尝试提取其他信息（简化处理）
                # 实际应用中需要根据具体截图格式进行调整
                parts = line.split()
                position = {
                    'stock_code': stock_code,
                    'stock_name': parts[1] if len(parts) > 1 else '',
                    'shares': 0,
                    'cost_price': 0,
                    'raw_text': line
                }

                # 尝试提取数字（可能是持仓数量或价格）
                numbers = re.findall(r'\d+\.?\d*', line)
                if len(numbers) >= 3:
                    # 假设第3个数字是持仓数量
                    position['shares'] = int(float(numbers[2]))
                    # 假设第4个数字是成本价
                    if len(numbers) >= 4:
                        position['cost_price'] = float(numbers[3])

                positions.append(position)

        return positions

    def save_ocr_record(self, image_path: str, ocr_result: Dict, parsed_data: List[Dict], confidence: float = 0.0) -> int:
        """
        保存OCR识别记录到数据库

        Args:
            image_path: 图片路径
            ocr_result: OCR识别结果
            parsed_data: 解析后的数据
            confidence: 识别置信度

        Returns:
            记录ID
        """
        sql = """
        INSERT INTO trade_ocr_record
        (image_path, ocr_type, ocr_result, parsed_data, confidence, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (
                image_path,
                'position',
                json.dumps(ocr_result, ensure_ascii=False),
                json.dumps(parsed_data, ensure_ascii=False),
                confidence,
                1
            ))
            conn.commit()
            record_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return record_id
        except Exception as e:
            print(f"保存OCR记录失败: {e}")
            return 0

    def process_position_image(self, image_path: str) -> List[Dict]:
        """
        处理持仓截图

        Args:
            image_path: 图片路径

        Returns:
            持仓信息列表
        """
        print(f"正在识别图片: {image_path}")

        # 识别图片
        ocr_result = self.recognize_image(image_path)

        if not ocr_result:
            print("OCR识别失败")
            return []

        # 解析持仓信息
        positions = self.parse_position_text(ocr_result)

        # 计算置信度（简化处理）
        confidence = 1.0 if positions else 0.0

        # 保存记录
        record_id = self.save_ocr_record(image_path, ocr_result, positions, confidence)

        if record_id:
            print(f"已保存OCR记录 (ID: {record_id})")

        return positions


class MockOCRService:
    """模拟OCR服务（用于测试）"""

    def process_position_image(self, image_path: str) -> List[Dict]:
        """模拟处理持仓截图"""
        print(f"[模拟] 正在识别图片: {image_path}")

        # 返回模拟数据
        return [
            {
                'stock_code': '600519.SH',
                'stock_name': '贵州茅台',
                'shares': 100,
                'cost_price': 1800.00
            },
            {
                'stock_code': '000858.SZ',
                'stock_name': '五粮液',
                'shares': 200,
                'cost_price': 150.00
            }
        ]


def main():
    """测试OCR服务"""
    # 使用模拟服务（因为没有配置百度OCR API密钥）
    ocr_service = MockOCRService()

    # 测试处理图片
    positions = ocr_service.process_position_image('/tmp/test.png')

    print("\n识别结果:")
    for pos in positions:
        print(f"  {pos['stock_code']} - {pos['stock_name']}: {pos['shares']}股 @ ¥{pos['cost_price']}")


if __name__ == "__main__":
    main()
