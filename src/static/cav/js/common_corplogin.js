$(function() {
    var generate = function() {
        $.ajax({
            type: "GET",
            cache: false,
            url: '/rest/check_code_scanned',
            data: {
                
            },
            success: function(data) {
                console.log(data);
                if(data.message=="登录成功")
                {
                    clearInterval(refreshIntervalId);
                    top.window.location.href = data.url;
                }
                if(data.error)
                {
                    // alert(data.error);
                    clearInterval(refreshIntervalId);
                    location.reload();
                }

            },
            error: function(data) {
                console.log(data);
                alert('网络错误！');
                clearInterval(refreshIntervalId);
                top.window.location.reload();
            },
            dataType: 'json'
        });
    };
    var refreshIntervalId = setInterval(generate, 3000);


});
