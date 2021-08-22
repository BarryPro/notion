# -*- coding: UTF-8 -*-
import csv

import arrow
import regex as regex
import notion


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
                save_wechat(row, 3, 1)
            except Exception:
                print("写微信数据异常")
                print(row)
        print("执行完成")


# 支持超时重试保存微信账单
def save_wechat(row, timeout, retry_count):
    try:
        if timeout > 10:
            print("超过最大超时时间")
            return
        response = notion.save_wechat(notion.token_auth, "651c89d606e64394ace3a6791594c183", row, timeout)
        code = response.status_code
        if code != 200:
            print(code)
            print(row)
        else:
            print(str(row["商品"])+":保存成功")
    except Exception:
        print(str(row['商品'])+":超时，第"+str(retry_count)+"次重试开始")
        save_wechat(row, timeout+1, retry_count + 1)


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

    # alipay('C:\\Users\\Administrator\\Desktop\\alipay_record_20210816_083101.csv')
