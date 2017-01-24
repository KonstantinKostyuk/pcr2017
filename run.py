#!flask/bin/python

from app import app

app.config['SECRET_KEY'] = '7d441f27d441f10567d441f2b6172z'
app.run(host='0.0.0.0', port=5000, debug = True)

