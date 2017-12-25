$(function() {
    var current_table = null;
    var type = "add";
    $._changeStatus = function(id) {
        if (confirm("你确定要删除吗？")) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/tag/delete',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    tag_id: id
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

    $.show_edit = function(tag_id,tag_name,tag_type){
       $("#tag_id").val(tag_id);
       $("#tag_name").val(tag_name);
       $("#tag_type").val(tag_type);
       $("#modal-new-tag").modal("show");
    };
    var show_dataTable = function() {
        if (current_table == null) {
            var disVisibleCol = [0];
            current_table = $('#news_list').DataTable({
                responsive: true,
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
                "ajax": "/rest/mgr/tag/table",
                "columns": [{
                    "data": "tag_id"
                }, {
                    "data": "tag_name"
                }, {
                    "data": "tag_type"
                }, {
                    "data": "tag_sort"
                }],
                "columnDefs": [{
                    "mRender": function(data, something, full) {
                        var mapcode = {"article_source":"文章来源","weixin_group":"微信群名","dataset_type":"数据类别","requirement_type":"需求来源"};
                        return mapcode[data];
                    },
                    "targets": 2
                }, {
                    "mRender": function(data, something, full) {
                        var html = '';
                            html += '<a class="btn btn-warning btn-xs" style="margin-left:5px;" onclick=$.show_edit("'+full['tag_id']+'","'+full['tag_name']+'","'+full['tag_type']+'") >' + '修改' + '</a>';
                            html += '<a class="btn btn-inverse btn-xs" onclick=$._changeStatus("' + full['tag_id'] + '") style="margin-left:5px;">' + '删除' + '</a>';
                            return html;
                    },
                    "targets": 3
                }],
                "aaSorting": [2, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            current_table.ajax.url("/rest/mgr/tag/table").load();
        }
    }
    var _init_ = function() {
        show_dataTable();
    }
    _init_();

    $('#btn_new').click(function() {
        type = "add";
        $("#tag_id").val("");
        $("#tag_name").val("");
        $("#tag_type").val("");
        $("#modal-new-tag").modal("show");
    });
    $('#new_submit').click(function(){
         $.ajax({
                type: "POST",
                url: '/rest/mgr/tag/add',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: $("#tag_id").val(),
                    name: $("#tag_name").val(),
                    type: $("#tag_type").find("option:selected").val()
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
         return false;
    });
});

