# -*- coding: UTF-8 -*-
import json

import requests


# 查询database数据
def query_database(token, database_id):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/"+database_id+"/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )


# 更新database数据
def save_database(token, database_id, body):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/"+database_id,
        json=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )


# 查询page数据
def query_page(token, page_id):
    return requests.request(
        "GET",
        "https://api.notion.com/v1/pages/"+page_id,
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
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
def save_wechat(token, database_id):
    r = query_database(token, database_id)
    json_context = r.json()
    # 遍历每一行元素
    for row in json_context['results']:
        # 读取属性
        row['properties']["备注"] = "python"
    # print(json_context)
    print(save_database(token, database_id, json_context))


# 查询支付宝总账单
def query_alipay(token, database_id):
    r = query_database(token, database_id)


if __name__ == '__main__':
    token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
    # query_wechat(token_auth, "651c89d606e64394ace3a6791594c183")
    save_wechat(token_auth, "651c89d606e64394ace3a6791594c183")
    # query_alipay(token_auth, "526f7c6fccc54ff5b468557fce038dce")
    # query_page(token_auth, "abf019c0-bbf3-4abe-ad48-f3110d386849")
    # query_database(token_auth, "d250ca9f916c4c0e82b66d451f434701")