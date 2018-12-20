from flask import Flask, request, render_template, Markup
import os
import markdown
from adr import recipes
from adr.recipe import run_recipe, get_docstring, get_recipe_contexts
from adr.util.config import Configuration
import adr


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
            recipe_lists.append(file.rsplit('.', 1)[0])

    recipe_lists.sort()


get_recipes()


@app.route('/')
def home():
    """
    Render a template with the list of availble recipes
    :returns: template
    """
    return render_template('error.html',
                           recipes=recipe_lists,
                           type="is-warning",
                           recipe="Warning",
                           error="Please choose recipe to run")


@app.route('/<recipe>')
def recipe_handler(recipe):
    """
    :param list recipe:the name of the selected recipe file
    :returns: template
    """
    if recipe not in recipe_lists:
        return render_template('error.html',
                               recipes=recipe_lists,
                               type="is-warning",
                               recipe="Warning",
                               error="Please choose recipe to run"), 404

    # If having args, mean running recipe
    if len(request.args) > 0:
        return handle_recipe(recipe, request)
    # Otherwise, just show recipe web

    recipe_contexts = get_recipe_contexts(recipe)

    return render_template('recipe.html', recipes=recipe_lists, recipe=recipe,
                           recipe_contexts=recipe_contexts,
                           docstring=Markup(get_docstring(recipe)))


def handle_recipe(recipename, request):
    recipe_contexts = get_recipe_contexts(recipename)

    args = request.args.to_dict(flat=True)
    for key in args:
        context_type = recipe_contexts[key][1].get('type')
        args[key] = context_type(args[key]) if context_type else args[key]

    config.fmt = 'markdown'
    result_md = run_recipe(recipename, args, config, False)
    table_html = markdown.markdown(result_md, extensions=['markdown.extensions.tables'])
    table_style = "<table class=\"table is-bordered is-striped is-hoverable is-fullwidth\">"
    table_html = table_html.replace("<table>", table_style)
    return render_template('recipe.html', recipes=recipe_lists, recipe=recipename,
                           recipe_contexts=recipe_contexts,
                           docstring=Markup(get_docstring(recipename)), result=Markup(table_html))


def main():
    """
    to run the app from the command line, use adr-app
    """
    app.run(host="0.0.0.0", debug=False)


if __name__ == '__main__':
    main()
