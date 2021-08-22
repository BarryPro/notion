# -*- coding: UTF-8 -*-
import csv

import arrow
import regex as regex
import notion

token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
wechat_database_id = "651c89d606e64394ace3a6791594c183"
total_bill_database_id = "d250ca9f916c4c0e82b66d451f434701"


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
        for row in csv_reader:
            try:
                save_wechat_row(row, 3, 1)
            except Exception:
                print("写微信数据异常")
                print(row)
        print("执行完成")


# 支持超时重试保存微信账单
def save_wechat_row(row, timeout, retry_count):
    try:
        if timeout > 10:
            print("超过最大超时时间")
            return
        response = save_wechat(notion.token_auth, wechat_database_id, row, timeout)
        code = response.status_code
        if code != 200:
            print(code)
            print(row)
        else:
            print(str(row["商品"])+":保存成功")
    except Exception:
        print(str(row['商品'])+":超时，第"+str(retry_count)+"次重试开始")
        save_wechat_row(row, timeout+1, retry_count + 1)


# 保存微信账单
def save_wechat(token, target_database_id, data, timeout):
    # 重写微信账单名称
    name = data["商品"]
    if data["商品"] == '/':
        name = data['交易类型']

    # 获取搜索账单名称
    search_text = ""
    try:
        search_text = gen_search_text(data)
    except Exception:
        print("生成搜索文本失败")
        search_text = gen_search_text(data)

    # 获取关联数据库ID
    relation_database_id = ""
    create_total_bill_response = ""
    try:
        search_response = notion.search(token, 3, search_text).json()
        find_result = find_total_bill(search_response)
        # 检查是否存在本日账单
        if find_result is None:
            print("没有当日总账单，新创建账单")
            create_total_bill_response = create_total_bill(token, total_bill_database_id, 5, search_text)
        # 创建成功搜索新创建的总账单
        else:
            relation_database_id = find_result['id']
            print("搜索成功："+str(relation_database_id))
    except Exception:
        print(str(search_text)+"关联异常")
        create_total_bill_response = create_total_bill(token, total_bill_database_id, 5, search_text)
        if create_total_bill_response.status_code == 200:
            search_response = notion.search(token, 3, search_text).json()
            find_result = find_total_bill(search_response)
            relation_database_id = find_result['id']
            print("Exception搜索成功：" + str(relation_database_id))
        else:
            raise Exception("需要重试异常")

    # 生成写入数据
    body = gen_body(target_database_id, data, relation_database_id, name)
    print(body)

    # 创建数据page
    return notion.create_page(token, body, timeout)


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
def gen_body(target_database_id, data, relation_id, name):
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
            "总账单": {
                "type": "relation",
                "relation": [
                    {"id": relation_id}
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
    response = notion.create_page(token, body, timeout)
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
    print(notion.create_page(token_auth, body, 3))


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
        for row in csv_reader:
            t = arrow.get(row["交易时间"]).replace(tzinfo="+08").datetime
            c = row["商品说明"] + "，" + row["交易对方"]
            a = row["金额"]
            d = row["收/支"]
            print(t, c, a, d)
            if a == "0":
                print("[未被计入]")
                continue
            elif d == "已收入" or d == "解冻":
                a = "-" + a
            elif d == "已支出" or d == "冻结":
                pass
            else:
                print("[未被计入]")
                continue


if __name__ == '__main__':
    # query_page('secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi')
    wechat('C:\\Users\\Administrator\\Desktop\\微信支付账单(20210701-20210731).csv')
    # mock_wechat("651c89d606e64394ace3a6791594c183")
    # alipay('C:\\Users\\Administrator\\Desktop\\alipay_record_20210816_083101.csv')
    # print(create_total_bill(token_auth, total_bill_database_id, 5, "2021/07/01"))