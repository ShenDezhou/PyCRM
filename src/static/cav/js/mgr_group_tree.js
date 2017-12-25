/**
 * Created by AJ Kipper on 10/14/16.
 */

$(function () {
    var JsonTree = function (data) {
        console.log(data);
        $('#container').jstree({
            'core': {
                'data': data
            }
        });
    };
    // $._clickGroup = function (id) {
    //     var url = '/res/get/group/info';
    //     group_id = id;
    //     $.ajax({
    //         url: url,
    //         type: 'post',
    //         dataType: 'json',
    //         data: {
    //             'group_id': group_id
    //         },
    //         success: function (data) {
    //             var html = '';
    //             var rows = '';
    //             group_info = data['group_staff'];
    //             group_name = '<h5 id="group_name" >' + '组织名称：' + data['group_name'] + '</h5>' +
    //                 '<p>' + '该组织下具有权限的用户信息' + '</p>';
    //             table = '<table class="table table-bordered">' + '<thead>' +
    //                 '<tr>' +
    //                 '<th>' + '姓名' + '</th>' +
    //                 '<th>' + '权限' + '</th>' +
    //                 '<th>' + '操作' + '</th>' +
    //                 '</tr>' + '</thead>';
    //             for (item in group_info) {
    //                 detail = group_info[item];
    //                 rows += '<tr>' +
    //                     '<th>' + detail['fullname'] + '</th>' +
    //                     '<th>' + detail['role_names'] + '</th>' +
    //                     '<th>' + '<a onclick="$._editRoles(\'' + detail['person_id'] + '\',\'' + detail['group_id'] + '\',\'' + detail['roles'] + '\')" class="btn btn-warning btn-xs m-r-5">修改权限</a>' +
    //                     '<a onclick="$._deleteAdmin(\'' + detail['person_id'] + '\')" class="btn btn-inverse btn-xs m-r-5">删除</a>' +
    //                     '</th>' +
    //                     '</tr>';
    //                 console.log(group_info[item]['fullname']);
    //             }
    //
    //             console.log(rows);
    //             html += group_name;
    //             html += table + rows + '</table>';
    //             $('#group_info').html(html);
    //         }
    //     })
    // };
    var url;
    url = "/rest/mgr/group/tree";
    $.ajax({
        type: "post",
        url: url,
        dataType: "json",
        success: function (data) {
            JsonTree(data['data'])
        },
        error: function () {
            alert("网络错误")
        }

    })

});