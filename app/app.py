import datetime
import json
import os

from flask import Flask, Markup, make_response, render_template, request
from requests.exceptions import HTTPError

from adr import config, recipe
from adr.context import validdatetime


app = Flask(__name__)
recipe_lists = []
recipe_path = config.sources[0]


def transform_time(time_string):
    # now, today, eod, today-week, today-month

    current = datetime.datetime.now()
    if time_string == 'now':
        result = current
    if time_string == 'today':
        result = current.replace(current.year, current.month, current.day, 0, 0, 0, 0)
    if time_string == 'eod':
        result = current.replace(current.year, current.month, current.day, 23, 59, 59)
    if time_string == 'today-week':
        result = current - datetime.timedelta(days=7)

    result = '{:%Y-%m-%d %H:%M:%S}'.format(result)
    return result


def transform_context_attributes(recipe_contexts, request_args):
    """
    Transform attibutes of contexts into useful information for displaying in web app
    :param recipe_contexts: OrderedDict
    :param request_args: ImmutableMultiDict
    :return: recipe_contexts
    """

    for k, v in recipe_contexts.items():
        # context with "choices" will be a single choice drop-down
        # context with "choices" & "append" will be a multiple choice drop-down
        if "choices" in v[1]:
            v[1]["type"] = "dropdown"

            if "default" in v[1]:
                default_value = set()
                for item in v[1]["default"]:
                    default_value.add(item)
                for i in range(len(v[1]["choices"])):
                    value = v[1]["choices"][i]
                    if value in default_value:
                        v[1]["choices"][i] = [value, "selected"]
                    else:
                        v[1]["choices"][i] = [value, ""]

            if ("action" in v[1]) and (v[1]["action"] == "append"):
                v[1]["action"] = ["is-multiple", "multiple"]
            else:
                v[1]["action"] = ["", ""]
        elif "type" in v[1]:
            context_type = v[1]["type"]
            if context_type == int:
                v[1]["type"] = "number"
            elif context_type == validdatetime:
                v[1]["type"] = "datetime"
                v[1]["default"] = transform_time(v[1]["default"])
        else:
            v[1]["type"] = "text"

    # If having args, mean running recipe
    if len(request_args) > 0:
        # Update value of context
        for k, v in recipe_contexts.items():
            if k in request_args:
                v[1]['default'] = request_args[k]

    return recipe_contexts


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

    recipe_contexts = recipe.get_recipe_contexts(recipe_name)
    transform_context_attributes(recipe_contexts, request.args)

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
        if context.get('type') == 'number':
            args[key] = int(value)

    config.fmt = fmt
    return recipe.run_recipe(recipe_name, args, False)


API_BASE_PATH = "/api/v1/"


@app.route(API_BASE_PATH + "<recipe_name>")
def run_recipe_api(recipe_name):
    try:
        data = run_recipe(recipe_name, request)
        result = make_response(data)
        result.mimetype = 'application/json'
        return result
    except HTTPError as e:
        content = json.loads(e.response.content)
        return make_response(content['cause']['cause']['template'], e.response.status_code)


def main():
    """
    to run the app from the command line, use adr-app
    """
    app.run(host="0.0.0.0", debug=False)


if __name__ == '__main__':
    main()
