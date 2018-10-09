from flask import Flask,render_template,Markup
import os
from adr.recipe import run_recipe
import markdown

app=Flask(__name__)
recipes=[]

def get_recipes():
    """
    Return a list of recipes located in /adr/recipes path
    """
    for root, dirs, files in os.walk("../adr/recipes"):
        for filename in files:
            if filename.endswith('.py') and  filename!='__init__.py':
                recipes.append(filename[0:len(filename)-3])
get_recipes()

@app.route('/')
def home():
    """
    Render a template with the list of availble recipes
    :returns: template
    """
    return render_template('home.html',recipes=recipes)

@app.route('/runrecipe/<recipename>')
def runrecipe(recipename):
    """
    :param list recipename:the name of the selected recipe file
    :returns: template
    """
    result_md=run_recipe(recipename, None,'markdown')
    table_html=markdown.markdown(result_md, extensions=['markdown.extensions.tables'])
    return render_template('home.html',recipes=recipes,format=Markup(table_html))

if __name__=='__main__':
    app.run(debug=True)
