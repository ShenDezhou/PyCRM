$(function() {
    var current_table = null;
    var detail_table = null;
    var message = { 'sign_up': '报名', 'register': '签到' }

    $._changeStatus = function(id, status) {
        var statu = true;
        if (status == "deleted") {
            statu = confirm("你确定要删除吗？");
        }
        if (statu) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/channel/update/status',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: id
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
                id: id
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
        if (src) {
            qrurl = '/rest/qrcode?link=' + '/page/event/' + id + '?src=' + $("#activity_source").val()
            imageFileName = $('#upload-image-previews img').attr('src');
            if (imageFileName) {
                picname = imageFileName.substr(imageFileName.lastIndexOf("/") + 1)
                qrurl = qrurl + '&iconurl=' + picname
            }
            $('#activity_qrcode_image').attr('src', qrurl);
            $('#modal-link-activity-link a[target=app_link]').attr('href', '/page/event/' + id + '?src=' + $("#activity_source").val());
            $('#modal-link-activity-link textarea').val(location.protocol + '//' + location.hostname + '/page/event/' + id + '?src=' + $("#activity_source").val());

        } else {
            qrurl = '/rest/qrcode?link=' + '/page/event/' + id;
            $('#activity_qrcode_image').attr('src', qrurl);
            $('#modal-link-activity-link a[target=app_link]').attr('href', '/page/event/' + id);
            $('#modal-link-activity-link textarea').val(location.protocol + '//' + location.hostname + '/page/event/' + id);
        }

    }

    $.show_link_modal = function(id, src) {
        $('#activity_source').select2({
            theme: "classic"
        });


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
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var month = date.getMonth() + 1;
        var strDate = date.getDate();
        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate + " " + date.getHours() + seperator2 + date.getMinutes() + seperator2 + date.getSeconds();
        return currentdate;
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
                "ajax": "/rest/mgr/get/channelinfo",
                "columns": [ {
                    "data": "name"
                }, {
                    "data": "picture",
                    "mRender": function(data, something, full) {
                        var html = '<img src="' +  $.get_file_url(data, "/assets/ticket/image/") + '">';
                        return html;

                    }
                },{
                    "data": "code_id",
                    "mRender": function(data, something, full) {
                        var html = '<a class="btn btn-warning btn-xs" style="margin-left:5px;" href="/console/channel_new?id=' + data + '">' + '修改' + '</a>';
                        html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus("' + data + '","deleted") style="margin-left:5px;">' + '删除' + '</a>';
                        return html;
                    }
                }],

                "aaSorting": [1, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            current_table.ajax.url("/rest/mgr/get/channelinfo").load();
        }

    }

    var _init_ = function() {
        show_dataTable();

    }
    _init_();


    $('#btn_new').click(function() {
        window.location.href = "/console/channel_new";
    });
});
