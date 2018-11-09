from flask import Flask, render_template, Markup, request
import os
import importlib
import markdown
from adr import recipes
from adr.recipe import run_recipe
from adr.util.config import Configuration
import adr


app = Flask(__name__)
recipe_names = []
recipe_path = os.path.dirname(recipes.__file__)
config_path = os.path.join(os.path.dirname(adr.__file__), 'config.yml')
config = Configuration(config_path)
recipe_desc = ''
recipe_args = []


def get_recipes():
    """
    Return a list of recipes located in /adr/recipes path
    """
    for file in os.listdir(recipe_path):
        if file.endswith('.py') and file != '__init__.py':
            recipe_names.append(file.rsplit('.', 1)[0])


get_recipes()


def check_args_empty(arg_values):
    """
    :param list arg_values: values of arguments passed wirg recipe
    :returns : Boolean
    """
    for r in arg_values:
        if r == '':
            return True
    return False


@app.route('/')
def home():
    """
    Render a template with the list of availble recipes
    :returns: template
    """
    return render_template('home.html', recipes=recipe_names)


@app.route('/<recipe_name>')
def display_recipe(recipe_name):
    """
    :param list recipe_name:the name of the selected recipe file
    :returns: recipe template
    """
    global recipe_desc
    global recipe_args
    modname = '.recipes.{}'.format(recipe_name)
    mod = importlib.import_module(modname, package='adr')
    recipe_desc = mod.get_recipe_desc()
    recipe_args = mod.get_recipe_args()
    return render_template('recipe.html', recipe_name=recipe_name,
                           recipe_desc=recipe_desc, recipe_args=recipe_args)


@app.route('/runrecipe/<recipe_name>', methods=['POST'])
def execute_recipe(recipe_name):
    """
    :param list recipename:the name of the selected recipe file
    :returns: recipe template with recipe output
    """
    arg_values = []
    args = []

    if len(recipe_args) > 0:
        for arg in recipe_args:
            arg_values.append(request.form[arg])

        if not check_args_empty(arg_values):
            for i in range(len(recipe_args)):
                args.append(recipe_args[i])
                args.append(arg_values[i])

    config.fmt = 'markdown'
    result_md = run_recipe(recipe_name, args, config)
    table_html = markdown.markdown(result_md, extensions=['markdown.extensions.tables'])
    return render_template('recipe.html', recipe_name=recipe_name,
                           recipe_desc=recipe_desc, recipe_args=recipe_args,
                           format=Markup(table_html))


def main():
    """
    to run the app from the command line, use adr-app
    """
    app.run(debug=True)
