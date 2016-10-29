$(function() {
    var start_id = $('#list-items li:last-child').attr('data-id') || '';
    var updateMore = function() {
        $('#btn-check-more').hide();
        $.ajax({
            type: "GET",
            cache: false,
            url: '/rest/common/requirements/person',
            data: {
                _xsrf: $.cookie("_xsrf"),
                start_id: start_id
            },
            success: function(data) {
                if (data.items && data.items.length) {
                    if (data.items.length == 10) {
                        $('#btn-check-more').show();
                    }
                    var items = data.items;
                    start_id = items[data.items.length - 1].id;
                    var html = '',
                        tpl = $('#tpl-list-item').html();
                    for (var i = 0; i < items.length; i++) {
                        var n = tpl;
                        for (var k in items[i]) {
                            var reg = new RegExp('\{' + k + '\}', 'igm');
                            var v = items[i][k];
                            if (k == 'pictures') {
                                if (items[i][k]) {
                                    v = '/assets/ticket/image/' + items[i][k].split(',')[0];
                                } else {
                                    v = '/static/cav/img/default-u.png';
                                }
                            } else if (k == 'activity_end_date') {
                                if (items[i]['activity_start_date'] == items[i]['activity_end_date']) {
                                    v = '';
                                }
                            } else if (k == 'general_place') {
                                v = v || '--';
                            }
                            n = n.replace(reg, v);
                        }
                        html += n;
                    }
                    $(html).appendTo($('#list-items'));
                }
            },
            error: function() {
                $('#btn-check-more').show();
            },
            dataType: 'json'
        });
    };
    $._changeStatus = function(id, status) {
        var statu = true;
        if (status == "deleted") {
            statu = confirm("你确定要删除吗？");
        }
        if (statu) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/requirement/update/status',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: id,
                    status: status
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '登录失败！');
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
    $('#btn-check-more').click(updateMore);
    updateMore();
});
