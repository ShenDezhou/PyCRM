$(function() {
    var handleBootstrapWizardsValidation = function() {
        "use strict";
        $("#wizard").bwizard({
            'validating': function(e, t) {
                if (t.index == 0) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-1")) {
                        return false
                    }
                } else if (t.index == 1) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-2")) {
                        return false
                    }
                } else if (t.index == 2) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-3")) {
                        return false
                    }
                }
            },
            backBtnText: '&larr; 上一步',
            nextBtnText: '下一步 &rarr;'
        });
    };
    var FormWizardValidation = function() {
        "use strict";
        return {
            init: function() {
                handleBootstrapWizardsValidation()
            }
        }
    }();

    FormWizardValidation.init();

    var id = getQueryString('id');
    if (id) {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/requirement/detail',
            cache: false,
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                data = data[0];
                for (var key in data) {
                    $('#' + key).val(data[key]);
                }
                console.log(data);
                $('#mycontent').val(data['content']);
                if (data['attachments'] != '')
                    $.initPreviewDocForNews(data['attachments'].split(','));
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $('#btn-submit').click(function() {
        $("#btn-submit").attr("disabled", true);
        var currentUrl = $("#submit-form").attr('action');
        if (id)
        {
            currentUrl += "?id="+id;
        }
        $.ajax({
            type: "POST",
            cache: false,
            url: currentUrl,
            data: $("#submit-form").serialize(),
            success: function(data) {
                $("#btn-submit").attr("disabled", false);
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(data.message || '提交成功');
                    location.href = '/common/requirements';
                }
            },
            error: function() {
                alert('网络错误，请检查重试！');
                $("#btn-submit").attr("disabled", false);
            },
            dataType: 'json'
        });
        return false;
    });
});
