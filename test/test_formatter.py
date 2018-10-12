import os
import io
import json
import pytest
import formatter_tests
from adr.formatter import all_formatters


test_data=([['Heading A', 'Heading B'],[1, 2],[3, 4],[5,6]],{'names': ['Heading A', 'Heading B', 'Heading C'],
    'Heading A': ['x', 'y'],
    'Heading B': [11, 20.5],
    'Heading C': [12, 30.5]
})

def get_data(path):
    with io.open(path,'r',encoding="utf-8") as f:
        data = json.load(f)
    return data


test_dir=os.path.dirname(formatter_tests.__file__)

expected_table=get_data(os.path.join(test_dir,'tableformatter_expected.json'))["expected_table"]
expected_json= get_data(os.path.join(test_dir,'jsonformatter_expected.json'))["expected_json"]
expected_markdown=get_data(os.path.join(test_dir,'markdownformatter_expected.json'))["expected_markdown"]



@pytest.mark.parametrize("test_data,expected_json",list(zip(test_data,expected_json)),ids=["jsonformat_case1", "jsonformat_case2"])
def test_jsonformatter(test_data,expected_json):
    """check MarkdownFormatter method """
    assert all_formatters['json'](test_data)==expected_json.strip()


@pytest.mark.parametrize("test_data,expected_table",list(zip(test_data,expected_table)),ids=["tableformat_case1", "tableformat_case2"])
def test_tableformatter(test_data,expected_table):
    """check MarkdownFormatter method """
    assert all_formatters['table'](test_data)==expected_table.strip()

@pytest.mark.parametrize("test_data,expected_markdown",list(zip(test_data,expected_markdown)),ids=["markdownformat1", "markdownformat2"])
def test_markdownformatter(test_data,expected_markdown):
    """check MarkdownFormatter method """
    assert all_formatters['markdown'](test_data)==expected_markdown.strip()
