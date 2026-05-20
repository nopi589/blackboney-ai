import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "blackboney_ultra_secret_key_multi_chat_2026"
app.config['SESSION_COOKIE_NAME'] = 'blackboney_session'

# T-2ked 3afak t-koun 7at GEMINI_KEY f l-Environment Variables dyal Vercel Settings kima hiya
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# Initialize l-client d Google s7ee7
client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)

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
    global client
    try:
        if not GEMINI_KEY:
            return jsonify({'response': "Moshkil: GEMINI_KEY khawya f Vercel Environment Variables!"}), 500
        
        if client is None:
            client = genai.Client(api_key=GEMINI_KEY)

        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message empty'}), 400
        
        all_chats = session.get('all_chats', {})
        active_id = session.get('active_chat_id')
        
        if not active_id or active_id not in all_chats:
            active_id = str(uuid.uuid4())[:8]
            all_chats[active_id] = {"title": "New Chat", "messages": []}
            session['active_chat_id'] = active_id

        current_chat = all_chats[active_id]
        
        if len(current_chat['messages']) == 0:
            current_chat['title'] = user_message[:22] + ('...' if len(user_message) > 22 else '')

        # Format custom content tailored l structural validation d new SDK
        formatted_contents = []
        for msg in current_chat['messages']:
            formatted_contents.append(
                types.Content(
                    role=msg['role'],
                    parts=[types.Part.from_text(text=msg['parts'][0]['text'])]
                )
            )
        
        # Zid dynamic user message jdid
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        )
        
        # Sifet dynamic request safely mn custom SDK config
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction="Your name is BlackBoney AI. You are a cool, smart, and futuristic AI assistant. Speak fluently in Darija (mainly), English, and French. Keep answers clear and short."
            )
        )
        
        ai_response = response.text
        
        # Save dynamic responses safe back inside session
        current_chat['messages'].append({"role": "user", "parts": [{"text": user_message}]})
        current_chat['messages'].append({"role": "model", "parts": [{"text": ai_response}]})
        
        all_chats[active_id] = current_chat
        session['all_chats'] = all_chats
        session.modified = True
        
        return jsonify({'response': ai_response, 'chat_title': current_chat['title']})

    except Exception as e:
        return jsonify({'response': f"Moshkil dynamic error f response SDK: {str(e)}"}), 500