from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from upstash_redis import Redis
import os
import hashlib
import json

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Upstash Redis 클라이언트 초기화 (환경 변수 자동 연동)
redis = Redis.from_env()

USER_DB_KEY = "hanso:users_db"

def load_user_db():
    # Upstash에서 회원 DB(Hash 형태) 가져오기
    db = redis.hgetall(USER_DB_KEY)
    if not db:
        return {}
    # Upstash 반환값이 바이트/문자열일 수 있으므로 정돈
    return {k.decode('utf-8') if isinstance(k, bytes) else k: 
            v.decode('utf-8') if isinstance(v, bytes) else v for k, v in db.items()}

def save_user_db(db):
    if db:
        redis.hset(USER_DB_KEY, values=db)

def make_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def get_user_data_key():
    user_hash = session.get('user_session')
    return f"hanso:chat_data:{user_hash}"

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
    
    key = get_user_data_key()
    
    if request.method == 'GET':
        raw_data = redis.get(key)
        if raw_data:
            # Redis에 저장된 JSON 문자열을 파싱
            try:
                data = json.loads(raw_data)
                if "me_name" not in data: data["me_name"] = "나"
                if "other_name" not in data: data["other_name"] = "상대방"
                return jsonify(data)
            except:
                pass
        
        # 데이터가 없을 경우 기본값 반환
        return jsonify({
            "saved_chats": [], 
            "me_name": "나", 
            "other_name": "상대방",
            "me_pic": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "other_pic": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "messages": []
        })
    else:
        # POST 요청: 전달받은 전체 JSON 상태를 Upstash Redis에 문자열로 저장
        req_data = request.json
        redis.set(key, json.dumps(req_data, ensure_ascii=False))
        return jsonify({"status": "success"})

@app.route('/custom_test')
def custom_test():
    return render_template('custom_test.html')
