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
                $(dom).summernote("insertImage", data.files[0].url, 'filename');
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
    $("#sign_up_check").click(function() {
        if (!$('#sign_up_check').is(":checked")) {
            if (confirm("确定取消报名确认吗?")) {
                $('#sign_up_check').prop("checked", false);
            } else {
                $('#sign_up_check').prop("checked", true);
            }
        }
    });
    var init_select = function(type, select_id) {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/get/mapcode',
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
                    html += "<option value='" + data[index]['code_id'] + "'>" + data[index]['code_name'] + "</option>";
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
        init_select("activity_type", "activity_type");
    };
    _init();

    if (getQueryString('id') != null) {
        id = getQueryString('id');
        $.ajax({
            type: "GET",
            url: '/rest/mgr/news/detail',
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
                if (data['event_corp_auth'] == "1")
                    $('#event_corp_auth').prop("checked", true);
                else
                    $('#event_corp_auth').prop("checked", false);

                if (data['sign_up_fields']) {
                    var fields = data.sign_up_fields.split(',');
                    for (var i = 0; i < fields.length; i++) {
                        $("#signup-check-" + fields[i]).attr('checked', 'checked');
                    }
                }

                if (data['sign_up_check'] == "1")
                    $('#sign_up_check').prop("checked", true);
                else
                    $('#sign_up_check').prop("checked", false);

                
                if (data['pictures'] != '')
                    $.initPreviewImageForTicket(data['pictures'].split(','));
                $(".content-header h1").html("修改" + type_name[type]);
                $('#mycontent').val(data['content']);
                $('#mycontent').summernote({
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
                $('#signup_content').summernote({
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

                if (data.sur_id) {
                    $('#sur_id').val(data.sur_id);
                    $('#sur_id_btn').text(data.sur_title);
                }


            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    } else {

        type = getQueryString("type");
        $(".content-header h1").html("新建" + type_name[type]);
        $('#mycontent').summernote({
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
        $('#signup_content').summernote({
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
    $("#published").val(new Date().Format("yyyy-MM-dd"));
    $('#save').click(function() {
        //防止多次点击重复提交
        $('#save').attr("disabled",true);
        $("#save_and_publish").attr("disabled",true);
        commitData("draft");
        return false;
    });
    $('#save_and_publish').click(function() {
        //防止多次点击重复提交
        $('#save').attr("disabled",true);
        $("#save_and_publish").attr("disabled",true);
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
        postData.type = type;
        var url = '';
        if (id != "") {
            url = '/rest/mgr/news/edit';
            postData.id = id;
        } else {
            url = '/rest/mgr/news/commit';
        }
        if (!$('#published').check().notNull() || !$('#title').check().notNull() || !$('#mycontent').check().notNull() || !$('#paid').check().notNull() || !$('#activity_start_time').check().notNull() || !$('#activity_end_time').check().notNull() || !$('#activity_place').check().notNull()) {
            alert("红色*号标识均为必填项");
            $('#save').attr("disabled",false);
            $("#save_and_publish").attr("disabled",false);
            return;
        }
        postData.title = $('#title').val();
        postData.published = $('#published').val();
        postData.content = $('#mycontent').val();
        postData.signup_content = $('#signup_content').val();
        postData.paid = $('#paid').val();
        postData.status = status;
        postData.type = 'activity';
        postData.activity_start_time = $('#activity_start_time').val();
        postData.activity_end_time = $('#activity_end_time').val();
        postData.activity_place = $('#activity_place').val();
        postData.general_place = $('#general_place').val();
        postData.activity_guider = $('#activity_guider').val();
        postData.activity_sponsor = $('#activity_sponsor').val();
        postData.activity_undertake = $('#activity_undertake').val();
        postData.pictures = $('#upload-images').val();
        postData.activity_online_offline = $("#activity_online_offline").find("option:selected").val();
        postData.activity_type = $("#activity_type").find("option:selected").val();
        postData.data_type = "internal";
        postData.sur_id = $('#sur_id').val();
        postData.activity_organizer = $('#activity_organizer').val();
        var sign_up_fields = [];
        $('.sign-up-field').each(function(item) {
            if ($(this).attr('checked')) {
                sign_up_fields.push($(this).attr('id').replace('signup-check-', ''));
            }
        });
        postData.sign_up_fields = sign_up_fields.join(',');
        if ($('#event_corp_auth').is(":checked"))
            postData.event_corp_auth = 1;
        else
            postData.event_corp_auth = 0;

        if ($('#sign_up_check').is(":checked"))
            postData.sign_up_check = 1;
        else
            postData.sign_up_check = 0;
        $.ajax({
            type: "POST",
            url: url,
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                location.href = "/console/activity_list";
            },
            error: function() {
                $('#save').attr("disabled",false);
                $("#save_and_publish").attr("disabled",false);
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $("#published").datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function(ev) {
        $('.datepicker').hide();
    });
    $("#activity_start_time").datetimepicker({}).on('changeDate', function(ev) {
        if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
            alert("开始时间不得晚于结束时间");
        } else
            $('.datetimepicker').hide();
        $('.datetimepicker').hide();
    });
    $("#activity_end_time").datetimepicker({}).on('changeDate', function(ev) {
        if ($("#activity_start_time").val() > $("#activity_end_time").val()) {
            alert("结束时间不得早于开始时间");
        } else
            $('.datetimepicker').hide();
    });

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
