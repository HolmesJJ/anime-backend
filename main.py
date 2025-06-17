import os
import shutil
import pandas as pd
import mysql.connector

from threading import Lock
from dotenv import load_dotenv
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_from_directory
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource


load_dotenv()

application = Flask(__name__)
application.config['CORS_HEADERS'] = 'Content-Type'
application.config['CORS_RESOURCES'] = {r'/api/*': {'origins': '*'}}
application.config['PROPAGATE_EXCEPTIONS'] = True

cors = CORS(application)
api = Api(application)
export_lock = Lock()

MYSQL = {
    'host': os.getenv('MYSQL_HOST'),
    'username': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

DATA_DIR = os.getenv('DATA_DIR')


def read_project_txt(project_id):
    txt_path = os.path.join(DATA_DIR, f'{project_id}.txt')
    if not os.path.isfile(txt_path):
        return None
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_project_txt(project_id, content):
    txt_path = os.path.join(DATA_DIR, f'{project_id}.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


class Index(Resource):
    def get(self):
        return send_from_directory('templates', 'index.html')


class Data(Resource):
    def get(self, path):
        full_path = os.path.join(os.getcwd(), DATA_DIR, path)
        if not os.path.isfile(full_path):
            return abort(404, description='File not found')
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)


class Styles(Resource):
    def get(self):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            query = 'SELECT id, style FROM style'
            df = pd.read_sql_query(query, cnx)
            cnx.close()
            data = df.to_dict(orient='records')
            return jsonify(data)
        except Exception as e:
            return {'error': str(e)}, 500


class Projects(Resource):
    def get(self):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            query = '''
                SELECT 
                    p.id, p.name, p.description, s.style 
                FROM 
                    project p 
                LEFT JOIN 
                    style s ON p.style_id = s.id
            '''
            df = pd.read_sql_query(query, cnx)
            cnx.close()
            data = df.to_dict(orient='records')
            return jsonify(data)
        except Exception as e:
            return {'error': str(e)}, 500


class ProjectText(Resource):
    def get(self, project_id):
        content = read_project_txt(project_id)
        if content is None:
            return {'message': 'Text file not found'}, 404
        return {'txt': content}

    def post(self, project_id):
        json_data = request.get_json()
        content = json_data.get('txt', '')
        write_project_txt(project_id, content)
        return {'message': 'Txt written successfully'}


class AddProject(Resource):
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            style_id = data.get('style_id')
            if not name or not description or not style_id:
                return {'error': 'Missing required fields'}, 400
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            insert_query = 'INSERT INTO project (name, description, style_id) VALUES (%s, %s, %s)'
            cursor.execute(insert_query, (name, description, style_id))
            project_id = cursor.lastrowid
            cnx.commit()
            cursor.close()
            cnx.close()
            return {
                'message': 'Project added successfully',
                'project_id': project_id
            }, 201
        except mysql.connector.Error as err:
            return {'error': str(err)}, 500


class GetProject(Resource):
    def get(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            query = '''
                SELECT 
                    p.id, p.name, p.description, s.style 
                FROM 
                    project p 
                LEFT JOIN 
                    style s ON p.style_id = s.id
                WHERE 
                    p.id = %s
            '''
            df = pd.read_sql_query(query, cnx, params=[project_id])
            cnx.close()
            if df.empty:
                return {'error': 'Project not found'}, 404
            project = df.to_dict(orient='records')[0]
            return jsonify(project)
        except Exception as e:
            return {'error': str(e)}, 500


class UpdateProject(Resource):
    def post(self, project_id):
        try:
            data = request.get_json()
            fields = []
            values = []
            if 'name' in data:
                fields.append('name = %s')
                values.append(data['name'])
            if 'style_id' in data:
                fields.append('style_id = %s')
                values.append(data['style_id'])
            if fields:
                cnx = mysql.connector.connect(
                    host=MYSQL['host'],
                    user=MYSQL['username'],
                    password=MYSQL['password'],
                    database=MYSQL['database']
                )
                cursor = cnx.cursor()
                query = f"UPDATE project SET {', '.join(fields)} WHERE id = %s"
                values.append(project_id)
                cursor.execute(query, values)
                cnx.commit()
                cursor.close()
                cnx.close()
            return {'message': 'Project updated successfully'}
        except Exception as e:
            return {'error': str(e)}, 500


class DeleteProject(Resource):
    def delete(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('DELETE FROM project WHERE id = %s', (project_id,))
            cnx.commit()
            cursor.close()
            cnx.close()
            folder_path = os.path.join(DATA_DIR, str(project_id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            for ext in ['txt', 'png']:
                file_path = os.path.join(DATA_DIR, f'{project_id}.{ext}')
                if os.path.exists(file_path):
                    os.remove(file_path)
            return {'message': 'Project deleted successfully'}
        except Exception as e:
            return {'error': str(e)}, 500


api.add_resource(Index, '/', endpoint='index')
api.add_resource(Data, '/data/<path:path>')
api.add_resource(Styles, '/api/styles', endpoint='styles')
api.add_resource(Projects, '/api/projects', endpoint='projects')
api.add_resource(AddProject, '/api/project/add', endpoint='add_project')
api.add_resource(GetProject, '/api/project/<int:project_id>', endpoint='get_project')
api.add_resource(UpdateProject, '/api/project/<int:project_id>/update', endpoint='update_project')
api.add_resource(DeleteProject, '/api/project/<int:project_id>/delete', endpoint='delete_project')
api.add_resource(ProjectText, '/api/project/<int:project_id>/text')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=6060)
