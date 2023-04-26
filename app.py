import os

from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # 从请求中获取用户输入的消息
    user_message = request.json['message']

    # 构造与API交互所需的消息列表
    messages = [
        {"role": "system", "content": "你好，我是一个聊天机器人。请问有什么问题我可以帮助您解答吗？"},
        {"role": "user", "content": user_message}
    ]

    # 调用OpenAI API来获取回复    
    completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.8,
            messages=messages
        )

    # 从API响应中提取回复文本
    response = completion.choices[0].message.content
    #response = completions.choices[0].message['content'].strip()

    # 将回复作为JSON格式返回
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)