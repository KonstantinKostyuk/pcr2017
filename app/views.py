from app import app
from flask import render_template, request, flash
from forms import ColorSelect
from modules.processors.monitoring import Monitoring

processMon = Monitoring()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if processMon.get_redis_state() == 0:
        vRedisState='active'
    else:
        vRedisState='stoped'

    form = ColorSelect(request.form)
    if form.active_color.data:
        ActiveColor = 'BLUE'
    else:
        ActiveColor = 'RED'

    if form.validate_on_submit():
        flash('Color = ' + str(form.active_color.data))
        if form.active_color.data:
            ActiveColor='BLUE'
        else:
            ActiveColor='RED'
	   
    return render_template('index.html', title='PCR2017', 
			    RedisState=vRedisState,
			    NavigatorState='stoped',
			    ServoState='wait',
			    CamState='debug',
			    SelectedColor=ActiveColor,
				form=form)
