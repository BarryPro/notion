# -*- coding: UTF-8 -*-

import my_notion

token_auth = "secret_phe6WVdTudowSUsErvQn8WXi1VILdE7li7SZ6uvjVAi"
# 账单明细表
alipay_database_id = "526f7c6fccc54ff5b468557fce038dce"


# 更新指定page页面内容
def update_bill(page_id, body):
    result = my_notion.update_page(token_auth, body, 10, page_id)
    print(result.content.decode())
    # print(body)


# 生成更新文本内容
def gen_update_content(database_id):
    return {
        "parent": {"type": "database_id", "database_id": database_id},
        "properties": {
            "账单来源": {
                "type": "select",
                "select": {
                    "name": "支付宝",
                }
            },
        }
    }


if __name__ == '__main__':
    update_bill('90f794ce-e4c4-416e-97e2-9a8e6ec0a041', gen_update_content(alipay_database_id))
