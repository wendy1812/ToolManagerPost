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
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('projects', [])
        return []
    except Exception as e:
        logging.error(f"Lỗi khi đọc dữ liệu: {str(e)}")
        return []

def save_data(projects):
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # Lưu dữ liệu vào file tạm thời trước
        temp_file = f"{DATA_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({'projects': projects}, f, ensure_ascii=False, indent=2)
            
        # Nếu lưu file tạm thành công, thay thế file gốc
        if os.path.exists(temp_file):
            if os.path.exists(DATA_FILE):
                os.replace(temp_file, DATA_FILE)
            else:
                os.rename(temp_file, DATA_FILE)
    except Exception as e:
        logging.error(f"Lỗi khi lưu dữ liệu: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
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
        return jsonify(data)
    except Exception as e:
        logging.error(f'Lỗi lấy danh sách dự án: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Tên dự án không được để trống'}), 400
            
        projects = load_data()
        new_project = {
            'id': len(projects) + 1,
            'name': name,
            'created_at': datetime.now().strftime('%d/%m'),
            'posts': []
        }
        projects.append(new_project)
        save_data(projects)
        return jsonify({'message': 'Dự án đã được thêm thành công'})
    except Exception as e:
        logging.error(f"Lỗi khi thêm dự án: {str(e)}")
        return jsonify({'error': 'Không thể thêm dự án'}), 500

@app.route('/get_posts/<int:project_id>')
@login_required
def get_posts(project_id):
    """Lấy danh sách bài viết của dự án"""
    try:
        data = load_data()
        project = next((p for p in data if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
        return jsonify(project['posts'])
    except Exception as e:
        logging.error(f'Lỗi lấy danh sách bài viết: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        links = data.get('links', [])
        
        if not project_id or not links:
            return jsonify({'error': 'Thiếu thông tin'}), 400
            
        projects = load_data()
        project = next((p for p in projects if p['id'] == project_id), None)
        
        if not project:
            return jsonify({'error': 'Không tìm thấy dự án'}), 404
            
        # Thêm các bài viết mới vào dự án
        for link in links:
            if link.strip():
                platform = get_platform_from_url(link)
                new_post = {
                    'id': len(project['posts']) + 1,
                    'link': link.strip(),
                    'platform': platform,
                    'date': datetime.now().strftime('%d/%m'),
                    'is_done': False
                }
                project['posts'].append(new_post)
                
        save_data(projects)
        return jsonify({'message': 'Bài viết đã được thêm thành công'})
    except Exception as e:
        logging.error(f"Lỗi khi thêm bài viết: {str(e)}")
        return jsonify({'error': 'Không thể thêm bài viết'}), 500

@app.route('/delete_project/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    try:
        projects = load_data()
        projects = [p for p in projects if p['id'] != project_id]
        save_data(projects)
        return jsonify({'message': 'Dự án đã được xóa thành công'})
    except Exception as e:
        logging.error(f"Lỗi khi xóa dự án: {str(e)}")
        return jsonify({'error': 'Không thể xóa dự án'}), 500

@app.route('/delete_all', methods=['DELETE'])
@login_required
def delete_all():
    try:
        save_data([])  # Lưu danh sách rỗng
        return jsonify({'message': 'Tất cả dữ liệu đã được xóa thành công'})
    except Exception as e:
        logging.error(f"Lỗi khi xóa tất cả dữ liệu: {str(e)}")
        return jsonify({'error': 'Không thể xóa dữ liệu'}), 500

@app.route('/toggle_done', methods=['POST'])
@login_required
def toggle_done():
    """Đánh dấu bài viết đã hoàn thành"""
    try:
        data = request.get_json()
        if not data or 'link' not in data or 'is_done' not in data:
            return jsonify({'error': 'Thiếu thông tin'}), 400
            
        # Đọc dữ liệu hiện tại
        projects = load_data()
        
        # Tìm và cập nhật trạng thái bài viết
        for project in projects:
            for post in project['posts']:
                if post['link'] == data['link']:
                    post['is_done'] = data['is_done']
                    # Lưu dữ liệu
                    save_data(projects)
                    return jsonify({'success': True})
                    
        return jsonify({'error': 'Không tìm thấy bài viết'}), 404
    except Exception as e:
        logging.error(f'Lỗi cập nhật trạng thái: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/delete_posts', methods=['POST'])
@login_required
def delete_posts():
    try:
        data = request.get_json()
        links_to_delete = set(data.get('links', []))
        
        if not links_to_delete:
            return jsonify({'error': 'Không có bài viết nào để xóa'}), 400
            
        projects = load_data()
        for project in projects:
            project['posts'] = [post for post in project['posts'] 
                              if post['link'] not in links_to_delete]
            
        save_data(projects)
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Lỗi khi xóa bài viết: {str(e)}")
        return jsonify({'error': 'Không thể xóa bài viết'}), 500

@app.route('/sort_posts/<int:project_id>')
@login_required
def sort_posts(project_id):
    """Sắp xếp bài viết theo nền tảng"""
    try:
        data = load_data()
        project = next((p for p in data if p['id'] == project_id), None)
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
        'projects': []
    }
    save_data(sample_data['projects'])
    logging.info('Đã tạo file dữ liệu mới')

# Export app cho passenger_wsgi.py
application = app
