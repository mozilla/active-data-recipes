[![Build Status](https://travis-ci.org/mozilla/active-data-recipes.svg?branch=master)](https://travis-ci.org/mozilla/active-data-recipes)
[![PyPI version](https://readthedocs.org/projects/active-data-recipes/badge/?version=latest)](https://active-data-recipes.readthedocs.io)

# ActiveData Recipes

This is a repository of various [ActiveData recipes][0]. A recipe is a small snippet that runs one
or more [ActiveData][3] queries and returns the output. Queries can sometimes be modified by command
line arguments and output can sometimes be post-processed.

Each recipe should try to answer a single question.

# Installation

First [install poetry][2], then run:

    $ git clone https://github.com/mozilla/active-data-recipes
    $ cd active-data-recipes
    $ poetry install

You will need Python 3.6 or higher.

# Usage

The `poetry install` command will create a virtualenv with all of the required dependencies
installed. You can use `poetry run <cmd>` to run a single command within the virtualenv context. Or
you can use `poetry shell` to spawn a new shell with the virtualenv activated. The commands below
assume you have run the latter.

Run:

    $ adr <recipe> <options>

For a list of recipes:

    $ adr list

For recipe specific options see:

    $ adr <recipe> -- --help

To serve the web app locally:

    $ adr-app

# Recipes

See the [recipe documentation][1] for more information on which recipes are available and how to run
them.

# Development

To contribute to `active-data-recipes` first follow the installation steps above.
You can run tests with:

    $ poetry run tox

Or:

    $ poetry shell
    $ tox

[0]: https://github.com/mozilla/active-data-recipes
[1]: https://active-data-recipes.readthedocs.io/en/latest/recipes.html
[2]: https://poetry.eustace.io/docs/#installation
[3]: https://github.com/mozilla/ActiveData
