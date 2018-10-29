from flask import Flask, render_template, Markup, request, abort
import os
import importlib
import markdown
import inspect
from adr import recipes
from adr.recipe import run_recipe
from adr.util.config import Configuration
import adr


app = Flask(__name__)
recipe_names = []
recipe_path = os.path.dirname(recipes.__file__)
config_path = os.path.join(os.path.dirname(adr.__file__), 'config.yml')
config = Configuration(config_path)


def get_recipes():
    """
    Return a list of recipes located in /adr/recipes path
    """
    for file in os.listdir(recipe_path):
        if file.endswith('.py') and file != '__init__.py':
            recipe_names.append(file.rsplit('.', 1)[0])


get_recipes()


@app.route('/')
def home():
    """
    Render a template with the list of availble recipes
    :returns: template
    """
    return render_template('home.html', recipes=recipe_names)


@app.route('/showrecipe/<recipe>', methods=['POST', 'GET'])
def showrecipe(recipe):
    """
    :param string recipename:the name of the selected recipe
    :returns: template
    """
    if recipe not in recipe_names:
        abort(404)
    module_name = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(module_name, package='adr')
    format = None
    if request.method == 'POST':
        args = []
        if request.form['arguments'] != '':
            args = request.form['arguments'].split(' ')
        config.fmt = 'markdown'
        result_md = run_recipe(recipe, args, config)
        table_html = markdown.markdown(result_md, extensions=['markdown.extensions.tables'])
        format = Markup(table_html)
    return render_template(
        'recipe.html',
        recipe=recipe,
        format=format,
        docstring=inspect.getdoc(mod))


def main():
    """
    to run the app from the command line, use adr-app
    """
    app.run(debug=True)
