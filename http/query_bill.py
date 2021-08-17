# -*- coding: UTF-8 -*-
import csv
import arrow
import regex as regex
from pip._vendor import requests


def query_page(token):
    r = requests.request(
        "POST",
        "https://api.notion.com/v1/databases/d250ca9f916c4c0e82b66d451f434701/query",
        headers={"Authorization": "Bearer " + token, "Notion-Version": "2021-07-27"},
    )
    print(r.text)


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
            t = arrow.get(row["交易时间"]).replace(tzinfo="+08").datetime
            c = row["商品"] + "，" + row["交易类型"] + "，" + row["交易对方"]
            a = row["金额(元)"]
            d = row["收/支"]
            print(t, c, a, d)
            if d == "收入":
                a = "-" + a[1:]
            elif d == "支出":
                a = a[1:]
            else:
                print("[未被计入]")
                continue


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
    # wechat('C:\\Users\\Administrator\\Desktop\\微信支付账单(20210701-20210731).csv')

    alipay('C:\\Users\\Administrator\\Desktop\\alipay_record_20210816_083101.csv')
