# -*- coding: UTF-8 -*-

# redis缓存相关操作

import redis

# host redis所在主机名
# port redis-server 开放的端口号
# db 指定操作数据的db号 1表示notion账单唯一ID数据库
# decode_responses 设置从redis取出来以字符串返回，默认是返回字节
r = redis.StrictRedis(host='10.0.0.140', port=6379, db=2, decode_responses=True)


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


def set_nx_bill_unique_id(bill_unique_id):
    #  是否设置唯一键成功，true成功，false设置失败，表示之前列表已经存在
    key_ = "bill_nx_"+bill_unique_id
    #  10分钟有效期
    r.expire(key_, 600)
    return r.setnx("bill_nx_"+bill_unique_id, 1) == 1


def save_dup_bill_key_list(date, bill_unique_id):
    r.hset("dup_bill_dict", date, bill_unique_id)


if __name__ == '__main__':
    key = "124235366"
    # print(save_bill_unique_id(key))
    print(is_exist_bill_unique_id(key))
