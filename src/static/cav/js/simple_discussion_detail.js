$(function() {
    var source = getQueryString('src');
    $("#source").val(source);
    $._quitData = function(activity_id) {
        var postData = {
            _xsrf: $.cookie("_xsrf"),
            activity_id: activity_id
        };
        if (confirm("你确定要取消报名吗?")) {

            $.ajax({
                type: "POST",
                url: '/rest/discussion/quit/register',
                data: postData,
                success: function(data) {
                     // window.location.href =location.href.substring(0,location.href.indexOf('?signin=true'));
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });

        }
    };
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

    $._bindCellphone = function(person_id){
        $('#modal-bind-cellphone').modal('show');
        $('#bind').click(function(){
            $.ajax({
                    type: "post",
                    cache: false,
                    url: '/rest/cellphone/binder',
                    data: {
                        _xsrf: $.cookie("_xsrf"),
                        cellphone:$('#cellphone').val(),
                        person_id:person_id,
                        vcode: $('#vcode').val()
                    },
                    success: function(data) {
                        if(data.error)
                        {
                            alert(data.error);
                            return;
                        }
                        $('#cellphone_info').text($('#cellphone').val());
                        $('#modal-bind-cellphone').modal('hide');
                    },
                    error: function() {
                        alert('网络错误！');
                    },
                    dataType: 'json'
                });
            return false;
        });
    };
    var addExtraOptions = function(){
        var d = eval('(' + $('.event-options').html() + ')');
        var html = "";
        if(d.length){
            for(var i = 0; i < d.length; i++){
                var r = '';
                if(d[i].type == 'select'){
                    for(var j = 0; j < d[i].options.length; j++){
                        r += '<option value="' + d[i].options[j].value + '">' + d[i].options[j].name + "</option>";
                    }
                    r = '<div class="form-group"><label class="col-md-4 control-label">' + d[i].name + '</label>' + 
                                    '<div class="col-md-8"><select class="form-control">' + 
                                    r +
                                    '</select></div></div>';
                }else if(d[i].type == 'checkbox'){
                    for(var j = 0; j < d[i].options.length; j++){
                        r += '<div class="checkbox"><label><input type="checkbox" value="' + d[i].options[j].value + '">' + d[i].options[j].name + '</label></div>';
                    }
                    r = '<div class="form-group event-checkbox"><label class="col-md-4 control-label">' + d[i].name + '</label>' + 
                                    '<div class="col-md-8"><div class="">' + 
                                    r +
                                    '</div></div></div>';
                }
                html += r;
            }
        }
        $('#form-extra-options').html(html);
    };
    var getExtraOptions = function(){
        var values = [];
        $('#form-extra-options select,#form-extra-options input:checkbox:checked').each(function(){
            if($(this).val()){
                values.push($(this).val());
            }
        });
        return values.join(',');
    };
    $._showSignUpModal = function(item_type, activity_id){
        $('#modal-sign-up-form').modal('show');
        try{
            addExtraOptions();
        }catch(e){}
    };
    $._postData = function(item_type, activity_id) {

        var postData = {
            _xsrf: $.cookie("_xsrf"),
            item_type: item_type,
            activity_id: activity_id
        };
        if (item_type == 'discussion'){
            var formData = $('#sign-up-form form').serializeArray();
            for(var i = 0; i < formData.length; i++){
                var k = formData[i].name, v = formData[i].value;
                if(k in postData){
                    postData[k] = postData[k] + '!!!!' + v;
                }else{
                    postData[k] = v;
                }
            }
            postData['status'] = 'sign_up_wait';
            postData['cellphone'] = $('#cellphone_info').text();
            postData['source'] = getQueryString('src');
            postData['corp'] = $('#corp_auth').val();
            // postData['fullname'] = $('#fullname').val();
            // postData['wechatid'] = $('#wechatid').val();
            // postData['email'] = $('#email').val();
            // postData['org_name'] = $('#org_name').val();
            // postData['position'] = $('#position').val();
            // postData['person_info'] = $('#person_info').val();
            // postData['is_volunteer'] = ($('#is_volunteer').attr("checked") ? 1 : 0);
            // postData['contribution'] = $('#contribution').val();
            // try{
            //     postData['contribution'] += getExtraOptions();
            // }catch(e){}
        }
            
        $.ajax({
            type: "POST",
            url: '/rest/discussion/handle',
            data: postData,
            success: function(data) {
                if (data.error) {
                    if (confirm(data.error)) {
                        if(data.error_name == 'access_need_login'){
                            window.location.href = "/login?corp=" + $('#corp_auth').val() + "&redirect_url=" + location.pathname;
                        }else if(data.error_name == 'access_need_person_info'){
                            // $._showSignUpModal();
                            
                            location.href = '#sign-up-form';
                        }
                    }
                } else {
                    window.location.href =location.href.substring(0,location.href.indexOf('?signin=true'));
                }

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };

    var fields = $('#sign-up-fields').val();
    if(fields){
        fields = fields.split(',');
        for(var i = 0; i < fields.length; i++){
            $('.sign-up-form-' + fields[i]).show();
        }
    }

    

    try{
        addExtraOptions();
    }catch(e){}
    
    var t = $('#modal-sign-up-form .modal-body');
    if(t && t.length){
        $('#sign-up-form').html(t.html());
        t.html('');
    }

});