// 页面加载完成后，绑定事件监听器
$(document).ready(function () {
    $("#sendButton").on("click", sendMessage);
    $("#messageInput").on("keypress", function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            sendMessage();
        }
    });

    // 在页面加载时清除历史记录
    clearHistory();
});

// 发送消息函数
function sendMessage() {
    const message = $("#messageInput").val();
    if (!message) return;

    displayUserMessage(message);
    $("#messageInput").val("");

    // 使用Ajax向后端发送请求
    $.ajax({
        url: "/chat",
        type: "POST",
        data: JSON.stringify({ message: message }),
        contentType: "application/json",
        success: function (response) {
            const botResponse = response.response;
            displayBotMessage(botResponse);
        },
        error: function (err) {
            console.log(err);
        },
    });
}

// 显示用户消息
function displayUserMessage(message) {
    $("#chatArea").append(`<div class="message"><span class="user">你: </span>${message}</div>`);
    scrollToBottom();

    // 将聊天记录保存到localStorage
    localStorage.setItem("chatHistory", $("#chatArea").html());
}

// 显示机器人消息
function displayBotMessage(message) {
    $("#chatArea").append(`<div class="message"><span class="bot">机器人: </span>${message}</div>`);
    scrollToBottom();

    // 更新localStorage中的聊天记录
    localStorage.setItem("chatHistory", $("#chatArea").html());
}

// 将聊天区域滚动到底部
function scrollToBottom() {
    $("#chatArea").scrollTop($("#chatArea")[0].scrollHeight);
}

// 清除历史记录函数
function clearHistory() {
    $.ajax({
        url: "/clear_history",
        type: "POST",
        success: function() {
            console.log("History cleared.");
        },
        error: function(err) {
            console.log(err);
        },
    });
}