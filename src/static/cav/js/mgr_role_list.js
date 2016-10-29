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
                "ajax": "/rest/mgr/roles/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "role_id"
                }, {
                    "data": "role_name"
                },{
                    "data": "role_pages",
                    "mRender": function(data, type, full) {
                        var html ="";
                        if(full.role_id != 'admin')
                            html += '<a onclick="$._editRole(\'' + full['role_id'] + '\',\'' + full['role_name'] + '\',\'' + full['role_pages'] + '\')" class="btn btn-warning btn-xs m-r-5">修改授权页面</a>';
                        return html;
                    }
                }],
                "language": TABLE_LANG
            })
        }
    };
    $._editRole = function(role_id, role_name, pages){
        $("#modal-edit-roles").modal("show");
        $("#modal-edit-roles #role_id").val(role_id);
        $("#modal-edit-roles #role_name").val(role_name);
        var checkboxs = $("#edit_check_roles input");
        var check = "";
        for (var i = 0; i < checkboxs.length; i++) {
            $(checkboxs[i]).prop("checked", false);
        }
        var all_pages = pages.split(',');
        for(var item in all_pages)
        {
            $('#modal-edit-roles #' + all_pages[item]).prop("checked", true);
        }
    };

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
                url: '/rest/mgr/roles/edit/pages',
                data: {
                    role_id: $("#modal-edit-roles #role_id").val(),
                    pages: check,
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



