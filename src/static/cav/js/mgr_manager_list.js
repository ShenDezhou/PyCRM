$(function(){
    var handleDataTableResponsive = function() {
        "use strict";
        // var rolesMap = {'admin':'超级管理员','operator':'事务性管理员','master':'秘书处管理员', 'requirement': '需求对接管理员'};
        if ($("#data-table").length !== 0) {
            $("#data-table").DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": false,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) { return load_dt_view(oSettings); },
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
                    "mRender": function(data, type, full) {
                        return '<img src="' + data + '" style="max-width:60px;border-radius:100px;"/>';
                    }
                }, {
                    "data": "nick_name",
                    "mRender": function(data, type, full) {
                        return '<div id="' + full.person_id + '">' + data + '</div>';
                    }
                }, {
                    "data": "province",
                    "mRender": function(data, type, full) {
                        return data + '.' + full.city;
                    }
                },{
                    "data": "member_auth_id",
                    "mRender": function(data, type, full) {
                        if (data)
                            return "是";
                        else
                            return "否";
                    }
                }, {
                    "data": "auth_date"
                }, {
                    "data": "roles",
                    "mRender": function(data, type, full) {
                        return full.role_names;
                    }
                },{
                    "data": "member_id",
                    "mRender": function(data, type, full) {
                        var html ="";
                        if (data)
                            html += '<a onclick="$._showMemberDetail(\'' + data + '\')" class="btn btn-info btn-xs m-r-5">会员信息</a>'
                        else
                            html = html;
                        if($('#person_roles').val().indexOf("admin")>=0)
                        {
                            html += '<a onclick="$._editRoles(\'' + full['nick_name'] + '\',\'' + full['person_id'] + '\',\'' + full['roles'] + '\')" class="btn btn-warning btn-xs m-r-5">修改权限</a>';
                            html += '<a onclick="$._deleteAdmin(\'' + full['person_id'] + '\')" class="btn btn-inverse btn-xs m-r-5">删除</a>';
                        }
                        return html;
                    }
                }],
                "aaSorting": [4, 'desc'],
                "language": TABLE_LANG
            })
        }
    };
    $._deleteAdmin = function(person_id){
         if (confirm("你确定要删除该管理员吗?")) {
                $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/admin/delete',
                data: {
                    person_id: person_id,
                    _xsrf: $.cookie("_xsrf")
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '删除失败！');
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
         }
    };
    $._editRoles = function(nick_name,person_id,roles){
        $("#modal-edit-roles").modal("show");
        $('#nick_name').val(nick_name);
        $('#person_id').val(person_id);
        var checkboxs = $("#edit_check_roles input");
        var check = "";
        for (var i = 0; i < checkboxs.length; i++) {
            $(checkboxs[i]).prop("checked", false);
        }
        var all_roles = roles.split(',');
        for(var item in all_roles)
        {
            $('#modal-edit-roles #' + all_roles[item]).prop("checked", true);
        }
    };
    $("#btn_new").click(function(){
        $("#modal-new-admin").modal("show");
    });
    $("#add").click(function(){
        if(!$("#cellphone").check().tel()){
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
                    roles:check,
                    _xsrf: $.cookie("_xsrf")
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '添加失败！');
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        return false;
    });
    
    $("#edit").click(function(){
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
                    person_id: $('#person_id').val(),
                    roles:check,
                    _xsrf: $.cookie("_xsrf")
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '修改失败！');
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        return false;
    });
    var TableManageResponsive = function() {
        "use strict";
        return {
            init: function() {
                handleDataTableResponsive();
            }
        }
    }();

    TableManageResponsive.init();
});



