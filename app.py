from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import hashlib
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here" # 세션 암호화를 위한 키

# [추가] 이미지 base64 데이터 전송을 위해 전송 용량 제한을 늘립니다 (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

USER_DB_FILE = "users_db.json"

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
    return f"chat_data_{user_hash}.json"

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
                return jsonify(json.load(f))
        
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
        # POST 요청: 전달받은 JSON 데이터를 유저별 파일에 저장
        with open(path, "w", encoding="utf-8") as f:
            json.dump(request.json, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "success"})

# --- 테스트용 경로 추가 ---
@app.route('/custom_test')
def custom_test():
    return render_template('custom_test.html')

if __name__ == '__main__':
    # 0.0.0.0으로 설정하면 같은 와이파이 내 다른 기기에서도 접속 가능합니다.
    app.run(debug=True, host='0.0.0.0', port=5000)