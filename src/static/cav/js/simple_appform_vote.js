$(function() {
    $._vote = function(form_id, attitue) {
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
                if (data.message) {
                    vote_it(form_id, attitue);
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    var vote_it = function(form_id, attitue) {
        $("#modal-reason").modal("show");
        $("#vote").click(function() {
            $.ajax({
                type: "POST",
                cache: false,
                url: '/rest/mgr/vote',
                data: {
                    form_id: form_id,
                    attitue: attitue,
                    reason: $('#reason').val(),
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
    $._bindCellphone = function(person_id) {
        $('#modal-bind-cellphone').modal('show');
        $('#bind').click(function() {
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/cellphone/binder',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    cellphone: $('#bind-cellphone').val(),
                    person_id: person_id,
                    vcode: $('#vcode').val()
                },
                success: function(data) {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
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
    var util = {
        wait: 0,
        hsTime: function(that) {
            _this = $(this);
            if (util.wait <= 0) {
                $('#btn-send-check-code').removeAttr("disabled").text('重发短信验证码');
                util.wait = 0;
            } else {
                var _this = this;
                $(that).attr("disabled", true).text('在' + util.wait + '秒后点此重发');
                util.wait--;
                setTimeout(function() {
                    util.hsTime(that);
                }, 1000)
            }
        }
    };
    // util.hsTime('#btn-send-check-code');
    $("#btn-send-check-code").click(function() {
        if (util.wait > 0) {
            return alert('请稍后再点击发送验证码！');
        }
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/common/person/phone/vcode',
            data: {
                '_xsrf': $.cookie("_xsrf"),
                'phone': $('#bind-cellphone').val()
            },
            success: function(data) {
                if (data.error)
                    alert(data.error);
                else {
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


