from __future__ import absolute_import
from os import path, environ
import json
from flask import Flask, Blueprint, abort, jsonify, request, session
import settings
from celery import Celery
from celery.task.control import inspect
import time

app = Flask(__name__)
app.config.from_object(settings)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task(name="tasks.add")
def add(x, y):
    time.sleep(60)
    print('sleep back====')
    return x + y

@celery.task(name="tasks.multiple")
def multiple(x, y):
    time.sleep(30)
    return x * y

@app.route("/test")
def hello_world(x=16, y=16):
    x = int(request.args.get("x", x))
    y = int(request.args.get("y", y))
    res = add.apply_async((x, y))
    context = {"id": res.task_id, "x": x, "y": y}
    result = "add((x){}, (y){})".format(context['x'], context['y'])
    goto = "{}".format(context['id'])
    return jsonify(result=result, goto=goto)

@app.route("/tasks")
def get_all_tasks():
    i = inspect()
    return jsonify(i.registered_tasks())

@app.route("/tasks/scheduled")
def scheduled_tasks():
    i = inspect()
    return jsonify(i.scheduled())

@app.route("/tasks/active")
def active_tasks():
    i = inspect()
    return jsonify(i.active())

@app.route("/test/result/<task_id>")
def show_result(task_id):
    retval = add.AsyncResult(task_id).get(timeout=1.0)
    return repr(retval)


if __name__ == "__main__":
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
