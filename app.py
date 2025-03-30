from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
import json
import logging
import re
from functools import wraps

# Khởi tạo Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Thay đổi key này thành một giá trị ngẫu nhiên phức tạp

# Đảm bảo đường dẫn tuyệt đối
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, 'data.json')

# Cấu hình logging đơn giản
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Giới hạn số lượng dòng tối đa
MAX_ROWS = 50

# Mật khẩu đơn giản
PASSWORD = '9998'  # Thay đổi mật khẩu này

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_data():
    """Đọc dữ liệu từ file JSON"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Giới hạn số lượng dòng
                for project in data['projects']:
                    if len(project['posts']) > MAX_ROWS:
                        project['posts'] = project['posts'][-MAX_ROWS:]
                return data
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

def get_platform_from_url(url):
    """Xác định nền tảng từ URL"""
    url = url.lower()
    if 'x.com' in url or 'twitter.com' in url:
        return 'X'
    elif 'coinmarketcap.com' in url:
        return 'Coinmarketcap'
    elif 'facebook.com' in url:
        return 'Facebook'
    elif 'quora.com' in url:
        return 'Quora'
    elif 'reddit.com' in url:
        return 'Reddit'
    elif 'tiktok.com' in url:
        return 'Tiktok'
    elif 'pumfund.com' in url:
        return 'Pumfund'
    elif 't.me' in url or 'telegram.org' in url:
        return 'Tele'
    else:
        return 'Khác'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Mật khẩu không đúng')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/get_projects')
@login_required
def get_projects():
    """Lấy danh sách dự án"""
    try:
        data = load_data()
        return jsonify(data['projects'])
    except Exception as e:
        logging.error(f'Lỗi lấy danh sách dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/add_project', methods=['POST'])
@login_required
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
            'created_at': datetime.now().strftime('%d/%m'),
            'posts': []
        }
        current_data['projects'].append(new_project)
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify(new_project)
    except Exception as e:
        logging.error(f'Lỗi thêm dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/get_posts/<int:project_id>')
@login_required
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

@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    """Thêm bài viết mới"""
    try:
        data = request.get_json()
        if not data or 'project_id' not in data or 'links' not in data:
            return jsonify({'error': 'Thiếu thông tin bài viết'}), 400
            
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Tìm dự án
        project = next((p for p in current_data['projects'] if p['id'] == data['project_id']), None)
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
            
        # Thêm các bài viết mới
        new_posts = []
        for link in data['links']:
            if not link.strip():
                continue
                
            new_post = {
                'id': len(project['posts']) + 1,
                'link': link.strip(),
                'platform': get_platform_from_url(link),
                'date': datetime.now().strftime('%d/%m'),
                'is_done': False
            }
            project['posts'].append(new_post)
            new_posts.append(new_post)
            
            # Giới hạn số lượng dòng
            if len(project['posts']) > MAX_ROWS:
                project['posts'] = project['posts'][-MAX_ROWS:]
        
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify({'success': True, 'posts': new_posts})
    except Exception as e:
        logging.error(f'Lỗi thêm bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/delete_project/<int:project_id>', methods=['DELETE'])
@login_required
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

@app.route('/delete_all', methods=['DELETE'])
@login_required
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

@app.route('/toggle_done', methods=['POST'])
@login_required
def toggle_done():
    """Đánh dấu bài viết đã hoàn thành"""
    try:
        data = request.get_json()
        if not data or 'link' not in data or 'is_done' not in data:
            return jsonify({'error': 'Thiếu thông tin'}), 400
            
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Tìm và cập nhật trạng thái bài viết
        for project in current_data['projects']:
            for post in project['posts']:
                if post['link'] == data['link']:
                    post['is_done'] = data['is_done']
                    # Lưu dữ liệu
                    save_data(current_data)
                    return jsonify({'success': True})
                    
        return jsonify({'error': 'Không tìm thấy bài viết'}), 404
    except Exception as e:
        logging.error(f'Lỗi cập nhật trạng thái: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/delete_posts', methods=['POST'])
@login_required
def delete_posts():
    """Xóa các bài viết đã chọn"""
    try:
        data = request.get_json()
        if not data or 'links' not in data:
            return jsonify({'error': 'Thiếu danh sách bài viết cần xóa'}), 400
            
        # Đọc dữ liệu hiện tại
        current_data = load_data()
        
        # Xóa các bài viết
        for project in current_data['projects']:
            project['posts'] = [post for post in project['posts'] if post['link'] not in data['links']]
            
        # Lưu dữ liệu
        save_data(current_data)
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f'Lỗi xóa bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/sort_posts/<int:project_id>')
@login_required
def sort_posts(project_id):
    """Sắp xếp bài viết theo nền tảng"""
    try:
        data = load_data()
        project = next((p for p in data['projects'] if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
            
        # Sắp xếp bài viết theo nền tảng
        project['posts'].sort(key=lambda x: x['platform'])
        
        # Lưu dữ liệu
        save_data(data)
        
        return jsonify(project['posts'])
    except Exception as e:
        logging.error(f'Lỗi sắp xếp bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Khởi tạo dữ liệu mẫu nếu chưa có
if not os.path.exists(DATA_FILE):
    sample_data = {
        'projects': [
            {
                'id': 1,
                'name': 'Dự án mẫu',
                'created_at': datetime.now().strftime('%d/%m'),
                'posts': [
                    {
                        'id': 1,
                        'link': 'https://facebook.com/sample',
                        'platform': 'Facebook',
                        'date': datetime.now().strftime('%d/%m'),
                        'is_done': False
                    }
                ]
            }
        ]
    }
    save_data(sample_data)
    logging.info('Đã tạo dữ liệu mẫu')

# Export app cho passenger_wsgi.py
application = app
