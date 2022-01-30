# -*- coding: UTF-8 -*-
import requests
import query_notion

version_date = '2021-05-13'
token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"


# 查询database数据
def query_database(token, database_id, timeout):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/" + database_id + "/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=timeout
    )


# 更新database数据
def save_database(token, database_id, body):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/" + database_id,
        data=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=3
    )


# 创建新页面
def create_page(token, body, timeout):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/pages",
        # 生成新页面数据
        json=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=timeout
    )


# 更新页面
def update_page(token, body, timeout, page_id):
    return requests.patch(
        "https://api.notion.com/v1/pages/"+page_id,
        # 生成新页面数据
        json=body,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=timeout
    )

# 查询page数据
def query_page(token, page_id):
    return requests.request(
        "GET",
        "https://api.notion.com/v1/pages/" + page_id,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
    )


# 搜索功能
def search(token, timeout, query, database_id):
    return requests.request(
        "POST",
        "https://api.notion.com/v1/databases/"+database_id+"/query",
        # 根据text查询数据
        json=query,
        headers={"Authorization": "Bearer " + token, "Notion-Version": version_date},
        timeout=timeout
    )


# 查询微信总账单
def query_wechat(token, database_id):
    r = query_database(token, database_id, 10)
    json_context = r.json()
    # 遍历每一行元素
    for row in json_context['results']:
        # 读取属性
        print(row['properties'])


# 查询支付宝总账单
def query_alipay(token, database_id):
    r = query_database(token, database_id, 10)


if __name__ == '__main__':
    # query_wechat(token_auth, "d250ca9f916c4c0e82b66d451f434701")
    # print(query_alipay(token_auth, "651c89d606e64394ace3a6791594c183"))
    # print(query_database(token_auth, "d250ca9f916c4c0e82b66d451f434701").json())
    # database = query_database(token_auth, "526f7c6fccc54ff5b468557fce038dce", 10).json()
    # print(database)
    # for row in database['results']:
    #     print(row['properties']['总账单'])
    page = search(token_auth, 10,
                  query_notion.gen_search_condition_title("2022/01/26", "标题"),
                  "53029b8eef9e47e0a3ee916f71018c9a").json()
    print(page)
    # response = search(token_auth, 5, "2021/08/28").json()
    # print(query_bill.find_total_bill(response))
    # time = "2021-07-31 15:07:01"
    # date = time.split(" ")[0]
    # print(date.replace("-", "/"))

