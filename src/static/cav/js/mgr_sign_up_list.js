$(function() {
    var detail_table = null;
    var checked = false;
    $('#check_all').click(function() {
        if (checked == false) {
            checked = true;
            $("#detail_list_table input:checkbox:enabled").prop("checked", true);
        } else {
            checked = false;
            $("#detail_list_table input:checkbox:enabled").prop("checked", false);
        }
        return false;
    });
    $('#sign_up_success').click(function() {
        if (confirm("确定将选中的都设置为报名成功状态吗？")) {
            var activity_id = getQueryString("activity");
            $.change_status(activity_id, getAllCheckIds(), "sign_up_success", "");
        }
    });
    $('#sign_up_fail').click(function() {
        if (confirm("确定将选中的都设置为报名失败状态吗？")) {
            $("#modal-reason").modal("show");
            var activity_id = getQueryString("activity");
            $("#save").click(function() {
                $.change_status(activity_id, getAllCheckIds(), "sign_up_fail", $("#reason").val());
                return false;
            });
        }
    });
    $('#sign_up_full').click(function() {
        if (confirm("确定将选中的都设置为人数已满状态吗？")) {
            var activity_id = getQueryString("activity");
            $.change_status(activity_id, getAllCheckIds(), "sign_up_full", "");
        }
    });
    $('#sign_up_success_and_register').click(function() {
        if (confirm("确定将选中的都设置为报名成功并已签到状态吗？")) {
            var activity_id = getQueryString("activity");
            $.change_status(activity_id, getAllCheckIds(), "sign_up_success_and_register", "");
        }
    });
    var getAllCheckIds = function() {
        var ids = "";
        $("#detail_list_table input:checkbox").each(function() {
            if ($(this).is(":checked")) {
                ids += $(this).attr('id') + ',';
            }
        });
        return ids.substring(0, ids.length - 1);
    };
    $.change_status = function(activity_id, person_id, status, reason) {
        var url;
        if (status == "sign_up_success_and_register") {
            url = '/rest/mgr/activity/sign_up_or_register/status';
        } else {
            url = '/rest/mgr/activity/sign/up/status';
        }
        $.ajax({
            type: "POST",
            url: url,
            data: {
                _xsrf: $.cookie("_xsrf"),
                activity_id: activity_id,
                person_id: person_id,
                status: status,
                reason: reason
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                if (status == 'sign_up_success' && confirm('是否发送报名成功确认短信？')) {
                    $.send_sms(activity_id, person_id);
                } else {
                    window.location.reload();
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $.view_survey_result = function(sur_id, auth_id) {
        $.ajax({
            type: "GET",
            url: '/rest/mgr/survey/' + sur_id + '/user/' + auth_id,
            data: {
                _xsrf: $.cookie("_xsrf")
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                var html = '';
                for (var i = 0; i < data.quizs.length; i++) {
                    var title = data.quizs[i].title,
                        value = '',
                        answers = data.quizs[i].answers;
                    for (var j = 0; answers && j < answers.length; j++) {
                        value += '<p>' + answers[j].label + '</p>';
                    }
                    html += '<div class="form-group">' +
                        '<label class="col-md-5 control-label">' + title + '</label>' +
                        '<div class="col-md-7">' +
                        value +
                        '</div>' +
                        '</div>';
                }
                $('#modal-survey-result .modal-body form').html(html);
                $('#modal-survey-result').modal('show');
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $.send_sms = function(activity_id, person_id) {
        $.ajax({
            type: "POST",
            url: '/rest/mgr/activity/sign/up/sms',
            data: {
                _xsrf: $.cookie("_xsrf"),
                activity_id: activity_id,
                person_id: person_id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '发送失败！');
                }
                if (data.message) {
                    alert(data.message);
                }
                window.location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $.input_fail_reason = function(activity_id, status, person_id) {
        $("#modal-reason").modal("show");
        $("#save").click(function() {
            $.change_status(activity_id, status, person_id, $("#reason").val());
            return false;
        });
    };

    $.change_status_filter = function(activity_id) {
        var v = $('#sign_up_status_option').val();
        $.stats_show_detail(activity_id, 'sign_up', v);
    };

    $.stats_show_detail = function(activity_id, type, status_type) {
        status_type = status_type || '';
        if (detail_table == null) {
            detail_table = $('#detail_list_table').DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) {
                    return load_dt_view(oSettings); },
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls"
                    }]
                },
                "ajax": "/rest/mgr/activity/sign_up_or_register/table?activity_id=" + activity_id + "&type=" + type + '&status_type=' + status_type,
                "columns": [{
                    "data": "fullname",
                    "mRender": function(data, something, full) {
                        return '<input id="' + full['person_id'] + '" type="checkbox" >' + "<a class='btn btn-link btn-xs' onclick=$.getPersonDetailInfo('" + full['person_id'] + "')>" + data + "</a>";
                    }
                }, {
                    "data": "created"
                }, {
                    "data": "code_name",
                    "mRender": function(data, something, full) {
                        if (data == "报名失败")
                            return data + ", 原因:" + full['reason'];
                        else
                            return data;
                    }
                }, {
                    "data": "member_type",
                    "mRender": function(data, something, full) {
                        if (data == "None")
                            return "否";
                        else
                            return '<span class="label label-success">' + data + '</span>';
                    }
                }, {
                    "data": "is_volunteer",
                    "mRender": function(data, something, full) {
                        if (data == 1)
                            return '<span class="label label-info">是</span>';
                        else
                            return '否';
                    }
                }, {
                    "data": "cellphone"
                }, {
                    "data": "org_name"
                }, {
                    "data": "position"
                }, {
                    "data": "email"
                }, {
                    "data": "wechatid"
                }, {
                    "data": "attachment",
                    "mRender": function(data, something, full) {
                        var html = "";
                        if (data)
                            html += '<img src="' + data + '" style="max-height:30px;"/>';
                        return html;
                    }
                }, {
                    "data": "contribution"
                }, {
                    "data": "person_id",
                    "mRender": function(data, something, full) {
                        var html = "";
                        // console.log(full['code_name']);
                        if (full.status == 'sign_up_success')
                            html += '<a class="btn btn-success btn-xs" onclick=$.send_sms("' + full['activity_id'] + '","' + full['person_id'] + '") style="margin-left:5px;">' + '重发报名成功短信' + '</a>';
                        if (full.status != 'sign_up_success')
                            html += '<a class="btn btn-info btn-xs" target="ac_news" onclick=$.change_status("' + full['activity_id'] + '","' + full['person_id'] + '","sign_up_success","") style="margin-left:5px;">' + '报名成功' + '</a>';
                        if (full.status != 'sign_up_fail')
                            html += '<a class="btn btn-danger btn-xs" style="margin-left:5px;" onclick=$.input_fail_reason("' + full['activity_id'] + '","' + full['person_id'] + '","sign_up_fail") >' + '报名失败' + '</a>';
                        if (full.status != 'sign_up_full')
                            html += '<a class="btn btn-warning btn-xs" onclick=$.change_status("' + full['activity_id'] + '","' + full['person_id'] + '","sign_up_full","") style="margin-left:5px;">' + '人数已满' + '</a>';
                        html += '<a class="btn btn-success btn-xs" onclick=$.change_status("' + full['activity_id'] + '","' + full['person_id'] + '","sign_up_success_and_register","") style="margin-left:5px;">' + '报名成功已签到' + '</a>';
                        if (full.sur_id)
                            html += '<a class="btn btn-primary btn-xs" onclick=$.view_survey_result("' + full['sur_id'] + '","' + full['person_id'] + '") style="margin-left:5px;">' + '查看表单结果' + '</a>';
                        return html;
                    }
                }, {
                    "data": "sur_value"
                }],
                "columnDefs": [],
                "aaSorting": [5, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            detail_table.ajax.url("/rest/mgr/activity/sign_up_or_register/table?activity_id=" + activity_id + "&type=" + type + '&status_type=' + status_type).load();
        }
    };
    $.stats_show_detail(getQueryString("activity"), "sign_up");

    var personInfo = function(person_info) {
        var output = "<tr><td>人员类型</td><td class='person_type'></td></tr><tr><td>公司名称</td><td class='org_name'></td></tr>" + personInfoTitle();

        var tables = '';
        tables += '<table id="person_info_table" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        $('#div_person').html(tables);
        $('#person_info_table tbody').html(output);
        for (var key in person_info) {
            if (key == 'gender') {
                if (person_info[key] == 2)
                    $('#person_info_table .' + key).html('女士');
                else
                    $('#person_info_table .' + key).html('先生');
            } else
                $('#person_info_table .' + key).html(person_info[key]);
        }
        if (person_info['attachment']) {
            $('#images').show();
            var images = person_info['attachment'].split(',');
            var image_output = "";
            for (var i = 0; i < images.length; i++) {
                image_output += "<tr><td><img width='500px' height='300px' src='" + $.get_file_url(images[i], '/assets/ticket/image/') + "'></td></tr>";
            }
            $('#image_table tbody').html(image_output);
        } else {
            $('#images').hide();
        }

    };
    $.getPersonDetailInfo = function(person_id) {
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/person/detail',
            data: {
                person_id: person_id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                personInfo(data);
                $("#modal-person-detail").modal("show");
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
});
