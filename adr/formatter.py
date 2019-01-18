from __future__ import absolute_import, print_function

import json
from itertools import zip_longest

from terminaltables import GithubFlavoredMarkdownTable, SingleTable


class JSONFormatter(object):
    def __init__(self, indent=None):
        self.indent = indent

    def __call__(self, data):
        if isinstance(data, bytes):
            data = json.loads(data)
        return json.dumps(data, indent=self.indent)


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
                header = list(data.keys())

            example = list(data.values())[0]
            if isinstance(example, list):
                values = [data[key] for key in header]
                data = list(zip_longest(*values, fillvalue=''))
            else:
                t = []
                for key in header:
                    t.append(data[key])
                data = [t]
            data.insert(0, header)
        table = self.table_cls(data)
        return table.table


class TabFormatter(object):
    def __init__(self):
        pass

    def __call__(self, data):
        if isinstance(data, bytes):
            data = json.loads(data)

        if not isinstance(data, list):
            raise TypeError("expecting a list")

        return "\n".join(
            "\t".join(str(c) for c in row)
            for row in data
        )


all_formatters = {
    'json': JSONFormatter(indent=2),
    'markdown': TableFormatter(table_cls=GithubFlavoredMarkdownTable),
    'table': TableFormatter(),
    'tab': TabFormatter()
}
