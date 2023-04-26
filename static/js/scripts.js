// 页面加载完成后，绑定事件监听器
$(document).ready(function() {
    $("#sendButton").on("click", sendMessage);
    $("#messageInput").on("keypress", function(event) {
      if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage();
      }
    });
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
      success: function(response) {
        const botResponse = response.response;
        displayBotMessage(botResponse);
      },
      error: function(err) {
        console.log(err);
      },
    });
  }
  
  // 显示用户消息
  function displayUserMessage(message) {
    $("#chatArea").append(`<div class="message"><span class="user">你: </span>${message}</div>`);
    scrollToBottom();
  }
  
  // 显示机器人消息
  function displayBotMessage(message) {
    $("#chatArea").append(`<div class="message"><span class="bot">机器人: </span>${message}</div>`);
    scrollToBottom();
  }
  
  // 将聊天区域滚动到底部
  function scrollToBottom() {
    $("#chatArea").scrollTop($("#chatArea")[0].scrollHeight);
  }
  