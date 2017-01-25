from app import app
from flask import render_template, request
from forms import ColorSelect

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ColorSelect(request.form)
    if form.active_color.data:
       ActiveColor='RED'
    else:
       ActiveColor='BLUE'

    if form.validate_on_submit():
       flash('Color = ' + str(form.active_color.data))
       if form.active_color.data:
	  ActiveColor='RED'
       else:
	  ActiveColor='BLUE'
	   
    return render_template('index.html', title='PCR2017', 
			    RedisState='stoped',
			    NavigatorState='active',
			    ServoState='wait',
			    CamState='debug',
			    SelectedColor=ActiveColor,
				form=form)
