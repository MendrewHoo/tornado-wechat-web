var fixHelperModified = function (e, tr) {
        var $originals = tr.children();
        var $helper = tr.clone();
        $helper.children().each(function (index) {
            $(this).width($originals.eq(index).width())
        });
        return $helper;
    },
    updateIndex = function (e, ui) {
        $('td.index', ui.item.parent()).each(function (i) {
            $(this).html(i + 1);
        });
    };

var setting = function (obj) {
    var $obj = $(obj);
    var $tbody = $obj.closest(".widget").find(".am-table tbody");
    var edit = 'am-icon-edit', save = 'am-icon-check-circle-o';
    if ($obj.hasClass(edit)) {
        $obj.parent().find('span').html("拖动插件进行排序, 保存修改→");
        $obj.removeClass(edit).addClass(save);
        $tbody.sortable({
            disabled: false,
            helper: fixHelperModified,
            stop: updateIndex
        }).disableSelection();
    } else {
        $obj.parent().find('span').html("");
        $obj.removeClass(save).addClass(edit);
        $tbody.sortable({disabled: true});
        updatePluginList($tbody);
    }
};

function updatePluginList($tbody) {
    var data = {
        action: 'sort',
        type: $tbody.closest('table').data('table-id'),
    };
    var list = new Array();
    var $trs = $tbody.children();
    $trs.each(function (index) {
        list.push({
            index: index,
            name: $trs.eq(index).data('tr-id'),
            toggle: $trs.eq(index).find('input.tpl-switch-btn')[0].checked
        });
    });
    data['list'] = JSON.stringify(list);
    console.log(data);
    ajaxUpdate(data);
}

var togglePlugin = function (type, plugin, obj) {
    var data = {
        action: 'toggle',
        index: parseInt($(obj).closest('tr').find('td.index').html()) - 1,
        type: type,
        plugin: plugin,
        toggle: obj.checked ? 1 : 0
    }
    ajaxUpdate(data);
}

// ajax更新配置
function ajaxUpdate(updata) {
    $.post('/plugins', updata, function (data) {
        console.log(data);
    });
}