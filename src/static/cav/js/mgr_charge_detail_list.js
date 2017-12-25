$(function() {
    var current_table = null;
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#data-table").length !== 0) {
                current_table = $('#data-table').DataTable({
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
                "ajax": "/rest/mgr/charge/detail/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "code_name"
                }, {
                    "data": "paid_start_time"
                }, {
                    "data": "paid_end_time"
                }, {
                    "data": "paid_money"
                }, {
                    "data": "created"
                },{
                    "data": "member_id",
                    "mRender": function(data, something, full) {
                        var html = "";
                        html =  '<a onclick="$._showMemberDetail(\'' + full.member_id + '\')" class="btn btn-info btn-xs m-r-5">会员详情</a>';
                        return html;
                    }
                }],
                "aaSorting": [5, 'desc'],
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
    $('.datatimerange input').each(function(){
        $(this).mask("9999/99/99");
    });

    $._reloadMgrDataTable = function (){
        current_table.ajax.url("/rest/mgr/charge/detail/table?_xsrf=" + $.cookie('_xsrf') + '&' + $('#mgr-table-filter-form').serialize()).load();
    };
});

