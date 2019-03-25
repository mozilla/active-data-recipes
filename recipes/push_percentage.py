"""
Percentage of tests that were run for the given push.
"""
from adr.query import run_query


def run(context):
    push_tests = run_query('unique_tests', context)['data']
    push_tests = {item[0]: item[1] for item in push_tests if item[0] is not None}

    context.pushid = None
    all_tests = run_query('unique_tests', context)['data']
    all_tests = {item[0]: item[1] for item in all_tests if item[0] is not None}

    data = []
    total_push = 0
    total_num = 0
    for platform, num in all_tests.items():
        push_num = push_tests.get(platform, 0)
        percentage = round(float(push_num)/num * 100, 1)
        data.append([platform, percentage])

        total_num += num
        total_push += push_num

    data.sort()

    total_percentage = round(float(total_push)/total_num * 100, 1)
    data.append(['total', total_percentage])
    data.insert(0, ['Platform', 'Percentage of Tests Run'])
    return data
