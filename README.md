GitMate 2
=========

The new version of GitMate - written in django!

Running the Project
-------------------

Make sure bower as well as a virtual environment with pip is available:

```
virtualenv ~/.venvs/coon
. ~/.venvs/coon/bin/activate
npm install bower
```

Now install the project specific requirements and create your initial database:

```
pip install -r requirements.txt
bower install
python3 manage.py migrate
```

You can now run the project:

```
python3 manage.py runserver
```

Testing
-------

Tests can be run with

```
python3 manage.py test
```

The code analysis can be run in the
[official coala container](http://docs.coala.io/en/latest/Users/Docker_Image.html)
or locally when installing the ``coala-bears`` pip package:

```
coala
```