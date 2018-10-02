import pytest
from adr.formatter import all_formatters

test_data=([['Heading A', 'Heading B'],[1, 2],[3, 4],[5,6]],{'names': ['Heading A', 'Heading B', 'Heading C'],
    'Heading A': ['x', 'y'],
    'Heading B': [11, 20.5],
    'Heading C': [12, 30.5]
})

expected_table=(
 """
┌───────────┬───────────┐
│ Heading A │ Heading B │
├───────────┼───────────┤
│ 1         │ 2         │
│ 3         │ 4         │
│ 5         │ 6         │
└───────────┴───────────┘""",
 """
┌───────────┬───────────┬───────────┐
│ Heading A │ Heading B │ Heading C │
├───────────┼───────────┼───────────┤
│ x         │ 11        │ 12        │
│ y         │ 20.5      │ 30.5      │
└───────────┴───────────┴───────────┘"""
)

expected_json=(
"""
[
  [
    "Heading A",
    "Heading B"
  ],
  [
    1,
    2
  ],
  [
    3,
    4
  ],
  [
    5,
    6
  ]
]

""",
"""
{
  "names": [
    "Heading A",
    "Heading B",
    "Heading C"
  ],
  "Heading A": [
    "x",
    "y"
  ],
  "Heading B": [
    11,
    20.5
  ],
  "Heading C": [
    12,
    30.5
  ]
}
"""
)

expected_tab=(
"""
Heading A	Heading B
1	2
3	4
5	6
"""
)

expected_markdown=(
"""
| Heading A | Heading B |
|-----------|-----------|
| 1         | 2         |
| 3         | 4         |
| 5         | 6         |
""",
"""
| Heading A | Heading B | Heading C |
|-----------|-----------|-----------|
| x         | 11        | 12        |
| y         | 20.5      | 30.5      |"""
)

@pytest.mark.parametrize("test_data,expected_json",list(zip(test_data,expected_json)))
def test_jsonformatter(test_data,expected_json):
    """check JSONFormatter method """
    assert all_formatters['json'](test_data)==expected_json.strip()

@pytest.mark.parametrize("test_data,expected_table",list(zip(test_data,expected_table)))
def test_tableformatter(test_data,expected_table):
    """check TableFormatter method """
    assert all_formatters['table'](test_data)==expected_table.strip()

@pytest.mark.parametrize("test_data,expected_markdown",list(zip(test_data,expected_markdown)))
def test_markdownformatter(test_data,expected_markdown):
    """check MarkdownFormatter method """
    assert all_formatters['markdown'](test_data)==expected_markdown.strip()

# @pytest.mark.parametrize("test_data,expected_tab",list(zip(test_data,expected_tab)))
# def test_tableformatter(test_data,expected_tab):
#     assert all_formatters['tab'](test_data)==expected_tab.strip()
