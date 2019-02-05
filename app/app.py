import collections
import os

from flask import Flask, Markup, make_response, render_template, request

import adr
from adr import recipe, recipes
from adr.context import sort_context_dict
from adr.util.config import Configuration


app = Flask(__name__)
recipe_lists = []
recipe_path = os.path.dirname(recipes.__file__)
config_path = os.path.join(os.path.dirname(adr.__file__), 'config.yml')
config = Configuration(config_path)


def get_recipes():
    """
    Return a list of recipes located in /adr/recipes path
    """
    for file in os.listdir(recipe_path):
        if file.endswith('.py') and file != '__init__.py':
            recipe_name = file.rsplit('.', 1)[0]
            if not recipe.is_fail(recipe_name):
                recipe_lists.append(recipe_name)

    recipe_lists.sort()


get_recipes()


@app.route('/')
def home():
    """
    Render a template with the list of availble recipes
    :returns: template
    """
    return render_template('home.html',
                           recipes=recipe_lists,
                           type="is-info",
                           recipe="Welcome",
                           welcome="Welcome to Active Data Recipe Tool."
                                   " Please choose recipe to run!")


@app.route('/<recipe_name>')
def recipe_handler(recipe_name):
    """
    :param list recipe:the name of the selected recipe file
    :returns: template
    """
    if recipe_name not in recipe_lists:
        return render_template('home.html',
                               recipes=recipe_lists,
                               type="is-warning",
                               recipe="Warning",
                               error="Please choose recipe to run"), 404

    recipe_contexts = collections.OrderedDict()
    recipe_contexts = sort_context_dict(recipe.get_recipe_contexts(recipe_name))

    # If having args, mean running recipe
    if len(request.args) > 0:
        # Update value of context
        for k, v in recipe_contexts.items():
            if k in request.args:
                v[1]['default'] = request.args[k]

    return render_template('recipe.html', recipes=recipe_lists, recipe=recipe_name,
                           recipe_contexts=recipe_contexts,
                           docstring=Markup(recipe.get_docstring(recipe_name)))


def run_recipe(recipe_name, request, fmt='json'):
    recipe_contexts = recipe.get_recipe_contexts(recipe_name)
    args = request.args.to_dict(flat=True)

    for key, value in recipe_contexts.items():
        if "default" in value[1]:
            args.setdefault(key, value[1]["default"])

    for key, value in args.items():
        context = recipe_contexts[key][1]

        if context.get('action') == 'append' and isinstance(value, str):
            args[key] = value.split()
        elif context.get('type'):
            args[key] = context['type'](value)

    config.fmt = fmt
    return recipe.run_recipe(recipe_name, args, config, False)


API_BASE_PATH = "/api/v1/"


@app.route(API_BASE_PATH + "<recipe_name>")
def run_recipe_api(recipe_name):
    data = run_recipe(recipe_name, request)
    result = make_response(data)
    result.mimetype = 'application/json'
    return result


def main():
    """
    to run the app from the command line, use adr-app
    """
    app.run(host="0.0.0.0", debug=False)


if __name__ == '__main__':
    main()
