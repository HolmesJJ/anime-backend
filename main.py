import os
import re
import time
import base64
import shutil
import pandas as pd
import mysql.connector

from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import send_from_directory
from flask import stream_with_context
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource
from moviepy.editor import ImageClip
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips


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

GPT_TEXT_MODEL = os.getenv('GPT_TEXT_MODEL')
GPT_IMAGE_MODEL = os.getenv('GPT_IMAGE_MODEL')
GPT_KEY = os.getenv('GPT_KEY')

ASSETS_DIR = os.getenv('ASSETS_DIR')
DATA_DIR = os.getenv('DATA_DIR')
FRONT_PATH = os.path.join(ASSETS_DIR, 'arial.ttf')


def generate_image(file_name, image_path, color, prompt_content):
    # client = OpenAI(api_key=GPT_KEY)
    # result = client.images.generate(
    #     model=GPT_IMAGE_MODEL,
    #     prompt=prompt_content
    # )
    # image_base64 = result.data[0].b64_json
    # image_bytes = base64.b64decode(image_base64)
    # with open(os.path.join(DATA_DIR, f'{file_name}.png'), 'wb') as f:
    #     f.write(image_bytes)
    width, height = 640, 480
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    font_size = 100
    font = ImageFont.truetype(FRONT_PATH, font_size)
    text = str(file_name)
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2 - bbox[0]
    text_y = (height - text_height) // 2 - bbox[1]
    draw.text((text_x, text_y), text, fill=color, font=font)
    img.save(image_path)


def generate_video(image_path, video_path):
    duration = 4
    fade_duration = 1
    clip = ImageClip(image_path, duration=duration)
    clip = clip.fx(ImageClip.fadein, fade_duration)
    clip = clip.fx(ImageClip.fadeout, fade_duration)
    clip.write_videofile(video_path, fps=24)
    clip.close()


def combine_videos(video_paths, full_video_path):
    clips = [VideoFileClip(p) for p in video_paths]
    final = concatenate_videoclips(clips, method='compose')
    final.write_videofile(full_video_path, codec='libx264', fps=24, audio=True)
    for c in clips:
        c.close()
    final.close()


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
            image_path = os.path.join(DATA_DIR, f'{project_id}.png')
            generate_image(project_id, image_path, 'blue', description)
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
                    image_path = os.path.join(DATA_DIR, f'{project_id}.png')
                    generate_image(project_id, image_path, 'blue', data['description'])
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
            for ext in ['txt', 'png', 'mp4']:
                file_path = os.path.join(DATA_DIR, f'{project_id}.{ext}')
                if os.path.exists(file_path):
                    os.remove(file_path)
            return {'message': 'Project deleted successfully'}
        except Exception as e:
            return {'error': str(e)}, 500


class ProjectDetails(Resource):
    def get(self, project_id, column):
        allowed_columns = {'paragraph', 'image_description', 'video_description'}
        if column not in allowed_columns:
            return {'error': f'Invalid column name: {column}'}, 400
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor(dictionary=True)
            query = f'''
                SELECT id, {column}
                FROM project_detail
                WHERE project_id = %s
            '''
            cursor.execute(query, (project_id,))
            rows = cursor.fetchall()
            cnx.close()
            result = [{'id': row['id'], column: row[column]} for row in rows]
            return result
        except Exception as e:
            return {'error': str(e)}, 500


class ProjectDetail(Resource):
    def get(self, project_detail_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor(dictionary=True)
            query = '''
                SELECT id,
                       project_id,
                       paragraph,
                       image_description,
                       video_description
                FROM   project_detail
                WHERE  id = %s
            '''
            cursor.execute(query, (project_detail_id,))
            row = cursor.fetchone()
            cursor.close()
            cnx.close()
            if row is None:
                return {'error': 'Project detail not found'}, 404
            return row
        except Exception as e:
            return {'error': str(e)}, 500


class Novel(Resource):
    def get(self, project_id):
        content = read_novel(project_id)
        if content is None:
            return {'error': 'Novel file not found'}, 404
        return {'txt': content}

    def post(self, project_id):
        json_data = request.get_json()
        content = json_data.get('txt', '')
        txt_path = os.path.join(DATA_DIR, f'{project_id}.txt')
        if content.strip() == '':
            try:
                cnx = mysql.connector.connect(
                    host=MYSQL['host'],
                    user=MYSQL['username'],
                    password=MYSQL['password'],
                    database=MYSQL['database']
                )
                cursor = cnx.cursor()
                cursor.execute('DELETE FROM project_detail WHERE project_id = %s', (project_id,))
                cnx.commit()
                cursor.close()
                cnx.close()
                folder_path = os.path.join(DATA_DIR, str(project_id))
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                if os.path.exists(txt_path):
                    os.remove(txt_path)
                    return {'message': 'Novel was empty and has been deleted'}
                else:
                    return {'message': 'Novel was empty and did not exist'}, 204
            except Exception as e:
                return {'error': str(e)}, 500
        else:
            try:
                cnx = mysql.connector.connect(
                    host=MYSQL['host'],
                    user=MYSQL['username'],
                    password=MYSQL['password'],
                    database=MYSQL['database']
                )
                cursor = cnx.cursor()
                cursor.execute('DELETE FROM project_detail WHERE project_id = %s', (project_id,))
                paragraphs = [p.strip() for p in re.split(r'\r?\n+', content) if p.strip()]
                query = '''
                    INSERT INTO project_detail (paragraph, project_id)
                    VALUES (%s, %s)
                '''
                data = [(para, project_id) for para in paragraphs]
                cursor.executemany(query, data)
                cnx.commit()
                cursor.close()
                cnx.close()
                folder_path = os.path.join(DATA_DIR, str(project_id))
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                write_novel(project_id, content)
            except Exception as e:
                return {'error': str(e)}, 500
            return {'message': 'Novel written successfully'}


class NovelContinue(Resource):
    def post(self, project_id):
        data = request.get_json()
        txt = data.get('txt', '')
        summary = data.get('summary', '')
        if summary.strip() == '':
            return {'error': 'Field "txt" is required'}, 400
        try:
            cnx = mysql.connector.connect(**MYSQL)
            cursor = cnx.cursor()
            cursor.execute('SELECT 1 FROM project WHERE id=%s LIMIT 1', (project_id,))
            row = cursor.fetchone()
            cursor.close()
            cnx.close()
            if row is None:
                return {'error': 'Project not found'}, 404
        except Exception as e1:
            return {'error': str(e1)}, 500
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are an excellent novelist. '
                    'First read the previous text and the provided outline, '
                    'then continue the story in the same tone. '
                    'Your continuation must strictly follow the outline '
                    'and stay within 300 characters (including spaces).'
                )
            },
            {
                'role': 'user',
                'content': (
                    f'Previous text:\n{txt}\n\n'
                    f'Outline for the next part:\n{summary}\n\n'
                    'Please continue the story within below. '
                    'Output ONLY the continuation, no extra words.'
                )
            }
        ]
        client = OpenAI(api_key=GPT_KEY)
        stream = client.chat.completions.create(
            model=GPT_TEXT_MODEL,
            messages=messages,
            temperature=0.7,
            stream=True
        )

        def token_generator():
            try:
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
            except Exception as e2:
                yield f'\n[ERROR] {e2}\n'

        return Response(
            stream_with_context(token_generator()),
            mimetype='text/event-stream',
            status=200
        )


class Comic(Resource):
    def get(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('SELECT id FROM project_detail WHERE project_id = %s ORDER BY id ASC', (project_id,))
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            return {'ids': ids}
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('SELECT id FROM project_detail WHERE project_id = %s ORDER BY id ASC', (project_id,))
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            folder_path = os.path.join(DATA_DIR, str(project_id))
            os.makedirs(folder_path, exist_ok=True)
            for pid in ids:
                image_path = os.path.join(folder_path, f'{pid}.png')
                generate_image(pid, image_path, 'green', '')
            return {'message': 'Comic generated successfully'}
        except Exception as e:
            return {'error': str(e)}, 500


class Anime(Resource):
    def get(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('SELECT id FROM project_detail WHERE project_id = %s ORDER BY id ASC', (project_id,))
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            return {'ids': ids}
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('SELECT id FROM project_detail WHERE project_id = %s ORDER BY id ASC', (project_id,))
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            folder_path = os.path.join(DATA_DIR, str(project_id))
            os.makedirs(folder_path, exist_ok=True)
            for pid in ids:
                image_path = os.path.join(folder_path, f'{pid}.png')
                video_path = os.path.join(folder_path, f'{pid}.mp4')
                if not os.path.exists(image_path):
                    continue
                generate_video(image_path, video_path)
            return {'message': 'Anime generated successfully'}
        except Exception as e:
            return {'error': str(e)}, 500


class FullAnime(Resource):
    def get(self, project_id):
        full_video_path = os.path.join(DATA_DIR, f'{project_id}.mp4')
        if os.path.exists(full_video_path):
            return {'message': 'Full anime exists'}
        else:
            return {'error': 'Full anime not found'}, 404

    def post(self, project_id):
        try:
            cnx = mysql.connector.connect(
                host=MYSQL['host'],
                user=MYSQL['username'],
                password=MYSQL['password'],
                database=MYSQL['database']
            )
            cursor = cnx.cursor()
            cursor.execute('SELECT id FROM project_detail WHERE project_id = %s ORDER BY id ASC', (project_id,))
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            folder_path = os.path.join(DATA_DIR, str(project_id))
            os.makedirs(folder_path, exist_ok=True)
            video_paths = []
            for pid in ids:
                video_path = os.path.join(folder_path, f'{pid}.mp4')
                if not os.path.exists(video_path):
                    continue
                video_paths.append(video_path)
            full_video_path = os.path.join(DATA_DIR, f'{project_id}.mp4')
            if video_paths:
                combine_videos(video_paths, full_video_path)
                return {'message': 'Full anime generated successfully'}
            else:
                return {'error': 'Amine not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500


class Regenerate(Resource):
    def post(self):
        try:
            data = request.get_json()
            project_detail_id = data.get('project_detail_id')
            image_description = data.get('image_description')
            video_description = data.get('video_description')
            print(project_detail_id, image_description, video_description)
            time.sleep(2)
        except mysql.connector.Error as err:
            return {'error': str(err)}, 500
        time.sleep(2)
        return {'message': 'Regenerate successfully'}


api.add_resource(Index, '/', endpoint='index')
api.add_resource(Data, '/data/<path:path>')
api.add_resource(Styles, '/api/styles', endpoint='styles')
api.add_resource(Projects, '/api/projects', endpoint='projects')
api.add_resource(Project, '/api/project', '/api/project/<int:project_id>', endpoint='project')
api.add_resource(Novel, '/api/project/<int:project_id>/novel', endpoint='novel')
api.add_resource(Comic, '/api/project/<int:project_id>/comic', endpoint='comic')
api.add_resource(Anime, '/api/project/<int:project_id>/anime', endpoint='anime')
api.add_resource(FullAnime, '/api/project/<int:project_id>/full_anime', endpoint='full_anime')
api.add_resource(ProjectDetails, '/api/project/<int:project_id>/details/<string:column>', endpoint='project_details')
api.add_resource(ProjectDetail, '/api/project/detail/<int:project_detail_id>', endpoint='project_detail')
api.add_resource(Regenerate, '/api/project/regenerate', endpoint='regenerate')
api.add_resource(NovelContinue, '/api/project/<int:project_id>/novel/continue', endpoint='novel_continue')


if __name__ == '__main__':
    # generate_image('temp', os.path.join(DATA_DIR, 'temp.png'), 'blue', '')
    # generate_video(os.path.join(DATA_DIR, 'temp.png'), os.path.join(DATA_DIR, 'temp.mp4'))
    application.run(host='0.0.0.0', port=5050)
