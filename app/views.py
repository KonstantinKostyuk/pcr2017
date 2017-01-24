from app import app
from flask import render_template, request
from forms import ColorSelect

@app.route('/')
@app.route('/index')
def index():
    form = ColorSelect(request.form)
    
    return render_template('index.html', title='PCR2017', 
			    RedisState='stoped',
			    NavigatorState='active',
			    ServoState='wait',
			    CamState='debug',
				form=form)
