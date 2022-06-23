# -*- coding: UTF-8 -*-

import my_notion

token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
# 账单明细表
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"
# 日报id
day_database_id = "53029b8eef9e47e0a3ee916f71018c9a"
# 月报ID
month_database_id = "bbc595d50e2b4db3b9a28fb404d2222d"
# 最大重试次数
MAX_RETRY_COUNT = 15


# 更新指定page页面内容
def update_bill(page_id, body, timeout, retry_count):
    try:
        if timeout > MAX_RETRY_COUNT:
            print("超过最大超时时间"+page_id)
            return
        response = my_notion.update_page(token_auth, body, timeout, page_id)
        code = response.status_code
        if code != 200:
            print(page_id+"code: "+str(code)+"=====>"+response.content.decode()+"\n")
            update_bill(page_id, body, timeout+1, retry_count + 1)
        else:
            return response
    except Exception as e:
        print(str(page_id)+"=====>超时，第"+str(retry_count)+"次重试开始"+"\n")
        update_bill(page_id, body, timeout+1, retry_count + 1)


# 生成更新文本内容
def gen_update_content(database_id, day_id, month_id):
    return {
        "parent": {"type": "database_id", "database_id": database_id},
        "properties": {
            "日报": {
                "type": "relation",
                "relation": [
                    {
                        "id": day_id
                    }
                ]
            },
            "月报": {
                "type": "relation",
                "relation": [
                    {
                        "id": month_id
                    }
                ]
            },
        }
    }


if __name__ == '__main__':
    update_bill('ce620594aac14b6badc867aa889cf8b2',
                gen_update_content(alipay_database_id, "aa51762e-bb28-4d86-b3c2-b4a5837ab780", "6378dd6a-a00e-4b6f-a9de-61c746414498"), 10, 1)
    # print(my_notion.search(token_auth, 10, "2022年1月", month_database_id, "月份").json())


