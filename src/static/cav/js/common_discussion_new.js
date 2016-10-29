$(function() {
    var type = "";
    var id = "";
    var type_name = {};

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
                $(dom).materialnote("insertImage", data.files[0].url, 'filename');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('图片上传出错！' + textStatus + " " + errorThrown);
                // console.log(textStatus + " " + errorThrown);
            }
        });
    }

    function getQueryString(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]);
        return null;
    }
    $("#data_type").click(function() {
        if (!$('#data_type').is(":checked")) {
            if (confirm("确定讨论为非公开讨论吗?")) {
                $('#data_type').prop("checked", false);
            } else {
                $('#data_type').prop("checked", true);
            }
        }
    });
    var init_select = function(type, select_id) {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/get/tagcode',
            cache: false,
            data: {
                type: type
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                var html = "";
                for (var index = 0; index < data.length; index++) {
                    var tag_value = data[index]['tag_name'].replace('群', '').replace('（已满）', '');
                    html += "<option value='" + tag_value + "'>" + tag_value + "</option>";
                }

                $('#' + select_id).html(html);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }
    var _init = function() {
        init_select("weixin_group", "subject");
    };
    _init();

    if (getQueryString('id') != null) {
        id = getQueryString('id');
        $.ajax({
            type: "GET",
            url: '/rest/common/discussion/detail',
            cache: false,
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                data = data[0];
                console.log(data);

                for (var key in data) {
                    $('#' + key).val(data[key]);
                }

                $("#published").val(new Date(data['published']).Format("yyyy-MM-dd HH:mm"));
                $("#activity_start_time").val(new Date(data['activity_start_time']).Format("yyyy-MM-dd HH:mm"));
                $("#activity_end_time").val(new Date(data['activity_end_time']).Format("yyyy-MM-dd HH:mm"));
                $("#published").combodate();
                $("#activity_start_time").combodate().on('change', function(ev) {
                    if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
                        alert("开始时间不得晚于结束时间");
                    } else
                        $('.datetimepicker').hide();
                    $('.datetimepicker').hide();
                });
                $("#activity_end_time").combodate().on('change', function(ev) {
                    if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
                        alert("结束时间不得早于开始时间");
                    } else
                        $('.datetimepicker').hide();
                });


                if (data['sign_up_fields']) {
                    var fields = data.sign_up_fields.split(',');
                    for (var i = 0; i < fields.length; i++) {
                        $("#signup-check-" + fields[i]).attr('checked', 'checked');
                    }
                }

                if (data['data_type'] == "external")
                    $('#data_type').prop("checked", true);
                else
                    $('#data_type').prop("checked", false);


                if (data['pictures'] != '')
                    $.initPreviewImageForTicket(data['pictures'].split(','));
                $(".content-header h1").html("修改" + type_name[type]);
                $('#mycontent').val(data['content']);
                $('#mycontent').materialnote({
                    height: 300, // set editor height
                    minHeight: null, // set minimum height of editor
                    maxHeight: 700,
                    callbacks: {
                        onImageUpload: function(files) {
                            var url = $(this).data('upload'); //path is defined as data attribute for  textarea
                            sendFile(files[0], url, $(this), '#mycontent');
                        }
                    }
                });
                $('#signup_content').val(data['signup_content']);
                $('#signup_content').materialnote({
                    height: 300, // set editor height
                    minHeight: null, // set minimum height of editor
                    maxHeight: 700,
                    callbacks: {
                        onImageUpload: function(files) {
                            var url = $(this).data('upload'); //path is defined as data attribute for  textarea
                            sendFile(files[0], url, $(this), '#signup_content');
                        }
                    }
                });

                // if (data.sur_id) {
                //     $('#sur_id').val(data.sur_id);
                //     $('#sur_id_btn').text(data.sur_title);
                // }


            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    } else {

        type = getQueryString("type");
        $(".content-header h1").html("新建" + type_name[type]);
        $('#mycontent').materialnote({
            height: 300, // set editor height
            minHeight: null, // set minimum height of editor
            maxHeight: 700,
            callbacks: {
                onImageUpload: function(files) {
                    var url = $(this).data('upload'); //path is defined as data attribute for  textarea
                    sendFile(files[0], url, $(this), '#mycontent');
                }
            }
        });
        $('#signup_content').materialnote({
            height: 300, // set editor height
            minHeight: null, // set minimum height of editor
            maxHeight: 700,
            callbacks: {
                onImageUpload: function(files) {
                    var url = $(this).data('upload'); //path is defined as data attribute for  textarea
                    sendFile(files[0], url, $(this), '#signup_content');
                }
            }
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
        location.href = "/console/activity_list";
    });
    var commitData = function(status) {
        var postData = {
            _xsrf: $.cookie("_xsrf")
        };
        var url = '';
        if (id != "") {
            url = '/rest/common/discussion/edit';
            postData.id = id;
        } else {
            url = '/rest/common/discussion/commit';
        }
        $('#mycontent').val($('.note-editable').eq(0).html());
        $('#signup_content').val($('.note-editable').eq(1).html());
        if (!$('#published').check().notNull() || !$('#title').check().notNull() || !$('#mycontent').check().notNull() || !$('#activity_start_time').check().notNull() || !$('#activity_end_time').check().notNull() || !$('#signup_content').check().notNull()) {
            alert("红色*号标识均为必填项");
            return;
        }
        postData.title = $('#title').val();
        postData.published = $('#published').val();
        postData.content = $('#mycontent').val();
        postData.subject = $('#subject').val();
        postData.signup_content = $('#signup_content').val();
        postData.status = status;
        postData.activity_start_time = $('#activity_start_time').val();
        postData.activity_end_time = $('#activity_end_time').val();
        postData.pictures = $('#upload-images').val();
        postData.activity_online_offline = $("#activity_online_offline").find("option:selected").val();
        postData.activity_type = 'online_discussion';
        postData.sign_up_check = 1;
        var sign_up_fields = [];
        $('.sign-up-field').each(function(item) {
            if ($(this).attr('checked')) {
                sign_up_fields.push($(this).attr('id').replace('signup-check-', ''));
            }
        });
        postData.sign_up_fields = sign_up_fields.join(',');
        if ($('#data_type').is(":checked"))
            postData.data_type = 'external';
        else
            postData.data_type = 'internal';
        $.ajax({
            type: "POST",
            url: url,
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                location.href = "/common/discussion";
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }
    if (getQueryString('id') == null) {
        $("#published").val(new Date().Format("yyyy-MM-dd HH:mm"));
        $("#activity_start_time").val(new Date().Format("yyyy-MM-dd HH:mm"));
        $("#activity_end_time").val(new Date().Format("yyyy-MM-dd HH:mm"));
        $("#published").combodate();
        $("#activity_start_time").combodate().on('change', function(ev) {
            if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
                alert("开始时间不得晚于结束时间");
            } else
                $('.datetimepicker').hide();
            $('.datetimepicker').hide();
        });
        $("#activity_end_time").combodate().on('change', function(ev) {
            if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
                alert("结束时间不得早于开始时间");
            } else
                $('.datetimepicker').hide();
        });
    }
    $.selectSurveyChoice = function(target) {
        var t = $(target).parent().parent();
        $('#event-select-survey-modal').modal('hide');
        $('#sur_id').val(t.attr('data-id'));
        $('#sur_id_btn').text($('.data-title', t).text());
    };
    var refreshSurSelects = function() {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/survey/choices',
            cache: false,
            data: {
                keyword: $('#survey-keyword').val()
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                var html = "";
                for (var i = 0; i < data.length; i++) {
                    html += '<tr data-id="' + data[i].id + '"><td class="data-title">' + data[i].title + '</td><td><a href="javascript:;" onclick="$.selectSurveyChoice(this)" class="btn btn-xs btn-danger m-r-5">选择</a></td></tr>';
                }

                $('#survey-select-body').html(html || '无搜索结果');
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $('#sur_id_btn').click(function() {
        refreshSurSelects();
        $('#event-select-survey-modal').modal('show');
    });
    $('#event-select-survey-search').click(function() {
        refreshSurSelects();
    });
    $('#event-select-survey-remove').click(function() {
        $('#event-select-survey-modal').modal('hide');
        $('#sur_id').val('');
        $('#sur_id_btn').text('未选择');
    });
});
