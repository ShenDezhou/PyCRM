$(function(){
	$._editPaidInfo = function(id,apply_member_type){
        var form_id = '';
        $('#modal-link-paid-info').modal('show');
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/paid/detail',
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                var output = "<tr><td>会员起始时间</td><td>会员有效期至</td><td>付费金额</td><td>付费号码</td><td>付费方式</td><td>备注</td><td>操作</td></tr>";;
                for(var index in data)
                {
                    output += "<tr><td>"+data[index]['paid_start_time']+"</td><td>"+data[index]['paid_end_time']+"</td><td>"+data[index]['paid_money']+"</td><td>"+data[index]['paid_number']+"</td><td>"+data[index]['paid_type']+"</td><td>"+data[index]['paid_remark'];
                    if (index != data.length -1 )
                        output += '</td><td><a onclick="$._deletePrePaid(\'' + data[index]['id'] + '\')" class="btn btn-danger btn-xs m-l-5">删除</a></td></tr>';
                    else
                        output += '</td><td><a onclick="$._editLastPaid(\'' + data[index]['id'] + '\')" class="btn btn-inverse btn-xs m-l-5">修改</a></td></tr>';
                }
                // var form_id_html = '<input '+'value="'+data[0]['form_id']+'"' +' type="hidden"'+'>';
                form_id = data[0]['form_id'];
                console.log(form_id);

                $('#paid_history_table tbody').html(output);

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        $('#modal-paid').click(function(){
            $._showFormPaid(form_id,apply_member_type);
        });
    };

    $._showFormPaid = function(form_id,apply_member_type){
        $('#modal-link-form-paid').modal('show');
        $('#modal-link-form-paid img').attr('src', '/rest/qrcode?link=' + '/page/form_paid_' + form_id);
        $('#modal-link-form-paid a[target=app_link]').attr('href', '/page/form_paid_' + form_id);
        $('#modal-link-form-paid textarea').val(location.protocol + '//' + location.hostname + '/page/form_paid_' + form_id);
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
                    form_id: form_id,
                    _xsrf:$.cookie("_xsrf"),
                    start_time:$('#start_time').val(),
                    end_time:$('#end_time').val(),
                    paid_money:$('#paid_money').val(),
                    paid_number:$('#paid_number').val(),
                    paid_type:'offline',
                    paid_pictures:$('#upload-images').val(),
                    paid_remark:$('#paid_remark').val()
                },
                success: function(data) {
                    if(data.error)
                    {
                        alert(data.error);
                        return;
                    }
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

    $._editLastPaid = function(id){
    	$.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/paid/id',
            data: {
                id: id
            },
            success: function(item) {
                if (item.error) {
                    return alert(item.error);
                }
                var id = item['id'];
                $('#modal-offline-paid').modal('show');
		    	$('#start_time').val(item['paid_start_time']);  
		        $('#end_time').val(item['paid_end_time']);
		        $('#paid_money').val(item['paid_money']);
		        $('#paid_number').val(item['paid_number']);
                $('#paid_remark').val(item['paid_remark']);
		        if(item['paid_pictures'])
		        {
		        	$.initPreviewImageForTicket(item['paid_pictures'].split(','));
		        }
		        $('#paid').click(function(){
		             $.ajax({
		                type: "post",
		                cache: false,
		                url: '/rest/mgr/form/paid/edit',
		                data: {
		                    id: id,
		                    _xsrf:$.cookie("_xsrf"),
		                    start_time:$('#start_time').val(),
		                    end_time:$('#end_time').val(),
		                    paid_money:$('#paid_money').val(),
		                    paid_number:$('#paid_number').val(),
		                    paid_type:'offline',
		                    paid_pictures:$('#upload-images').val(),
                            paid_remark:$('#paid_remark').val()
		                },
		                success: function(data) {
		                    if(data.error)
		                    {
		                        alert(data.error);
		                        return;
		                    }
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

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    	
    };

    $._deletePrePaid = function(id){
        if(confirm("你确定要删除该条缴费记录吗"))
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/paid/delete',
            data: {
                id: id,
                _xsrf:$.cookie("_xsrf")
            },
            success: function(item) {
                if (item.error) {
                    return alert(item.error);
                }
                window.location.reload(); 
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
});