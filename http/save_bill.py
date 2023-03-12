# -*- coding: UTF-8 -*-
import csv

import regex as regex
import my_notion
from cache import my_redis
from util import thread_util
from util import file_util
from threading import Thread

total_bill_database_id = "d250ca9f916c4c0e82b66d451f434701"
# 账单明细表
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"


# 线程池数量-账单行数
THREAD_POOL_SUM_ROW = 200
# 超时时间10秒
TIME_OUT = 10
# 最大重试次数
MAX_RETRY_COUNT = 5

WECHAT = "wechat"
ALIPAY = "alipay"

REPEAT = "repeat"


def wechat(filepath):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        lines = f.readlines()
        striped_lines = []
        start = False
        BILL_PERSON = lines[1].replace("微信昵称：[", "").replace("],,,,,,,,", "")
        for line in lines:
            if not start:
                if line.startswith("----------------------"):
                    start = True
                continue
            striped_lines.append(line.strip())

        csv_reader = csv.DictReader(striped_lines)
        csv_list = []
        for csv_reader_item in csv_reader:
            csv_list.append({"BILL_PERSON": BILL_PERSON, "CSV_READER_ITEM": csv_reader_item})
        thread_util.thread_pool_processor(csv_list, save_wechat_row_thread, THREAD_POOL_SUM_ROW)
        print("微信账单-执行完成\n")


def alipay(filepath):
    with open(filepath, "r", encoding="gbk", newline="") as f:
        lines = f.readlines()
        striped_lines = []
        start = False
        BILL_PERSON = ''
        for line in lines:
            if not start:
                if line.startswith("------------------------支付宝"):
                    start = True
                    continue
            if line.startswith("--------------------------------------------"):
                BILL_PERSON = lines[lines.index(line)+2].replace("姓名：", "")
                continue
            if start:
                # 有效的账单记录
                striped_lines.append(regex.sub(r"\s+,", ",", line))

        csv_reader = csv.DictReader(striped_lines)
        csv_list = []
        for csv_reader_item in csv_reader:
            csv_list.append({"BILL_PERSON": BILL_PERSON, "CSV_READER_ITEM": csv_reader_item})
        thread_util.thread_pool_processor(csv_list, save_alipay_row_thread, THREAD_POOL_SUM_ROW)
        print("支付宝账单-执行完成\n")


def save_wechat_row_thread(csv_list):
    save_wechat_row(csv_list["CSV_READER_ITEM"], 10, 1, csv_list["BILL_PERSON"])


def save_alipay_row_thread(csv_list):
    save_alipay_row(csv_list["CSV_READER_ITEM"], 10, 1, csv_list["BILL_PERSON"])


# 支持超时重试保存微信账单
def save_wechat_row(row, timeout, retry_count, bill_person):
    try:
        if retry_count > MAX_RETRY_COUNT:
            print("超过最大超时时间"+row["商品"]+"\n")
            return
        response = save_wechat(my_notion.token_auth, alipay_database_id, row, timeout, bill_person)
        if response == REPEAT:
            return
        code = response.status_code
        if code != 200:
            print(row["商品"]+"code: "+str(code)+"=====>"+response.content.decode())
        else:
            print(str(row["商品"])+":保存成功\n")
            # 写入缓存
            my_redis.save_bill_unique_id(gen_unique_id(WECHAT, row))
    except Exception:
        print(str(row['商品'])+"=====>超时，第"+str(retry_count)+"次重试开始\n")
        save_wechat_row(row, timeout+1, retry_count + 1, bill_person)


# 支持超时重试保存微信账单
def save_alipay_row(row, timeout, retry_count, bill_person):
    try:
        if retry_count > MAX_RETRY_COUNT:
            print("超过最大超时时间"+row["商品说明"]+"\n")
            return
        response = save_alipay(my_notion.token_auth, alipay_database_id, row, timeout, bill_person)
        if response == REPEAT:
            return
        code = response.status_code
        if code != 200:
            print(row["商品说明"]+"code: "+str(code)+"=====>"+response.content.decode()+"\n")
        else:
            print(str(row["商品说明"])+":保存成功\n")
            # 写入缓存
            my_redis.save_bill_unique_id(gen_unique_id(ALIPAY, row))
    except Exception as e:
        print(str(row['商品说明'])+"=====>超时，第"+str(retry_count)+"次重试开始"+"\n")
        save_alipay_row(row, timeout+1, retry_count + 1, bill_person)


def save_alipay(token, target_database_id, data, timeout, bill_person):
    # 重写微信账单名称
    name = data["商品说明"]
    if data["商品说明"] == '/':
        name = data['交易分类']

    # 生成写入数据
    body = gen_body_alipay(target_database_id, data, name, bill_person)

    # 查询缓存，如果缓存不存在写notion数据库
    if not my_redis.is_exist_bill_unique_id(gen_unique_id(ALIPAY, data)):
        # 创建数据page
        return my_notion.create_page(token, body, timeout)
    else:
        print(name+": notion数据库已经存在\n")
        return REPEAT


# 保存微信账单
def save_wechat(token, target_database_id, data, timeout, bill_person):
    # 重写微信账单名称
    name = data["商品"]
    if data["商品"] == '/':
        name = data['交易对方']+"-"+data['交易类型']
    elif data['交易类型'] == '转账':
        name = data['交易对方'] + "-" + data['交易类型']

    # 生成写入数据
    body = gen_body_wechat(target_database_id, data, name, bill_person)
    # 查询缓存,如果缓存不存在操作写notion数据库
    if not my_redis.is_exist_bill_unique_id(gen_unique_id(WECHAT, data)):
        # 创建数据page
        return my_notion.create_page(token, body, timeout)
    else:
        print(name+": notion数据库已经存在\n")
        return REPEAT


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
def gen_body_wechat(target_database_id, data, name, bill_person):
    pay_method = data["支付方式"] if data["支付方式"] != '/' else "默认"
    pay_method = pay_method.replace("浦发银行", "浦发银行储蓄卡").replace("北京银行", "北京银行储蓄卡")
    money = str(data["金额(元)"]).replace("¥", "")
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
                "type": "select",
                "select": {
                    "name": data["交易类型"],
                }
            },
            "交易说明": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["商品"]}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易对方"]}}
                ]
            },
            "账单归属人": {
                "type": "select",
                "select": {
                    "name": bill_person,
                }
            },
            "交易状态": {
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
            "收/付款方式": {
                "type": "select",
                "select": {
                    "name": pay_method,
                }
            },
            "金额": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": money
                        }
                    }
                ]
            },
            "账单来源": {
                "type": "select",
                "select": {
                    "name": "微信",
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


def gen_body_alipay(target_database_id, data, name, bill_person):
    pay_method = data["收/付款方式"] if data["收/付款方式"] != '' else "默认"
    if pay_method.find('花呗') >= 0:
        pay_method = "花呗"
    if pay_method.find("北京银行信用卡(6657)") >= 0:
        pay_method = "北京银行信用卡(6657)"
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
                "type": "select",
                "select": {
                    "name": data["交易分类"],
                }
            },
            "交易说明": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["商品说明"]}}
                ]
            },
            "交易对方": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["交易对方"]}}
                ]
            },
            "账单归属人": {
                "type": "select",
                "select": {
                    "name": bill_person,
                }
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
            "收/付款方式": {
                "type": "select",
                "select": {
                    "name": pay_method,
                }
            },
            "金额": {
                "rich_text": [
                    {"type": "text", "text": {"content": data["金额"]}}
                ]
            },
            "账单来源": {
                "type": "select",
                "select": {
                    "name": "支付宝",
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
    response = my_notion.create_page(token, body, timeout)
    print(name+"创建成功\n")
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
    print(my_notion.create_page(my_notion.token_auth, body, 3))


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

    print(my_notion.create_page(my_notion.token_auth, body, 3))


# 生成唯一标识
def gen_unique_id(pay_type, data):
    if pay_type == WECHAT:
        name = data["商品"]
        if data["商品"] == '/':
            name = data['交易对方'] + "-" + data['交易类型']
        elif data['交易类型'] == '转账':
            name = data['交易对方'] + "-" + data['交易类型']
        return name + data["交易时间"] + data["金额(元)"]
    else:
        name = data["商品说明"]
        if data["商品说明"] == '/':
            name = data['交易分类']
        return name + data["交易时间"] + data["金额"]


# 读取账单文件名
def read_bill_file():
    root_dir = "/root/bill/"
    map = {}
    ali_list = []
    we_list = []
    map["alipay"] = ali_list
    map["wechat"] = we_list
    for file_name in file_util.read_files_path(root_dir):
        if "alipay" in file_name:
            map["alipay"].append(root_dir+file_name)
        if "微信" in file_name:
            map["wechat"].append(root_dir+file_name)
    return map


if __name__ == '__main__':
    map = read_bill_file()
    # 多线程执行
    for we_file in map.get("wechat"):
        wec = Thread(target=wechat, args=(we_file,))
        wec.start()
    for ali_file in map.get("alipay"):
        ali = Thread(target=alipay, args=(ali_file,))
        ali.start()

    # mock_wechat(wechat_database_id)
    # mock_alipay(alipay_database_id)
    # print(create_total_bill(token_auth, total_bill_database_id, 5, "2021/07/01"))