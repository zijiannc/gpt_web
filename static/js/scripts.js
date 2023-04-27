let chatID = "default";

$(document).ready(function () {
    // 获取当前页面的URL
    window.currentPage = window.location.pathname;
    window.chatID = 'default';
    $("#sendButton").on("click", sendMessage);
    $("#messageInput").on("keypress", function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            sendMessage();
        }
    });

    // 在页面加载时清除历史记录
    //clearHistory();
});

function sendMessage() {
    const message = $("#messageInput").val();
    if (!message) return;

    displayUserMessage(message);
    $("#messageInput").val("");

    let requestUrl;
    switch (window.currentPage) {
        case '/wise_group':
            requestUrl = '/chat_wise_group';
            break;
        case '/question_answer':
            requestUrl = '/chat_question_answer';
            break;
        default:
            requestUrl = '/chat';
            break;
    }

    $.ajax({
        url: requestUrl,
        type: "POST",
        data: JSON.stringify({ message: message,page: currentPage, chat_id: chatID }),
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

function displayUserMessage(message) {
    $("#chatArea").append(`<div class="message"><span class="user">你: </span>${message}</div>`);
    scrollToBottom();

    localStorage.setItem("chatHistory", $("#chatArea").html());
}

function displayBotMessage(message) {
    $("#chatArea").append(`<div class="message bot-message"><span class="bot">机器人: </span>${message}</div>`);
    scrollToBottom();

    localStorage.setItem("chatHistory", $("#chatArea").html());
}

function scrollToBottom() {
    $("#chatArea").scrollTop($("#chatArea")[0].scrollHeight);
}

function clearHistory() {
    $.ajax({
        url: "/clear_history",
        type: "POST",
        data: JSON.stringify({ page: currentPage, chat_id: chatID }),
        contentType: "application/json",
        success: function() {
            console.log("History cleared.");
        },
        error: function(err) {
            console.log(err);
        },
    });
}