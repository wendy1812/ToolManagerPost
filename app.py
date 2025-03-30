from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import json
import logging

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình cho môi trường production
app.config['APPLICATION_ROOT'] = '/quanlybaiviet'

# Đảm bảo đường dẫn tuyệt đối
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, 'data.json')

# Cấu hình logging đơn giản
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def load_data():
    """Đọc dữ liệu từ file JSON"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'projects': []}
    except Exception as e:
        logging.error(f'Lỗi đọc file dữ liệu: {str(e)}')
        return {'projects': []}

def save_data(data):
    """Lưu dữ liệu vào file JSON"""
    try:
        # Đảm bảo thư mục logs tồn tại
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f'Lỗi lưu file dữ liệu: {str(e)}')
        raise

@app.route('/quanlybaiviet/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/quanlybaiviet/get_projects')
def get_projects():
    """Lấy danh sách dự án"""
    try:
        data = load_data()
        return jsonify(data['projects'])
    except Exception as e:
        logging.error(f'Lỗi lấy danh sách dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/quanlybaiviet/add_project', methods=['POST'])
def add_project():
    """Thêm dự án mới"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Thiếu tên dự án'}), 400
            
        project_name = data['name'].strip()
        if not project_name:
            return jsonify({'error': 'Tên dự án không được để trống'}), 400
            
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Kiểm tra dự án đã tồn tại chưa
        if any(p['name'] == project_name for p in current_data['projects']):
            return jsonify({'error': 'Dự án đã tồn tại'}), 400
            
        # Thêm dự án mới
        new_project = {
            'id': len(current_data['projects']) + 1,
            'name': project_name,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'posts': []
        }
        current_data['projects'].append(new_project)
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify(new_project)
    except Exception as e:
        logging.error(f'Lỗi thêm dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/quanlybaiviet/get_posts/<int:project_id>')
def get_posts(project_id):
    """Lấy danh sách bài viết của dự án"""
    try:
        data = load_data()
        project = next((p for p in data['projects'] if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
        return jsonify(project['posts'])
    except Exception as e:
        logging.error(f'Lỗi lấy danh sách bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/quanlybaiviet/add_post', methods=['POST'])
def add_post():
    """Thêm bài viết mới"""
    try:
        data = request.get_json()
        if not data or 'project_id' not in data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Thiếu thông tin bài viết'}), 400
            
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Tìm dự án
        project = next((p for p in current_data['projects'] if p['id'] == data['project_id']), None)
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
            
        # Thêm bài viết mới
        new_post = {
            'id': len(project['posts']) + 1,
            'title': data['title'],
            'content': data['content'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        project['posts'].append(new_post)
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify(new_post)
    except Exception as e:
        logging.error(f'Lỗi thêm bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/quanlybaiviet/delete_project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Xóa dự án"""
    try:
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Tìm dự án
        project_index = next((i for i, p in enumerate(current_data['projects']) if p['id'] == project_id), None)
        if project_index is None:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
            
        # Xóa dự án
        current_data['projects'].pop(project_index)
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify({'message': 'Đã xóa dự án thành công'})
    except Exception as e:
        logging.error(f'Lỗi xóa dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/quanlybaiviet/delete_all', methods=['DELETE'])
def delete_all():
    """Xóa tất cả dữ liệu"""
    try:
        # Xóa tất cả dữ liệu
        current_data = {'projects': []}
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify({'message': 'Đã xóa tất cả dữ liệu thành công'})
    except Exception as e:
        logging.error(f'Lỗi xóa tất cả dữ liệu: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Khởi tạo dữ liệu mẫu nếu chưa có
if not os.path.exists(DATA_FILE):
    sample_data = {
        'projects': [
            {
                'id': 1,
                'name': 'Dự án mẫu',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'posts': [
                    {
                        'id': 1,
                        'title': 'Bài viết mẫu',
                        'content': 'Đây là nội dung bài viết mẫu',
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                ]
            }
        ]
    }
    save_data(sample_data)
    logging.info('Đã tạo dữ liệu mẫu')

# Export app cho passenger_wsgi.py
application = app
