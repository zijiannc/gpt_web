import os
import functools

from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 创建一个字典来存储每个用户的消息历史
user_histories = {}

def get_history_key(user_ip, page, chat_id):
    return f"{user_ip}-{page}-{chat_id}"


@app.route('/question_answer')
def question_answer():
    return render_template('question_answer.html')

@app.route('/wise_group')
def wise_group():
    return render_template('wise_group.html')

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

def route_decorator(route, temperature, system_setting_message):
    def route_decorator_inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
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

@app.route('/chat_question_answer', methods=['GET', 'POST'])
@route_decorator('/chat_question_answer', 0.2,"你好,我是您的私人顾问,我可以回答任何问题.")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
