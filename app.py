import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "blackboney_ultra_secret_key_multi_chat_2026"
app.config['SESSION_COOKIE_NAME'] = 'blackboney_session'

# N-khlliw l-key safe f frontend dynamic direct
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyAJpdUKnDPr-OKK6N4qnd99RVMSEawhW_8")

@app.route('/')
def home():
    if 'all_chats' not in session:
        session['all_chats'] = {}
    if 'active_chat_id' not in session:
        new_id = str(uuid.uuid4())[:8]
        session['all_chats'] = {new_id: {"title": "New Chat", "messages": []}}
        session['active_chat_id'] = new_id
        session.modified = True
    return render_template('index.html')

@app.route('/api/chats', methods=['GET'])
def get_all_chats():
    all_chats = session.get('all_chats', {})
    active_id = session.get('active_chat_id', '')
    return jsonify({
        'chats': [{'id': cid, 'title': cdata['title']} for cid, cdata in all_chats.items()],
        'active_id': active_id,
        'api_key': GEMINI_KEY
    })

@app.route('/api/chats/new', methods=['POST'])
def create_new_chat():
    all_chats = session.get('all_chats', {})
    new_id = str(uuid.uuid4())[:8]
    all_chats[new_id] = {"title": "New Chat", "messages": []}
    session['all_chats'] = all_chats
    session['active_chat_id'] = new_id
    session.modified = True
    return jsonify({'status': 'created', 'id': new_id})

@app.route('/api/chats/switch/<chat_id>', methods=['POST'])
def switch_chat(chat_id):
    all_chats = session.get('all_chats', {})
    if chat_id in all_chats:
        session['active_chat_id'] = chat_id
        session.modified = True
        return jsonify({'status': 'switched', 'messages': all_chats[chat_id]['messages']})
    return jsonify({'error': 'Chat not found'}), 404

@app.route('/api/chat/sync', methods=['POST'])
def sync_messages():
    try:
        data = request.get_json()
        chat_id = session.get('active_chat_id')
        all_chats = session.get('all_chats', {})
        
        if chat_id in all_chats:
            all_chats[chat_id]['messages'] = data.get('messages', [])
            if len(all_chats[chat_id]['messages']) <= 2:
                user_msg = data.get('first_msg', 'New Chat')
                all_chats[chat_id]['title'] = user_msg[:22] + ('...' if len(user_msg) > 22 else '')
            session['all_chats'] = all_chats
            session.modified = True
            return jsonify({'status': 'synced', 'title': all_chats[chat_id]['title']})
    except:
        pass
    return jsonify({'status': 'ignored'})