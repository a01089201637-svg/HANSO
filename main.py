from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import hashlib
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Vercel 쓰기 가능 임시 경로(/tmp)로 변경
USER_DB_FILE = "/tmp/users_db.json"

# --- 유틸리티 함수 ---
def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_db(db):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def make_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def get_user_data_path():
    user_hash = session.get('user_session')
    return f"/tmp/chat_data_{user_hash}.json"

# --- 경로 설정 ---
@app.route('/')
def index():
    if 'user_session' not in session:
        return render_template('login.html')
    return render_template('index.html', display_id=session.get('display_id'))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = load_user_db()
    user_id = data.get('id')
    pw = data.get('pw')
    
    if user_id in db and db[user_id] == make_hash(pw):
        session['user_session'] = make_hash(user_id + pw)
        session['display_id'] = user_id
        return jsonify({"status": "success"})
    return jsonify({"status": "fail", "message": "아이디 또는 비밀번호 불일치"})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    db = load_user_db()
    user_id = data.get('id')
    pw = data.get('pw')
    
    if not user_id or not pw:
        return jsonify({"status": "fail", "message": "아이디와 비밀번호를 입력해주세요."})
    
    if user_id in db:
        return jsonify({"status": "fail", "message": "이미 존재하는 아이디입니다."})
    
    db[user_id] = make_hash(pw)
    save_user_db(db)
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if 'user_session' not in session: 
        return jsonify({"error": "unauthorized"}), 401
    
    path = get_user_data_path()
    
    if request.method == 'GET':
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 기존 파일에 이름 값이 없을 경우를 대비한 기본값 보정
                if "me_name" not in data:
                    data["me_name"] = "나"
                if "other_name" not in data:
                    data["other_name"] = "상대방"
                return jsonify(data)
        
        # 유저 데이터 파일이 없을 경우 초기 기본값 반환
        return jsonify({
            "saved_chats": [], 
            "me_name": "나", 
            "other_name": "상대방",
            "me_pic": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "other_pic": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "messages": []
        })
    else:
        # POST 요청: 전달받은 JSON 데이터(이름, 사진, 메시지 등 전체 상태)를 유저별 파일에 저장
        req_data = request.json
        
        # 기존에 저장된 데이터가 있다면 불러와서 이름이나 프로필 등이 유실되지 않도록 병합하거나 그대로 저장
        # 프론트엔드에서 전체 상태(me_name, other_name 포함)를 통째로 보내고 있다면 그대로 저장해도 무방합니다.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(req_data, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})

# --- 테스트용 경로 추가 ---
@app.route('/custom_test')
def custom_test():
    return render_template('custom_test.html')
