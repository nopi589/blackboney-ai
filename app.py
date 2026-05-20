import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "blackboney_ultra_secret_key_multi_chat_2026"
app.config['SESSION_COOKIE_NAME'] = 'blackboney_session'

# N-rj3o key dynamic mn dynamic variables aw l-key direct s7ee7a
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyCOQrwTTpDw3O66fbybl4NyMUxdWSGf6U0")

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
        'active_id': active_id
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

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message empty'}), 400
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        all_chats = session.get('all_chats', {})
        active_id = session.get('active_chat_id')
        
        if not active_id or active_id not in all_chats:
            active_id = str(uuid.uuid4())[:8]
            all_chats[active_id] = {"title": "New Chat", "messages": []}
            session['active_chat_id'] = active_id

        current_chat = all_chats[active_id]
        
        if len(current_chat['messages']) == 0:
            current_chat['title'] = user_message[:22] + ('...' if len(user_message) > 22 else '')

        current_chat['messages'].append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        payload = {
            "contents": current_chat['messages'],
            "systemInstruction": {
                "parts": [{
                    "text": "Your name is BlackBoney AI. You are a cool, smart, and futuristic AI assistant. Speak fluently in Darija (mainly), English, and French. Keep answers clear and short."
                }]
            }
        }
        
        # Beddelna l-post bch Render/Vercel i-safet request secure bla bypass mchmoukh
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
            
            current_chat['messages'].append({
                "role": "model",
                "parts": [{"text": ai_response}]
            })
            
            all_chats[active_id] = current_chat
            session['all_chats'] = all_chats
            session.modified = True
            
            return jsonify({'response': ai_response, 'chat_title': current_chat['title']})
        else:
            # Ila Google 3tat error t-ban lina exact chna hiya
            error_msg = response_data.get('error', {}).get('message', 'Unknown Gemini API Error')
            return jsonify({'response': f"Moshkil mn API d Gemini: {error_msg}"}), 500

    except Exception as e:
        return jsonify({'response': f"Moshkil f Server d Vercel: {str(e)}"}), 500