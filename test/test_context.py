import pytest

from adr import context

CONTEXTS = [
    ({
         "from": "mozilla"
     }, []),
    ({
         "$eval": "branches"
     }, ["branches"]),
    ({
         "in": {"repo.branch.name": {"$eval": "branches"}}
     }, ["branches"]),
    ({
         "in": {"repo.branch.name": {"$eval": "branches"}},
         "where": {"condition": {"$eval": "branches + build"}}
     }, ["branches", "build"]),
    ({
         "$eval": "branches + type"
     }, ["branches", "type"]),
]


@pytest.mark.parametrize("query, expected_contexts", CONTEXTS, ids=str)
def test_extract_context_names(query, expected_contexts):
    contexts = context.extract_context_names(query)
    assert set(expected_contexts) == contexts


DEFINITIONS = [
    (["branches"],
     {'branches': [['-B', '--branch'],
                   {'default': ["mozilla-central"],
                    'type': str,
                    'choices': ["mozilla-central", "mozilla-inbound", "autoland",
                                "beta", "release"],
                    'action': 'append',
                    'help': "Branches to query results from",
                    }]}),
    (["branches", {'custom': [['-C', '--custom'],
                              {'default': 'custom value',
                               'help': "Custom value not in common",
                               }]}],
     {'branches': [['-B', '--branch'],
                   {'default': ["mozilla-central"],
                    'type': str,
                    'choices': ["mozilla-central", "mozilla-inbound", "autoland",
                                "beta", "release"],
                    'action': 'append',
                    'help': "Branches to query results from",
                    }],
      'custom': [['-C', '--custom'],
                 {'default': 'custom value',
                  'help': "Custom value not in common",
                  }]})
]


def id_fn(val):
    return str(val)


@pytest.mark.parametrize("contexts, expected_definitions", DEFINITIONS, ids=id_fn)
def test_get_definitions(contexts, expected_definitions):
    definitions = context.get_context_definitions(contexts)
    assert expected_definitions == definitions
