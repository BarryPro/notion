# -*- coding: UTF-8 -*-
import json

import requests


def query_page_all(token):
    r = requests.request(
        "POST",
        "https://api.notion.com/v1/databases/d250ca9f916c4c0e82b66d451f434701/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )
    print(r.text)


# 查询微信总账单
def query_page_wechat(token):
    r = requests.request(
        "POST",
        "https://api.notion.com/v1/databases/651c89d606e64394ace3a6791594c183/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )
    json_context = r.json()
    print(json_context)


# 查询支付宝总账单
def query_page_alipay(token):
    r = requests.request(
        "POST",
        "https://api.notion.com/v1/databases/526f7c6fccc54ff5b468557fce038dce/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )


if __name__ == '__main__':
    token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
    query_page_wechat(token_auth)
    # query_page_alipay(token_auth)
