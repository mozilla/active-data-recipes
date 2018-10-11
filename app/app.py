from flask import Flask, render_template, Markup
import os
import markdown
from adr import recipes
from adr.recipe import run_recipe

app = Flask(__name__)
recipe_names = []
recipe_path = os.path.dirname(recipes.__file__)


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


@app.route('/runrecipe/<recipename>')
def runrecipe(recipename):
    """
    :param list recipename:the name of the selected recipe file
    :returns: template

    """
    result_md = run_recipe(recipename, None, 'markdown')
    table_html = markdown.markdown(result_md, extensions=['markdown.extensions.tables'])
    return render_template('home.html', recipes=recipe_names, format=Markup(table_html))


if __name__ == '__main__':
    app.run(debug=True)
