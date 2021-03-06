$(".am-icon-plus").on("click", function () {
    var $form = $("form#add-admin");
    console.log($form.length);
    if ($form.length == 0) {
        myprompt(addAdminTemp, "添加管理员", addAdmin)
    }else {
        myprompt(null, "添加管理员", addAdmin)
    }
});

function addAdmin() {
    var $form = $("form#add-admin");
    $.post('/settings/addadmin', $form.serialize(), function (data) {
        console.log(data);
        if (data.status == 'success'){
            location.reload();
        }else {
            myalert(data.info);
        }
    })
}

var addAdminTemp = '<form class="am-form tpl-form-border-form tpl-form-border-br" id="add-admin" >\n' +
    '    <div class="am-form-group">\n' +
    '        <label class="am-u-sm-3 am-form-label">用户id</label>\n' +
    '        <div class="am-u-sm-9">\n' +
    '            <input type="text" class="tpl-form-input" name="userid" required>\n' +
    '        </div>\n' +
    '    </div>\n' +
    '    <div class="am-form-group">\n' +
    '        <label class="am-u-sm-3 am-form-label">密码</label>\n' +
    '        <div class="am-u-sm-9">\n' +
    '            <input type="password" class="tpl-form-input" name="password" minlength="6">\n' +
    '        </div>\n' +
    '    </div>\n' +
    '    <div class="am-form-group">\n' +
    '        <label class="am-u-sm-3 am-form-label">验证密码</label>\n' +
    '        <div class="am-u-sm-9">\n' +
    '            <input type="password" class="tpl-form-input" name="repassword" ' +
    '               data-equal-to="[name=\'password\'] data-error-msg="两次输入的密码不一致">\n' +
    '        </div>\n' +
    '    </div>\n' +
    '</form>';
