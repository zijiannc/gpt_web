import os

from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 创建一个字典来存储每个用户的消息历史
user_histories = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # 从请求中获取用户输入的消息
    user_message = request.json['message']
    
    # 获取用户的IP地址
    user_ip = request.remote_addr

    # 如果用户历史记录中没有该IP地址，创建一个空列表
    if user_ip not in user_histories:
        user_histories[user_ip] = [{"role": "system", "content": "你好,我是您的私人顾问,我可以回答任何问题."}] # 机器人的欢迎语
    
    # 向历史记录中添加用户的消息
    user_histories[user_ip].append({"role": "user", "content": user_message})

    # 调用OpenAI API来获取回复
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.8,
        messages=user_histories[user_ip]
    )

    # 从API响应中提取回复文本
    response = completion.choices[0].message.content

    # 向历史记录中添加机器人的回复
    user_histories[user_ip].append({"role": "assistant", "content": response})

    # 将回复作为JSON格式返回
    return jsonify({"response": response})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    user_ip = request.remote_addr
    if user_ip in user_histories:
        user_histories.pop(user_ip)
    return "OK"

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)