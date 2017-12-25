$(function(){
    var vote_list = null;
    var handleVoteTableResponsive = function(form_id) {
        "use strict";
        if ($("#vote_list").length !== 0 && vote_list==null) {
            vote_list = $("#vote_list").DataTable({
                responsive: true,
                "dom": 'tip',
                "processing": true,
                "serverSide": true,
                "searching": false,
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
                "ajax": "/rest/mgr/vote/detail/table?form_id="+form_id+"&_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "attitue"
                }, {
                    "data": "create_time"
                }, {
                    "data": "message"
                }],
                "aaSorting": [3, 'desc'],
                "language": TABLE_LANG
            })
        }
        else
        {
            vote_list.ajax.url("/rest/mgr/vote/detail/table?form_id="+form_id+"&_xsrf=" + $.cookie('_xsrf')).load();
        }
    };
    $._showVoteDetail = function(form_id){
        $('#modal-vote-detail').modal("show");
        handleVoteTableResponsive(form_id);
    };
});