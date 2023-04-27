import os
import functools


from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logged_in'

app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passwd = db.Column(db.String(120), unique=True, nullable=False)
    #is_active = db.Column(db.Boolean(), default=True)  # 定义 is_active 属性，默认为 True
    def __repr__(self):
        return f'<User {self.username}>'


openai.api_key = os.getenv("OPENAI_API_KEY")

# 创建一个字典来存储每个用户的消息历史
user_histories = {}

def get_history_key(user_ip, page, chat_id):
    return f"{user_ip}-{page}-{chat_id}"


@app.route('/question_answer')
@login_required
def question_answer():
    return render_template('question_answer.html')

@app.route('/wise_group')
@login_required
def wise_group():
    return render_template('wise_group.html')

@app.route('/re_word')
@login_required
def re_word():
    return render_template('re_word.html')

@app.route('/')
def index():
    return render_template('index.html')

def process_chat_request(route, temperature, system_setting_message):
    user_message = request.json['message']
    page = request.json.get('page', 'index')
    chat_id = request.json.get('chat_id', 'default')
    user_ip = request.remote_addr
    history_key = get_history_key(user_ip, page, chat_id)

    if history_key not in user_histories:
        user_histories[history_key] = [{"role": "system", "content": system_setting_message}]

    user_histories[history_key].append({"role": "user", "content": user_message})
    print(user_histories)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=user_histories[history_key]
    )

    response = completion.choices[0].message.content
    user_histories[history_key].append({"role": "assistant", "content": response})

    return jsonify({"response": response})

def process_chat_request2(route, temperature, system_setting_message):
    user_message = request.json['message']
    page = request.json.get('page', 'index')
    chat_id = request.json.get('chat_id', 'default')
    user_ip = request.remote_addr
    history_key = get_history_key(user_ip, page, chat_id)

    user_histories[history_key] = [{"role": "system", "content": system_setting_message}]
    user_histories[history_key].append({"role": "user", "content": "help me re-word and give a 主题:" + user_message})
    print(user_histories)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=user_histories[history_key]
    )

    response = completion.choices[0].message.content
    user_histories[history_key].append({"role": "assistant", "content": response})

    return jsonify({"response": response})


def route_decorator(route, temperature, system_setting_message):
    def route_decorator_inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                if route == '/chat_re_word':
                    return process_chat_request2(route, temperature, system_setting_message)
                return process_chat_request(route, temperature, system_setting_message)
            return func(*args, **kwargs)
        return wrapper
    return route_decorator_inner

@app.route('/chat', methods=['GET', 'POST'])
@route_decorator('/chat', 0.8, "你好,我是您的私人顾问,我可以回答任何问题.")
def chat():
    return None

@app.route('/chat_wise_group', methods=['GET', 'POST'])
@route_decorator('/chat_wise_group', 1.2, "你好,我是您的私人讨论小组,我们会根据您提出的问题进行详尽的讨论.模拟一个由智囊团成员回答我的问题,在这个讨论组里面有:乔布斯,特斯拉,比尔盖茨,苏格拉底,老子,和一个叫尼尔的角色,他是软件和硬件高级AI工程师.讨论组里每个人的回答至少有两三句话,并且会相互讨论.")
def chat_wise_group():
    return None

@app.route('/chat_re_word', methods=['GET', 'POST'])
@route_decorator('/chat_re_word', 1.0, "你好,我是您的语言助理,我可以帮助您根据您发的文字重新排版.")
def chat_re_word():
    return None

@app.route('/chat_question_answer', methods=['GET', 'POST'])
@route_decorator('/chat_question_answer', 0.8,"你好,我是您的私人顾问,我可以回答任何问题.")
def chat_question_answer():
    return None


@app.route('/clear_history', methods=['POST'])
def clear_history():
    user_ip = request.remote_addr
    page = request.json.get('page', 'index')
    chat_id = request.json.get('chat_id', 'default')
    history_key = get_history_key(user_ip, page, chat_id)

    if history_key in user_histories:
        user_histories.pop(history_key)
    return "OK"

@app.route('/check_login', methods=['POST'])
def check_login():
    data = request.get_json()
    username = data.get('username')
    passwd = data.get('passwd')
    
    print('Username:', username)
    print('Passwd:', passwd)

    user = User.query.filter_by(username=username, passwd=passwd).first()
    
    print('User:', user)

    if user:
        login_user(user,remember=True)

        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '用户名或密钥错误'})




def add_user(username, passwd):
    existing_user = User.query.filter_by(username=username).first()
    #print username and passwd to console
    print(f"Username: {username}")
    print(f"Passwd: {passwd}")

    if existing_user:
        print(f"Username {username} already exists. Updating API key.")
        existing_user.passwd = passwd
    else:
        new_user = User(username=username, passwd=passwd)
        db.session.add(new_user)

    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logged_in')
def logged_in():
    return jsonify({'logged_in': current_user.is_authenticated})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_user('admin','admin')
    app.run(host='0.0.0.0', port=5001, debug=True)
