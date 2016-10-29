var table;
$(function () {
    var handleDataTableResponsive = function () {
        "use strict";
        // var rolesMap = {'admin':'超级管理员','operator':'事务性管理员','master':'秘书处管理员', 'requirement': '需求对接管理员'};
        if ($("#data-table").length !== 0) {
            table = $("#data-table").DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function (oSettings, oData) {
                    save_dt_view(oSettings, oData);
                },
                "fnStateLoad": function (oSettings) {
                    return load_dt_view(oSettings);
                },
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls"
                    }]
                },
                "ajax": "/rest/mgr/admin/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "head_img_url",
                    "mRender": function (data, type, full) {
                        return '<img src="' + data + '" style="max-width:60px;border-radius:100px;"/>';
                    }
                }, {
                    "data": "nick_name",
                    "mRender": function (data, type, full) {
                        return '<div id="' + full.person_id + '">' + data + '</div>';
                    }
                }, {
                    "data": "province",
                    "mRender": function (data, type, full) {
                        return data + '.' + full.city;
                    }
                }, {
                    "data": "auth_date"
                }, {
                    "data": "roles",
                    "mRender": function (data, type, full) {
                        return full.role_names;
                    }
                }, {
                    "data": "person_id",
                    "mRender": function (data, type, full) {
                        var html = "";
                        if ($('#person_roles').val().indexOf("admin") >= 0) {
                            html += '<a onclick="$._editRoles(\'' + full['fullname'] + '\',\'' + full['nick_name'] + '\',\'' + full['person_id'] + '\',\'' + full['group_name'] + '\',\'' + full['roles'] + '\')" class="btn btn-warning btn-xs m-r-5">修改权限</a>';
                            html += '<a onclick="$._deleteAdmin(\'' + full['person_id'] + '\')" class="btn btn-inverse btn-xs m-r-5">删除</a>';
                        }
                        return html;
                    }
                }],
                "aaSorting": [3, 'desc'],
                "language": TABLE_LANG
            })
        }
    };
    $._deleteGroup = function (group_id) {
        del_group_name = $("#group_name_hidden").val();
        $("#del_group_name").replaceWith('<h4 id="del_group_name">' + del_group_name + '</h4>');
        $("#modal-del-group").modal('show')
    };

    $("#del_group").click(function () {
        alert('测试中，暂时不能删除!');
        return false
    });
    $._addGroup = function (group_id) {
        $("#modal-add-group").modal('show');
        parent_group_name = $("#group_name_hidden").val();
        $("#parent_group").html('<h5>' + parent_group_name + '</h5>');
    };
    $("#add_group").click(function () {
        var url = '/rest/add/group';
        var parent_id = $("#group_id_hidden").val();
        var group_name = $("#child_group").val();
        $.ajax({
            url: url,
            type: 'post',
            data: {
                parent_id: parent_id,
                group_name: group_name
            },
            success: function (data) {
                window.location.reload();
            }
        })
    });
    $._deleteAdmin = function (person_id) {
        if (confirm("你确定要删除该管理员吗?")) {
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/admin/delete',
                data: {
                    person_id: person_id,
                    _xsrf: $.cookie("_xsrf")
                },
                success: function (data) {
                    if (data.error) {
                        return alert(data.error || '删除失败！');
                    }
                    window.location.reload();
                },
                error: function () {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        }
    };
    $._editRoles = function (fullname, nick_name, person_id, group_name, roles) {
        $("#modal-edit-roles").modal("show");
        $('#nick_name').replaceWith('<h5 id="nick_name" style="form-control" >' + fullname + ' ( ' + nick_name + ' ) ' + '</h5>');
        $('#admin_person_id').val(person_id);
        $("#edit_group_name").replaceWith('<h5 id="edit_group_name" style="form-control" >' + group_name + '</h5>' +
            '<input id="edit_group" type="hidden" value="' + group_name + '"' + '/>');
        var checkboxs = $("#edit_check_roles input");
        var check = "";
        for (var i = 0; i < checkboxs.length; i++) {
            $(checkboxs[i]).prop("checked", false);
        }
        var all_roles = roles.split(',');
        for (var item in all_roles) {
            $('#modal-edit-roles #' + all_roles[item]).prop("checked", true);
        }
    };
    $("#cellphone").blur(function () {
        var url = '/rest/admin/cellphone/person_info';
        if (!$("#cellphone").check().tel()) {
            $("#error").show();
        }
        else {
            $("#error").hide();
        }
        $.ajax({
            url: url,
            type: "post",
            data: {
                cellphone: $("#cellphone").val()
            },
            success: function (data) {
                var html = '';
                if (data['message'] == 'true') {
                    html = '<div class="note note-success" >' +
                        '<p style="form-control">' + '姓名(昵称)：   ' + data['name_info'] + '</p>' +
                        '<input id="add_person_id" type="hidden" value="' + data['person_id'] + '"' + '/>';
                    for (item in data['org_info']) {
                        count = parseInt(item) + 1;
                        html += '<p style="form-control">' + '关联组织(职位)' + count + '：' + data['org_info'][item] + '</p>'
                    }
                    html += '</div>';
                    $("#name_info").html(html);
                    $('#add').attr("disabled", false);
                }
                else {
                    html += '<div class="note note-danger" >' +
                        '<p style="form-control" >' + '此手机号在系统尚未绑定微信号。' + '</p>' +
                        '<p style="form-control" >' + '请先让该手机号用户登录系统，绑定手机号之后进行此操作。' + '</p>' +
                        '</div>';
                    $("#name_info").html(html);
                    $('#add').attr("disabled", true);
                }
            },
            dataType: "json"


        })

    });
    $("#btn_new").click(function () {
        if ($("#add_group_id").val() == undefined) {
            // TODO 这段代码中的组织id和name都是写死，因为暂未确定默认的组织
            var html = '';
            group_name = '<h5 id="add_group_name" >' + '清华大学产业联合会' + '</h5>' +
                '<input id="add_group_id" type="hidden" value="' + '7217ed7f-e485-4ac8-ac9a-4b8027aeb7dd' + '"' + '/>';
            html += group_name;
            $('#add_role_group').html(html);
        }
        $("#error").hide();
        $("#modal-new-admin").modal("show");
    });
    $("#add").click(function () {
        if ($("#add").attr("disabled") == 'disabled') {
            return false
        }
        if (!$("#cellphone").check().tel()) {
            alert("手机号码格式错误");
            return false;
        }
        var checkboxs = $("#check_roles input");
        var check = "";
        for (var i = 0; i < checkboxs.length; i++) {
            if ($(checkboxs[i]).is(":checked")) {
                // check.push($(checkboxs[i]).attr("id"));
                var id = $(checkboxs[i]).attr("id");
                check += id + ',';
            }
        }
        check = check.substring(0, check.length - 1);
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/admin/add',
            data: {
                cellphone: $('#cellphone').val(),
                group_id: $('#add_group_id').val(),
                person_id: $('#add_person_id').val(),
                roles: check,
                _xsrf: $.cookie("_xsrf")
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                window.location.reload();
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });

    $("#edit").click(function () {
        var checkboxs = $("#edit_check_roles input");
        var check = "";
        for (var i = 0; i < checkboxs.length; i++) {
            if ($(checkboxs[i]).is(":checked")) {
                // check.push($(checkboxs[i]).attr("id"));
                var id = $(checkboxs[i]).attr("id");
                check += id + ',';
            }
        }
        check = check.substring(0, check.length - 1);
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/admin/edit/roles',
            data: {
                person_id: $('#admin_person_id').val(),
                group_name: $("#edit_group").val(),
                roles: check,
                _xsrf: $.cookie("_xsrf")
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error || '修改失败！');
                }
                window.location.reload();
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });
    var TableManageResponsive = function () {
        "use strict";
        return {
            init: function () {
                handleDataTableResponsive();
            }
        }
    }();

    TableManageResponsive.init();

    var JsonTree = function (data) {
        var jstree = $("#container");
        jstree.jstree({
            'core': {
                'data': data
            }
        });

    };
    var url;
    url = "/rest/mgr/group/tree";
    $.ajax({
        type: "post",
        url: url,
        dataType: "json",
        success: function (data) {
            JsonTree(data['data']);
        },
        error: function () {
            alert("网络错误")
        }

    });
    $("#container").on('106');
    console.log('%%%%%%%%%%%%%%%%%%%%');
});
var data_reload = function (id) {
    parameter = "&group_id=" + id;
    var url = "/rest/mgr/admin/table?" + parameter + "&_xsrf=" + $.cookie('_xsrf');
    table.ajax.url(url).load();
};


$._clickGroup = function (id) {
    var url = '/res/get/group/info';
    group_id = id;
    $.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        data: {
            'group_id': group_id
        },
        success: function (data) {
            var html = '';
            group_name = '<h5 id="add_group_name" >' + data['group_name'] + '</h5>' +
                '<input id="add_group_id" type="hidden" value="' + group_id + '"' + '/>';
            html += group_name;
            $('#add_role_group').html(html);
            $('#select_group_name').replaceWith('<h4 class="media-heading" id="select_group_name">' + '组织名称：' + data['group_name'] + '</h4>' +
                '<input id="group_name_hidden" type="hidden" value="' + data['group_name'] + '"' + '/>' +
                '<input id="group_id_hidden" type="hidden" value="' + group_id + '"' + '/>');

        }
    });
    data_reload(id)
};