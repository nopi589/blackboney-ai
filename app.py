import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

app = Flask(__name__)
CORS(app)
app.secret_key = "blackboney_ultra_secret_key_multi_chat_2026"

GEMINI_KEY = "AIzaSyCOQrwTTpDw3O66fbybl4NyMUxdWSGf6U0"

@app.route('/')
def home():
    # 'all_chats' dict khwi khass b kulla user f session dyalo
    if 'all_chats' not in session:
        session['all_chats'] = {}
    # 'active_chat_id' huwa l-ID d l-chat li khdam fiha dba
    if 'active_chat_id' not in session:
        # n-creew awel chat auto
        new_id = str(uuid.uuid4())[:8]
        session['all_chats'] = {new_id: {"title": "New Chat", "messages": []}}
        session['active_chat_id'] = new_id
    return render_template('index.html')

# API bch njbdo gha l-list d l-chats l-foq d l-sidebar
@app.route('/api/chats', methods=['GET'])
def get_all_chats():
    all_chats = session.get('all_chats', {})
    active_id = session.get('active_chat_id', '')
    return jsonify({
        'chats': [{'id': cid, 'title': cdata['title']} for cid, cdata in all_chats.items()],
        'active_id': active_id
    })

# API bch n-creew chat jdid bla ma nms7o l-9dam
@app.route('/api/chats/new', methods=['POST'])
def create_new_chat():
    all_chats = session.get('all_chats', {})
    new_id = str(uuid.uuid4())[:8]
    all_chats[new_id] = {"title": "New Chat", "messages": []}
    session['all_chats'] = all_chats
    session['active_chat_id'] = new_id
    session.modified = True
    return jsonify({'status': 'created', 'id': new_id})

# API bch n-bdlo mn chat l chat mlli user i-cliki f l-sidebar
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
        
        # Ila madkhlch l awl mra normal
        if not active_id or active_id not in all_chats:
            active_id = str(uuid.uuid4())[:8]
            all_chats[active_id] = {"title": "New Chat", "messages": []}
            session['active_chat_id'] = active_id

        current_chat = all_chats[active_id]
        
        # Update dynamic title mlli user i-safet awel msg
        if len(current_chat['messages']) == 0:
            current_chat['title'] = user_message[:22] + ('...' if len(user_message) > 22 else '')

        # Zid message d user f cache d l-chat active
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
        
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response_data = response.json()
        
        try:
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Zid message d l-AI hta hwa
            current_chat['messages'].append({
                "role": "model",
                "parts": [{"text": ai_response}]
            })
            
            all_chats[active_id] = current_chat
            session['all_chats'] = all_chats
            session.modified = True
            
            return jsonify({'response': ai_response, 'chat_title': current_chat['title']})
            
        except KeyError:
            return jsonify({'response': "Smhli, kayn moshkil f jawb Gemini."}), 500

    except Exception as e:
        return jsonify({'response': "Smhli, kayn moshkil f server."}), 500

print("✨ Ultimate Multi-Chat Storage Running...")
if __name__ == '__main__':
    app.run(debug=True, port=5000)