$(function(){
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#data-table").length !== 0) {
            $("#data-table").DataTable({
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
                "ajax": "/rest/mgr/authorized/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "head_img_url",
                    "mRender": function(data, type, full) {
                        return '<img src="' + data + '" style="max-width:60px;border-radius:100px;"/>';
                    }
                }, {
                    "data": "nick_name",
                    "mRender": function(data, type, full) {
                        return '<div id="' + full.auth_id + '">' + data + '</div>';
                    }
                }, {
                    "data": "province",
                    "mRender": function(data, type, full) {
                        return data+"."+full['city'];
                    }

                },{
                    "data": "cellphone"
                    
                },{
                    "data": "member_auth_id",
                    "mRender": function(data, type, full) {
                        if (data != 'None')
                            return "是";
                        else
                            return "否";
                    }
                }, {
                    "data": "auth_date"
                },{
                    "data": "member_id",
                    "mRender": function(data, type, full) {
                        if (data != 'None')
                            return '<a onclick="$._showMemberDetail(\'' + data + '\')" class="btn btn-info btn-xs m-r-5">会员信息</a>';
                        else
                            return "";
                    }
                }],
                // "aoColumnDefs": [{ "bVisible": false, "aTargets": [0]}],
                // "columnDefs": [{
                //     "targets": [1],
                //     "visible": false
                // }],
                "aaSorting": [5, 'desc'],
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



