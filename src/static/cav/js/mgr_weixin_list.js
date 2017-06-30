$(function(){
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
                "fnStateLoad": function(oSettings) { return load_dt_view(oSettings); },
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls"
                    }]
                },
                "ajax": "/rest/mgr/weixin/person/table?_xsrf=" + $.cookie('_xsrf'),
                "columns": [{
                    "data": "fullname"
                }, {
                    "data":"wechatid"
                }, {
                    "data":"weixin_group",
                    "mRender": function(data, type, full) {
                        if(data=="None")
                            return "";
                        else
                            return data;
                    }
                }, {
                    "data": "create_date"
                }, {
                    "data": "org_name"
                }, {
                    "data": "position"
                }, {
                    "data": "cellphone"
                }, {
                    "data": "email"
                }, {
                    "data": "person_id"
                }],
                "aaSorting": [3, 'desc'],
                "columnDefs": [{
                    "mRender": function(data, type, full) {
                        return '<a onclick="$._showMemberDetail(\'' + full.person_id + '\')" class="btn btn-info btn-xs m-r-5">详情</a>'+
                        '<a onclick="$._showDeliveryInfo(\'' + full.person_id + '\')" class="btn btn-warning btn-xs m-l-5">个人名片</a>'; 
                                // '<a href="javascript:;" class="btn btn-primary btn-xs m-r-5">投票</a>' + 
                                // '<a href="javascript:;" class="btn btn-warning btn-xs m-r-5">缴费</a>' + 
                                // '<a href="javascript:;" class="btn btn-success btn-xs m-r-5">更多</a>';
                    },
                    "targets": 8
                }],
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
    $._showDeliveryInfo = function(id){
        $('#modal-link-delivery-info').modal('show');
        $('#modal-link-delivery-info img').attr('src', '/rest/qrcode?link=' + '/page/delivery_info_' + id);
        $('#modal-link-delivery-info a[target=app_link]').attr('href', '/page/delivery_info_' + id);
        $('#modal-link-delivery-info textarea').val(location.protocol + '//' + location.hostname + '/page/delivery_info_' + id);
    };
    var memberPersonInfo = function(person_info) {
        $('#weixin_group').val(person_info[0]['weixin_group']);
        var output = personInfoTitle();
        output += "<tr><td>微董会微信群友推荐人1</td><td class='first_normal_recommend'></td></tr>";
        output += "<tr><td>微董会微信群友推荐人2</td><td class='second_normal_recommend'></td></tr>";
        output += "<tr><td>期望获取哪些服务或资源</td><td class='expects'></td></tr>";
        output += "<tr><td>可提供哪些服务或资源</td><td class='wills'></td></tr>";     
        var tables = '';
        for (var i in person_info)
        {
            tables += '<table id="member_person_info_table'+i+'" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        }
        $('#div_member_person').html(tables);
        for (var i in person_info)
        {            
            $('#member_person_info_table'+i+' tbody').html(output);
            for (var key in person_info[i])
            {
                if(key=='gender')
                {
                    if(person_info[i][key]==2)
                        $('#member_person_info_table'+i+' .' + key).html('女');
                    else if(person_info[i][key]==1)
                        $('#member_person_info_table'+i+' .' + key).html('男');
                }
                else
                    $('#member_person_info_table'+i+' .' + key).html(person_info[i][key]);
            }


        }


    };
    var memberOrgInfo = function(org_info) {
        var output = orgInfoTitle();       
        $('#member_org_info_table tbody').html(output);
        for (var key in org_info)
        {
            $('#member_org_info_table .' + key).html(org_info[key]);
        }

    };
    var initWeixinGroup = function(groups)
    {
        var output = "<option>未分配微信群</option>";
        for(var index in groups)
        {
            output += "<option value='"+groups[index]['tag_id']+"'>"+groups[index]['tag_name']+"</option>";
        }
        $('#weixin_group').html(output);
    }
    var getMemberDetailInfo = function (person_id) {
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
    $._showMemberDetail = function(id){
        getMemberDetailInfo(id);
        $('#modal-member-detail').modal('show');
        $('#modal-member-detail .nav li').each(function(){
            $(this).removeClass("active");            
        });
        $('#modal-member-detail .tab-content div').each(function(){
            $(this).removeClass("active in");            
        });
        $("#modal-member-detail .nav li:nth-child(1)").addClass("active"); 
        $("#modal-member-detail .tab-content div:nth-child(1)").addClass("active in"); 
        $('#save').click(function(){
            var postData = {_xsrf: $.cookie("_xsrf")};
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



