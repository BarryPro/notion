# -*- coding: UTF-8 -*-
import json
import sys

import requests

version_date = '2021-08-16'
token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"


# 查询database数据
def query_database(token, database_id):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/" + database_id + "/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=0.5
    )


# 更新database数据
def save_database(token, database_id, body):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/" + database_id,
        data=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=0.5
    )


# 创建新页面
def create_page(token, body, timeout):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/pages",
        # 生成新页面数据
        json=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-05-13"},
        timeout=timeout
    )


# 查询page数据
def query_page(token, page_id):
    return requests.request(
        "GET",
        "https://api.notion.com/v1/pages/" + page_id,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
    )


# 查询微信总账单
def query_wechat(token, database_id):
    r = query_database(token, database_id)
    json_context = r.json()
    # 遍历每一行元素
    for row in json_context['results']:
        # 读取属性
        print(row['properties'])


# 保存微信账单
def save_wechat(token, target_database_id, data, timeout):
    body = {
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
            "总账单": {
                "type": "relation",
                "relation": [
                    {"id": "ecdd3db8-3853-4168-9009-a62257eb5ba1"}
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
                    {"type": "text", "text": {"content": data["商品"]}}
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
    return create_page(token, body, timeout)


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
            "总账单": {
                "type": "relation",
                "relation": [
                    {"id": "ecdd3db8-3853-4168-9009-a62257eb5ba1"}
                ]
            },
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
    print(create_page(token_auth, body, 3))


# 查询支付宝总账单
def query_alipay(token, database_id):
    r = query_database(token, database_id)


if __name__ == '__main__':
    # query_wechat(token_auth, "651c89d606e64394ace3a6791594c183")
    mock_wechat("651c89d606e64394ace3a6791594c183")
    # query_alipay(token_auth, "526f7c6fccc54ff5b468557fce038dce")
    # print(query_database(token_auth, "1a6a5e229797468f80df3f5732730148").json())
    # database = query_database(token_auth, "651c89d606e64394ace3a6791594c183").json()
    # for row in database['results']:
    #     print(row['properties']['总账单'])
    # page = query_page(token_auth, "9f41a7db-d256-4376-bca2-555690ea633b").json()
    # print(page)
