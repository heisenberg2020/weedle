import requests
import hashlib
import json
import pandas as pd
from datetime import datetime
import time
import execjs
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util import Padding
import base64

cookies = {
    'btoken': 'G71R5783MO7GKLEX66TGFJZ33DW33A47',
    'Hm_lvt_42317524c1662a500d12d3784dbea0f8': '1754136835',
    'HMACCOUNT': '8109C8618175ADDE',
    'Hm_lpvt_42317524c1662a500d12d3784dbea0f8': '1754136855',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.xiniudata.com',
    'priority': 'u=1, i',
    'referer': 'https://www.xiniudata.com/industry/newest?from=data',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
}


def get_all_trade_data(c, page_no=1):
    payload = f'{{"sort": 1, "start": {page_no}, "limit": 20}}'
    get_payload_rst = c.call('get_payload', payload)
    get_sig_rst = c.call('get_sig', get_payload_rst)

    json_data = {
        'payload': get_payload_rst,
        'sig': get_sig_rst,
        'v': 1,
    }

    response = requests.post(
        'https://www.xiniudata.com/api2/service/x_service/person_industry_list/list_industries_by_sort',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    # 解密响应数据
    response_data = response.json()
    if 'd' in response_data:
        decrypted_data = c.call('getBody', response_data['d'])
        return decrypted_data
    else:
        return []


def save_to_excel(data, filename="trade_data.xlsx"):
    """
    将数据保存到Excel文件
    """
    if not data:
        print("数据格式不正确，无法保存到Excel")
        return

    df = pd.DataFrame(data)

    # 保存到Excel
    df.to_excel(filename, index=False)


if __name__ == "__main__":
    with open('01-decrypt/002-犀牛/old.js', 'r', encoding='utf-8') as f:
        js_file = f.read()
    c = execjs.compile(js_file)
    all_data = []
    page = 1
    while True:
        data = get_all_trade_data(c, page)
        if not data or page > 100:
            break
        all_data.extend(data)
        print(f"第{page}页数据获取成功，当前共收集到{len(all_data)}条记录")
        page += 1

    save_to_excel(all_data)
