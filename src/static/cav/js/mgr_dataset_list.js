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
                url: '/rest/mgr/dataset/update/status',
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
        $('#modal-link-news-link img').attr('src', '/rest/qrcode?link=' + '/page/article/' + id);
        $('#modal-link-news-link a[target=app_link]').attr('href','/page/article/'+ id);
        $('#modal-link-news-link textarea').val(location.protocol + '//' + location.hostname + '/page/article/'+ id);
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
                "ajax": "/rest/mgr/dataset/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "title"
                }, {
                    "data": "org_name"
                }, {
                    "data": "industry"
                }, {
                    "data": "data_type"
                }, {
                    "data": "connect_person"
                }, {
                    "data": "connect_cellphone"
                }, {
                    "data": "created"
                }, {
                    "data": "status"
                }, {
                    "data": "name"
                }, {
                    "data": "id"
                }],
                "columnDefs": [{
                    "mRender": function(data, something, full) {
                        //  html = '<a class="btn btn-info btn-xs" target="ac_news" onclick=$.show_link_modal("'+full['id']+'") style="margin-left:5px;">' + '详情' + '</a>';
                        var html = '<a class="btn btn-warning btn-xs" style="margin-left:5px;" href="/console/dataset_new?id=' + full['id']+'">' + '修改' + '</a>';
                            html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus(' + full['id'] + ',"deleted") style="margin-left:5px;">' + '删除' + '</a>';
                            if (full['status'] != "已发布")
                                html += '<a class="btn btn-success btn-xs" onclick=$._changeStatus(' + full['id'] + ',"published") style="margin-left:5px;">' + '发布' + '</a>';
                        return html;
                    },
                    "targets": 9
                }],
                "aaSorting": [6, 'desc'],
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
        window.location.href = "/console/dataset_new";
    });
});

