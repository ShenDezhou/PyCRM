$(function () {

    var table;
    var handleDataTableResponsive = function () {
        "use strict";
        if ($("#data-table").length !== 0) {
            table = $("#data-table").DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": false,
                "fnStateSave": function (oSettings, oData) {
                    save_dt_view(oSettings, oData);
                },
                "fnStateLoad": function (oSettings) {
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
                "ajax": "/rest/mgr/member/org/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "org_name"
                }, {
                    "data": "apply_member_type"
                }, {
                    "data": "due_date"
                }, {
                    "data": "create_date"
                }, {
                    "data": "org_id"
                }],
                "aaSorting": [3, 'desc'],
                "columnDefs": [{
                    "mRender": function (data, type, full) {
                        if (full.is_primary == 1 || full.is_primary == '1') {
                            return '<div class="row">' +
                                '<div class="col-xs-7">公司名称：' +
                                full.org_name + '<br/>' +
                                (full.primaries) +
                                '</div>' +
                                '</div>';
                        }
                        else {
                            return '<div class="row">' +
                                '<div class="col-xs-7">公司名称：' +
                                full.org_name + '<br/>' +
                                '</div>' + '</div>';
                        }
                    },
                    "targets": 0
                }, {
                    "mRender": function (data, type, full) {
                        if (full.apply_member_type == '企业普通会员') {
                            return '<span class="badge badge-success normal-font">' + full.apply_member_type + '</span>';
                        } else if (full.apply_member_type == '企业理事会员') {
                            return '<span class="badge badge-danger normal-font">' + full.apply_member_type + '</span>';
                        } else {
                            return "";
                        }
                    },
                    "targets": 1
                }, {
                    "mRender": function (data, type, full) {
                        var html = '';
                        if (full.status != 'None') {
                            html = '<span class="badge badge-info normal-font"' + ' id' + '=' + full.org_id + ' >' + full.status + '</span>';
                        }
                        if (full.due_date != 'None') {
                            return '<p>' + html + '</p><small> 有效期至:' + (full.due_date || '暂无') + '</small>';
                        }
                        else {
                            return ""
                        }
                    },
                    "targets": 2
                }, {
                    "mRender": function (data, type, full) {
                        if (data == 'None')
                            return "";
                        else
                            return data;
                    },
                    "targets": 3
                }, {
                    "mRender": function (data, type, full) {
                        var html = '';
                        html += '<a onclick="$._showOrgDetail(\'' + full.org_id + '\',\'org\')" class="btn btn-info btn-xs m-r-5">详情</a>';
                        if (full.apply_member_type != 'None') {
                            html += '<a onclick="$._changeMemberStatus(\'' + full.org_id + '\')" class="btn btn-success btn-xs m-r-5">会员状态</a>';
                        }
                        // html += '<a onclick="$._deleteMember(\'' + full.org_id + '\')" class="btn btn-danger btn-xs m-r-5">删除</a>';
                        html += '<a href="edit_member_info?org_id=' + full.org_id + '&redirect_url=' + location.pathname + '" class="btn btn-xs btn-warning m-r-5">修改</a>';
                        html += '<a class="btn btn-primary btn-xs m-r-5" style="margin-left:5px;" href="/console/member_person_list?org_id=' + full['org_id'] + '">' + '人员管理' + '</a>';
                        html += '<a onclick="$._editPaidInfo(\'' + full.org_id + '\',\'' + full['apply_member_type'] + '\')" class="btn btn-warning btn-xs m-r-5">缴费管理</a>';
                        return html;
                    },
                    "targets": 4
                }],
                "language": TABLE_LANG
            })
        }
    };
    var data_reload = function (tag) {
        IDs = ["normal_org_member", "advanced_org_member"];
        for (i in IDs) {
            tag = "#" + IDs[i];
            if ($(tag).is(':checked')) {
                $(tag).val(1);
            }
            else {
                $(tag).val("");
            }
        }
        var normal_org_member = $("#normal_org_member").val();
        var advanced_org_member = $("#advanced_org_member").val();
        parameter = "&normal_org_member=" + normal_org_member + "&advanced_org_member=" + advanced_org_member;
        var url = "/rest/mgr/member/org/table?_xsrf=" + parameter;
        table.ajax.url(url).load();
    };
    $("#normal_org_member").click(function () {
        data_reload("normal_org_member")
    });
    $("#advanced_org_member").click(function () {
        data_reload("advanced_org_member")
    });
    $._showDeliveryInfo = function (id) {
        $('#modal-link-delivery-info').modal('show');
        $('#modal-link-delivery-info img').attr('src', '/rest/qrcode?link=' + '/page/delivery_info_' + id);
        $('#modal-link-delivery-info a[target=app_link]').attr('href', '/page/delivery_info_' + id);
        $('#modal-link-delivery-info textarea').val(location.protocol + '//' + location.hostname + '/page/delivery_info_' + id);
    };
    var TableManageResponsive = function () {
        "use strict";
        return {
            init: function () {
                handleDataTableResponsive();
            }
        }
    }();

    TableManageResponsive.init();
    $._deleteMember = function (id) {
        if (confirm("你确定要删除该会员吗?")) {
            $.ajax({
                type: "get",
                cache: false,
                url: '/rest/mgr/member/delete',
                data: {
                    member_id: id
                },
                success: function (data) {
                    if (data.error) {
                        return alert(data.error || '删除失败！');
                    }
                    window.location.reload();
                },
                error: function () {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        }
    };
    $._removePerson = function (form_id, person_id) {
        if (confirm("你确定移除该成员吗？")) {
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/org/remove',
                data: {
                    form_id: form_id,
                    person_id: person_id
                },
                success: function (data) {
                    if (data.error) {
                        return alert(data.error);
                    }
                    alert(data.message);
                    location.reload();
                },
                error: function () {
                    alert('网络错误！');
                },
                dataType: 'json'
            });
        }
    };
    var personEditInfo = function (form_id, person_info) {
        var output = personInfoTitle();
        var tables = '';
        for (var i in person_info) {
            tables += '<a class="btn btn-sm btn-danger m-b-5" onclick=$._removePerson("' + form_id + '","' + person_info[i]['person_id'] + '") >移除</a>'
            tables += '<a onclick="$._showDeliveryInfo(\'' + person_info[i]['person_id'] + '\')" class="btn btn-primary btn-xs m-l-5">个人名片</a>';
            tables += '<table id="person_info_table' + i + '" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        }
        $('#div_edit_person').html(tables);
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
    $("#add_person").click(function () {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/org/add/cellphone',
            data: {
                form_id: $("#form_id").val(),
                cellphone: $("#add_cellphone").val()
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                alert(data.message);
                location.reload();
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });
    $("#birthday").mask("9999/99/99");
    $("#school_start").mask("9999/99/99");
    $._editPerson = function (form_id) {
        $("#modal-form-person").modal("show");
        $("#form_id").val(form_id);
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/form/detail',
            data: {
                form_id: form_id
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                personEditInfo(form_id, data['person']);
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };

    $("#save_person").click(function () {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/org/add/person?form_id=' + $("#form_id").val(),
            data: $('#form_info').serialize(), // 你的formid
            dataType: 'json',
            success: function (data) {
                if (data.error)
                    alert(data.error);
                if (data.message) {
                    location.reload();
                }
            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });

    });
    var memberInfo = function (form_info, person_will) {
        var output = "";
        // form_info =;
        // person_will = person_will[0];
        for(index in form_info){
            for (var key in form_info[index]) {
            $('#member_info_table .' + key).html(form_info[index][key]);
        }
        }
        output += "<tr><td>会员类型</td><td class='apply_member_type'></td></tr>";
        output += "<tr><td>缴费金额</td><td class='paid_money'></td></tr>";
        output += "<tr><td>有效期至</td><td class='paid_end_time'></td></tr>";
        output += "<tr><td>支付方式</td><td class='paid_type'></td></tr>";
        output += willAndExpect();
        $('#member_info_table tbody').html(output);
        for (var key in form_info) {
            $('#member_info_table .' + key).html(form_info[key]);
        }
        for (var key in person_will) {
            $('#member_info_table .' + key).html(person_will[key]);
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
                    else if (person_info[i][key] == 1)
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

                if (form_info['apply_member_type'] == "normal_member" || form_info['apply_member_type'] == "advanced_member")
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
    };
    // 修改会员状态
    $._changeMemberStatus = function (org_id) {
        $.ajax({
            type: "post",
            cache: false,
            url: '/rest/mgr/member/status/change',
            data: {
                org_id: org_id
            },
            success: function (data) {
                // if(data.error){
                //     return alert(data.error || '获取失败！');
                // }
                $('#changeMemberStatus').modal('show');
                var member_status = '<span class="badge badge-success normal-font">' + data.member_status + '</span>';
                member_status += '<input ' + "type='hidden' " + 'value=' + org_id + ' id=' + "'click_org'" + ' />';
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
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $('#save_status').click(function () {
        var org_id = $('#click_org').val();
        var member_status = $('#select_status').val();
        $.ajax({
            type: "post",
            cache: false,
            url: "/rest/mgr/member/status/save",
            data: {
                org_id: org_id,
                member_status: member_status
            },
            success: function (data) {
                var html = '<span class="badge badge-info normal-font"' + ' id' + '=' + org_id + ' >' + member_status + '</span>';
                $('#' + org_id).replaceWith(
                    html
                )
            }
        })
    });
    var memberHandleInfo = function (org, person) {
        $('#person_member').hide();
        tagInfo(org['tag_group']);
        // $('#tag_group').val(member['tag_group']);

    };
    var getOrgDetailInfo = function (org_id) {
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/org/member/detail',
            data: {
                org_id: org_id
            },
            success: function (data) {
                if (data.error) {
                    return alert(data.error);
                }
                // start --如果企业是会员
                $("#person_info").remove();
                if (data['type'] == 'member') {
                    // memberPersonInfo(data['person']);
                    memberOrgInfo(data['org'], data['person'], data['form']);
                    memberInfo(data['form'], data['person']);
                    // $("#member_control").hide();
                    memberHandleInfo(data['org'], data['person']);
                }
                // end --如果企业是会员
                else {

                }

            },
            error: function () {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $._showOrgDetail = function (org_id, detail_type) {
        g_detail_type = detail_type;
        getOrgDetailInfo(org_id);
        $('#modal-member-detail').modal('show');
        $('#modal-member-detail .nav li').each(function () {
            $(this).removeClass("active");
        });
        $('#modal-member-detail .tab-content div').each(function () {
            $(this).removeClass("active in");
        });
        $("#modal-member-detail .nav li:nth-child(1)").addClass("active");
        $("#modal-member-detail .tab-content div:nth-child(1)").addClass("active in");
        $('#save').click(function () {
            var postData = {_xsrf: $.cookie("_xsrf")};
            postData.form_id = id;
            var str = "";
            $("#tag_group option:selected").each(function () {
                str += $(this).text() + ",";
            });
            postData.tag_group = str.substring(0, str.length - 1);
            $.ajax({
                type: "post",
                cache: false,
                url: '/rest/mgr/org/edit',
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
    };
    $('#btn_export').click(function(){
        if(isIE(7) || isIE(8) || isIE(9) || isIE(10) || isIE(11)){
            if(confirm("导出功能不能支持本浏览器，请改用360、火狐、谷歌Chrome等浏览器下载。点击确定转到浏览器下载页面，点击取消留在本页。")){
                location.href = '/old_msie';
            }
            return;
        }
        var params=table.ajax.params();
        var filename = $(this).attr('filename');
        params['export']=true;
        params.cols = encodeURIComponent("org_name,contacts,office_address,industry,general_description,domain_description,first_normal_recommend,paid_money,create_date,due_date");
        params.headers = encodeURIComponent("企业名称,代表人,办公地址,行业,公司简介,业务范围,推荐人,缴费金额,入会日期,到期时间");
        params.filename = encodeURIComponent(filename);
        var url = "/rest/mgr/member/org/table/export?_xsrf=" + $.cookie('_xsrf')//table.ajax.url();
        console.log(url);
        if(url.indexOf('?') < 0) {
            url += '?';
        }else{
            url += '&';
        }

        url += decodeURIComponent( $.param( params ) );
        $.fileDownload(url, {
            successCallback: function (url) {
            },
            failCallback: function (responseHtml, url) {
                alert('下载失败');
            }
        });
    });
});
