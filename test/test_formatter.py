from adr.formatter import JSONFormatter, TabFormatter, TableFormatter
from terminaltables import GithubFlavoredMarkdownTable, SingleTable
import json
import unittest


class TestJSONFormatter(unittest.TestCase):
    actual = [('Table',), ('coverage',), ('firefox-files',), ('fx-test',), ('repo',),
              ('saved_queries',), ('task',), ('treeherder',), ('unittest',)]

    expected = """[
  [
    "Table"
  ],
  [
    "coverage"
  ],
  [
    "firefox-files"
  ],
  [
    "fx-test"
  ],
  [
    "repo"
  ],
  [
    "saved_queries"
  ],
  [
    "task"
  ],
  [
    "treeherder"
  ],
  [
    "unittest"
  ]
]"""

    def test_init_none(self):
        f = JSONFormatter()
        self.assertEqual(f.indent, None)

    def test_init(self):
        f = JSONFormatter(4)
        self.assertEqual(f.indent, 4)

    def test_call(self):
        f = JSONFormatter(2)
        self.assertEqual(f(self.actual), self.expected)

    def test_call_bytes(self):
        f = JSONFormatter(2)
        self.assertEqual(f(self.expected.encode()), self.expected)


class TestTabFormatter(unittest.TestCase):
    actual = [('Table',), ('activedata_requests',), ('coverage',), ('firefox-files',),
              ('fx-test',), ('jobs',), ('repo',), ('saved_queries',), ('task',),
              ('treeherder',), ('unittest',)]
    expected = """Table
activedata_requests
coverage
firefox-files
fx-test
jobs
repo
saved_queries
task
treeherder
unittest"""

    def test_non_list(self):
        f = TabFormatter()
        data = {'key': 'value'}
        with self.assertRaises(Exception) as expected:
            f(data)
        self.assertTrue('expecting a list' in str(expected.exception))

    def test_call(self):
        f = TabFormatter()
        self.assertEqual(f(self.actual), self.expected)

    def test_call_bytes(self):
        f = TabFormatter()
        actual_bytes = json.dumps(self.actual).encode()
        self.assertEqual(f(actual_bytes), self.expected)


class TestTableFormatter(unittest.TestCase):
    def test_init(self):
        f = TableFormatter()
        self.assertEqual(f.table_cls, SingleTable)

    def test_init_table(self):
        f = TableFormatter(GithubFlavoredMarkdownTable)
        self.assertEqual(f.table_cls, GithubFlavoredMarkdownTable)

    def test_call_markdown(self):
        actual = [('Table',), ('activedata_requests',), ('coverage',), ('firefox-files',),
                  ('fx-test',),
                  ('jobs',), ('repo',), ('saved_queries',), ('task',), ('treeherder',),
                  ('unittest',)]
        expected = """| Table               |
|---------------------|
| activedata_requests |
| coverage            |
| firefox-files       |
| fx-test             |
| jobs                |
| repo                |
| saved_queries       |
| task                |
| treeherder          |
| unittest            |"""
        f = TableFormatter(GithubFlavoredMarkdownTable)
        self.assertEqual(f(actual), expected)

    def test_call_dict(self):
        f = TableFormatter(GithubFlavoredMarkdownTable)
        actual = {'Table': ['activedata_requests', 'coverage', 'jobs', 'repo']}
        expected = """| Table               |
|---------------------|
| activedata_requests |
| coverage            |
| jobs                |
| repo                |"""
        self.assertEqual(f(actual), expected)

    def test_call_dict2(self):
        f = TableFormatter(GithubFlavoredMarkdownTable)
        actual = {'names': ['Table', 'Coverage'],
                  'Table': ['activedata_requests', 'coverage', 'jobs', 'repo'],
                  'Coverage': [0, 15, 55, 100]}
        expected = """| Table               | Coverage |
|---------------------|----------|
| activedata_requests | 0        |
| coverage            | 15       |
| jobs                | 55       |
| repo                | 100      |"""
        self.assertEqual(f(actual), expected)

