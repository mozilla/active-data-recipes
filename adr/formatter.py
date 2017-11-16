from __future__ import print_function, absolute_import

import json

from terminaltables import GithubFlavoredMarkdownTable, SingleTable


class JSONFormatter(object):
    def __call__(self, data):
        if isinstance(data, bytes):
            data = json.loads(data)
        return json.dumps(data, indent=2)


class TableFormatter(object):
    def __init__(self, table_cls=SingleTable):
        self.table_cls = table_cls

    def __call__(self, data):
        if isinstance(data, bytes):
            data = json.loads(data)

        if isinstance(data, dict):
            if 'names' in data.keys():
                header = data.pop('names')
            else:
                header = data.keys()

            if isinstance(list(data.values())[0], list):
                data = [[i for i in data[key]] for key in header]
            else:
                t = []
                for key in header:
                    t.append(data[key])
                data = [t]
            data.insert(0, header)

        table = self.table_cls(data)
        return table.table


all_formatters = {
    'json': JSONFormatter(),
    'markdown': TableFormatter(table_cls=GithubFlavoredMarkdownTable),
    'table': TableFormatter(),
}
