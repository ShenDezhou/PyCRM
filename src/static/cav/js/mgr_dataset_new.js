$(function() {
    var type = "";
    var id = "";

    function sendFile(file, editor, welEditable, dom) {
        var data = new FormData();
        data.append("file", file);
        $.ajax({
            url: "/fileupload/mgr/image",
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                $(dom).summernote("insertImage", data.files[0].url, 'filename');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('图片上传出错！' + textStatus + " " + errorThrown);
                // console.log(textStatus + " " + errorThrown);
            }
        });
    }
    if (getQueryString('id') != null) {
        id = getQueryString('id');
        $(".content-header h1").html("修改数据源");
        $.ajax({
            type: "GET",
            url: '/rest/mgr/dataset/detail',
            cache: false,
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                data = data[0];
                console.log(data+id);
                for (var key in data) {
                    $('#' + key).val(data[key]);
                }
                $('#mycontent').val(data['content']);
                if (data['pictures'] != '')
                    $.initPreviewImageForTicket(data['pictures'].split(','));
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
    } else {
        $(".content-header h1").html("新建数据源");
        $('#mycontent').summernote({
            height: 300, // set editor height
            minHeight: null, // set minimum height of editor
            maxHeight: 400
        });
    }
    Date.prototype.Format = function(formatStr) {
        var str = formatStr;
        var Week = ['日', '一', '二', '三', '四', '五', '六'];

        str = str.replace(/yyyy|YYYY/, this.getFullYear());
        str = str.replace(/yy|YY/, (this.getYear() % 100) > 9 ? (this.getYear() % 100).toString() : '0' + (this.getYear() % 100));

        str = str.replace(/MM/, (this.getMonth() + 1) > 9 ? (this.getMonth() + 1).toString() : '0' + (this.getMonth() + 1));
        str = str.replace(/M/g, this.getMonth());

        str = str.replace(/w|W/g, Week[this.getDay()]);

        str = str.replace(/dd|DD/, this.getDate() > 9 ? this.getDate().toString() : '0' + this.getDate());
        str = str.replace(/d|D/g, this.getDate());

        str = str.replace(/hh|HH/, this.getHours() > 9 ? this.getHours().toString() : '0' + this.getHours());
        str = str.replace(/h|H/g, this.getHours());
        str = str.replace(/mm/, this.getMinutes() > 9 ? this.getMinutes().toString() : '0' + this.getMinutes());
        str = str.replace(/m/g, this.getMinutes());

        str = str.replace(/ss|SS/, this.getSeconds() > 9 ? this.getSeconds().toString() : '0' + this.getSeconds());
        str = str.replace(/s|S/g, this.getSeconds());

        return str;
    }
    $('#save').click(function() {
        commitData("draft");
        return false;
    });
    $('#save_and_publish').click(function() {
        commitData("published");
        return false;
    });
    $('#return').click(function() {
        location.href = "/console/dataset_list";
    });
    var commitData = function(status) {
        var postData = {
            _xsrf: $.cookie("_xsrf")
        };
        postData.type = type;
        var url = '';
        if (id != "") {
            url = '/rest/mgr/dataset/edit';
            postData.id = id;
        } else {
            url = '/rest/mgr/dataset/commit';
        }
        postData.status = status;
        postData.title = $('#title').val();
        postData.org_name = $('#org_name').val();
        postData.industry = $('#industry').val();
        postData.org_type = $('#org_type').val();
        postData.connect_person = $('#connect_person').val();
        postData.connect_cellphone = $('#connect_cellphone').val();
        postData.org_describle = $('#org_describle').val();
        postData.data_describle = $('#data_describle').val();
        postData.content = $('#mycontent').val();
        postData.data_type = $("#data_type").find("option:selected").val();
        postData.pictures = $('#upload-images').val();
        postData.attachments = $('#upload-docs').val();
        console.log(postData);
        $.ajax({
            type: "POST",
            url: url,
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                location.href = "/console/dataset_list";
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $('#data_type').change(function() {
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
                'type': 'dataset_type',
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

    $("#published").datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function(ev) {
        $('.datepicker').hide();
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