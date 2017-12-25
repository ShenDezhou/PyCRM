$(function(){
	$("#check_student").click(function(){
		if($('#check_student').is(":checked")) {
			$(".student").show();
        } else {
            $(".student").hide();
        }
	});
    $._applyToBeAdvanced = function(id){
        if(confirm("您确定申请成为理事会员吗？"))
        {

        $.ajax({
                type: "post",
                cache: false,
                url: '/rest/apply/advanced',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    member_id:id
                },
                success: function(data) {
                    if(data.error)
                        alert(data.error);
                    else
                        window.location.reload(); 
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
                    
        }
    };
	$.ajax({
            type: "get",
            cache: false,
            url: '/rest/common/person',
            success: function(data) {
	                for(item in data['person'])
	                {
	                	$("#"+item).val(data['person'][item]);
	                }
	                for(item in data['org'])
	                {
	                	$("#"+item).val(data['org'][item]);
	                	if(data['org']['is_primary']!=1)
	                	{

	                		$("#"+item).attr("readonly",true);
	                	}
	                }
	                if(data['org']['is_primary']!=1){
						$("#expects").attr("readonly",true);
						$("#wills").attr("readonly",true);
	                };
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
	$._bindCellphone = function(auth_id){
		$('#modal-bind-cellphone').modal('show');
		$('#bind').click(function(){
			$.ajax({
	                type: "post",
	                cache: false,
	                url: '/rest/cellphone/binder',
	                data: {
	                    _xsrf: $.cookie("_xsrf"),
	                    cellphone:$('#cellphone').val(),
	                    auth_id:auth_id,
                        vcode: $('#vcode').val()
	                },
	                success: function(data) {
	                	if(data.error)
	                	{
	                		alert(data.error);
	                		return;
	                	}
	                    alert(data.message);
	                    $('#modal-bind-cellphone').modal('hide'); 
	                    $('#cellphone_info').html($('#cellphone').val());
	                    $('#cellphone').val($('#cellphone').val());
	                    $('#div_person').show(); 
	                    $('#info').hide(); 
	                    if(!data['person_info'])
	                    {
	                    	var controls = $('#div_person input');
	                    	for(var i=0; i< controls.length; i++)
							      controls[i].value='';		
							$("#check_student").attr("checked",false);
		                	$('.student').hide(); 					  
	                    }
	                    else
	                    {
		                    for(item in data['person_info'])
		                    {
		                    	$("#"+item).val(data['person_info'][item]);
		                    }
		                    if(data['person_info']['school_department'])
		                    {
		                    	$("#check_student").attr("checked",true);
		                		$('.student').show(); 
		                    }
		                    else
		                    {
		                    	$("#check_student").attr("checked",false);
		                		$('.student').hide(); 
		                    }

		                    if(data['person_info']['attachment']!='')
	                    		$.initPreviewImageForTicket(data['person_info']['attachment'].split(','));
	                    }
	                    
	                },
	                error: function() {
	                    alert('网络错误！');
	                },
	                dataType: 'json'
	            });
			return false;
		});
	};
	$("#save").click(function(){
		if(checkInfo())
		{
			$.ajax({
            type: "post",
            cache: false,
            url: '/page/member/info/commit',
            data:$('#form_info').serialize(),// 你的formid
            dataType:'json',
            success: function(data) {
            	if(data.error)
            		alert(data.error);
            	if(data.message)
            	{
            		location.href = "/common/articles";
            	}
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
		}
		
	});

	var checkInfo = function(){
		if (!$('#cellphone').check().notNull()) {
            alert("*号标识均为必填项");
            return false;
        }
        if (!$('#cellphone').check().tel()) {
            alert("电话号码格式错误");
            return false;
        }
        return true;
	};


 	$("#birthday").datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function(ev) {
        $('.datepicker').hide();
    });  
    $("#school_start").datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function(ev) {
        $('.datepicker').hide();
    }); 


    var util = {
        wait: 0,
        hsTime: function (that) {
            _this = $(this);
            if (util.wait <= 0) {
                $('#btn-send-check-code').removeAttr("disabled").text('重发短信验证码');
                util.wait = 0;
            } else {
                var _this = this;
                $(that).attr("disabled", true).text('在' + util.wait + '秒后点此重发');
                util.wait--;
                setTimeout(function () {
                    util.hsTime(that);
                }, 1000)
            }
        }
    };
    // util.hsTime('#btn-send-check-code');
    $("#btn-send-check-code").click(function(){
        if(util.wait > 0){
            return alert('请稍后再点击发送验证码！');
        }
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/common/person/phone/vcode',
            data: {
                '_xsrf': $.cookie("_xsrf"),
                'phone': $('#cellphone').val()
            },
            success: function(data) {
                if(data.error)
                    alert(data.error);
                else{
                    alert(data.message);
                }
                
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        util.wait = 90;
        util.hsTime('#btn-send-check-code');
    });


});