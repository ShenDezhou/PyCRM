$(function() {

    var handleBootstrapWizardsValidation = function() {
        "use strict";
        $("#wizard").bwizard({
            'validating': function(e, t) {
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
    $('#birthday').combodate(
        {
            customClass: "form-control",
            smartDays: true,
            minYear: 1945,
            maxYear: 2016,
            firstItem: "none"
        }
    );
    $('#school_start').combodate(
        {
            customClass: "form-control",
            smartDays: true,
            minYear: 1960,
            maxYear: 2016,
            firstItem: "none"
        }
    );
    // start 从cookie读取表单信息
    var GetCookie = function() {
        var person_keys = ['fullname', 'cellphone', 'gender', 'birthday', 'school', 'school_start',
            'education', 'address', 'weixin_group', 'wechatid', 'city', 'email', 'position', 'person_info',
            'school_department', 'school_number'];
        for (i in person_keys) {
            if ((person_keys[i] == 'school_start' || person_keys[i] == 'birthday') && $.cookie(person_keys[i]) == null) {
                $("#school_start").val("2000-09-01");
                $("#birthday").val("1980-09-01");
            } else {
                $("#" + person_keys[i]).val($.cookie(person_keys[i]));
            }
            // console.log(person_keys[i] + ":" + $.cookie(person_keys[i]));
        }
        var other_keys = ['org_name', 'representative', 'general_description', 'domain_description',
            'industry', 'office_address', 'high_tech', 'website', 'comments', 'first_normal_recommend',
            'second_normal_recommend', 'first_advanced_recommend', 'expects', 'wills'];
        for (i in other_keys) {
            // console.log(other_keys[i] + ":" + $.cookie(other_keys[i]));
            $("#" + other_keys[i]).val($.cookie(other_keys[i]));
        }
    };
    GetCookie();
    // end 从cookie读取表单信息

    //实现城市,学校,系部字段填写时,下拉提示功能
    var callback_industry = function(data) {
        var industry_list = data['industry'];
        $(".autocomplete").autocomplete({
            source: industry_list
        });
    };
    $("#industry").focus(function() {
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

    var callback_city = function(data) {
        var city_list = data['city'];
        $(".autocomplete").autocomplete({
            source: city_list
        });
    };
    $("#city").focus(function() {
        var city_name = $("#city").val();
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
    var callback_school = function(data) {
        var school_list = data['school'];
        // console.log(school_list);
        $(".autocomplete").autocomplete({
            source: school_list
        });
    };
    $("#school").focus(function() {
        var school_name = $("#school").val();
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

    var callback_school_department = function(data) {
        var school_department_list = data['school_department'];
        $(".autocomplete").autocomplete({
            source: school_department_list
        });
    };
    $("#school_department").focus(function() {
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
    var callback_position = function(data) {
        var position_list = data['position'];
        $(".autocomplete").autocomplete({
            source: position_list
        });

    };
    $("#position").focus(function() {
        var position = $("#position").val();
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
    var callback_org = function(data) {
        var org_list = data['org'];
        $(".autocomplete").autocomplete({
            source: org_list
        });
    };
    $("#org_name").focus(function() {
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
    $("#person_info").keyup(function() {
        var info_number = $("#person_info").val().length;
        info_number = 200 - info_number;
        if (info_number > 0) {
            document.getElementById("info_number").innerHTML = "<ul>" + info_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("info_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#expects").keyup(function() {
        var expects_number = $("#expects").val().length;
        expects_number = 200 - expects_number;
        if (expects_number > 0) {
            document.getElementById("expects_number").innerHTML = "<ul>" + expects_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("expects_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#wills").keyup(function() {
        var wills_number = $("#wills").val().length;
        wills_number = 200 - wills_number;
        if (wills_number > 0) {
            document.getElementById("wills_number").innerHTML = "<ul>" + wills_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("wills_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#general_description").keyup(function() {
        var general_description_number = $("#general_description").val().length;
        general_description_number = 200 - general_description_number;
        if (general_description_number > 0) {
            document.getElementById("general_description_number").innerHTML = "<ul>" + general_description_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("general_description_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#domain_description").keyup(function() {
        var domain_description_number = $("#domain_description").val().length;
        domain_description_number = 200 - domain_description_number;
        if (domain_description_number > 0) {
            document.getElementById("domain_description_number").innerHTML = "<ul>" + domain_description_number + "/200" + "</ul>";
        }
        else {
            document.getElementById("domain_description_number").innerHTML = "<ul>" + "0/200" + "</ul>";
        }
    });
    $("#comments").keyup(function() {
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
    $(function() {
        var educations = ['请选择', '中专', '大专', '本科', '硕士研究生', '博士研究生'];
        for (index in educations) {
            if (educations[index] == '请选择') {
                $("#education").append("<option value=''>" + educations[index] + "</option>");
            }
            else {
                $("#education").append("<option value=" + educations[index] + ">" + educations[index] + "</option>");

            }
        }
    });
    // $("#birthday").mask("9999/99/99");
    // $("#school_start").mask("9999/99/99");
    // birthday.datepicker({
    //     format: 'yyyy-mm-dd',
    //     changMonth:true,
    //     yearRange : 'yyyy-50:yyyy+1',
    //     changYear:true
    // }).on('changeDate', function(ev) {
    //     $('.datepicker').hide();
    // });
    // school_start.datepicker({
    //     format: 'yyyy-mm-dd'
    // }).on('changeDate', function(ev) {
    //     $('.datepicker').hide();
    // });
    $("#student").hide();
    $("#check_student").click(function() {
        if ($('#check_student').is(":checked")) {
            $("#student").show();
        } else {
            $("#student").hide();
        }
    });
    $("#bind-cellphone").click(function() {
        $.ajax({
            type: "get",
            url: "/rest/mgr/person/bind/cellphone",
            data: {
                cellphone: $("#cellphone").val(),
                vcode: $("#vcode").val()
            },
            success: function(data) {
                if (data && data.error) {
                    return alert(data.error || '添加失败！');
                }
                $("#modal-bind-cellphone").modal("hide");
                $("#phonecode").val($("#vcode").val());
                if (data) {
                    for (var item in data) {
                        $("#" + item).val(data[item]);
                    }
                    if (data['school_department']) {
                        $("#check_student").prop("checked", true);
                        $("#student").show();
                        if (data['attachment'])
                            $.initPreviewImageForTicket(data['attachment'].split(','));
                    } else {
                        $("#check_student").prop("checked", false);
                        $("#student").hide();
                        $.initPreviewImageForTicket([]);
                    }
                    if (data['member_id'])
                        alert("该手机号码绑定的用户已为会员，无需重复申请");
                    else if (data['form_id'])
                        alert("该手机号码绑定的用户已提交过申请，正在审批，请耐心等候");
                }

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        return false;
    });
    var util = {
        wait: 0,
        hsTime: function(that) {
            _this = $(this);
            if (util.wait <= 0) {
                $('#bind').removeAttr("disabled").text('绑定');
                util.wait = 0;
            } else {
                var _this = this;
                $('#bind').attr("disabled", true).text('在' + util.wait + '秒后点此重发');
                util.wait--;
                setTimeout(function() {
                    util.hsTime(that);
                }, 1000)
            }
        }
    };
    $("#bind").click(function() {
        if (util.wait > 0) {
            return alert('请稍后再点击发送验证码！');
        }
        if (!$('#cellphone').check().notNull()) {
            alert("手机号码不可为空");
            return false;
        }
        if (!$('#cellphone').check().tel()) {
            alert("手机号码格式错误");
            return false;
        }
        $("#modal-bind-cellphone").modal("show");
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/common/person/phone/vcode',
            data: {
                '_xsrf': $.cookie("_xsrf"),
                'phone': $('#cellphone').val(),
                'message_type': 'bind_phone_sms'
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
        return false;
    });
    var SetCookie = function() {
        var person_keys = ['fullname', 'cellphone', 'gender', 'birthday', 'school', 'school_start',
            'education', 'address', 'weixin_group', 'wechatid', 'city', 'email', 'position', 'person_info',
            'school_department', 'school_number'];
        for (i in person_keys) {
            // console.log(person_keys[i] + ":" + $("#" + person_keys[i]).val());
            $.cookie(person_keys[i], $("#" + person_keys[i]).val(), {expires: 365})
        }
        var other_keys = ['org_name', 'representative', 'general_description', 'domain_description',
            'industry', 'office_address', 'high_tech', 'website', 'comments', 'first_normal_recommend',
            'second_normal_recommend', 'first_advanced_recommend', 'expects', 'wills'];
        for (i in other_keys) {
            // console.log(other_keys[i] + ":" + $("#" + other_keys[i]).val());
            $.cookie(other_keys[i], $("#" + other_keys[i]).val(), {expires: 365})
        }
        // console.log("setcookie");
    };
    $('#btn-submit').click(function() {
        $("#btn-submit").attr("disabled", true);
        if (!$("#submit-form").parsley().validate('step1')) {
            alert("请输入所有必填项");
            $("#btn-submit").attr("disabled", false);
            return;
        }
        $.showLoading("正在提交...");
        SetCookie();
        $.ajax({
            type: "POST",
            cache: false,
            url: $("#submit-form").attr('action'),
            data: $("#submit-form").serialize(),
            success: function(data) {
                $("#btn-submit").attr("disabled", false);
                $.hideLoading();
                if (data.error) {
                    alert(data.error);
                }
                else {

                    location.href = data.page;
                }
            },
            error: function() {
                $.hideLoading();
                $("#btn-submit").attr("disabled", false);
            },
            dataType: 'json'
        });
        return false;
    });
});
