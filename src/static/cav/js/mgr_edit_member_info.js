$(function() {
    $("#check_student").click(function() {
        if ($('#check_student').is(":checked")) {
            $(".student").show();
        } else {
            $(".student").hide();
        }
    });
    var person_id = getQueryString('person_id');
    console.log(person_id);
    $("#person_id").val(person_id);
    var org_id = getQueryString('org_id');
    console.log(org_id);
    $("#org_id").val(org_id);
    $.ajax({
        type: "get",
        cache: false,
        url: '/rest/mgr/member/detail',
        data: {
            'person_id': person_id,
            'org_id': org_id
        },
        success: function(data) {
            for (item in data['person'][0]) {
                $("#" + item).val(data['person'][0][item]);
            }
            for (item in data['org'][0]) {
                $("#" + item).val(data['org'][0][item]);
            }
            for (item in data['member'][0]) {
                $("#" + item).val(data['member'][0][item]);
            }
            // for (item in data['form_info'][0]) {
            //     $("#" + item).val(data['form_info'][0][item]);
            // }
        },
        error: function() {
            alert('网络错误！');
        },
        dataType: 'json'
    });
    $("#save").click(function() {
        var member_type = $('#is_person_or_org').val();
        var url;
        if (member_type == 'person')
            url = '/page/person/info/edit';
        else
            url = '/page/org/info/edit';
        $.ajax({
            type: "post",
            cache: false,
            url: url,
            data: $('#form_info').serialize(), // 你的formid
            dataType: 'json',
            success: function(data) {
                if (data.error)
                    alert(data.error);
                if (data.message) {
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


    // $("#birthday").datepicker({
    //       format: 'yyyy-mm-dd'
    //   }).on('changeDate', function(ev) {
    //       $('.datepicker').hide();
    //   });  
    //   $("#school_start").datepicker({
    //       format: 'yyyy-mm-dd'
    //   }).on('changeDate', function(ev) {
    //       $('.datepicker').hide();
    //   }); 
    // $("#due_date").mask("9999/99/99");
    // $("#birthday").mask("9999/99/99");
    // $("#school_start").mask("9999/99/99");

});
