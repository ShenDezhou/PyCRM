$(function(){
	$._vote= function(form_id,attitue){
        // vote_it(form_id,attitue);
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/check/vote/role',
            data: {
                form_id: form_id,
                _xsrf: $.cookie("_xsrf")
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                if(data.message){
                    vote_it(form_id,attitue);
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
	};
    var vote_it = function(form_id,attitue){
        $("#modal-reason").modal("show");
        $("#vote").click(function(){
            $.ajax({
            type: "POST",
            cache: false,
            url: '/rest/mgr/vote',
            data: {
                form_id: form_id,
                attitue:attitue,
                reason:$('#reason').val(),
                _xsrf: $.cookie("_xsrf")
            },
            success: function(data) {
                if (data.error) {
                     window.location.reload();
                    return alert(data.error);
                }
                window.location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        });
    };
});