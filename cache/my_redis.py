# -*- coding: UTF-8 -*-

# redis缓存相关操作

import redis

# host redis所在主机名
# port redis-server 开放的端口号
# db 指定操作数据的db号 1表示notion账单唯一ID数据库
# decode_responses 设置从redis取出来以字符串返回，默认是返回字节
r = redis.StrictRedis(host='10.0.0.140', port=6379, db=1, decode_responses=True)


# 缓存中写账单唯一ID
def save_bill_unique_id(bill_unique_id):
    return r.set(bill_unique_id, 1)


# 缓存中写账单唯一ID
def get_bill_unique_id(bill_unique_id):
    return r.get(bill_unique_id)


# 检查账单唯一Id是否存在
def is_exist_bill_unique_id(bill_unique_id):
    bill_id = get_bill_unique_id(bill_unique_id)
    return bill_id == '1'


if __name__ == '__main__':
    key = "124235366"
    # print(save_bill_unique_id(key))
    print(is_exist_bill_unique_id(key))
