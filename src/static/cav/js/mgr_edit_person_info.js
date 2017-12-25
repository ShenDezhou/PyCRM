$(function(){
	$("#check_student").click(function(){
		if($('#check_student').is(":checked")) {
			$(".student").show();
        } else {
            $(".student").hide();
        }
	});
    var person_id = getQueryString('person_id');
    console.log('person_id' + person_id);
    $("#person_id").val(person_id);
	$.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/person/edit_detail',
            data: {
                person_id: person_id
            },
            success: function(data) {
                for(item in data['person'][0])
                {
                    $("#"+item).val(data['person'][0][item]);
                    // console.log($("#"+form_id + " input[name='"+item+"']"));
                }
                

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
	$("#save").click(function(){
		if(checkInfo())
		{
			$.ajax({
            type: "post",
            cache: false,
            url: '/page/person/info/edit',
            data:$('#form_info').serialize(),// 你的formid
            dataType:'json',
            success: function(data) {
            	if(data.error)
            		alert(data.error);
            	if(data.message)
            	{
            		location.href = "form_list";
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


 	// $("#birthday").datepicker({
  //       format: 'yyyy-mm-dd'
  //   }).on('changeDate', function(ev) {
  //       $('.datepicker').hide();
  //   });  
  //   $("#school_start").datepicker({
  //       format: 'yyyy-mm-dd'
  //   }).on('changeDate', function(ev) {
  //       $('.datepicker').hide();
  //   }); 
    $("#due_date").mask("9999/99/99");
    $("#birthday").mask("9999/99/99");
    $("#school_start").mask("9999/99/99");

});