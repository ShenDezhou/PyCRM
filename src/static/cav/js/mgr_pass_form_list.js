$(function(){
    $._showFormVote = function(id){
        $('#modal-link-form-vote').modal('show');
        $('#modal-link-form-vote img').attr('src', '/rest/qrcode?link=' + '/page/form_vote_' + id);
        $('#modal-link-form-vote a[target=app_link]').attr('href', '/page/form_vote_' + id);
        $('#modal-link-form-vote textarea').val(location.protocol + '//' + location.hostname + '/page/form_vote_' + id);
    };
    function getNowFormatDate(year,month,day) {
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var year = date.getFullYear()+year;
        var month = date.getMonth() + 1+month;
        var strDate = date.getDate()+day;
        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = year + seperator1 + month + seperator1 + strDate;
        return currentdate;
    };
    $._showFormPaid = function(id,apply_member_type){
        $('#modal-link-form-paid').modal('show');
        $('#modal-link-form-paid img').attr('src', '/rest/qrcode?link=' + '/page/form_paid_' + id);
        $('#modal-link-form-paid a[target=app_link]').attr('href', '/page/form_paid_' + id);
        $('#modal-link-form-paid textarea').val(location.protocol + '//' + location.hostname + '/page/form_paid_' + id);
        $('#modal-link-form-paid a[target=app_paid]').click(function() {
            if($('#roles').val().indexOf('operator')<0)
            {
                alert("您非事务性管理员，无该操作权限");
                return false;
            }
            $('#modal-offline-paid').modal('show');
            $('#start_time').val(getNowFormatDate(0,0,0));
            $('#end_time').val(getNowFormatDate(1,0,0));    
            if (apply_member_type=='normal_member')
                $('#paid_money').val(500);
            else if(apply_member_type=='advanced_member')
                $('#paid_money').val(10000);
            else if(apply_member_type=='normal_org_member')
                $('#paid_money').val(2000);
            else if(apply_member_type=='advanced_org_member')
                $('#paid_money').val(20000);   
            return false;
        });
       
        $('#paid').click(function(){
             $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/form/paid',
                data: {
                    form_id: id,
                     _xsrf:$.cookie("_xsrf"),
                    start_time:$('#start_time').val(),
                    end_time:$('#end_time').val(),
                    paid_money:$('#paid_money').val(),
                    paid_number:$('#paid_number').val(),
                    paid_type:'offline',
                    paid_pictures:$('#upload-images').val()
                },
                success: function(data) {
                    $('#modal-offline-paid').modal('hide'); 
                    $('#modal-link-form-paid').modal('hide');
                    window.location.reload(); 
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
             return false;
        });
    };
    $._deleteForm = function(id){
         if (confirm("你确定要删除该申请吗?")) {
             $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/form/delete',
            data: {
                form_id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '删除失败！');
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
    $._examineForm = function(id){
        $('#examine-modal').modal("show");
        var form_id = id ;
        $('#pass').click(function(){
            examine(form_id,"voting");
        });
        $('#not_pass').click(function(){
            examine(form_id,"reviewed_failed");
        });
    };
    var examine = function(id,status){
        $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/form/examine',
                data: {
                    form_id: id,
                    status:status,
                    _xsrf: $.cookie("_xsrf")
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '删除失败！');
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
    }
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
                "ajax": "/rest/mgr/pass/form/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "form_code",
                    "mRender": function(data, type, full) {
                        return '<a onclick="$._showFormDetail(\'' + full.form_id + '\')" class="btn btn-xs btn-link">' + data + '</a>';
                    }
                }, {
                    "data": "apply_member_type",
                    "mRender": function(data, type, full) {
                        if(data == 'advanced_member'){
                            return '<span class="badge badge-warning normal-font">' + full.apply_member_type_name + '</span>';
                        }else if(data == 'normal_member'){
                            return '<span class="badge badge-primary normal-font">' + full.apply_member_type_name + '</span>';
                        }else if(data == 'advanced_org_member'){
                            return '<span class="badge badge-danger normal-font">' + full.apply_member_type_name + '</span>';
                        }else if(data == 'normal_org_member'){
                            return '<span class="badge badge-success normal-font">' + full.apply_member_type_name + '</span>';
                        }else{
                            return '<span class="badge badge-info normal-font">' + full.apply_member_type_name + '</span>';
                        }
                    }
                }, {
                    "data": "org_name",
                    "mRender": function(data, type, full) {
                        return '<p>' + '公司: ' + full.org_name + '</p>'+
                        '<p>' + '第一申请人: ' + full.fullname + '</p>';
                    }
                }, {
                    "data": "apply_date"
                }, {
                    "data": "vote_start_time",
                    "mRender": function(data, type, full) {
                        if(full.form_status=='voting')
                            return '<p>'+ full.form_status_name + '</p>'+
                        '<p>' + '开始时间：' + full.vote_start_time + '</p>';
                        else
                            return full.form_status_name;
                    }
                }, {
                    "data": "form_id",
                    "mRender": function(data, type, full) {
                        var html = "";
                        html += '<a onclick="$._deleteForm(\'' + full.form_id + '\')" class="btn btn-xs btn-inverse m-l-5">删除</a>';
                        return html;
                    }
                }],
                "aaSorting": [3, 'desc'],
                "language": TABLE_LANG
            })
        }
    };
    $._showDeliveryInfo = function(id){
        $('#modal-link-delivery-info').modal('show');
        $('#modal-link-delivery-info img').attr('src', '/rest/qrcode?link=' + '/page/delivery_info_' + id);
        $('#modal-link-delivery-info a[target=app_link]').attr('href', '/page/delivery_info_' + id);
        $('#modal-link-delivery-info textarea').val(location.protocol + '//' + location.hostname + '/page/delivery_info_' + id);
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



