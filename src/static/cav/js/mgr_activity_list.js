$(function() {
    var current_table = null;
    var sub_table = null;
    var event_id = null;
    var detail_table = null;
    var message = { 'sign_up': '报名', 'register': '签到' }

    var channel_fields = null;
    var init_select = function(type, select_id) {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/get/channel',
            cache: true,
            data: {
                type: type
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                var html = "";
                for (var index = 0; index < data.length; index++) {
                    html += "<option value='" + data[index]['code_id'] + ',' + data[index]['picture'] + "'>" + data[index]['name'] + "</option>";
                }

                $('#' + select_id).html(html);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $._changeStatus = function(id, status) {
        var statu = true;
        if (status == "deleted") {
            statu = confirm("你确定要删除吗？");
        }
        if (statu) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/news/update/status',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: id,
                    status: status
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '登录失败！');
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
    $._changeSignUpStatus = function(id, status) {
        var statu = true;
        $.ajax({
            type: "POST",
            url: '/rest/mgr/news/update/signup/status',
            data: {
                _xsrf: $.cookie("_xsrf"),
                id: id,
                status: status
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                window.location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };

    $._changeAllowSignUpAndRegister = function(id, status) {
        var statu = true;
        $.ajax({
            type: "POST",
            url: '/rest/mgr/news/update/signupandregister/status',
            data: {
                _xsrf: $.cookie("_xsrf"),
                id: id,
                status: status
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                window.location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };

    $.change_qr_src = function(id) {
        src = $("#activity_source").val();
;
        if (src) {
            channel_id = $("#activity_source").val().split(',')[0];
            channel_picture = $("#activity_source").val().split(',')[1];
            qrurl = '/rest/qrcode?link=' + '/page/event/' + id + '?src=' + channel_id + '&iconurl=' + channel_picture;

            $('#activity_qrcode_image').attr('src', qrurl);
            $('#modal-link-activity-link a[target=app_link]').attr('href', '/page/event/' + id + '?src=' + channel_id);
            $('#modal-link-activity-link textarea').val(location.protocol + '//' + location.hostname + '/page/event/' + id + '?src=' + channel_id);

        } else {
            qrurl = '/rest/qrcode?link=' + '/page/event/' + id;
            $('#activity_qrcode_image').attr('src', qrurl);
            $('#modal-link-activity-link a[target=app_link]').attr('href', '/page/event/' + id);
            $('#modal-link-activity-link textarea').val(location.protocol + '//' + location.hostname + '/page/event/' + id);
        }

    }

    $.show_link_modal = function(id, src, title) {
        $('#activity_preview a[target=app_link]').attr('href', '/page/event/' + id);
        $('#activity_title').text(title);
        event_id = id;

        get_channel_fields(id);
        show_qr_dataTable(id,  "qr-data-table");


        init_select("activity_source", "activity_source");


        $('#modal-link-activity-link').modal("show");

        $.change_qr_src(id);

        $('#modal-link-activity-link a[target=qr_link]').attr('href', "javascript:$.change_qr_src(\'" + id + "\')");

    };

    $.show_link_modal_signin = function(id) {
        $('#modal-link-activity-signin-link').modal("show");
        $('#modal-link-activity-signin-link img').attr('src', '/rest/qrcode?link=' + '/page/event/' + id + '%3Fsignin=true');
        $('#modal-link-activity-signin-link a[target=app_link]').attr('href', '/page/event/' + id + '?signin=true');
        $('#modal-link-activity-signin-link textarea').val(location.protocol + '//' + location.hostname + '/page/event/' + id + '?signin=true');
    };
    $.stats_show_detail = function(activity_id, type, title) {
        if (detail_table == null) {
            detail_table = $('#detail_list_table').DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) {
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
                "ajax": "/rest/mgr/activity/sign_up_or_register/table?activity_id=" + activity_id + "&type=" + type,
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "created"
                }],
                "columnDefs": [],
                "aaSorting": [1, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            detail_table.ajax.url("/rest/mgr/activity/sign_up_or_register/table?activity_id=" + activity_id + "&type=" + type).load();
        }
        $('#each_detail_modal').modal("show");
        $('#each_detail_modal .modal-title').html(message[type] + "信息明细");
        $('#each_detail_modal .admin-btn-print').attr('filename', title + message[type] + "列表");
    };

    function getNowFormatDate() {

        // var date = new Date();
        // var seperator1 = "-";
        // var seperator2 = ":";
        // var month = date.getMonth() + 1;
        // var strDate = date.getDate();
        // if (month >= 1 && month <= 9) {
        //     month = "0" + month;
        // }
        // if (strDate >= 0 && strDate <= 9) {
        //     strDate = "0" + strDate;
        // }
        // var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate + " " + date.getHours() + seperator2 + date.getMinutes() + seperator2 + date.getSeconds();
        // console.log(moment(new Date()).format('YYYY-MM-DD hh:mm:ss'));
        return moment(new Date()).format('YYYY-MM-DD hh:mm:ss');
    }
    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;',
        ' ': '&nbsp;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/ ]/g, function(s) {
            return entityMap[s];
        });
    }
    var show_dataTable = function() {
        if (current_table == null) {
            current_table = $('#data-table').DataTable({
                "responsive": true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) {
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
                "ajax": "/rest/mgr/activity/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "title"
                }, {
                    "data": "status",
                    "mRender": function(data, something, full) {
                        var html = "";
                        if (data == '已保存') {
                            html += '<span class="badge badge-primary normal-font">' + data + '</span>';
                        } else if (data == '已发布') {
                            html += '<span class="badge badge-warning normal-font">' + data + '</span>';
                        }
                        html += "<br />";
                        if (full['activity_end_time'] < getNowFormatDate())
                            html += '<span class="badge badge-info normal-font m-t-5">活动结束不可报名</span>';
                        else if (full['sign_up_limit'] == 0)
                            html += '<span class="badge badge-danger normal-font m-t-5">正常报名</span>';
                        else if (full['sign_up_limit'] == 1)
                            html += '<span class="badge badge-inverst normal-font m-t-5">截止报名</span>';
                        return html;

                    }
                }, {
                    "data": "sign_up",
                    "mRender": function(data, something, full) {
                        var html = '<a class="btn btn-info btn-xs m-r-3" href="/console/sign_up_list?activity=' + full['id'] + '">' + data + '<i class="fa fa-fw fa-search"></i></a>';
                        if (full.sur_id) {
                            html += '<a class="btn btn-default btn-xs" target="_blank" href="/console/survey_result?id=' + full['sur_id'] + '">' + '表单' + '<i class="fa fa-fw fa-search"></i></a>'
                        }
                        return html;

                    }
                }, {
                    "data": "register",
                    "mRender": function(data, something, full) {
                        var html = '<a class="btn btn-warning btn-xs" href="/console/register_list?activity=' + full['id'] + '">' + data + '<i class="fa fa-fw fa-search"></i></a>';
                        return html;

                    }
                }, {
                    "data": "visits",
                    "mRender": function(data, something, full) {
                        var html = '<a class="btn btn-default btn-xs" href="/console/activity_visit_list?activity=' + full['id'] + '">' + data + '<i class="fa fa-fw fa-search"></i></a>';
                        return html;

                    }
                }, {
                    "data": "activity_start_time"
                }, {
                    "data": "activity_end_time"
                }, {
                    "data": "activity_place"
                }, {
                    "data": "activity_online_offline"
                }, {
                    "data": "activity_type"
                }, {
                    "data": "paid",
                    "mRender": function(data, something, full) {

                        if (data == 0)
                            return '免费';
                        else
                            return data;
                    }
                }, {
                    "data": "name"
                }, {
                    "data": "id",
                    "mRender": function(data, something, full) {

                        var html = '<a class="btn btn-info btn-xs" target="ac_news" href="/page/event/' + full['id'] + '") style="margin-left:5px;">' + '预览' + '</a>';
                        html += '<a class="btn btn-info btn-xs" target="ac_news" onclick=$.show_link_modal("' + full['id'] + '","","' + escapeHtml(full['title']) + '") style="margin-left:5px;">' + '渠道' + '</a>';
                        html += '<a class="btn btn-warning btn-xs" style="margin-left:5px;" href="/console/activity_new?id=' + full['id'] + '">' + '修改' + '</a>';
                        html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus(' + full['id'] + ',"deleted") style="margin-left:5px;">' + '删除' + '</a>';
                        if (full['status'] != "已发布")
                            html += '<a class="btn btn-success btn-xs" onclick=$._changeStatus(' + full['id'] + ',"published") style="margin-left:5px;">' + '发布' + '</a>';
                        if (full['activity_end_time'] < getNowFormatDate())
                            html += '';
                        else if (full['sign_up_limit'] == 0)
                            html += '<a class="btn btn-warning btn-xs" onclick=$._changeSignUpStatus(' + full['id'] + ',1) style="margin-left:5px;">' + '停止报名' + '</a>';
                        else if (full['sign_up_limit'] == 1)
                            html += '<a class="btn btn-warning btn-xs" onclick=$._changeSignUpStatus(' + full['id'] + ',0) style="margin-left:5px;">' + '开始报名' + '</a>';
                        if (full['allow_onsite_checkin'] == 0)
                            html += '<a class="btn btn-warning btn-xs" onclick=$._changeAllowSignUpAndRegister(' + full['id'] + ',1) style="margin-left:5px;">' + '开放签到' + '</a>';
                        else if (full['allow_onsite_checkin'] == 1)
                            html += '<a class="btn btn-warning btn-xs" onclick=$._changeAllowSignUpAndRegister(' + full['id'] + ',0) style="margin-left:5px;">' + '停止开放签到' + '</a>';
                        html += '<a class="btn btn-info btn-xs" target="ac_news" onclick=$.show_link_modal_signin("' + full['id'] + '") style="margin-left:5px;">' + '签到链接' + '</a>';
                        return html;
                    }
                }],

                "aaSorting": [5, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            current_table.ajax.url("/rest/mgr/activity/table?type=activity").load();
        }

    }
    var get_channel_fields = function(id) {

        $.ajax({
            type: "GET",
            url: '/rest/mgr/news/detail',
            cache: false,
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                data = data[0];
                channel_fields = data['channel_fields'];
            },
            error: function() {
                channel_fields = null;
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    var show_qr_dataTable = function(id, data_table_id) {
        if(sub_table!=null)
        {
            sub_table.row().remove();
            sub_table.destroy();
            sub_table = null;
        }
        if (sub_table == null) {
            sub_table = $('#' + data_table_id).DataTable({
                "responsive": true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) {
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
                "ajax": "/rest/mgr/get/channelinfo",
                "columns": [{
                    "data": "name"
                }, {
                    "data": "picture",
                    "mRender": function(data, something, full) {
                        var qrurl = '/rest/qrcode?link=' + '/page/event/' + id + '?src=' + full["code_id"] + '&iconurl=' + full["picture"];
                        var html = '<img style="width:100%;max-width:350px;" src="' + qrurl + '">';
                        return html;
                    }
                }, {
                    "data": "code_id",
                    "mRender": function(data, something, full) {
                        var html = '<p class="text-info">' + location.protocol + '//' + location.hostname + '/page/event/' + id + '?src=' + data + '</p>';
                        return html;
                    }
                }, {
                    "data": "code_id",
                    "mRender": function(data, something, full) {
                        var html = "";
                        if (channel_fields && channel_fields.match(full['code_id']))
                            html += '<div class="checkbox m-r-10"><label><input id="' + full['code_id'] + '" type="checkbox" data-render="switchery" data-theme="default" checked>选择渠道</label></div>';
                        else
                            html += '<div class="checkbox m-r-10"><label><input id="' + full['code_id'] + '" type="checkbox" data-render="switchery" data-theme="default" >选择渠道</label></div>';
                        return html;
                    }
                }],

                "aaSorting": [0, 'desc'],
                "language": TABLE_LANG
            });


        } else {

            sub_table.ajax.url("/rest/mgr/get/channelinfo").load();
        }
    }
    var getAllCheckIds = function() {
        var ids = "";
        $("#qr-data-table input:checkbox").each(function() {
            if ($(this).is(":checked")) {
                ids += $(this).attr('id') + ',';
            }
        });
        return ids.substring(0, ids.length - 1);
    };

    $("#save").click(function() {
        $.ajax({
            type: "POST",
            url: '/rest/mgr/news/edit/channel',
            data: {
                _xsrf: $.cookie("_xsrf"),
                id: event_id,
                channel_fields: getAllCheckIds()
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                location.href = "/console/activity_list";
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });



    var _init_ = function() {
        show_dataTable();

    }
    _init_();



    $('#btn_new').click(function() {
        window.location.href = "/console/activity_new";
    });
});
