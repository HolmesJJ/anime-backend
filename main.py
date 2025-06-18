import os
import time
import base64
import shutil
import pandas as pd
import mysql.connector

from openai import OpenAI
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

MYSQL = {
    'host': os.getenv('MYSQL_HOST'),
    'username': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

GPT_IMAGE_MODEL = os.getenv('GPT_IMAGE_MODEL')
GPT_KEY = os.getenv('GPT_KEY')

DATA_DIR = os.getenv('DATA_DIR')


def generate(project_id, prompt_content):
    client = OpenAI(api_key=GPT_KEY)
    result = client.images.generate(
        model=GPT_IMAGE_MODEL,
        prompt=prompt_content
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(os.path.join(DATA_DIR, f'{project_id}.png'), 'wb') as f:
        f.write(image_bytes)


def read_novel(project_id):
    txt_path = os.path.join(DATA_DIR, f'{project_id}.txt')
    if not os.path.isfile(txt_path):
        return None
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_novel(project_id, content):
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


class Novel(Resource):
    def get(self, project_id):
        content = read_novel(project_id)
        if content is None:
            return {'message': 'Novel file not found'}, 404
        return {'txt': content}

    def post(self, project_id):
        json_data = request.get_json()
        content = json_data.get('txt', '')
        txt_path = os.path.join(DATA_DIR, f'{project_id}.txt')
        if content.strip() == '':
            if os.path.exists(txt_path):
                os.remove(txt_path)
                return {'message': 'Novel was empty and has been deleted'}
            else:
                return {'message': 'Novel was empty and did not exist'}, 204
        else:
            write_novel(project_id, content)
            return {'message': 'Novel written successfully'}


class Project(Resource):
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
            generate(project_id, description)
            return {
                'message': 'Project added successfully',
                'project_id': project_id
            }, 201
        except mysql.connector.Error as err:
            return {'error': str(err)}, 500

    def put(self, project_id):
        try:
            data = request.get_json()
            fields = []
            values = []
            if 'name' in data:
                fields.append('name = %s')
                values.append(data['name'])
            if 'description' in data:
                fields.append('description = %s')
                values.append(data['description'])
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
                if 'description' in data:
                    generate(project_id, data['description'])
            return {'message': 'Project updated successfully'}
        except Exception as e:
            return {'error': str(e)}, 500

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


class GenerateComic(Resource):
    def get(self, project_id):
        print(project_id)
        time.sleep(2)
        return {'message': 'Comic generated successfully'}


class GenerateAnime(Resource):
    def get(self, project_id):
        print(project_id)
        time.sleep(2)
        return {'message': 'Anime generated successfully'}


class GenerateFullAnime(Resource):
    def get(self, project_id):
        print(project_id)
        time.sleep(2)
        return {'message': 'Full anime generated successfully'}


class Regenerate(Resource):
    def post(self):
        try:
            data = request.get_json()
            project_detail_id = data.get('project_detail_id')
            image_description = data.get('image_description')
            video_description = data.get('video_description')
            print(project_detail_id, image_description, video_description)
        except mysql.connector.Error as err:
            return {'error': str(err)}, 500
        time.sleep(2)
        return {'message': 'Regenerate successfully'}


api.add_resource(Index, '/', endpoint='index')
api.add_resource(Data, '/data/<path:path>')
api.add_resource(Styles, '/api/styles', endpoint='styles')
api.add_resource(Projects, '/api/projects', endpoint='projects')
api.add_resource(Project, '/api/project', '/api/project/<int:project_id>', endpoint='project')
api.add_resource(Novel, '/api/project/novel/<int:project_id>', endpoint='novel')
api.add_resource(GenerateComic, '/api/project/generate_comic/<int:project_id>', endpoint='generate_comic')
api.add_resource(GenerateAnime, '/api/project/generate_anime/<int:project_id>', endpoint='generate_anime')
api.add_resource(GenerateFullAnime, '/api/project/generate_full_anime/<int:project_id>', endpoint='generate_full_anime')
api.add_resource(Regenerate, '/api/project/regenerate', endpoint='regenerate')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5050)
