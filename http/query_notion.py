# -*- coding: UTF-8 -*-

import future as future

import my_notion
import update_bill
import traceback
import thread_util

version_date = '2021-05-13'
token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
# 账单明细表
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"
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
        if retry_count <= 0:
            print("超过最大超时时间"+query)
            return
        response = my_notion.search(token_auth, timeout, gen_search_condition_title(query, property_name), database_id)
        code = response.status_code
        if code != 200:
            print(query+"code: "+str(code)+"=====>"+response.content.decode()+"\n")
            search_processor(query, property_name, database_id, timeout + 1, retry_count - 1)
        else:
            return response
    except Exception as e:
        print(str(query)+"=====>超时，第"+str(retry_count)+"次重试开始"+"\n")
        search_processor(query, property_name, database_id, timeout+1, retry_count - 1)


def get_id(query_context, query_prop, database_id, timeout, retry_count):
    # 执行搜索
    page_result = search_processor(query_context, query_prop, database_id, timeout, retry_count)
    if page_result is not None:
        if page_result.json()['results'] is not None:
            if len(page_result.json()['results']) > 0:
                return page_result.json()['results'][0]['id']
    return None


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


def thread_search_day_id(day):
    day_dict = {}
    day_id = get_id(day, "标题", "53029b8eef9e47e0a3ee916f71018c9a", 20, 3)
    if day_id is not None:
        day_dict[day] = day_id
    else:
        day_dict[day] = ""
    return day_dict


# 账单结构转换为dict提高查询效率
def convert_month_day_dict(bills):
    # 月份与日期映射关系 格式{12月:{1日:[账单1,账单2],day_id:"日期ID"},month_id:"12月id"}
    month_day_dict = {}
    # 填装月日dict结构
    for bill in bills:
        month = bill["properties"]["月份"]["formula"]["string"]
        day = bill["properties"]["日期"]["formula"]["string"]
        if month in month_day_dict.keys():
            # 天与账单映射 格式{1日:[账单1,账单2],day_id:"日期ID"}
            day_map = month_day_dict[month]
            # 账单对象列表
            if day in day_map.keys():
                bill_list = day_map[day]["data"]
                bill_list.append(bill["id"])
            else:
                day_map[day] = {}
                day_map[day]["data"] = [bill["id"]]
        else:
            month_day_dict[month] = {}
            month_id = get_id(month, "月份", "bbc595d50e2b4db3b9a28fb404d2222d", 10, 5)
            if month_id is None:
                return "查询月份ID失败，请重新查询"
            month_day_dict["month_id"] = month_id
    # 填充day_id
    for month in month_day_dict.keys():
        if month == "month_id":
            continue
        # 单独多线程查询当月的日报id
        days_dict = \
            thread_util.thread_pool_submit_processor(month_day_dict[month], thread_search_day_id, THREAD_POOL_SUM_ROW)
        days_result = thread_util.thread_pool_feature_result_processor(days_dict)
        # print(days_result)
        for day in days_result:
            for day_key in day.keys():
                # print(month_day_dict[month][day_key])
                # print(day[day_key])
                month_day_dict[month][day_key]["day_id"] = day[day_key]

    return month_day_dict


def update_bill_month_day(bill):
    bill_item = bill.split("#")
    bill_id = bill_item[0]
    day_id = bill_item[1]
    month_id = bill_item[2]
    # 设置月份id
    update_content = update_bill.gen_update_content(alipay_database_id, day_id, month_id)
    # print(update_content)
    update_result = update_bill.update_bill(bill_id, update_content, 5, 5)
    print("page_id: " + bill_id + "更新成功")
    print(update_result)


def convert_bill_list_4_month_day(month_day_dict):
    bill_result = []
    for month_key in month_day_dict.keys():
        if month_key != "month_id":
            for day_key in month_day_map[month_key].keys():
                for bill in month_day_map[month_key][day_key]["data"]:
                    bill_item = bill+"#"+month_day_map[month_key][day_key]["day_id"]+"#"+month_day_dict["month_id"]
                    bill_result.append(bill_item)
    return bill_result


if __name__ == '__main__':
    page = my_notion.search(token_auth, 15, gen_search_condition_time("2021-04-26", "2021-04-26", "交易时间"),
                            "526f7c6fccc54ff5b468557fce038dce")
    page_json = page.json()
    index = 1
    results = page_json['results']
    print("一共"+str(len(results))+"条数据")
    # 低效率按账单条数查询与插入
    # thread_util.thread_pool_processor(results, update_thread, THREAD_POOL_SUM_ROW)

    # 格式转换dict按月和日做聚合
    month_day_map = convert_month_day_dict(results)
    bills_list = convert_bill_list_4_month_day(month_day_map)
    print(bills_list)
    thread_util.thread_pool_processor(bills_list, update_bill_month_day, THREAD_POOL_SUM_ROW)






