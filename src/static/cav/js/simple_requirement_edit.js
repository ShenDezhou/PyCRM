$(function() {
    var type = "";
    var id = $("#id").val();
    $.ajax({
        type: "GET",
        url: '/rest/mgr/requirement/detail',
        cache: false,
        data: {
            id: id
        },
        success: function(data) {
            if (data.error) {
                return alert(data.error || '失败！');
            }
            data = data[0];
            for (var key in data) {
                $('#' + key).val(data[key]);
            }
            $('#mycontent').val(data['content']);
            if(data['attachments']!='')
                $.initPreviewDocForNews(data['attachments'].split(','));
            $('#mycontent').summernote({
                height: 100, // set editor height
                minHeight: null, // set minimum height of editor
                maxHeight: 400
            });
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });

    $('#save').click(function() {
        commitData("exam_pending");
        return false;
    });
    $('#return').click(function() {
        history.go(-1);
    });
    var commitData = function(status) {
        var postData = {
            _xsrf: $.cookie("_xsrf")
        };
        postData.type = type;
        var url = '';
        url = '/rest/mgr/requirement/commit';
        if (id != "") {
            postData.id = id;
        }
        postData.status = status;
        postData.contact_name = $('#contact_name').val();
        postData.contact_cellphone = $('#contact_cellphone').val();
        postData.contact_wechatid = $('#contact_wechatid').val();
        postData.title = $('#title').val();
        postData.subject = $('#subject').val();
        postData.intro_content = $('#intro_content').val();
        postData.content = $('#mycontent').val();
        postData.repay_content = $('#repay_content').val();
        postData.attachments = $('#upload-docs').val();
        $.ajax({
            type: "POST",
            url: url,
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                // history.go(-1);
                location.href = '/common/requirements_person';
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $('#subject').change(function() {
        var v = $(this).val();
        if (v == '_NEW_') {
            $('#subject-modal').modal('show');
            $('#subject-tag-name').val('');
        }
    });
    $('#subject-tag-save-btn').click(function() {
        var val = $('#subject-tag-name').val();
        if (!val) {
            return alert('请先填写名称');
        }
        $.ajax({
            type: "POST",
            url: '/rest/mgr/tag/add',
            data: {
                'type': 'requirement_type',
                'name': val
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                $('#subject-modal').modal('hide');
                $('#subject').prepend('<option value="' + data.tag_id + '">' + data.tag_name + '</option>');
                $('#subject').val(data.tag_id);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });


    $('#btn-fetch-content').click(function() {
        var url = $('#data_source').val();
        if (!url) {
            return alert('链接不能为空！');
        }
        $.ajax({
            type: "POST",
            url: '/rest/mgr/fetch/weixin',
            data: {
                url: url
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                $('#title').val(data.title);
                $('#mycontent').summernote("code", data.content);
                $('#published').val(data.date);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });

});