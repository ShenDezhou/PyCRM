$(function() {
    var current_table = null;
    $._changeStatus = function(id, status) {
        var statu = true;
        if (status == "deleted") {
            statu = confirm("你确定要删除吗？");
        }
        if (statu) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/survey/update/status',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: id,
                    status: status
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '失败！');
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

    $.show_link_modal = function(id) {
        $('#modal-link-news-link').modal("show");
        $('#modal-link-news-link img').attr('src', '/rest/qrcode?link=' + '/page/survey/' + id);
        $('#modal-link-news-link a[target=app_link]').attr('href', '/page/survey/' + id);
        $('#modal-link-news-link textarea').val(location.protocol + '//' + location.hostname + '/page/survey/' + id);
    }
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#news_list").length !== 0) {
            $('#news_list').DataTable({
                "responsive": false,
                "dom": 'B<"clear">frtip',
                "processing": true,
                "serverSide": false,
                "searching": true,
                "iDisplayLength": 20,
                buttons: [
                    { extend: "copy", className: "btn-sm btn-info" }, 
                    { extend: "csv", className: "btn-sm btn-info"}, 
                    { extend: "excel", className: "btn-sm btn-info" }, 
                    { extend: "pdf", className: "btn-sm btn-info" }, 
                    { extend: "print", className: "btn-sm btn-info" }
                ],
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls",
                        sCharSet: 'utf8', 
                        bBomInc: true
                    }]
                },
                "aaSorting": [1, 'desc'],
                "language": TABLE_LANG
            });
        }
    }

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