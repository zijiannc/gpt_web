
$("#login-form").submit(function (event) {
    event.preventDefault();

    const username = $("#username").val().trim();
    const passwd = $("#passwd").val().trim();

    $.ajax({
        url: "/check_login",
        type: "POST",
        data: JSON.stringify({ username: username, passwd: passwd }),
        contentType: "application/json",
        success: function (response) {
            if (response.success) {
                // 登录成功，重定向到其他页面
                window.location.href = "/question_answer";
            } else {
                // 登录失败，显示错误消息
                alert(response.message);
            }
        },
        error: function () {
            // 发生错误，显示错误消息
            alert("无法连接服务器");
        }
    });
});

