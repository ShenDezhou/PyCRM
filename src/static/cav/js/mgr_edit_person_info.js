var op_count = 0;
$(function() {
    var person_id = getQueryString('person_id');
    $("#person_id").val(person_id);
    $.ajax({
        type: "get",
        cache: false,
        url: '/rest/mgr/person/edit_detail',
        data: {
            person_id: person_id
        },
        success: function(data) {
            $("#form_id").val(data['form_id']);
            // console.log("form_id"+data['form_id']);
            for (item in data['person']) {
                $("#" + item).val(data['person'][item]);
                // console.log(item + " : " + data['person'][item])
            }
            var op_data = data['op_info'];
            var html = '';
            var t_html = '';
            var delete_html = '';
            var edit_html = '';
            for (item in op_data) {
                op_count += 1;
                html += '<tr>' + '<th>' + '<a' + ' href=' + 'edit_member_info?' + 'org_id=' + op_data[item]['org_id'] + ' target=_blank' + ' >' + op_data[item]["org_name"] + '</a>' +
                    '<input '+'type="hidden"'+' id=' + '\'' +'org_name'+op_count+'\''+' value='+'\''+op_data[item]["org_name"]+'\''+' />' +
                    '</th>' +
                    '<th>' + '<input' + ' class="form-control"' +' id=' + '\'' +'department'+op_count+'\''+' value='+'\''+op_data[item]["department"] + '\''+'>' + '</th>' +
                    '<th>' + '<input' + ' id=' + '\'' +'title_name' + op_count +'\''+ ' class="form-control"' + ' value=' + op_data[item]["title_name"] + '>' + '</th>' +
                    '<th>';
                if (op_data[item]["is_primary"] == '是') {
                    t_html = '<select class="form-control"'+ ' id=' + '\'' +'is_primary' + op_count +'\''+ ' >' +
                        '<option value="1">' + '是' + '</option>' +
                        '<option value="0">' + '否' + '</option>' +
                        '</select>';
                }
                else {
                    t_html = '<select class="form-control"'+ ' id=' + '\'' +'is_primary' + op_count +'\''+'>' +
                        '<option value="0">' + '否' + '</option>' +
                        '<option value="1">' + '是' + '</option>' +
                        '</select>';
                }
                delete_html = '<th>' + '<a class="btn btn-danger m-r-5 m-b-5"' + ' onclick="$._deleteOp(\'' + op_data[item]['org_id'] + '\')"' + '>' + '删除' +

                    '</a>' + '<input type="hidden" id="org_id'+op_count+'"'+' name="org_id'+op_count+'"'+' value="'+op_data[item]['org_id']+'"'+'/>';
                edit_html = '<a class="btn btn-primary m-r-5 m-b-5"' + ' onclick="$._editOp(\'' + op_count+ '\')"' + '>' + '保存' +

                    '</a>' + '</th>';

                html = html + t_html + '</th>' + delete_html + edit_html + '</tr>';
            }
            $("#op_info").html(html);
            // console.log(op_count);
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
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
            "person_id": $("#person_id").val()
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
$("#save").click(function() {
    if (checkInfo()) {
        $.ajax({
            type: "post",
            cache: false,
            url: '/page/apply/person/info/edit',
            data:$('#form_info').serialize(),
            dataType: 'json',
            success: function(data) {
                if (data.error)
                    alert(data.error);
                if (data.message) {
                    alert("信息修改成功!");
                    location.reload();
                }
            },
            error: function() {
                alert('网络错误！');
            }
        });
    }

});

var checkInfo = function() {
    if (!$('#cellphone').check().notNull()) {
        alert("*号标识均为必填项");
        return false;
    }
    if (!$('#cellphone').check().tel()) {
        alert("电话号码格式错误");
        return false;
    }
    return true;
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
$("#due_date").mask("9999/99/99");
$("#birthday").mask("9999/99/99");
$("#school_start").mask("9999/99/99");