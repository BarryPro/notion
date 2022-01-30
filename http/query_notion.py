# -*- coding: UTF-8 -*-
import my_notion
import json

version_date = '2021-05-13'
token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"


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


if __name__ == '__main__':
    page = my_notion.search(token_auth, 5, gen_search_condition_time("2022-01-26", "2022-01-27", "交易时间"),
                            "526f7c6fccc54ff5b468557fce038dce")
    page_json = page.json()
    for result in page_json['results']:
        properties = result['properties']
        print(properties['月份']['formula']['string'])
        print(properties['日期']['formula']['string'])



