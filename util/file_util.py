# -*- coding: UTF-8 -*-

# 读取notion token
def read_notion_token():
    f = open("../notion_token.txt", encoding="utf-8")
    return f.read()
