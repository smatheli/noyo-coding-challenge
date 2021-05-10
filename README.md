## Overview

This Flask application contains an API that performs CRUD actions on a person object. This API supports object versioning.

## Installation Instructions

Pull down source code from this GitHub repository:

```sh
$ git repo
```

Create a new virtual environment, activate it and install the requirements:

```sh
$ pip install virtualenv # if not already installed
$ cd noyo
$ virtualenv venv
$ pip install -r requirements.txt
```

Activate the virtual environment:

```sh
$ source venv/bin/activate
```

Install the python packages in requirements.txt:

```sh
(venv) $ pip install -r requirements.txt
```

## Setting Up Database

For the purpose of this coding challenge, Apache XAMPP was leveraged to create a database object.

XAMPP can be installed [here](https://www.apachefriends.org/download.html).

Once installed on your computer, start the XAMPP control panel and then start the Apache and MySQL servers. On your browser open http://localhost/dashboard/, select phpAdmin at the top right-hand corner, then create a database with the name **person**.

## Serve Flask Application

Once the installation has been completed and the database has been set up, run the development server to serve the Flask application:

```sh
(venv) $ flask run
```

Requests can now be served on http://localhost:5000!
