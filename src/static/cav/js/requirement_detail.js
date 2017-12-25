$(function() {
    $("#save").click(function() {
        $.ajax({
            type: "POST",
            url: '/rest/requirement/comments/commit',
            cache: false,
            data: {
                comments: $("#comments").val(),
                requirement_id: $("#requirement_id").val()
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                // alert(data.message);
                location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });
    $._deleteComment = function(id) {
        if (confirm("你确定要删除该回复吗？")) {
            $.ajax({
                type: "POST",
                url: '/rest/requirement/comments/delete',
                cache: false,
                data: {
                    id: id
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '失败！');
                    }
                    // alert(data.message);
                    location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        }

    };

});
