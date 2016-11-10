$(function () {
    var counts = 1;
    var current = 1;
    var handleBootstrapWizardsValidation = function () {
        "use strict";
        $("#wizard").bwizard({
            'validating': function (e, t) {
                if (t.index == 0 && t.nextIndex > t.index) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-1")) {
                        return false
                    }
                } else if (t.index == 1 && t.nextIndex > t.index) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-2")) {
                        return false
                    }
                } else if (t.index == 2 && t.nextIndex > t.index) {
                    if (false === $('form[name="form-wizard"]').parsley().validate("wizard-step-3")) {
                        return false
                    }
                }
            },
            backBtnText: '&larr; 上一步',
            nextBtnText: '下一步 &rarr;'
        })
    };
    var FormWizardValidation = function () {
        "use strict";
        return {
            init: function () {
                handleBootstrapWizardsValidation()
            }
        }
    }();
    FormWizardValidation.init();
    // $('#weixin_group'+(counts-1)).html($('#weixin_group0').html());
    $("#birthday0").combodate(
        {
            customClass: "form-control",
            smartDays: true,
            minYear: 1945,
            maxYear: 2016,
            firstItem: "none"
        }
    );
    // start 会员信息修改

    var GetCookie = function () {
        var person_keys = ['fullname', 'cellphone', 'gender', 'birthday', 'school', 'school_start',
            'education', 'address', 'weixin_group', 'wechatid', 'city', 'email', 'position', 'person_info'];
        for (i in person_keys) {
            console.log(person_keys[i] + '0' + ":" + $.cookie(person_keys[i]+'0'));
            $("#" + person_keys[i] + '0').val($.cookie(person_keys[i]+'0'));
        }
        var other_keys = ['org_name', 'representative', 'general_description', 'domain_description',
            'industry', 'office_address', 'high_tech', 'website', 'comments', 'first_normal_recommend',
            'second_normal_recommend', 'first_advanced_recommend', 'expects', 'wills'];
        for (i in other_keys) {
            console.log(other_keys[i] +  ":" + $.cookie(other_keys[i]));
            $("#" + other_keys[i]).val($.cookie(other_keys[i]));
        }
    };
    GetCookie();

    // end 会员信息修改

    $('#school_start0').combodate(
        {
            customClass: "form-control",
            smartDays: true,
            minYear: 1960,
            maxYear: 2016,
            firstItem: "none"
        }
    );

    //实现城市,学校,系部字段填写时,下拉提示功能
    var callback_industry = function (data) {
        var industry_list = data['industry'];
        $(".autocomplete").autocomplete({
            source: industry_list
        });
    };
    $("#industry").focus(function () {
        var industry_name = $("#industry").val();
        jQuery.ajax(
            {
                url: '/rest/page/form_normal',
                type: "POST",
                data: {
                    'school_department': 'None',
                    'city': 'None',
                    'school': 'None',
                    'position': 'None',
                    'org': 'None',
                    'industry': industry_name
                },
                dataType: "json",
                success: callback_industry
            }
        )
    });

    var callback_city = function (data) {
        var city_list = data['city'];
        $(".autocomplete").autocomplete({
            source: city_list
        });
    };
    $("#city0").focus(function () {
        var city_name = $("#city0").val();
        jQuery.ajax(
            {
                url: '/rest/page/form_normal',
                type: "POST",
                data: {
                    'city': city_name,
                    'school': 'None',
                    'school_department': 'None',
                    'position': 'None',
                    'org': 'None',
                    'industry': 'None'
                },
                dataType: "json",
                success: callback_city
            }
        )
    });
    var callback_school = function (data) {
        var school_list = data['school'];
        $(".autocomplete").autocomplete({
            source: school_list
        });
    };
    $("#school0").focus(function () {
        var school_name = $("#school0").val();
        jQuery.ajax(
            {
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
                success: callback_school
            }
        )
    });

    var callback_school_department = function (data) {
        var school_department_list = data['school_department'];
        $(".autocomplete").autocomplete({
            source: school_department_list
        });
    };
    $("#school_department").focus(function () {
        var school_department = $("#school_department").val();
        jQuery.ajax(
            {
                url: '/rest/page/form_normal',
                type: "POST",
                data: {
                    'school_department': school_department,
                    'city': 'None',
                    'school': 'None',
                    'position': 'None',
                    'org': 'None',
                    'industry': 'None'
                },
                dataType: "json",
                success: callback_school_department
            }
        )
    });
    var callback_position = function (data) {
        var position_list = data['position'];
        $(".autocomplete").autocomplete({
            source: position_list
        });
    };
    $("#position0").focus(function () {
        var position = $("#position0").val();
        jQuery.ajax(
            {
                url: '/rest/page/form_normal',
                type: "POST",
                data: {
                    'school_department': 'None',
                    'city': 'None',
                    'school': 'None',
                    'position': position,
                    'org': 'None',
                    'industry': 'None'
                },
                dataType: "json",
                success: callback_position
            }
        )
    });
    var callback_org = function (data) {
        var org_list = data['org'];
        $(".autocomplete").autocomplete({
            source: org_list
        });
    };
    $("#org_name").focus(function () {
        var org = $("#org_name").val();
        jQuery.ajax(
            {
                url: '/rest/page/form_normal',
                type: "POST",
                data: {
                    'school_department': 'None',
                    'city': 'None',
                    'school': 'None',
                    'position': 'None',
                    'org': org,
                    'industry': 'None'
                },
                dataType: "json",
                success: callback_org
            }
        )
    });
    // 个人背景信息字数统计
    $("#person_info0").keyup(function () {
        var info_number = $("#person_info0").val().length;
        info_number = 200 - info_number;
        if (info_number > 0) {
            document.getElementById("info_number").innerHTML = "<ul>" + info_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("info_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#expects").keyup(function () {
        var expects_number = $("#expects").val().length;
        expects_number = 200 - expects_number;
        if (expects_number > 0) {
            document.getElementById("expects_number").innerHTML = "<ul>" + expects_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("expects_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#wills").keyup(function () {
        var wills_number = $("#wills").val().length;
        wills_number = 200 - wills_number;
        if (wills_number > 0) {
            document.getElementById("wills_number").innerHTML = "<ul>" + wills_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("wills_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#general_description").keyup(function () {
        var general_description_number = $("#general_description").val().length;
        general_description_number = 200 - general_description_number;
        if (general_description_number > 0) {
            document.getElementById("general_description_number").innerHTML = "<ul>" + general_description_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("general_description_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#domain_description").keyup(function () {
        var domain_description_number = $("#domain_description").val().length;
        domain_description_number = 200 - domain_description_number;
        if (domain_description_number > 0) {
            document.getElementById("domain_description_number").innerHTML = "<ul>" + domain_description_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("domain_description_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#comments").keyup(function () {
        var comments_number = $("#comments").val().length;
        comments_number = 200 - comments_number;
        if (comments_number > 0) {
            document.getElementById("comments_number").innerHTML = "<ul>" + comments_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("comments_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });

    //添加学历选项
    $(function () {
        var educations = ['请选择', '中专', '大专', '本科', '硕士研究生', '博士研究生'];
        for (i in educations) {
            if (educations[i] == '请选择') {
                $("#education0").append("<option value=''>" + educations[i] + "</option>");
            }
            else {
                $("#education0").append("<option value=" + educations[i] + ">" + educations[i] + "</option>");
            }
        }
    });
    var initCellphone = function (code, counts) {
        $.ajax({
            type: "get",
            url: "/rest/mgr/person/bind/cellphone",
            data: {
                cellphone: $("#cellphone" + counts).val(),
                vcode: code
            },
            success: function (data) {
                if (data && data.error) {
                    return alert(data.error || '添加失败！');
                }
                else if (data) {
                    for (var item in data) {
                        $("#" + item + counts).val(data[item]);
                    }
                    if (data['member_id'])
                        alert("该手机号码绑定的用户已为会员，无需重复申请");
                    else if (data['form_id'])
                        alert("该手机号码绑定的用户已提交过申请，正在审批，请耐心等候");
                }
                $("#modal-bind-cellphone").modal("hide");

            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }
    $("#bind-cellphone").click(function () {
        initCellphone($('#vcode').val(), current);

    });
    $("#bind1").click(function () {

        if (!$('#cellphone1').check().notNull()) {
            alert("手机号码不可为空");
            return false;
        }
        if (!$('#cellphone1').check().tel()) {
            alert("手机号码格式错误");
            return false;
        }
        $("#modal-bind-cellphone").modal("show");
        $('#vcode').val("");
        current = 1;
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/common/person/phone/vcode',
            data: {
                '_xsrf': $.cookie("_xsrf"),
                'phone': $('#cellphone1').val(),
                'message_type': 'bind_phone_sms'
            },
            success: function (data) {
                if (data.error)
                    alert(data.error);
                else {
                    alert(data.message);
                }

            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });
    var getInfo = function (counts) {
        return '<div class="row">' +
            '<div class="col-md-4">' +
            '<div class="form-group block1">' +
            '<label>姓名 *</label>' +
            '<input type="text" id="fullname' + counts + '" name="fullname' + counts + '" placeholder="请填写姓名" class="form-control" data-parsley-group="wizard-step-1" required value="" data-parsley-error-message="姓名不能使用除中、英、空格之外的字符,位数在2-20位" pattern="^[\u4e00-\u9fa5 a-zA-Z]{2,20}$" maxlength="20"/>' +
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<div class="form-group block1">' +
            '<label>手机号 *</label>' +
            '<input type="text" id="cellphone' + counts + '" name="cellphone' + counts + '" placeholder="请填写手机号" class="form-control" data-parsley-group="wizard-step-1" data-parsley-type="number" required value="" data-parsley-error-message="请填写合法的手机号" pattern="^1[3|4|5|7|8]\\d{9}$" maxlength="11"/>' +
            // '<a class="btn btn-info btn-xs m-t-10" id="bind'+counts+'">绑定</a>'+
            // '<span style="margin-top:5px;">通过手机号码绑定已录入过的个人信息</span>'+
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>性别 *</label>' +
            '<select class="form-control" id="gender' + counts + '" name="gender' + counts + '" data-parsley-group="wizard-step-1" required data-parsley-error-message="请选择性别">' +
            '<option value="">请选择</option>' +
            '<option value="1">男</option>' +
            '<option value="2">女</option>' +
            '</select>' +
            '</div>' +
            '</div>' +

            '</div>' +
            '<div class="row">' +
            '<div class="col-md-4">' +
            '<label>出生日期 *</label>' +
            '<div class="form-inline">' +
            '<input type="text" id="birthday' + counts + '" name="birthday' + counts + '" data-format="YYYY-MM-DD" data-template="YYYY MM DD" value="1980-06-15" class="form-inline"/>' +
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<div class="form-group block1">' +
            '<label>毕业院校 *</label>' +
            '<input type="text" id="school' + counts + '" name="school' + counts + '" placeholder="请填写毕业院校" class="form-control autocomplete" data-parsley-group="wizard-step-1" required value="" data-parsley-error-message="请填写毕业院校"  />' +
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<label>入学年份 *</label>' +
            '<div class="form-inline">' +
            '<input type="text" id="school_start' + counts + '"  name="school_start' + counts + '" data-format="YYYY-MM-DD" data-template="YYYY MM DD" value="2000-09-01" class="form-inline" />' +
            '</div>' +
            '</div>' +

            '</div>' +
            '<div class="row">' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>学历 *</label>' +
            '<select type="text" id="education' + counts + '" name="education' + counts + '" placeholder="请填写最高学历" class="form-control" data-parsley-group="wizard-step-1" required value="" data-parsley-error-message="请填写学历" />' +
            '</select>' +
            '</div>' +
            '</div>' +
            '<div class="col-md-8">' +
            '<div class="form-group block1">' +
            '<label>通讯地址 *</label>' +
            '<input class="form-control" id="address' + counts + '" name="address' + counts + '" placeholder="请留下准确的通讯地址，以便联合会可以将证书等邮寄给您"  data-parsley-group="wizard-step-1" required value="" pattern="^[0-9a-zA-Z\u4e00-\u9fa5]{2,30}$" data-parsley-error-message="请填写通讯地址" /> ' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="row">' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>申请加入的微信群 *</label>' +
            '<select class="form-control" id="weixin_group' + counts + '" name="weixin_group' + counts + '" data-parsley-group="wizard-step-1" required data-parsley-error-message="请选择微信群">' +
            '</select>' +
            '</div>' +
            '</div>' +
            '<div class="col-md-8">' +
            '<div class="form-group">' +
            '<label>微信号 *</label>' +
            '<input type="text" id="wechatid' + counts + '" name="wechatid' + counts + '" placeholder="请留下正确的微信ID号【注意，是微信唯一ID，不是微信昵称】" class="form-control" data-parsley-group="wizard-step-1" required value="" pattern="^[a-zA-Z][a-zA-Z0-9_]*$" data-parsley-error-message="请填写微信号" />' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="row">' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>所在城市 *</label>' +
            '<input type="text" id="city' + counts + '" name="city' + counts + '" placeholder="如：北京" class="form-control autocomplete" data-parsley-group="wizard-step-1" required value=""  data-parsley-error-message="请填写城市" />' +
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>邮箱 *</label>' +
            '<input type="email" id="email' + counts + '" name="email' + counts + '" placeholder="例如: you@abc.com" class="form-control" data-parsley-group="wizard-step-1" data-parsley-type="email" required value="" data-parsley-error-message="请填写合法的邮箱地址" />' +
            '</div>' +
            '</div>' +
            '<div class="col-md-4">' +
            '<div class="form-group">' +
            '<label>公司职位 *</label>' +
            '<input type="text" id="position' + counts + '" name="position' + counts + '" placeholder="请填写公司职位" class="form-control autocomplete" data-parsley-group="wizard-step-1" required value="" data-parsley-error-message="请填写职位名称" />' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="row">' +
            '<div class="col-md-12">' +
            '<div class="form-group block1">' +
            '<label>个人背景简介 *</label>' +
            '<textarea class="form-control" id="person_info' + counts + '" name="person_info' + counts + '" placeholder="请填写个人背景" rows="3" data-parsley-group="wizard-step-1" required data-parsley-error-message="个人背景不能为空" maxlength="200" ></textarea>' +
            '<ul style="text-align: right" id="info_number"></ul>' +
            '</div>' +
            '</div>' +
            '</div>';
    };
    $('#add_person').click(function () {
        counts = counts + 1;
        $('#counts').val(counts);
        $('#person').append('<div id="person' + (counts - 1) + '"><hr>' + getInfo(counts - 1) + '</div>');
        var GetCookie = function () {
            var person_keys = ['fullname', 'cellphone', 'gender', 'birthday', 'school', 'school_start',
                'education', 'address', 'weixin_group', 'wechatid', 'city', 'email', 'position', 'person_info'];
            for (i in person_keys) {
                console.log("#" + person_keys[i] + (counts-1) + ":" + $.cookie(person_keys[i] + (counts-1)));
                $("#" + person_keys[i] + (counts-1)).val($.cookie(person_keys[i] + (counts-1)));
            }
        };
        GetCookie();
        $("#birthday" + (counts - 1)).combodate(
            {
                customClass: "form-control",
                smartDays: true,
                minYear: 1945,
                maxYear: 2016,
                firstItem: "none"
            }
        );
        $('#school_start' + (counts - 1)).combodate(
            {
                customClass: "form-control",
                smartDays: true,
                minYear: 1960,
                maxYear: 2016,
                firstItem: "none"
            }
        );
        $(function () {
            var educations = ['请选择', '中专', '大专', '本科', '硕士研究生', '博士研究生'];
            for (i in educations) {
                if (educations[i] == '请选择') {
                    $("#education" + (counts - 1)).append("<option value=''>" + educations[i] + "</option>");
                }
                else {
                    $("#education" + (counts - 1)).append("<option value=" + educations[i] + ">" + educations[i] + "</option>");
                }
            }
        });
        $("#person_info" + (counts - 1)).keyup(function () {
            var info_number = $("#person_info" + (counts - 1)).val().length;
            info_number = 200 - info_number;
            if (info_number > 0) {
                document.getElementById("info_number").innerHTML = "<ul>" + info_number + "/200" + "</ul>";
            }
            else {
                document.getElementById("info_number").innerHTML = "<ul>" + "0/200" + "</ul>";
            }
        });
        var callback_city = function (data) {
            var city_list = data['city'];
            $(".autocomplete").autocomplete({
                source: city_list
            });
        };
        $("#city" + (counts - 1)).focus(function () {
            var city_name = $("#city" + (counts - 1)).val();
            jQuery.ajax(
                {
                    url: '/rest/page/form_normal',
                    type: "POST",
                    data: {
                        'city': city_name,
                        'school': 'None',
                        'school_department': 'None',
                        'position': 'None',
                        'org': 'None',
                        'industry': 'None'
                    },
                    dataType: "json",
                    success: callback_city
                }
            )
        });
        var callback_school = function (data) {
            var school_list = data['school'];
            $(".autocomplete").autocomplete({
                source: school_list
            });
        };
        $("#school" + (counts - 1)).focus(function () {
            var school_name = $("#school" + (counts - 1)).val();
            jQuery.ajax(
                {
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
                    success: callback_school
                }
            )
        });
        var callback_position = function (data) {
            var position_list = data['position'];
            $(".autocomplete").autocomplete({
                source: position_list
            });
        };
        $("#position" + (counts - 1)).focus(function () {
            var position = $("#position" + (counts - 1)).val();
            jQuery.ajax(
                {
                    url: '/rest/page/form_normal',
                    type: "POST",
                    data: {
                        'school_department': 'None',
                        'city': 'None',
                        'school': 'None',
                        'position': position,
                        'org': 'None',
                        'industry': 'None'
                    },
                    dataType: "json",
                    success: callback_position
                }
            )
        });
        $('#bind' + counts).click(function () {
            var id = $(this).attr("id");
            current = id.substring(4, id.length);
            if (!$('#cellphone' + counts).check().notNull()) {
                alert("手机号码不可为空");
                return false;
            }
            if (!$('#cellphone' + counts).check().tel()) {
                alert("手机号码格式错误");
                return false;
            }
            $("#modal-bind-cellphone").modal("show");
            $('#vcode').val("");
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/common/person/phone/vcode',
                data: {
                    '_xsrf': $.cookie("_xsrf"),
                    'phone': $('#cellphone' + counts).val(),
                    'message_type': 'bind_phone_sms'
                },
                success: function (data) {
                    if (data.error)
                        alert(data.error);
                    else {
                        alert(data.message);
                    }

                },
                error: function () {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
            return false;
        });
        $('#weixin_group' + (counts - 1)).html($('#weixin_group0').html());
        datepickerFun();
    });
    $('#remove_person').click(function () {
        if (counts == 1) {
            alert("无法再移除");
            return;
        }
        $('div').remove("#person" + (counts - 1));
        counts = counts - 1;
        $('#counts').val(counts);
    });
    var SetCookie = function () {
        var person_keys = ['fullname', 'cellphone', 'gender', 'birthday', 'school', 'school_start',
            'education', 'address', 'weixin_group', 'wechatid', 'city', 'email', 'position', 'person_info'];
        for (i in person_keys) {
            for (var j = 0; j < counts; j++) {
                console.log(person_keys[i]+ j + ":" + $("#" + person_keys[i] + j).val());
                $.cookie(person_keys[i] + j, $("#" + person_keys[i] + j).val(), {expires: 365})
            }
        }
        var other_keys = ['org_name', 'representative', 'general_description', 'domain_description',
            'industry', 'office_address', 'high_tech', 'website', 'comments', 'first_normal_recommend',
            'second_normal_recommend', 'first_advanced_recommend', 'expects', 'wills'];
        for (i in other_keys) {
            console.log(other_keys[i] +  ":" + $("#" + other_keys[i]).val());
            $.cookie(other_keys[i],$("#" + other_keys[i]).val(), {expires: 365})
        }
        console.log("setcookie");
    };
    var datepickerFun = function () {
        $(".birthday").mask("9999/99/99");
        $(".school_start").mask("9999/99/99");
    };
    datepickerFun();
    $('#btn-submit').click(function () {
        $("#btn-submit").attr("disabled", true);
        if (!$("#submit-form").parsley().validate('step1')) {
            alert("请输入所有必填项");
            $("#btn-submit").attr("disabled", false);
            return;
        }
        SetCookie();
        $.showLoading("正在提交...");
        $.ajax({
            type: "POST",
            cache: false,
            url: $("#submit-form").attr('action'),
            data: $("#submit-form").serialize(),
            success: function (data) {
                $("#btn-submit").attr("disabled", false);
                $.hideLoading();
                if (data.error) {
                    alert(data.error);
                }
                else {
                    location.href = data.page;
                }
            },
            error: function () {
                $("#btn-submit").attr("disabled", false);
                $.hideLoading();
            },
            dataType: 'json'
        });
        return false;
    });
});
