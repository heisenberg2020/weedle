# main.py
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


def generate_sign(params, js_file, prefix="B3978D054A72A7002063637CCDF6B2E5"):
    return execjs.compile(js_file).call('sign', params)


def get_trade_data(c, page_no=1, page_size=20):
    """
    获取交易数据
    """
    # 请求参数
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "total": 0,  # 初始值设为0，第一次请求后会获取真实总数
        "AREACODE": "",
        "M_PROJECT_TYPE": "",
        "KIND": "GCJS",
        "GGTYPE": "1",
        "PROTYPE": "",
        "timeType": "6",
        "BeginTime": "2025-02-01 00:00:00",
        "EndTime": "2025-08-02 23:59:59",
        "createTime": "",
        "ts": int(datetime.now().timestamp() * 1000)  # 当前时间戳
    }

    # 生成签名
    # sign = c.call('sign', params)
    sign = sign_python(params)
    # 请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://ggzyfw.fj.gov.cn',
        'Referer': 'https://ggzyfw.fj.gov.cn/business/list/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'portal-sign': sign,
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    # 发送请求
    url = 'https://ggzyfw.fj.gov.cn/FwPortalApi/Trade/TradeInfo'
    response = requests.post(url, headers=headers, json=params)

    if response.status_code == 200:
        try:
            data = response.json()
            # print("响应数据:", data)
            return data
        except json.JSONDecodeError:
            print("响应不是有效的JSON格式")
            print("响应内容:", response.text)
            return None
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)
        return None


def get_all_trade_data():
    """
    获取所有交易数据
    """
    print("开始获取第1页数据...")

    with open('./new.js', 'r', encoding='utf-8') as f:
        js_file = f.read()
    c = execjs.compile(js_file)

    first_page_data = get_trade_data(c, page_no=1, page_size=20)

    if not first_page_data:
        print("获取第一页数据失败")
        return None

    # 检查响应是否成功
    if first_page_data.get("State") != "200":
        print(f"获取第一页数据失败: {first_page_data.get('Msg')}, {first_page_data.get('State')}")
        return None

    # 解密第一页数据
    # decrypted_data = c.call('decryptData', first_page_data['Data'])
    decrypted_data = decrypt_data(first_page_data['Data'])
    print("第1页数据解密成功:", decrypted_data)


    first_page_body = json.loads(decrypted_data)

    # 获取总记录数和总页数
    total = first_page_body.get("Total", 0)  # 从解密后的数据中获取
    total_pages = first_page_body.get("PageTotal", 0)  # 从解密后的数据中获取

    print(f"总记录数: {total}, 总页数: {total_pages}")

    # 收集所有数据
    all_data = []

    # 添加第一页数据
    if "Table" in first_page_body:
        all_data.extend(first_page_body["Table"])
        print(f"第1页数据获取成功，当前共收集到{len(all_data)}条记录")

    # 获取剩余页面的数据
    # for page_no in range(2, total_pages + 1):
    for page_no in range(2, 5):
        print(f"正在获取第{page_no}页数据...")
        data = get_trade_data(c, page_no=page_no, page_size=20)

        if data and "Data" in data:
            # 检查响应是否成功
            if data.get("State") != "200":
                print(f"获取第{page_no}页数据失败: {data.get('Msg')}")
                continue

            # 解密数据
            # decrypted_data = c.call('decryptData', data['Data'])
            decrypted_data = decrypt_data(data['Data'])
            page_body = json.loads(decrypted_data)

            if "Table" in page_body:
                all_data.extend(page_body["Table"])
                print(f"第{page_no}页数据获取成功，当前共收集到{len(all_data)}条记录")
            else:
                print(f"第{page_no}页数据格式不正确")
        else:
            print(f"第{page_no}页数据获取失败")

        # 添加延时，避免请求过于频繁
        # time.sleep(1)

    result = {
        "Total": total,
        "Table": all_data,
        "TotalPages": total_pages
    }

    return result


def save_to_excel(data, filename="trade_data.xlsx"):
    """
    将数据保存到Excel文件
    """
    if not data or "Table" not in data:
        print("数据格式不正确，无法保存到Excel")
        return

    df = pd.DataFrame(data["Table"])

    # 保存到Excel
    df.to_excel(filename, index=False)
    print(f"数据已保存到 {filename}，共{len(df)}条记录")





def sign_python(t):
    """
    计算请求参数的签名

    Args:
        t (dict): 请求参数字典

    Returns:
        str: 签名值（小写）
    """
    # 过滤掉空字符串和None值
    filtered_t = {k: v for k, v in t.items() if v != "" and v is not None}

    # 固定前缀
    prefix = "B3978D054A72A7002063637CCDF6B2E5"

    # 生成待签名字符串
    sign_str = prefix + u(filtered_t)

    # MD5签名并转为小写
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().lower()


def u(t):
    """
    根据参数生成待签名字符串

    Args:
        t (dict): 过滤后的请求参数

    Returns:
        str: 待签名字符串
    """
    # 按键名排序（不区分大小写）
    sorted_keys = sorted(t.keys(), key=lambda x: x.upper())

    result = ""
    for key in sorted_keys:
        if t[key] is not None:
            # 如果值是对象或数组，转换为JSON字符串
            if isinstance(t[key], (dict, list)):
                result += key + json.dumps(t[key], separators=(',', ':'))
            else:
                result += key + str(t[key])

    return result


def decrypt_data(encrypted_data):
    """
    解密响应数据

    Args:
        encrypted_data (str): Base64编码的加密数据

    Returns:
        str: 解密后的明文
    """
    # 密钥和IV
    key = "EB444973714E4A40876CE66BE45D5930"
    iv = "B5A8904209931867"

    # 将密钥和IV转换为bytes
    key_bytes = key.encode('utf-8')
    iv_bytes = iv.encode('utf-8')

    # 解码Base64格式的加密数据
    encrypted_bytes = base64.b64decode(encrypted_data)

    # 创建AES解密器
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)

    # 解密并去除填充
    decrypted = cipher.decrypt(encrypted_bytes)
    unpadded = unpad(decrypted, AES.block_size)

    # 转换为字符串返回
    return unpadded.decode('utf-8')



def main():
    """
    主函数
    """
    print("开始获取所有交易数据...")

    # 获取所有数据
    all_data = get_all_trade_data()

    if all_data:
        print("所有数据获取完成")
        print("保存数据到Excel...")
        save_to_excel(all_data)
    else:
        print("数据获取失败")


if __name__ == "__main__":
    main()
