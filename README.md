## Overview

This Flask application contains an API that performs CRUD actions on a person object. This API supports object versioning.

## Installation Instructions

Pull down source code from this GitHub repository:

```sh
$ git clone https://github.com/smatheli/noyo-coding-challenge
```

## Setup Virtual Environment

Create a new virtual environment:

```sh
$ pip install virtualenv # if not already installed
$ cd noyo-coding-challenge
$ virtualenv venv
```

Activate the virtual environment:

```sh
$ source venv/bin/activate
```

Install the python packages in requirements.txt:

```sh
(venv) $ pip install -r requirements.txt
```

## Set Up Database

Initialize and then migrate a local SQLite database:

```sh
(venv) $ flask db init
(venv) $ flask db migrate
(venv) $ flask db upgrade
```

You should then see a local **app.db** file.  You can view the database with [DB Browser for SQLite](https://sqlitebrowser.org/).

## Test Application

Tests can be run using pytest in the base directory of the project:

```sh
(venv) $ python -m pytest
```

## Serve Flask Application

After the virtual environment and database have been set up, run the development server to serve the Flask application:

```sh
(venv) $ gunicorn wsgi:handler
```

Requests can now be served on http://localhost:8080!
