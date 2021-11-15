# -*- coding: UTF-8 -*-
import csv
import traceback

import regex as regex
import my_notion
import thread_util

token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
wechat_database_id = "651c89d606e64394ace3a6791594c183"
total_bill_database_id = "d250ca9f916c4c0e82b66d451f434701"
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"


# 线程池数量-账单行数
THREAD_POOL_SUM_ROW = 200
# 超时时间10秒
TIME_OUT = 10


def wechat(filepath):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        lines = f.readlines()
        striped_lines = []
        start = False
        for line in lines:
            if not start:
                if line.startswith("----------------------"):
                    start = True
                continue
            striped_lines.append(line.strip())

        csv_reader = csv.DictReader(striped_lines)
        thread_util.thread_pool_processor(csv_reader, save_wechat_row_thread, THREAD_POOL_SUM_ROW)
        print("微信账单-执行完成")


def alipay(filepath):
    with open(filepath, "r", encoding="gbk", newline="") as f:
        lines = f.readlines()
        striped_lines = []
        start = False
        for line in lines:
            if not start:
                if line.startswith("------------------------"):
                    start = True
                continue
            if line.startswith("----------------------------"):
                break
            l = regex.sub(r"\s+,", ",", line)
            striped_lines.append(l)

        csv_reader = csv.DictReader(striped_lines)
        thread_util.thread_pool_processor(csv_reader, save_alipay_row_thread, THREAD_POOL_SUM_ROW)
        print("支付宝账单-执行完成")


def save_wechat_row_thread(row):
    save_wechat_row(row, 10, 1)


def save_alipay_row_thread(row):
    save_alipay_row(row, 10, 1)


# 支持超时重试保存微信账单
def save_wechat_row(row, timeout, retry_count):
    try:
        if timeout > 20:
            print("超过最大超时时间"+row["商品"])
            return
        response = save_wechat(my_notion.token_auth, wechat_database_id, row, timeout)
        code = response.status_code
        if code != 200:
            print("code: "+str(code)+"=====>"+response.content.decode())
        else:
            print(str(row["商品"])+":保存成功")
    except Exception:
        print(str(row['商品'])+"=====>超时，第"+str(retry_count)+"次重试开始"+"exception:\n"+traceback.format_exc())
        save_wechat_row(row, timeout+1, retry_count + 1)


# 支持超时重试保存微信账单
def save_alipay_row(row, timeout, retry_count):
    try:
        if timeout > 20:
            print("超过最大超时时间"+row["商品说明"])
            return
        response = save_alipay(my_notion.token_auth, alipay_database_id, row, timeout)
        code = response.status_code
        if code != 200:
            print("code: "+str(code)+"=====>"+response.content.decode())
        else:
            print(str(row["商品说明"])+":保存成功")
    except Exception as e:
        print(str(row['商品说明'])+"=====>超时，第"+str(retry_count)+"次重试开始"+"exception:\n"+traceback.format_exc())
        save_alipay_row(row, timeout+1, retry_count + 1)


def save_alipay(token, target_database_id, data, timeout):
    # 重写微信账单名称
    name = data["商品说明"]
    if data["商品说明"] == '/':
        name = data['交易分类']

    # 生成写入数据
    body = gen_body_alipay(target_database_id, data, name)

    # 创建数据page
    return my_notion.create_page(token, body, timeout)


# 保存微信账单
def save_wechat(token, target_database_id, data, timeout):
    # 重写微信账单名称
    name = data["商品"]
    if data["商品"] == '/':
        name = data['交易类型']

    # 生成写入数据
    body = gen_body_wechat(target_database_id, data, name)

    # 创建数据page
    return my_notion.create_page(token, body, timeout)


def find_total_bill(search_response):
    for row in search_response['results']:
        try:
            var = row['properties']['微信账单']
            return row
        except Exception:
            continue
    return None


# 生成搜索内容
def gen_search_text(data):
    data_time = data["交易时间"]
    date = data_time.split(" ")[0]
    search_text = date.replace("-", "/")
    return search_text


# 生成数据响应体
def gen_body_wechat(target_database_id, data, name):
    return {
        "parent": {"type": "database_id", "database_id": target_database_id},
        "properties": {
            "交易时间": {
                "type": "date",
                "date": {
                    "start": data["交易时间"]
                }
            },
            "交易类型": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易类型"]}}
                ]
            },
            "商品": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["商品"]}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易对方"]}}
                ]
            },
            "当前状态": {
                "type": "select",
                "select": {
                    "name": data["当前状态"],
                }
            },
            "收/支": {
                "type": "select",
                "select": {
                    "name": data["收/支"],
                }
            },
            "金额(元)": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": data["金额(元)"]
                        }
                    }
                ]
            },
            "支付方式": {
                "type": "select",
                "select": {
                    "name": data["支付方式"],
                }
            },
            "Name": {
                "title": [
                    {"type": "text", "text": {"content": name}}
                ]
            }
        },
        # 设置文本内容
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": ""}}]
                }
            }
        ]
    }


def gen_body_alipay(target_database_id, data, name):
    return {
        "parent": {"type": "database_id", "database_id": target_database_id},
        "properties": {
            "交易时间": {
                "type": "date",
                "date": {
                    "start": data["交易时间"]
                }
            },
            "交易分类": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易分类"]}}
                ]
            },
            "商品说明": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["商品说明"]}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易对方"]}}
                ]
            },
            "交易状态": {
                "type": "select",
                "select": {
                    "name": data["交易状态"],
                }
            },
            "收/支": {
                "type": "select",
                "select": {
                    "name": data["收/支"],
                }
            },
            "金额": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["金额"]}}
                ]
            },
            "Name": {
                "title": [
                    {"type": "text", "text": {"content": name}}
                ]
            }
        },
        # 设置文本内容
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": ""}}]
                }
            }
        ]
    }


# 创建总账单页
def create_total_bill(token, target_database_id, timeout, name):
    body = {
        "parent": {"type": "database_id", "database_id": target_database_id},
        "properties": {
            "Name": {
                "title": [
                    {"type": "text", "text": {"content": name}}
                ]
            }
        }
    }
    response = my_notion.create_page(token, body, timeout)
    print(name+"创建成功")
    return response


# 模拟微信账单
def mock_wechat(target_database_id):
    body = {
        "parent": {"type": "database_id", "database_id": target_database_id},
        "properties": {
            "交易时间": {
                "type": "date",
                "date": {
                    "start": "2021-07-31 15:07:01"
                }
            },
            "交易类型": {
                "rich_text": [
                    {"type": "text", "text": {"content": "转账"}}
                ]
            },
            "商品": {
                "rich_text": [
                    {"type": "text", "text": {"content": "转账备注:兄弟 早生贵子  哈哈哈"}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": "杨占邦"}}
                ]
            },
            # "总账单": {
            #     "type": "relation",
            #     "relation": [
            #         {"id": "ecdd3db8-3853-4168-9009-a62257eb5ba1"}
            #     ]
            # },
            "当前状态": {
                "type": "select",
                "select": {
                    "name": "支付成功",
                }
            },
            "收/支": {
                "type": "select",
                "select": {
                    "name": "收入",
                }
            },
            "金额(元)": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "¥500.00"
                        }
                    }
                ]
            },
            "支付方式": {
                "type": "select",
                "select": {
                    "name": "默认",
                }
            },
            "Name": {
                "title": [
                    {"type": "text", "text": {"content": "车祸时候9"}}
                ]
            }
        },
        # 设置文本内容
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": ""}}]
                }
            }
        ]
    }
    print(my_notion.create_page(token_auth, body, 3))


# 模拟支付宝账单
def mock_alipay(target_database_id):
    body = {
        "parent": {"type": "database_id", "database_id": target_database_id},
        "properties": {
            "交易时间": {
                "type": "date",
                "date": {
                    "start": "2021-07-31 15:07:01"
                }
            },
            "交易分类": {
                "rich_text": [
                    {"type": "text", "text": {"content": "日用百货"}}
                ]
            },
            "商品说明": {
                "rich_text": [
                    {"type": "text", "text": {"content": "商品说明"}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": "天弘"}}
                ]
            },
            "交易状态": {
                "type": "select",
                "select": {
                    "name": "支付成功",
                }
            },
            "收/支": {
                "type": "select",
                "select": {
                    "name": "其他",
                }
            },
            "金额": {
                "rich_text": [
                    {"type": "text", "text": {"content": "50"}}
                ]
            },
            "Name": {
                "title": [
                    {"type": "text", "text": {"content": "测试"}}
                ]
            }
        },
        # 设置文本内容
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": ""}}]
                }
            }
        ]
    }

    print(my_notion.create_page(token_auth, body, 3))


if __name__ == '__main__':
    # wechat('C:\\Users\\Administrator\\Desktop\\微信支付账单(20210801-20211031).csv')
    # mock_wechat(wechat_database_id)
    # mock_alipay(alipay_database_id)
    alipay('C:\\Users\\Administrator\\Desktop\\alipay_record_219701-1031.csv')
    # print(create_total_bill(token_auth, total_bill_database_id, 5, "2021/07/01"))