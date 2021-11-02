# -*- coding: UTF-8 -*-
import threadpool


# 线程池执行
def thread_pool_processor(sources, thread_function, thread_sum):
    task_pool = threadpool.ThreadPool(thread_sum)
    requests = threadpool.makeRequests(thread_function, sources)
    [task_pool.putRequest(req) for req in requests]
    # 等待执行完
    task_pool.wait()


def execute(source):
    print(source)


if __name__ == '__main__':
    thread_pool_processor(["234", "234", "234"], execute, 10)
