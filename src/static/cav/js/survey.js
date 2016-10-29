$(function() {
    $('#btn-submit').click(function() {
        $("#btn-submit").attr("disabled",true);
        $.ajax({
            type: "POST",
            cache: false,
            url: $("#submit-form").attr('action'),
            data: $("#submit-form").serialize(),
            success: function(data) {
                $("#btn-submit").attr("disabled",false);
                if(data.error)
                {
                    alert(data.error);
                }
                else
                {
                    alert(data.message || '提交成功！');
                    location.reload()
                }
            },
            error: function() {
                $("#btn-submit").attr("disabled",false);
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });
});
