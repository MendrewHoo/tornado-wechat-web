function qrcode(str, title) {
    myalert('<div id="qrcode"></div>', title, {width: 280});
    $("#qrcode").qrcode({
        text: str,
        width: 240,
        height: 240,
        foreground: "#282d2f",
        background: "#ffffff",
        correctLevel: 3
    });
}

$(".tpl-login-btn").on('click', function () {
    $.post('/login', $(this).closest("form").serialize(), function (data) {
        console.log(data);
        if (data.status == 'pass') {
            myloading('登录成功, 准备跳转', 'open');
            setTimeout(function () {
                location.href = data.info;
            }, 2000);
        } else if (data.status == 'success') {
            var strarr = data.info.key.split(":");
            console.log(strarr[0]);
            if (strarr[0] == 'auth_login') {
                qrcode(data.info.url, '微信扫描二维码进行认证登录');
            }else {
                qrcode(data.info.url, '尚未绑定微信, 扫描二维码绑定');
            }
            auth_qrcode(data.info.key);
        } else {
            showinfo(data.info)
        }
    })
    return false;
});

function auth_qrcode(key) {
    $.get('/auth/qrcode', {key: key}, function (data) {
        console.log(data);
        if (data.status == 'pass'){
            var strarr = key.split(":");
            if (strarr[0] == 'auth_login'){
                myloading('登录成功, 准备跳转', 'open');
            }else {
                myloading('绑定微信成功, 请登录', 'open');
            }
            setTimeout(function () {
                location.href = data.info;
            }, 2000);
        } else if (data.status == 'overtime') {
            auth_qrcode(key);
        } else {
            myalert(data.info, '错误提示', 'open');
        }
    })
}

function showinfo(info) {
    var animation = 'am-animation-slide-top';
    var $auth_info = $('.auth-info');
    $auth_info.css('display', 'block');
    if ($.AMUI.support.animation) {
        $auth_info.addClass(animation).one($.AMUI.support.animation.end, function () {
            $auth_info.removeClass(animation);
        });
    }
    $auth_info.html(info);
}
