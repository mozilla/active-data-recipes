from adr.formatter import JSONFormatter, TabFormatter, TableFormatter
from terminaltables import GithubFlavoredMarkdownTable, SingleTable
import json
import pytest
import yaml


class TestJSONFormatter(object):

    def test_init_none(self):
        f = JSONFormatter()
        assert f.indent is None

    def test_init(self):
        f = JSONFormatter(4)
        assert f.indent == 4

    def test_call_bytes(self, json_formatter_test):
        f = JSONFormatter(2)
        actual = f(json_formatter_test['expected'].encode())
        expected = json_formatter_test['expected']
        assert actual == expected

    def test_call(self, json_formatter_test):
        f = JSONFormatter(2)
        actual = f(json_formatter_test['actual'])
        expected = json_formatter_test['expected']
        assert actual == expected


class TestTabFormatter():

    def test_call(self, tab_formatter_test):
        f = TabFormatter()
        actual = f(tab_formatter_test['actual'])
        expected = tab_formatter_test['expected']
        assert actual == expected

    def test_call_bytes(self, tab_formatter_test):
        f = TabFormatter()
        actual = f(json.dumps(tab_formatter_test['actual']).encode())
        expected = tab_formatter_test['expected']
        assert actual == expected


class TestTableFormatter():
    def test_init(self):
        f = TableFormatter()
        assert f.table_cls == SingleTable

    def test_init_table(self):
        f = TableFormatter(GithubFlavoredMarkdownTable)
        assert f.table_cls == GithubFlavoredMarkdownTable

    def test_call(self, table_formatter_test):
        f = TableFormatter(GithubFlavoredMarkdownTable)
        actual = f(table_formatter_test['actual'])
        expected = table_formatter_test['expected']
        assert actual == expected
