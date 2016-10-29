$(function() {
    var handleDataTableResponsive = function() {
        "use strict";
        if ($("#data-table").length !== 0) {
            $("#data-table").DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": false,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
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
                "ajax": "/rest/mgr/weixin/contact/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "fullname"
                }, {
                    "data": "nick_name"
                }, {
                    "data": "head_img_url",
                    "mRender": function(data, type, full) {
                        return "<img style='max-width:220px' src='" + data + "'/>"
                    }
                }, {
                    "data": "sex",
                    "mRender": function(data, type, full) {
                        if (data == 1)
                            return "男";
                        else
                            return "女";
                    }
                }, {
                    "data": "cellphone"
                }, {
                    "data": "auth_date"
                }, {
                    "data": "kf_account"
                }, {
                    "data": "kf_id"
                }, {
                    "data": "kf_nickname"
                }, {
                    "data": "invite_wx"
                },{
                    "data": "invite_status"
                }, {
                    "data": "auth_id",
                    "mRender": function(data, type, full) {
                        var html = '<a class="btn btn-warning btn-xs" style="margin-left:5px;" onclick=$._showDeliveryInfo("' + data + '","' + full['kf_account'] + '","' + full['kf_nickname'] + '","' + full['invite_wx'] + '")>' + '修改' + '</a>';
                        html += '<a class="btn btn-warning btn-xs" style="margin-left:5px;" onclick=$._refreshList("' + data + '","' + full['kf_account'] + '")>' + '刷新' + '</a>';
                        html += '<a class="btn btn-danger btn-xs" onclick=$._changeStatus("' + data + '","' + full['kf_account'] + '") style="margin-left:5px;">' + '删除' + '</a>';
                        html += '<a class="btn btn-danger btn-xs" onclick=$._uploadimg(\'' + full['kf_account'] + '\',\'' + full['head_img_url'] + '\') style="margin-left:5px;">' + '头像上传' + '</a>';
                        return html;
                    }
                }],
                "aaSorting": [5, 'desc'],
                "columnDefs": [],
                "language": TABLE_LANG
            })
        }
    };
    var TableManageResponsive = function() {
        "use strict";
        return {
            init: function() {
                handleDataTableResponsive();
            }
        }
    }();

    TableManageResponsive.init();
    $._showDeliveryInfo = function(id, account, nickname, invite_wx) {
        $('#modal-link-delivery-info').modal('show');
        $('#auth_id').val(id);
        $('#account').val(account);
        $('#nickname').val(nickname);
        $('#invite_wx').val(invite_wx);
       
    };
    $("#contact-save").click(function() {
        if (!$('#account').parsley().isValid() || !$('#nickname').parsley().isValid())
            return false;
        var postData = { _xsrf: $.cookie("_xsrf") };
        postData.auth_id = $('#auth_id').val();
        postData.kf_account = $('#account').val();
        postData.nickname = $('#nickname').val();
        postData.invite_wx = $('#invite_wx').val();
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/contact/edit',
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                window.location.reload();
                console.log(data);
            },
            error: function(e) {
                alert("网络错误！");
                console.error(e);
            },
            dataType: 'json'
        });
    });
    $._refreshList = function(id, account) {
        var postData = { _xsrf: $.cookie("_xsrf") };
        postData.auth_id = id;
        postData.kf_account = account;
        $.ajax({
            type: "post",
            cache: false,
            url: '/wechat/contact/lst',
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                window.location.reload();

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $._changeStatus = function(auth_id, kf_account) {
        var statu = true;
        statu = confirm("你确定要删除吗？");

        if (statu) {
            $.ajax({
                type: "POST",
                url: '/rest/mgr/contact/delete',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    auth_id: auth_id,
                    kf_account: kf_account
                },
                success: function(data) {
                    if (data.error) {
                        return alert(data.error || '登录失败！');
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        }
    };
    $._uploadimg = function(kf_account,url) {
        console.log(url);
        $.ajax({
            type: "POST",
            url: '/rest/mgr/contact/upload',
            data: {
                _xsrf: $.cookie("_xsrf"),
                kf_account: kf_account,
                url: url
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '登录失败！');
                }
                window.location.reload();
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
        
    };
    var memberPersonInfo = function(person_info) {
        $('#weixin_group').val(person_info[0]['weixin_group']);
        var output = personInfoTitle();
        output += "<tr><td>联合会微信群友推荐人1</td><td class='first_normal_recommend'></td></tr>";
        output += "<tr><td>联合会微信群友推荐人2</td><td class='second_normal_recommend'></td></tr>";
        output += "<tr><td>期望获取哪些服务或资源</td><td class='expects'></td></tr>";
        output += "<tr><td>可提供哪些服务或资源</td><td class='wills'></td></tr>";
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
                    else if (person_info[i][key] == 1)
                        $('#member_person_info_table' + i + ' .' + key).html('男');
                } else
                    $('#member_person_info_table' + i + ' .' + key).html(person_info[i][key]);
            }


        }


    };
    var memberOrgInfo = function(org_info) {
        var output = orgInfoTitle();
        $('#member_org_info_table tbody').html(output);
        for (var key in org_info) {
            $('#member_org_info_table .' + key).html(org_info[key]);
        }

    };
    var initWeixinGroup = function(groups) {
        var output = "<option>未分配微信群</option>";
        for (var index in groups) {
            output += "<option value='" + groups[index]['tag_id'] + "'>" + groups[index]['tag_name'] + "</option>";
        }
        $('#weixin_group').html(output);
    }
    var getMemberDetailInfo = function(person_id) {
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/person/org/detail',
            data: {
                person_id: person_id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                initWeixinGroup(data['weixin_group']);
                memberPersonInfo(data['person']);
                memberOrgInfo(data['org'][0]);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $._showMemberDetail = function(id) {
        getMemberDetailInfo(id);
        $('#modal-member-detail').modal('show');
        $('#modal-member-detail .nav li').each(function() {
            $(this).removeClass("active");
        });
        $('#modal-member-detail .tab-content div').each(function() {
            $(this).removeClass("active in");
        });
        $("#modal-member-detail .nav li:nth-child(1)").addClass("active");
        $("#modal-member-detail .tab-content div:nth-child(1)").addClass("active in");
        $('#save').click(function() {
            var postData = { _xsrf: $.cookie("_xsrf") };
            postData.weixin_group = $('#weixin_group').val();
            postData.person_id = id;
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/person/weixin_group/edit',
                data: postData,
                success: function(data) {
                    if (data.error) {
                        return alert(data.error);
                    }
                    window.location.reload();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        });
    };

});
