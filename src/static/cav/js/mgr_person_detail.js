var g_detail_type = "";
$(function () {
    var current_person_id = "";
    var g_tag_option_count = 0;
    var personInfo = function (person_info) {
        var output = personInfoTitle();
        var tables = '';
        for (i in person_info) {
            tables += '<table id="person_info_table' + i + '" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        }
        $('#div_person').html(tables);
        for (var i in person_info) {
            $('#person_info_table' + i + ' tbody').html(output);
            for (var key in person_info[i]) {
                if (key == 'gender') {
                    if (person_info[i][key] == 2)
                        $('#person_info_table' + i + ' .' + key).html('女');
                    else if (person_info[i][key] == 1)
                        $('#person_info_table' + i + ' .' + key).html('男');
                } else
                    $('#person_info_table' + i + ' .' + key).html(person_info[i][key]);
            }

        }

    };
    var orgInfo = function (org_info, person_info) {
        var output = orgInfoTitle() + willAndExpect();
        $('#org_info_table tbody').html(output);
        for (var key in org_info) {
            $('#org_info_table .' + key).html(org_info[key]);
        }

        for (var key in person_info) {
            $('#org_info_table .' + key).html(person_info[key]);
        }
        if (org_info['attachment']) {
            $('#images').show();
            var images = org_info['attachment'].split(',');
            var image_output = "";
            for (var i = 0; i < images.length; i++) {
                image_output += "<tr><td><img width='500px' height='300px' src='" + $.get_file_url(images[i], '/assets/ticket/image/') + "'></td></tr>";
            }
            $('#image_table tbody').html(image_output);
        } else {
            $('#images').hide();
        }

    };


    $('#save').click(function () {
        var postData = {_xsrf: $.cookie("_xsrf")};
        if ($('#certificate').is(":checked")) {
            postData.certificate = 1;
        } else {
            postData.certificate = 0;
        }
        if ($('#if_in_member_group').is(":checked")) {
            postData.if_in_member_group = 1;
        } else {
            postData.if_in_member_group = 0;
        }
        postData.weixin_group = $('#weixin_groups').val();
        postData.person_id = current_person_id;
        postData.type = g_detail_type;
        var str = "";
        $("#tag_group option:selected").each(function () {
            str += $(this).text() + ",";
        });
        postData.tag_group = str.substring(0, str.length - 1);
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/member/edit',
            data: postData,
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                window.location.reload();
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });
    var getFormDetailInfo = function (form_id, type) {
        var url = '';
        if (type == "person") {
            url = '/rest/mgr/person/form/detail'
        }
        else if (type == "org") {
            url = '/rest/mgr/org/form/detail'
        }
        $.ajax({
            type: "get",
            cache: false,
            url: url,
            data: {
                form_id: form_id
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                personInfo(data['person']);
                orgInfo(data['org'][0], data['person'][0]);

            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };

    $._showFormDetail = function (id, type) {
        getFormDetailInfo(id, type);
        $('#modal-form-detail').modal('show');
        $('#modal-form-detail .nav li').each(function () {
            $(this).removeClass("active");
        });
        $('#modal-form-detail .tab-content div').each(function () {
            $(this).removeClass("active in");
        });
        $("#modal-form-detail .nav li:nth-child(1)").addClass("active");
        $("#modal-form-detail .tab-content div:nth-child(1)").addClass("active in");
    };
    var memberInfo = function (form_info, person_will, member_info) {
        var output = "";
        output += "<tr><td>会员类型</td><td class='apply_member_type'></td></tr>";
        output += "<tr><td>缴费金额</td><td class='paid_money'></td></tr>";
        output += "<tr><td>有效期至</td><td class='due_date'></td></tr>";
        output += "<tr><td>支付方式</td><td class='paid_type'></td></tr>";
        output += willAndExpect();
        $('#member_info_table tbody').html(output);
        for (var key in form_info) {
            $('#member_info_table .' + key).html(form_info[key]);
        }
        for (var key in person_will) {
            $('#member_info_table .' + key).html(person_will[key]);
        }

        for (var key in member_info) {
            $('#member_info_table .' + key).html(member_info[key]);
        }

    };
    var memberPersonInfo = function (person_info) {
        var output = personInfoTitle();
        var tables = '';
        for (var i in person_info) {
            tables += '<table id="member_person_info_table' + i + '" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        }
        $('#div_member_person').html(tables);
        for (var i in person_info) {
            $('#member_person_info_table' + i + ' tbody').html(output);
            for (var key in person_info[i]) {
                if (key == 'gender') {
                    if (person_info[i][key] == 2)
                        $('#member_person_info_table' + i + ' .' + key).html('女');
                    else
                        $('#member_person_info_table' + i + ' .' + key).html('男');
                } else
                    $('#member_person_info_table' + i + ' .' + key).html(person_info[i][key]);
            }

        }

    };
    var memberOrgInfo = function (org_info, person_info, form_info) {
        var output = orgInfoTitle();
        $('#member_org_info_table tbody').html(output);
        for (var key in org_info) {
            $('#member_org_info_table .' + key).html(org_info[key]);
        }
        if (org_info['attachment'] || form_info['paid_pictures']) {
            $('#member_images').show();
            var image_output = "";
            if (org_info['attachment']) {
                var images = org_info['attachment'].split(',');
                if (form_info['apply_member_type'] == "个人普通会员" || form_info['apply_member_type'] == "个人理事会员")
                    image_output = "<tr><td>个人签名照片</td></tr>";
                else
                    image_output = "<tr><td>企业的营业执照</td></tr>";
                for (var i = 0; i < images.length; i++) {
                    image_output += "<tr><td><img width='500px' height='300px' src='" + $.get_file_url(images[i], '/assets/ticket/image/') + "'></td></tr>";
                }
            }
            if (form_info['paid_pictures']) {
                var images = form_info['paid_pictures'].split(',');
                image_output += "<tr><td>支付凭证</td></tr>";
                for (var i = 0; i < images.length; i++) {
                    image_output += "<tr><td><img width='500px' height='300px' src='" + $.get_file_url(images[i], '/assets/ticket/image/') + "'></td></tr>";
                }
            }
            $('#member_image_table tbody').html(image_output);
        } else {
            $('#member_images').hide();
        }

    };
    var tagInfo = function (tag_info) {
        $.ajax({
            url: "/rest/mgr/get/tagcode",
            dataType: 'json',
            delay: 250,
            data: {
                type: 'tag_root'
            },
            success: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                g_tag_option_count = data.length;
                var output = "";
                for (var index in data) {
                    findpos = -1;
                    // findpos = tag_info.indexOf(data[index]['tag_name'], 0);
                    if (findpos == -1)
                        output += "<option value='" + data[index]['tag_id'] + "'>" + data[index]['tag_name'] + "</option>";
                    else
                        output += "<option value='" + data[index]['tag_id'] + "' selected>" + data[index]['tag_name'] + "</option>";
                }
                $('#tag_group').html(output);
                $('#tag_group').select2({
                    placeholder: {
                        id: '-1', // the value of the option
                        text: 'Select an option'
                    },
                    tags: true,
                    tokenSeparators: [',', ' ']
                })
                $('#tag_group').on('change', function (evt) {

                    if (evt.target.length > g_tag_option_count) {

                        $.ajax({
                            url: "/rest/mgr/set/tagcode",
                            dataType: 'json',
                            data: {
                                tag_type: 'tag_root',
                                tag_name: this.options[this.options.length - 1].text
                            },
                            success: function (data, params) {
                                if (data.error) {
                                    return alert(data.error);
                                }

                            },
                            error: function () {
                                alert('网络错误！');
                            },

                            cache: false

                        });
                    }
                });

            },
            error: function () {
                alert('网络错误！');
            },

            cache: false

        });
    }

    var memberHandleInfo = function (member, person) {
        $('#weixin_groups').val(person[0]['weixin_group']);
        if (member[0]['certificate'] == 1) {
            $('#certificate').prop("checked", true);
        } else {
            $('#certificate').prop("checked", false);
        }
        if (person[0]['if_in_member_group'] == 1) {
            $('#if_in_member_group').prop("checked", true);
        } else {
            $('#if_in_member_group').prop("checked", false);
        }
        tagInfo(person[0]['tag_group']);
        // $('#tag_group').val(member['tag_group']);

    };
    var initWeixinGroup = function (groups) {
        var output = "<option value='none'>未分配微信群</option>";
        for (var index in groups) {
            output += '<option value="' + groups[index]['tag_id'] + '">' + groups[index]['tag_name'] + "</option>";
        }
        $("#weixin_groups").html(output);
    };
    var getPersonDetailInfo = function (person_id) {
        var url = '';
        current_person_id = person_id;
        url = '/rest/mgr/person/info/detail';
        $.ajax({
            type: "get",
            cache: false,
            url: url,
            data: {
                "person_id": person_id
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                console.log(data);
                if (data['type'] == 'member') {
                    initWeixinGroup(data['weixin_group']);
                    memberPersonInfo(data['person']);
                    memberOrgInfo(data['org'], data['person'], data['form']);
                    memberInfo(data['form'], data['person'], data['member']);
                    memberHandleInfo(data['member'], data['person']);
                }
                else if (data['type'] == 'not_member') {
                    $("#member_info").remove();
                    // $("#person_info").attr("","active");
                    // memberPersonInfo(data['person']);
                    // memberOrgInfo(data['org'], data['person'], data['form']);
                    initWeixinGroup(data['weixin_group']);
                    memberPersonInfo(data['person']);
                    memberOrgInfo(data['org'], data['person'], data['form']);
                    memberInfo(data['form'], data['person'], data['member']);
                    memberHandleInfo(data['member'], data['person']);

                }
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $._showPersonDetail = function (person_id) {
        getPersonDetailInfo(person_id);
        $('#modal-member-detail').modal('show');
        $('#modal-member-detail .nav li').each(function () {
            $(this).removeClass("active");
        });
        $('#modal-member-detail .tab-content div').each(function () {
            $(this).removeClass("active in");
        });
        $("#modal-member-detail .nav li:nth-child(1)").addClass("active");
        $("#modal-member-detail .tab-content div:nth-child(1)").addClass("active in");
    };
});
