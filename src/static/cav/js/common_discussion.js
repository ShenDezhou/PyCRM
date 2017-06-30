$(function() {
    var updateMore = function() {
        $('#btn-check-more').hide();
        var content = $("#search_content").val();
        var to_skip = $('#list-items li').length;
        if (content == "") {
            $.ajax({
                type: "GET",
                cache: false,
                url: '/rest/common/discussion',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    to_skip: to_skip
                },
                success: function(data) {
                    if (data.discussion.length == 10) {
                        $('#btn-check-more').show();
                    }
                    // start_id = discussion[data.discussion.length - 1].id;
                    render(data);
                },
                error: function() {
                    $('#btn-check-more').show();
                },
                dataType: 'json'
            });
        } else {
            search_discussion(false);
        }
    };
    $('#btn-check-more').click(updateMore);
    updateMore();


    function heredoc(fn) {
        return fn.toString().split('\n').slice(1, -1).join('\n') + '\n'
    }
    var tmpl = heredoc(function() {
        /*!
        复旦IT汇北京
	复旦IT汇上海
	大数据直播
	信息安全
	VR
	区块链
	AI
	智能互联双创联盟
	互联网+传统文化
	云计算
	私有云
	*/
    });
    var tag_data = [];
    var tag_str_list = tmpl.split('\n');
    for (var i = 1; i < tag_str_list.length - 2; i++) {
        tag_data.push({ "tag": tag_str_list[i].trim() });
    };

    $('#quick_tag').material_chip({
        data: tag_data
            // placeholder: '继续增加标签',
            // secondaryPlaceholder: '增加标签'
    });
    $('.chips').on('chip.add', function(e, chip) {
        // you have the added chip here
        console.log("add");
    });

    $('.chips').on('chip.delete', function(e, chip) {
        // you have the deleted chip here
        console.log("delete");
    });

    $('.chips').on('chip.select', function(e, chip) {
        // you have the selected chip here
        console.log(chip);
        if ($("#search_content").val() == chip['tag']) {
            $("#search_content").val('');
        } else {
            $("#search_content").val(chip['tag']);
        }
        $('#list-items').html('');
        search_discussion(true);
    });

    var search_discussion = function(clear) {
        if (clear == true)
            $('#list-items').html('');

        $('#btn-check-more').hide();
        var content = $("#search_content").val();
        var to_skip = $('#list-items li').length;

        $.ajax({
            type: "GET",
            url: "/rest/common/discussion/query",
            data: {
                to_skip: to_skip,
                "q": content
            },
            success: function(data) {
                if (data.discussion.length == 10) {
                    $('#btn-check-more').show();
                }
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                render(data);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }
    $('#search').click(function() {
        search_discussion(true);
    });
    $('#search_content').on("keyup", function() {
        search_discussion(true);
    });


    var render = function(data) {
        var discussion = data.discussion;
        var html = '',
            tpl = $('#tpl-list-item').html();
        for (var i = 0; i < discussion.length; i++) {
            var n = tpl;
            for (var k in discussion[i]) {
                var reg = new RegExp('\{' + k + '\}', 'igm');
                var v = discussion[i][k];
                if (k == 'pictures') {
                    if (discussion[i][k]) {
                        v = '/assets/ticket/image/' + discussion[i][k].split(',')[0];
                    } else {
                        v = '/static/cav/img/default-u.png';
                    }
                } else if (k == 'activity_end_date') {
                    if (discussion[i]['activity_start_date'] == discussion[i]['activity_end_date']) {
                        v = '';
                    }
                } else if (k == 'general_place') {
                    v = v || '--';
                    if (discussion[i].sign_up_status == "报名成功") {
                        var place_reg = new RegExp('\{' + 'general_place' + '\}');
                        n = n.replace(place_reg, discussion[i].activity_place);
                    }
                } else if (k == 'sign_up_status') {
                    v = discussion[i].event_time_status ? discussion[i].event_time_status : discussion[i].sign_up_status;
                    var color_reg = new RegExp('\{' + 'color' + '\}');
                    if (discussion[i].sign_up_status == "报名成功") {
                        n = n.replace(color_reg, 'green');
                    } else if (discussion[i].sign_up_status == "人数已满") {
                        n = n.replace(color_reg, 'red');
                    } else if (discussion[i].sign_up_status == "报名未成功") {
                        n = n.replace(color_reg, 'red');
                    } else if (discussion[i].sign_up_status == "正在审核") {
                        n = n.replace(color_reg, 'green');
                    }
                    // else if(discussion[i].sign_up_status == "报名成功"){
                    //     n = n.replace(place_reg,discussion[i].activity_place);
                    //      console.log(discussion[i].activity_place);
                    // }
                } else if (k == 'reason' && discussion[i].sign_up_status == "报名未成功") {
                    console.log(discussion[i].reason);
                    if (discussion[i].reason != null && discussion[i].reason.length > 0) {
                        v = discussion[i].reason;
                        // v = '';
                    } else {
                        v = '';
                    }
                } else if (k == 'reason' && discussion[i].sign_up_status != "报名未成功") {
                    v = '';
                } else if (k == 'can_modify') {
                    if (discussion[i].can_modify == 1) {
                        v = 'block';
                    } else {
                        v = 'none';
                    }
                }
                n = n.replace(reg, v);
            }


            html += n;
        }
        console.log($('#list-items'));
        $(html).appendTo($('#list-items'));

        $('.materialnote').materialnote({
            airMode:true,
            followingToolbar: false,
            height: 300, // set editor height
            minHeight: null, // set minimum height of editor
            maxHeight: 700,
            callbacks: {
                // onImageUpload: function(files) {
                //     var url = $(this).data('upload'); //path is defined as data attribute for  textarea
                //     sendFile(files[0], url, $(this), '#mycontent');
                // }
            }
        });
    }

    //delete
    $._changeStatus = function(id, status) {
        var _ = true;
        if (status == "deleted") {
            _ = confirm("你确定要删除吗？");
        }
        if (_) {
            $.ajax({
                type: "POST",
                url: '/rest/discussion/update/status',
                data: {
                    _xsrf: $.cookie("_xsrf"),
                    id: id,
                    status: status
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


});
