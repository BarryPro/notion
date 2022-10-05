# -*- coding: UTF-8 -*-
import os

# 读取notion token
def read_notion_token():
    f = open("../notion_token.txt", encoding="utf-8")
    return f.read()


# 读取目录下所有文件名
def read_files_path(path):
    return os.listdir(path)


if __name__ == '__main__':
    list = read_files_path("/root/bill")
    for file_name in list:
        print(file_name)
