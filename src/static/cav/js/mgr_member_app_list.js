$(function(){
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#data-table").length !== 0) {
            $("#data-table").DataTable({
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
                "ajax": "/rest/mgr/member/person/app/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "type"
                }, {
                    "data": "status"
                }, {
                    "data": "cellphone"
                }, {
                    "data": "email"
                }],
                "aaSorting": [4, 'desc'],
                "columnDefs": [{
                    "mRender": function(data, type, full) {
                        return '<div class="row">' + 
                                    '<div class="col-xs-5">' +
                                        '<img style="width:100%;max-width:80px;border-radius:100px;" src="' + (full.head_img_url || 'http://wx.qlogo.cn/mmopen/2kpMNDYsSfDrf9ZwO6wVUYSZlwgZUqC9yZxgrP8oR6aR91sXKUoUfWlFkwm8oW5hL7hoiaxlWqA5a4r6YXvlUWQ/0') + '"/>' + 
                                    '</div>' +
                                    '<div class="col-xs-7">' +
                                        full.fullname + ' (' + (full.title || '职称无') + ')' + '<br/>' + 
                                        (full.company || '公司无') + 
                                    '</div>' +
                                '</div>';
                    },
                    "targets": 0
                },{
                    "mRender": function(data, type, full) {
                        if(data == 'advanced'){
                            return '<span class="badge badge-warning normal-font">' + full.member_type + '</span>';
                        }else if(data == 'normal'){
                            return '<span class="badge badge-primary normal-font">' + full.member_type + '</span>';
                        }else{
                            return '<span class="badge badge-info normal-font">' + full.member_type + '</span>';
                        }
                    },
                    "targets": 1
                },{
                    "mRender": function(data, type, full) {
                        var html = '';
                        if(data == 'valid'){
                            html = '<span class="badge badge-primary normal-font">' + full.member_status + '</span>';
                        }else if(data == 'overdue'){
                            html = '<span class="badge badge-danger normal-font">' + full.member_status + '</span>';
                        }else{
                            html = '<span class="badge badge-info normal-font">' + full.member_status + '</span>';
                        }
                        return '<p>'  + html + '</p><small> 有效期至:' + (full.due_date || '暂无') + '</small>';
                    },
                    "targets": 2
                },{
                    "mRender": function(data, type, full) {
                        return '<p>电话: ' + full.cellphone + '<br/>' + 
                                '邮箱: ' + full.email + '</p>';
                    },
                    "targets": 3
                },{
                    "mRender": function(data, type, full) {
                        return '<a href="javascript:;" class="btn btn-info btn-xs m-r-5">详情</a>' + 
                                '<a href="javascript:;" class="btn btn-primary btn-xs m-r-5">投票</a>' + 
                                '<a href="javascript:;" class="btn btn-warning btn-xs m-r-5">缴费</a>' + 
                                '<a href="javascript:;" class="btn btn-success btn-xs m-r-5">更多</a>';
                    },
                    "targets": 4
                }],
                "language": TABLE_LANG
            })
        }
    };
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



