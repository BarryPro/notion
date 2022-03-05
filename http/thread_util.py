# -*- coding: UTF-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed

import threadpool


# 线程池执行
def thread_pool_processor(sources, thread_function, thread_sum):
    task_pool = threadpool.ThreadPool(thread_sum)
    requests = threadpool.makeRequests(thread_function, sources)
    [task_pool.putRequest(req) for req in requests]
    # 等待执行完
    task_pool.wait()


# 线程池带返回值
def thread_pool_submit_processor(sources, thread_function, thread_sum):
    with ThreadPoolExecutor(thread_sum) as t:
        result = [t.submit(thread_function, i) for i in sources]
        return result


# 线程池返回值处理
def thread_pool_feature_result_processor(all_tasks):
    results = []
    for future in as_completed(all_tasks):
        result = future.result()
        results.append(result)
    return results


def execute(source):
    print(source)


if __name__ == '__main__':
    thread_pool_processor(["234", "234", "234"], execute, 10)
