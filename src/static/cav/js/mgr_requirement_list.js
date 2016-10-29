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
                url: '/rest/mgr/requirement/update/status',
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

    $.show_link_modal = function(id){
        $('#modal-link-news-link').modal("show");
        $('#modal-link-news-link img').attr('src', '/rest/qrcode?link=' + '/page/requirement/' + id);
        $('#modal-link-news-link a[target=app_link]').attr('href','/page/requirement/'+ id);
        $('#modal-link-news-link textarea').val(location.protocol + '//' + location.hostname + '/page/requirement/'+ id);
    }
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#news_list").length !== 0) {
                $('#news_list').DataTable({
                "responsive": true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
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
                "ajax": "/rest/mgr/requirement/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "title"
                }, {
                    "data": "status"
                }, {
                    "data": "published"
                }, {
                    "data": "updated"
                }, {
                    "data": "contact_name"
                }, {
                    "data": "contact_cellphone"
                }, {
                    "data": "contact_wechatid"
                }, {
                    "data": "name"
                }, {
                    "data": "id"
                }],
                "columnDefs": [{
                    "mRender": function(data, something, full) {
                        var html = '<a class="btn btn-info btn-xs" target="ac_news" onclick=$.show_link_modal("'+full['id']+'") style="margin-left:5px;">' + '详情' + '</a>';
                            html += '<a class="btn btn-warning btn-xs" style="margin-left:5px;" href="/console/requirement_new?id=' + full['id']+'">' + '修改' + '</a>';
                            html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus(' + full['id'] + ',"deleted") style="margin-left:5px;">' + '删除' + '</a>';
                            if (full['status'] == "已保存")
                                html += '<a class="btn btn-success btn-xs" onclick=$._changeStatus(' + full['id'] + ',"published") style="margin-left:5px;">' + '发布' + '</a>';
                            if (full['status'] == "待审核")
                            {
                                html += '<a class="btn btn-success btn-xs" onclick=$._changeStatus(' + full['id'] + ',"published") style="margin-left:5px;">' + '通过并发布' + '</a>';
                                html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus(' + full['id'] + ',"back") style="margin-left:5px;">' + '审核不通过' + '</a>';
                            }
                        return html;
                    },
                    "targets": 8
                }],
                "aaSorting": [3, 'desc'],
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

    $('#btn_new').click(function() {
        window.location.href = "/console/requirement_new";
    });
});

