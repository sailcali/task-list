import re
from flask import Blueprint, jsonify, make_response, request, abort
from flask.signals import request_finished
from sqlalchemy import desc
from app import db
from app.models.task import Task
from app.models.goal import Goal
import requests
import os

task_bp = Blueprint('task_bp',__name__, url_prefix='/tasks')
goal_bp = Blueprint('goal_bp', __name__, url_prefix='/goals')

@task_bp.route("", methods=['GET', 'POST'])
def tasks_functions():
    if request.method == 'GET':
        tasks = Task.query.order_by(desc(Task.title)).all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            })
        sort_query = request.args.get("sort")
        # if sort_query == 'asc':
        #     # tasks_response = sorted(tasks_response, key = lambda i: i['title'])
        # elif sort_query == 'desc':
        #     # tasks_response = sorted(tasks_response, key = lambda i: i['title'], reverse=True)
        return jsonify(tasks_response)

    elif request.method == 'POST':
        request_body = request.get_json()
        if "title" in request_body and 'description' in request_body and 'completed_at' in request_body:
            new_task = Task(title=request_body["title"],
                            description=request_body["description"],
                            completed_at=request_body["completed_at"])

            db.session.add(new_task)
            db.session.commit()
            # requests.post('https://slack.com/api/chat.postMessage',
                            # headers={'Authorization': 'Bearer '+ os.environ.get('BOT_TOKEN')},
                            # params = {'channel': 'paiges_channel', 'text': f'task created {new_task.title}'})
            j = {'task': {'id': new_task.task_id,
                        'title': new_task.title,
                        'description': new_task.description,
                        'is_complete': False}}

            return make_response(j, 201)
        else:
            return make_response({'details': "Invalid data"}, 400)

@task_bp.route("/<requested_task>", methods=['GET', 'PUT', 'DELETE'])
def return_by_title(requested_task):
    task = Task.query.get(requested_task)
    if task is None:
        abort(404)
    if request.method == 'GET':
        return {'task':{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }}
    elif request.method == 'PUT':
        form_data = request.get_json()
        
        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        return make_response({'task':{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }}, 200)
    elif request.method == 'DELETE':
        name = task.title
        db.session.delete(task)
        db.session.commit()
        return make_response({
                             "details": f'Task {requested_task} "{name}" successfully deleted'
                             }, 200)

@goal_bp.route('', methods=['GET', 'POST'])
def get_goals():
    
    if request.method == 'GET':
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        # sort_query = request.args.get("sort")
        # if sort_query == 'asc':
        #     tasks_response = sorted(tasks_response, key = lambda i: i['title'])
        # elif sort_query == 'desc':
        #     tasks_response = sorted(tasks_response, key = lambda i: i['title'], reverse=True)
        return jsonify(goals_response)

    elif request.method == 'POST':
        request_body = request.get_json()
        if "title" in request_body:
            new_goal = Goal(title=request_body["title"])

            db.session.add(new_goal)
            db.session.commit()
            j = {'goal': {'id': new_goal.goal_id,
                        'title': new_goal.title}}

            return make_response(j, 201)
        else:
            return make_response({'details': "Invalid data"}, 400)

@goal_bp.route("/<requested_goal>", methods=['GET', 'PUT', 'DELETE'])
def return_by_title(requested_goal):
    goal = Goal.query.get(requested_goal)
    if goal is None:
        abort(404)
    if request.method == 'GET':
        return {'goal':{
            "id": goal.goal_id,
            "title": goal.title
        }}
    elif request.method == 'PUT':
        form_data = request.get_json()
        
        goal.title = form_data["title"]

        db.session.commit()

        return make_response({'goal':{
                "id": goal.task_id,
                "title": goal.title,
            }}, 200)
    elif request.method == 'DELETE':
        name = goal.title
        db.session.delete(goal)
        db.session.commit()
        return make_response({
                             "details": f'Goal {requested_goal} "{name}" successfully deleted'
                             }, 200)