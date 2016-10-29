$(function(){
    // $('#modal-link-person-app textarea').val(location.protocol + '//' + location.hostname + $('#modal-link-person-app textarea').val());
    // $('#modal-link-person-advanced-app textarea').val(location.protocol + '//' + location.hostname + $('#modal-link-person-advanced-app textarea').val());
     $.ajax({
            type: "get",
            url: "/rest/mgr/person/form/info",
            success: function(data) {
               	if(data.length>0)
               	{
               		$("#info").show();
               		$("#info").html("<h4>您正在申请成为"+data[0]['member_type']+", 当前状态为："+data[0]['status']+", 已无法再申请其他选项</h4>");
               	}
               	else
               		$("#info").hide();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
});



