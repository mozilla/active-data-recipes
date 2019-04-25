import os
from itertools import chain
from pathlib import Path

from adr import config


class Source:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        self._recipes = None
        self._queries = None

    @property
    def recipes(self):
        if self._recipes:
            return self._recipes

        self._recipes = [os.path.splitext(item)[0] for item in os.listdir(self.path / 'recipes')
                         if item != '__init__.py' and item.endswith('.py')]
        return self._recipes

    @property
    def queries(self):
        if self._queries:
            return self._queries

        self._queries = [os.path.splitext(item)[0] for item in os.listdir(self.path / 'queries')
                         if item.endswith('.query')]
        return self._queries


class MergedSources:

    def __init__(self, sources):
        self._sources = [Source(s) for s in sources]

    def __len__(self):
        return len(self._sources)

    def __getitem__(self, i):
        return self._sources[i]

    @property
    def recipes(self):
        return chain(*[s.recipes for s in self._sources])

    @property
    def queries(self):
        return chain(*[s.queries for s in self._sources])

    def has_recipe(self, name):
        return any(s.has_recipe(name) for s in self._sources)


sources = MergedSources(config.sources)
