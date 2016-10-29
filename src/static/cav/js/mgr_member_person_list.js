$(function() {
    var table;
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#data-table").length !== 0) {
            var url;
            if (getQueryString('org_id') != null)
                url = "/rest/mgr/member/person/table?org_id=" + getQueryString("org_id") + "&_xsrf=" + $.cookie('_xsrf');
            else
                url = "/rest/mgr/member/person/table?_xsrf=" + $.cookie('_xsrf');

            table = $("#data-table").DataTable({
                "responsive": true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": false,
                "fnStateSave": function(oSettings, oData) {
                    save_dt_view(oSettings, oData);
                },
                "fnStateLoad": function(oSettings) {
                    return load_dt_view(oSettings);
                },
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls"
                    }]
                },
                "ajax": url,
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "p_type"
                }, {
                    "data": "org_name"
                }, {
                    "data": "certificate"
                }, {
                    "data": "p_create_date"
                }],
                "aaSorting": [4, "DESC"],
                "columnDefs": [{
                    "mRender": function(data, type, full) {
                        var head_img_url = "http://www.soozhu.com/stac/cmstpl/default2015/public/images/default_head.jpg";
                        if (full.head_img_url != "None")
                            head_img_url = full.head_img_url;
                            head_img_url.replace("http","https");
                        if (full.org_name == "None") {
                            return '<img style="width:100%;max-width:44px;border-radius:100px;margin-bottom:5px;" src="' + head_img_url + '"/>' +
                                '<br/>' + full.fullname + '<br/>';
                        }
                        else {
                            return '<img style="width:100%;max-width:44px;border-radius:100px;margin-bottom:5px;" src="' + head_img_url + '"/>' +
                                '<br/>' + full.fullname + '<br/>';
                        }
                    },
                    "targets": 0
                }, {
                    "mRender": function(data, type, full) {
                        var html = '';
                        if (full.p_status != "None") {
                            html = "<span" + " id=" + full.person_id + " >" + "状态: " + full.p_status + '</span>';
                        }
                        if (full.p_due_date == "None") {
                            html = '<p>' + html + '</p><small> 有效期至: ' + '无' + '</small>';
                        }
                        else {
                            html = '<p>' + html + '</p><small> 有效期至: ' + (full.p_due_date || '无') + '</small>';
                        }

                        if (data == 'normal_member') {
                            return "个人会员类型: " + '<span class="badge badge-primary normal-font">' + full.p_member_type + '</span>' + html;
                        } else if (data == 'advanced_member') {
                            return "个人会员类型: " + '<span class="badge badge-warning normal-font">' + full.p_member_type + '</span>' + html;
                        } else if (data == 'weixin_group') {
                            return "个人会员类型: " + '<span class="badge badge-success normal-font">' + full.p_member_type + '</span>' + html;
                        }
                        else {
                            return "个人会员类型: " + '无' + '</span>' + html;
                        }
                    },
                    "targets": 1
                }, {
                    "mRender": function(data, type, full) {
                        var html = '';
                         html = html + '<p style="font-size: 110%">' + "公司: " + '<strong>' + data + '</strong>' + '<p>';
                        return html;
                        // var html = '';
                        // if (full.org_name != "None") {
                        //     html = html + '<p style="font-size: 120%">' + "公司: " + '<strong>' + full.org_name + '</strong>' + '<p>';
                        // }
                        // else {
                        //     html = html + '<p style="font-size: 100%">' + "公司: " + "无" + '<p>';
                        // }
                        // if (data == 'advanced_org_member') {
                        //     html += "企业会员类型: " + '<span class="badge badge-danger normal-font">' + full.o_member_type + '</span>';
                        // } else if (data == 'normal_org_member') {
                        //     html += "企业会员类型: " + '<span class="badge badge-success normal-font">' + full.o_member_type + '</span>';
                        // }
                        // else {
                        //     html += "企业会员类型: " + '无' + '</span>';
                        // }
                        // if (full.o_status != "None") {
                        //     html += '<p>' + "状态: " + full.o_status + '</span>';
                        // }
                        // else {
                        //     html += '<p>' + "状态: " + '无' + '</span>';
                        // }
                        // if (full.o_due_date == "None") {
                        //     html = '<p>' + html + '</p><small> 有效期至: ' + '无' + '</small>';
                        // }
                        // else {
                        //     html = '<p>' + html + '</p><small> 有效期至: ' + (full.o_due_date || '无') + '</small>';
                        // }
                        // if (full.is_primary == 1) {
                        //     return html + '<p>' + "是否代表: " + "是"
                        // }
                        // else {
                        //     return html + '<p>' + "是否代表: " + "否"
                        // }
                    },
                    "targets": 2
                },
                    {
                        "mRender": function(data, type, full) {
                            if (data == 1 || data == "1")
                                return "是";
                            else
                                return "否";
                        },
                        "targets": 3
                    }, {
                        "mRender": function(data, type, full) {
                            var html = '';
                            if (data == 'None') {
                                if (full.o_create_date == 'None') {
                                    html += "企业会员: " + '无';
                                }
                                else {
                                    html += "企业会员: " + full.o_create_date;
                                }
                                return "个人会员: " + "无" + '<p>' + html;
                            }
                            else {
                                if (full.o_create_date == 'None') {
                                    html += "企业会员: " + '无';
                                }
                                else {
                                    html += "企业会员: " + full.o_create_date;
                                }
                                return "个人会员: " + data + '<p>' + html;
                            }
                        },
                        "targets": 4
                    }, {
                        "mRender": function(data, type, full) {
                            var html = "";
                            html += '<a onclick="$._showPersonDetail(\'' + full.person_id + '\')" class="btn btn-info btn-xs m-r-5">详情</a>';
                            if (full.p_type != 'None') {
                                html += '<a onclick="$._changeMemberStatus(\'' + full.person_id + '\')" class="btn btn-success btn-xs">会员状态</a>';
                            }
                            if (getQueryString('org_id') != null) {
                                html += '<a onclick="$._deletePerson(\'' + full.person_id + '\')" class="btn btn-danger btn-xs">删除</a>';
                            }
                            if (full.person_id != 'None') {
                                html += '<a href="edit_member_info?person_id=' + full.person_id + '&redirect_url=' + location.pathname + '" class="btn btn-xs btn-warning m-l-5">修改</a>';
                            }
                            html += '<a onclick="$._showDeliveryInfo(\'' + full.person_id + '\')" class="btn btn-inverse btn-xs m-l-5">个人名片</a>';
                            if ((full.p_type != 'None' ) && $('#roles').val().indexOf('operator') > 0)
                                html += '<a onclick="$._editPaidInfo(\'' + full.person_id + '\',\'' + full['type'] + '\')" class="btn btn-info btn-xs m-l-5">缴费管理</a>';
                            return html;

                            // '<a href="javascript:;" class="btn btn-warning btn-xs m-r-5">缴费</a>' +
                            // '<a href="javascript:;" class="btn btn-success btn-xs m-r-5">更多</a>';
                        },
                        "targets": 5
                    }],
                "language": TABLE_LANG
            })
        }
    };

    var data_reload = function(tag) {
        IDs = ["weixin_group", "normal_member", "advanced_member", "normal_org_member", "advanced_org_member"];
        for (i in IDs) {
            tag = "#" + IDs[i];
            if ($(tag).is(':checked')) {
                $(tag).val(1);
            }
            else {
                $(tag).val("");
            }
        }
        var weixin_group = $("#weixin_group").val();
        var normal_member = $("#normal_member").val();
        var advanced_member = $("#advanced_member").val();
        var normal_org_member = $("#normal_org_member").val();
        var advanced_org_member = $("#advanced_org_member").val();
        parameter = "&weixin_group=" + weixin_group + "&normal_member=" + normal_member + "&advanced_member=" + advanced_member + "&normal_org_member=" + normal_org_member + "&advanced_org_member=" + advanced_org_member;
        var url;
        if (getQueryString('org_id') != null)
            url = "/rest/mgr/member/person/table?org_id=" + getQueryString("org_id") + parameter + "&_xsrf=" + $.cookie('_xsrf');
        else
            url = "/rest/mgr/member/person/table?" + parameter.substr(1) + "&_xsrf=" + $.cookie('_xsrf');
        table.ajax.url(url).load();
    };

    $("#weixin_group").click(function() {
        data_reload("weixin_group")
    });
    $("#normal_member").click(function() {
        data_reload("normal_member")
    });
    $("#advanced_member").click(function() {
        data_reload("advanced_member")
    });
    $("#normal_org_member").click(function() {
        data_reload("normal_org_member")
    });
    $("#advanced_org_member").click(function() {
        data_reload("advanced_org_member")
    });

    $("#add_person").click(function() {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/org/add/cellphone',
            data: {
                org_id: $("#org_id").val(),
                cellphone: $("#add_cellphone").val(),
                is_primary: $("#is_primary").val()
            },
            success: function(data) {
                if (data.error) {
                    alert(data.error);
                    return
                }
                alert(data.message);
                location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });
    // $("#birthday").mask("9999/99/99");
    // $("#school_start").mask("9999/99/99");
    $("#org_id").val(getQueryString("org_id"));
    $("#btn_addperson").click(
        function() {
            if (getQueryString("org_id") != null) {
                $("#modal-form-person").modal("show");
                $("#org_id").val(getQueryString("org_id"));

            }
        }
    );

    $("#save_person").click(function() {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/org/add/person?org_id=' + getQueryString("org_id"),
            data: $('#form_info').serialize(), // 你的formid
            dataType: 'json',
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                if (data.message) {
                    location.reload();
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });

    });

    var TableManageResponsive = function() {
        "use strict";
        return {
            init: function() {
                handleDataTableResponsive();
            }
        }
    }();

    TableManageResponsive.init();
    $._deletePerson = function(person_id) {
        var org_id = getQueryString("org_id");
        if (org_id != null) {
            if (confirm("你确定移除该成员吗？")) {
                $.ajax({
                    type: "post",
                    cache: false,
                    url: '/rest/mgr/org/remove',
                    data: {
                        org_id: org_id,
                        person_id: person_id
                    },
                    success: function(data) {
                        if (data.error) {
                            return alert(data.error);
                        }
                        alert(data.message);
                        location.reload();
                    },
                    error: function() {
                        alert('网络错误！');
                    },
                    dataType: 'json'
                });
            }
        } else {
            if (confirm("你确定要删除该会员吗?")) {
                $.ajax({
                    type: "get",
                    cache: false,
                    url: '/rest/mgr/member/delete',
                    data: {
                        member_id: person_id
                    },
                    success: function(data) {
                        if (data.error) {
                            return alert(data.error || '删除失败！');
                        }
                        window.location.reload();
                    },
                    error: function() {
                        alert('网络错误！');
                    },
                    dataType: 'json'
                });
            }

        }
        ;
    };
    // 修改会员状态
    $._changeMemberStatus = function(person_id) {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/member/status/change',
            data: {
                person_id: person_id
            },
            success: function(data) {
                // if(data.error){
                //     return alert(data.error || '获取失败！');
                // }
                $('#changeMemberStatus').modal('show');
                var member_status = '<span class="badge badge-success normal-font">' + data.member_status + '</span>';
                member_status += '<input ' + "type='hidden' " + 'value=' + person_id + ' id=' + "'click_person'" + ' />';
                $('#member_status').html(member_status);
                var html = '';
                html += '<option' + ' ' + 'value' + '=' + data.member_status + '>' + data.member_status + '</' + 'option>';
                for (item in data.all_status) {
                    if (data.all_status[item] != data.member_status) {
                        html += '<option' + ' ' + 'value' + '=' + data.all_status[item] + '>' + data.all_status[item] + '</' + 'option>'
                    }
                }

                $('#select_status').html(html)
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $('#save_status').click(function() {
        var person_id = $('#click_person').val();
        var member_status = $('#select_status').val();
        $.ajax({
            type: "post",
            cache: false,
            url: "/rest/mgr/member/status/save",
            data: {
                person_id: person_id,
                member_status: member_status
            },
            success: function(data) {
                var html = "<span" + " id=" + person_id + " >" + "状态: " + member_status + '</span>';
                $('#' + person_id).replaceWith(html)
            }
        })
    });


    $._showDeliveryInfo = function(id) {
        $('#modal-link-delivery-info').modal('show');
        $('#modal-link-delivery-info img').attr('src', '/rest/qrcode?link=' + '/page/delivery_info_' + id);
        $('#modal-link-delivery-info a[target=app_link]').attr('href', '/page/delivery_info_' + id);
        $('#modal-link-delivery-info textarea').val(location.protocol + '//' + location.hostname + '/page/delivery_info_' + id);
    };

});



