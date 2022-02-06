# -*- coding: UTF-8 -*-
import my_notion
import update_bill
import traceback
import thread_util

version_date = '2021-05-13'
token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
# 账单明细表
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"
# 最大重试次数
MAX_RETRY_COUNT = 15
# 线程池数量-账单行数
THREAD_POOL_SUM_ROW = 200


# 按时间范围查找
def query_time(start, end):
    print(start)


# 生成根据title的查询条件
def gen_search_condition_title(text, property_name):
    return {
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time"
            },
            "filter": {
                "and": [
                    {
                        "property": property_name,
                        "text": {
                            "contains": text
                        }
                    }
                ]
            }
        }


# 生成根据时间范围的查询条件
def gen_search_condition_time(start, end, property_name):
    return {
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time"
            },
            "filter": {
                "and": [
                    {
                        "property": property_name,
                        "date": {
                            "on_or_after": start
                        }
                    },
                    {
                        "property": property_name,
                        "date": {
                            "on_or_before": end
                        }
                    }
                ]
            }
        }


# 支持超时重试保存微信账单
def search_processor(query, property_name, database_id, timeout, retry_count):
    try:
        if timeout > MAX_RETRY_COUNT:
            print("超过最大超时时间"+query)
            return
        response = my_notion.search(token_auth, timeout, gen_search_condition_title(query, property_name), database_id)
        code = response.status_code
        if code != 200:
            print(query+"code: "+str(code)+"=====>"+response.content.decode()+"\n")
            search_processor(query, property_name, database_id, timeout + 1, retry_count + 1)
        else:
            return response
    except Exception as e:
        print(str(query)+"=====>超时，第"+str(retry_count)+"次重试开始"+"\n")
        search_processor(query, property_name, database_id, timeout+1, retry_count + 1)


def update_thread(page_result):
    properties = page_result['properties']
    page_id = page_result['id']
    # 搜索月报
    month = properties['月份']['formula']['string']
    month_page = search_processor(month, "月份", "bbc595d50e2b4db3b9a28fb404d2222d", 5, 10)
    day_id = ""
    month_id = ""
    if month_page is not None:
        if month_page.json()['results'] is not None:
            if len(month_page.json()['results']) > 0:
                month_id = month_page.json()['results'][0]['id']
                print("month_id: "+month_id)

    # 搜索日报
    day = properties['日期']['formula']['string']
    day_page = search_processor(day, "标题", "53029b8eef9e47e0a3ee916f71018c9a", 10, 1)
    if day_page is not None:
        if day_page.json()['results'] is not None:
            if len(day_page.json()['results']) > 0:
                day_id = day_page.json()['results'][0]['id']
                print("day_id: "+day_id)

    # 参数是否合法检查
    if month_id == "" or day_id == "":
        return
    # 设置月份id
    update_content = update_bill.gen_update_content(alipay_database_id, day_id, month_id)
    # print(update_content)
    update_result = update_bill.update_bill(page_id, update_content, 5, 1)
    print("page_id: "+page_id+","+page_result['url'])
    print(update_result)


if __name__ == '__main__':
    page = my_notion.search(token_auth, 10, gen_search_condition_time("2021-04-24", "2021-04-24", "交易时间"),
                            "526f7c6fccc54ff5b468557fce038dce")
    page_json = page.json()
    index = 1
    results = page_json['results']
    print("一共"+str(len(results))+"条数据")
    # print(page_json)
    thread_util.thread_pool_processor(results, update_thread, THREAD_POOL_SUM_ROW)





