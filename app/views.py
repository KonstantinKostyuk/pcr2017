import redis
from app import app
from flask import render_template, request, flash
from forms import ColorSelect
from modules.processors.monitoring import Monitoring

processMon = Monitoring()
#RedisServer = redis.StrictRedis(host='localhost', port=6379, db=0)

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

    if request.method == 'POST':
#    if form.validate_on_submit():
        flash('request.method == POST')
        #RedisServer.set('Navigation' + '.State', 'active')
        processMon.set_processor_key('Navigation','State', 'active')
        if form.active_color.data:
            ActiveColor='BLUE'
        else:
            ActiveColor='RED'

#ToDo Add load processors names from json file
#ToDo Change render_template to send processors names as list
#ToDo Change template index.html, process list of processors names as loop
    return render_template('index.html', title='PCR2017',
			    RedisState=vRedisState,
			    NavigatorState=processMon.get_processor_redis('Navigation'), # stopped, active, wait, debug
			    ServoState=processMon.get_processor_redis('Servo'),
			    FrontCamState=processMon.get_processor_redis('FrontCam'),
                PuckCamState=processMon.get_processor_redis('PuckCam'),
			    SelectedColor=ActiveColor,
				form=form)
