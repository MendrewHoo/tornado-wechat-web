var fixHelperModified = function (e, tbody) {
        var $ori_trs = tbody.children();
        var $helper = tbody.clone();
        $helper.children().each(function (index) {
            $(this).children().each(function (index) {
                $(this).width($ori_trs.children().eq(index).width())
            })
        });
        return $helper;
    },
    updateIndex = function (e, ui) {
        var index_arr = new Array();
        $('tbody.ui-sortable-handle', ui.item.parent()).each(function (i) {
            index_arr.push($(this).data("menu-id"));
        });
        // 与原数据不一致, ajax提交排序结果
        if (ui.item.parent().data("menu-sort").toString() != index_arr.toString()) {
            upstatus.update_status("load", "更新排序中");
            ui.item.parent().data("menu-sort", index_arr);
            $.post('/menu', {
                action: 'updatesort',
                sort: JSON.stringify(index_arr)
            }, function (data) {
                upstatus.update_status(data.status, data.info);
            })
        }
    };

$(function () {
    $("table.am-table").sortable({
        helper: fixHelperModified,
        stop: updateIndex
    }).disableSelection();

    $("#new-menu-btn").on("click", function () {
        var $form = $(".html_temp .temp_new_menu").clone();
        myprompt($form, "添加菜单", postEditMenu)
    });
});

// 更新数据状态显示条
var upstatus = {
    $upsta_icon: $("#update-status i"),
    $upstd_title: $("#update-status span"),
    icons: {
        load: "am-icon-spinner am-icon-spin",
        success: "am-icon-check-circle",
        fail: "am-icon-times-circle"
    },
    update_status: function (status, title) {
        this.$upsta_icon.attr("class", this.icons[status]);
        this.$upstd_title.html(title);
    }
}

// 编辑菜单, 联网获取资源
var editmenu = function (obj) {
    var $tr = $(obj).closest("tr");
    var menuid = $tr.data("menu-id");
    $.get('/menu', {action: 'edit', id: menuid}, function (data) {
        myprompt(data, "修改菜单", postEditMenu);
    });
};

// 编辑菜单提交方法
function postEditMenu(e) {
    var $form = $(e.target).find("form");
    var type = $form.data("menu-type");
    // 移除不添加的列表
    $form.find("#under_list").remove();
    var formdata = $form.serializeArray();
    var menu = {
        action: 'edit',
        id: $form.data("menu-id")
    };
    var sub_button = new Array(), args = {};
    for (var i = 0; i < formdata.length; i++) {
        switch (formdata[i].name) {
            case 'name':
            case 'type':
                menu[formdata[i].name] = formdata[i].value;
                break;
            case 'sub_button':
                sub_button.push(formdata[i].value);
                break;
            case 'key':
                args[formdata[i].value] = formdata[i + 1].value;
                i++;
                break;
        }
    }
    switch (type) {
        case 'new':
            menu['action'] = 'new';
            delete menu.id;
            break;
        case 'supmenu':
            menu['sub_button'] = JSON.stringify(sub_button);
            break;
        default:
            menu['args'] = JSON.stringify(args);
            break;
    }
    console.log(menu);
    $.post('/menu', menu, function (data) {
        if (data.status == 'success') {
            location.reload();
        } else {
            myalert(data.info, "操作失败");
        }
    })
}

// 删除菜单
var delmenu = function (id) {
    myconfirm("是否删除此菜单?<br><small>注: 删除父级菜单将会一同删除其子菜单</small>", "菜单删除", {}, function () {
        $.post('/menu', {action: 'del', id: id}, function (data) {
            if (data.status == 'success') {
                location.reload();
            } else {
                myalert(data.info, "操作失败");
            }
        });
    })
};

var dbAndWechat = function (action, content) {
    myconfirm(content, "谨慎操作", {}, function () {

        $.get("/menu", {action: action}, function (data) {
            if (data.status == 'success') {
                myloading(data.info + ', 准备更新', 'open');
                setTimeout(function () {
                    location.reload();
                }, 1500);
            } else {
                myalert(data.info, "错误提示");
            }
        })
    })
};

var removeArg = function (obj) {
    var $tr = $(obj).closest("tr");
    $tr.remove();
}

var addArg = function (obj) {
    var $tbody = $(obj).closest(".am-form-group").find(".am-table tbody");
    $tbody.append($(".html_temp .temp_add_arg").clone());
}
