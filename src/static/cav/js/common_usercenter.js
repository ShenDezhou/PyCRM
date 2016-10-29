var op_count = 0;
$(function() {
    $("#userinfo").validate({
        rules: {
            fullname: {
                required: true
            },
            wechatid: {
                required: true
            },
            email: {
                required: true,
                email: true
            },
            org_name: {
                required: true
            }
        },
        //For custom messages
        messages: {
            fullname: {
                required: "名字不能为空"
            },
            email: {
                required: "邮箱不能为空",
                email: "请输入正确的邮箱"
            },
            wechatid: {
                required: "微信号不能为空"
            },
            org_name: {
                required: "单位或学校名称不能为空"
            }
        },
        errorElement: 'div',
        errorPlacement: function(error, element) {
            var placement = $(element).data('error');
            if (placement) {
                $(placement).append(error)
            } else {
                error.insertAfter(element);
            }
        }
    });
    $("#school").focus(function() {
        var school_name = $("#school").val();
        jQuery.ajax({
            url: '/rest/page/form_normal',
            type: "POST",
            data: {
                'school': school_name,
                'city': 'None',
                'school_department': 'None',
                'position': 'None',
                'org': 'None',
                'industry': 'None'
            },
            dataType: "json",
            success: function(data) {
                $(".autocomplete-content.dropdown-content").remove();
                var school_lis = data['school'];
                var school_list = {};
                for (var i = 0; i < school_lis.length; i++) {
                    school_list[school_lis[i]] = null
                }
                $('#school').autocomplete({
                    data: school_list
                });
            }
        })
    });
    $("#position").focus(function() {
        var position_name = $("#position").val();
        jQuery.ajax({
            url: '/rest/page/form_normal',
            type: "POST",
            data: {
                'school': 'None',
                'city': 'None',
                'school_department': 'None',
                'position': position_name,
                'org': 'None',
                'industry': 'None'
            },
            dataType: "json",
            success: function(data) {
                $(".autocomplete-content.dropdown-content").remove();
                position_list = data['position'];
                var title_list = {};
                for (var i = 0; i < position_list.length; i++) {
                    title_list[position_list[i]] = null
                }
                $('#position').autocomplete({
                    data: title_list
                });
            }
        })
    });

    $("#org_name").focus(function() {
        var org_name = $("#org_name").val();
        jQuery.ajax({
            url: '/rest/page/form_normal',
            type: "POST",
            data: {
                'school': 'None',
                'city': 'None',
                'school_department': 'None',
                'position': 'None',
                'org': org_name,
                'industry': 'None'
            },
            dataType: "json",
            success: function(data) {
                $(".autocomplete-content.dropdown-content").remove();
                var org_lis = data['org'];
                var org_list = {};
                for (var i = 0; i < org_lis.length; i++) {
                    org_list[org_lis[i]] = null
                }
                $('#org_name').autocomplete({
                    data: org_list
                });
            }
        })
    });
    $("#industry").focus(function() {
        var industry = $("#industry").val();
        jQuery.ajax({
            url: '/rest/page/form_normal',
            type: "POST",
            data: {
                'school': 'None',
                'city': 'None',
                'school_department': 'None',
                'position': 'None',
                'org': 'None',
                'industry': industry
            },
            dataType: "json",
            success: function(data) {
                $(".autocomplete-content.dropdown-content").remove();
                var industry_lis = data['industry'];
                var industry_list = {};
                for (var i = 0; i < industry_lis.length; i++) {
                    industry_list[industry_lis[i]] = null
                }
                $('#industry').autocomplete({
                    data: industry_list
                });
                console.log(industry_list);
            }
        })
    });
    $(function() {
        var educations = ['请选择', '中专', '大专', '本科', '硕士研究生', '博士研究生'];
        for (index in educations) {
            if (educations[index] == '请选择') {
                $("#education").append("<option value=''>" + educations[index] + "</option>");
            } else {
                $("#education").append("<option value=" + educations[index] + ">" + educations[index] + "</option>");

            }
        }
    });
    $("#check_student").click(function() {
        if ($('#check_student').is(":checked")) {
            $(".student").show();
        } else {
            $(".student").hide();
        }
    });

    $.ajax({
        type: "get",
        cache: false,
        url: '/rest/common/person',
        success: function(data) {
            // }
            var op_data = data['op_info'];
            var html = '';
            var t_html = '';
            var delete_html = '';
            for (item in op_data) {
                op_count += 1;
                console.log(op_data[item]);
                html += '<div class="card">' +
                    '<div class="row">' +
                    '<div class="card-content horizontal center">' +
                    '<div class="row">' +
                    '<div class="input-field col s12">' +
                    '<label for="org_name">公司或学校*</label>' +
                    '<input id="org_name'+op_count+'"'+' name="fullname'+op_count+'"'+ ' type="text"' + ' value="' + op_data[item]['org_name'] + '"' + ' data-error=".errorTxt4">' +
                    '<div class="errorTxt4" style="color: red"></div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="row">' +
                    '<div class="input-field col s12">' +
                    '<label for="department">部门或系部</label>' +
                    '<input id="department'+op_count+'"'+' name="fullname'+op_count+'"'+ ' type="text"' + ' value="' + op_data[item]['department'] + '"' + ' data-error=".errorTxt1">' +
                    '<div class="errorTxt1" style="color: red"></div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="row">' +
                    '<div class="input-field col s12">' +
                    '<label for="title_name">职位*</label>' +
                    '<input id="title_name'+op_count+'"'+' name="fullname'+op_count+'"'+ ' type="text"' + ' value="' + op_data[item]['title_name'] + '"' + ' data-error=".errorTxt1">' +
                    '<div class="errorTxt1" style="color: red"></div>' +
                    '</div>' +
                    '</div>' +
                    '<a '+ ' onclick="$._deleteOp(\'' + op_data[item]['org_id'] + '\')"'+ ' class="btn waves-effect waves-light red lighten-1">' + '删除' +
                        '<input type="hidden" id="org_id'+op_count+'"'+' name="org_id'+op_count+'"'+' value="'+op_data[item]['org_id']+'"'+'/>' +
                    '</a>' + '<a ' +' onclick="$._editOp(\'' + op_count + '\')"'+ ' class="btn waves-effect waves-light">' + '保存修改' +
                    '</a>' +
                    '</div>' +
                    '</div>' + '</div>';
            }
            $("#op_info").html(html);
            if (data['auth_info']['cellphone']) {
                $('#div_person').show();
                for (item in data['person']) {
                    $("#" + item).val(data['person'][item]);
                }
                $("#person_id").val(data['person']['person_id']);
                $("#birthday").combodate({
                    format: 'YYYY-MM-DD',
                    value: data['person']['birthday'],
                    customClass: "col-md-3 input-sm"
                });
                $("#school_start").combodate({
                    format: 'YYYY-MM-DD',
                    value: data['person']['school_start'],
                    customClass: "col-md-3 input-sm"

                });
                for (item in data['org']) {
                    $("#" + item).val(data['org'][item]);
                }
                if (data['person'] && data['person']['school_department']) {
                    $("#check_student").attr("checked", true);
                    $('.student').show();
                    if (data['person']['attachment'] != null)
                        $.initPreviewImageForTicket(data['person']['attachment'].split(','));
                } else {
                    $("#check_student").attr("checked", false);
                    $('.student').hide();
                }
            } else {
                $('#div_person').hide();
            }
            Materialize.updateTextFields();
            var options = [];
            var fields = Object.assign({}, data['person']);
            fields = Object.assign(fields, data['org']);
            for (item in fields) {
                var fire = new Object();
                fire["selector"] = "#" + item;
                fire["offset"] = 50;
                fire["callback"] = function(item) {
                    var title = $('label[for="' + item.name + '"]')[0].innerText;
                    if (title.indexOf('*') > -1 && item.value == "")
                        Materialize.toast(title + "*为必填项", 1500);
                };
                options.push(fire);
            }
            Materialize.scrollFire(options);

        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
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

    $("#save").click(function() {
        $.ajax({
            type: "post",
            cache: false,
            url: '/page/common/person/commit',
            data: $('#userinfo').serialize(),

            success: function(data) {
                if (data.error)
                    alert(data.error);
                else {
                    alert(data.message);
                    var arr = location.href.split('redirect_url=');
                    if (arr.length > 0) {
                        location.href = arr[arr.length - 1];
                    }
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });

    // $("#birthday").datepicker({
    //     format: 'yyyy-mm-dd',
    //     autoclose: true
    // });
    // $("#school_start").datepicker({
    //     format: 'yyyy-mm-dd',
    //     autoclose: true
    // });


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


});
$("#add_op").click(function() {
    $("#modal-form-person").modal("show")
});
$("#add_op_save").click(function() {
    $.ajax({
        type: "post",
        cache: false,
        url: '/rest/mgr/add/org_person',
        data: {
            "org_name": $("#add_org").val(),
            "title_name": $("#add_title").val(),
            "department": $("#add_department").val(),
            "is_primary": $("#is_primary").val(),
            "person_id": 'user_center'
        },
        success: function(data) {
            if (data.error)
                alert(data.error);
            location.reload();
            if (data.message) {
                alert("增加成功!");
                location.reload();
            }
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
});
$._deleteOp = function(org_id) {
    $.ajax({
        type: "post",
        cache: false,
        url: '/rest/mgr/delete/org_person',
        data: {
            "org_id": org_id,
            "person_id": $("#person_id").val()
        },
        success: function(data) {
            if (data.error)
                alert(data.error);
            location.reload();
            if (data.message) {
                alert("删除成功!");
                location.reload();
            }
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
};
$._editOp = function(count) {
    var org_id = $("#org_id"+count).val();
    var org_name = $("#org_name"+count).val();
    var title_name = $("#title_name"+count).val();
    var department = $("#department"+count).val();
    var person_id = $("#person_id").val();
    console.log("count: " + count);
    console.log(org_name,title_name,department,person_id,org_id);
    $.ajax({
        type: "post",
        cache: false,
        url: '/rest/mgr/edit/org_person',
        data: {
            "org_name": org_name,
            "title_name": title_name,
            "department": department,
            "person_id": person_id,
            "old_org_id": org_id
        },
        success: function(data) {
            if (data.error)
                alert(data.error);
            location.reload();
            if (data.message) {
                alert("修改成功!");
                location.reload();
            }
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
};
$("#showActivityRecords").click(function () {
    $.ajax({
        type: "get",
        cache: false,
        url: '/rest/common/person/activity/records',
        success: function(data) {
            //console.log(data['activity_records']);
            $("div").remove("#record_title").remove("#record_count").remove("#acitivity_records");
            $("#record_count").remove();
            $("#acitivity_records").remove();

            sign_up_times=data['activity_records'].length
            register_times=0;

            if(sign_up_times>0){
                record_title='<div class="center" id="record_title">\
                                <h4>活动记录</h4>\
                                </div>';

                record_table='<div id="acitivity_records">\
                        <table class="table table-bordered display responsive nowrap table-striped">\
                            <tr>\
                                <th>活动名称</th>\
                                <th>报名时间</th>\
                                <th>签到时间</th>\
                            </tr>';
                $.each(data['activity_records'],function(n,record){
                    record_table+='<tr><td>'+record.title+'</td><td>'+record.sign_up_time+'</td><td>'+(record.register_time?record.register_time:"无")+'</td></tr>';
                    if(record.register_time){
                        register_times++;
                    }
                });
                record_table+='</table></div>'
                record_count='<div id="record_count">共报名'+sign_up_times+'次，签到' + register_times + '次</div>'
                $("#div_person").append(record_title+record_count+record_table);
            }
            else{
                $("#div_person").append('<div id="record_count" class="center">未查到活动报名或签到记录！</div>');
            }

        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
});