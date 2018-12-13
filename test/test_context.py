# from adr import context
# import pytest
#
# CONTEXTS = [
#     ({
#         "from": "mozilla"
#     }, []),
#     ({
#         "$eval": "branch"
#     }, ["branch"]),
#     ({
#         "in": {"repo.branch.name": {"$eval": "branch"}}
#     }, ["branch"]),
#     ({
#         "in": {"repo.branch.name": {"$eval": "branch"}},
#         "where": {"condition": {"$eval": "branch + build"}}
#     }, ["branch", "build"]),
#     ({
#         "$eval": "branch + type"
#     }, ["branch", "type"]),
# ]
#
#
# @pytest.mark.parametrize("query, expected_contexts", CONTEXTS, ids=str)
# def test_extract_context_names(query, expected_contexts):
#     contexts = context.extract_context_names(query)
#     assert set(expected_contexts) == contexts
#
#
# DEFINITIONS = [
#     (["branch"],
#      {'branch': [['-B', '--branch'],
#                  {'default': 'mozilla-central',
#                   'help': "Branches to query results from",
#                   }]}),
#     (["branch", {'custom': [['-C', '--custom'],
#                             {'default': 'custom value',
#                              'help': "Custom value not in common",
#                              }]}],
#      {'branch': [['-B', '--branch'],
#                  {'default': 'mozilla-central',
#                   'help': "Branches to query results from",
#                   }],
#       'custom': [['-C', '--custom'],
#                  {'default': 'custom value',
#                   'help': "Custom value not in common",
#                   }]})
# ]
#
#
# def id_fn(val):
#     return str(val)
#
#
# @pytest.mark.parametrize("contexts, expected_definitions", DEFINITIONS, ids=id_fn)
# def test_get_definitions(contexts, expected_definitions):
#     definitions = context.get_context_definitions(contexts)
#     assert expected_definitions == definitions
