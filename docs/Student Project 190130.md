# active-data-recipes Student Project 2019

## Background

`active-data-recipes` - provides a framework for writing and running "recipes": A collection of queries against ActiveData, along with a Python script to glue the query results together to make them useful. 

`ActiveData` - a service endpoint for querying many billions of records covering aspects of Mozilla CI infrastructure.

You can run recipes now at https://adr-dev.herokuapp.com/

## Problem

Writing new recipes requires you to fork the repo, copy an existing recipe and queries, register the query, and eventually submit a PR. This process if fine if you already know what you are making, but it is a barrier to exploration: What if you want to look at the data, learn from an existing recipe, but unsure if you will make a recipe in the end?

## Solution

Streamline the exploration phase of recipe writing.

## Project Plan

The plan is to build a JSX/React application that will allow users to fork an existing recipe, and allow the user to change-and-debug the queries of that fork to meet a new purpose.

## Expected Features

The following features are expected:

* Fork a recipe - The main purpose of this app is to copy an existing recipe with its supporting queries to begin the exploration process.
* Start a new recipe - In case you know what you are doing, but still unsure if you want to make a whole recipe. 
* Code editor - Recipes and queries are code, so an editor is required. (eg [https://ace.c9.io/](https://ace.c9.io/))
* Manage multiple queries - A recipe can consist of multiple queries, it is important that more then one query can be edited during the same session
* Queries must be able to accept parameters, just like they do now in `active-data-recipes`
* Must be able to send queries (with parameters filled) to ActiveData for testing and debugging 
* Queries should translate between JSON, YAML and SQL so user can use their preferred format
* Should generate a PR with the forked queries (and recipe). This will probably require server-side support. 


## Similar Tools

* [Query Tool](https://activedata.allizom.org/tools/query.html) - You write queries against ActiveData directly, but it demands JSON (not YAML) It can not accept parameters, it's dreadfully ugly. It should be replaced.
* [Iodide](https://extremely-alpha.iodide.io/) is an interactive data analysis tool. It can already pull data from multiple data sources, and can run Python in the browser. Do we need more?  Can we use its Python interpreter?
* [stmo](https://sql.telemetry.mozilla.org/) is Mozilla's ReDash instance. It can pull data from multiple sources, and can be used to build dashboards. It also accepts SQL for basic ActiveData queries. If recipes were written here they must be done in SQL, against the Redash metadata database.


## Bonus Points

If the following is done before the end of the term, there is alwasy more to do:

* Execute the Python in the browser - Iodide does this already, and it would complete the recipe-writing process.
* Add charts - Data can be interpreted faster if it can be charted. Mozilla is working on a library of dashboarding React components that may make this easy.






