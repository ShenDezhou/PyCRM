$(function() {
    var type = "";
    var id = "";

    function sendFile(file, editor, welEditable, dom) {
        var data = new FormData();
        data.append("file", file);
        $.ajax({
            url: "/fileupload/mgr/image",
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                $(dom).summernote("insertImage", data.files[0].url, 'filename');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert('图片上传出错！' + textStatus + " " + errorThrown);
                // console.log(textStatus + " " + errorThrown);
            }
        });
    }
    if (getQueryString('id') != null) {
        id = getQueryString('id');
        $(".content-header h1").html("修改表单");
        $.ajax({
            type: "GET",
            url: '/rest/mgr/survey/detail',
            cache: false,
            data: {
                id: id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                for (var key in data) {
                    $('#' + key).val(data[key]);
                }
                $('#sur_content').val(data['sur_content']);
                if(data['sur_image'])
                    $.initPreviewImageForTicket(data['sur_image'].split(','));
                $('#sur_content').summernote({
                    height: 100, // set editor height
                    minHeight: null, // set minimum height of editor
                    maxHeight: 400
                });
                for(var i = 0; i < data.quizs.length; i++){
                    var q = data.quizs[i];
                    updateQuizTable(q.id, q.title, q.type, q.sort, q.required, q.opts);
                }
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    } else {
        $(".content-header h1").html("新建表单");
        $('#sur_content').summernote({
            height: 300, // set editor height
            minHeight: null, // set minimum height of editor
            maxHeight: 400
        });
    }
    Date.prototype.Format = function(formatStr) {
        var str = formatStr;
        var Week = ['日', '一', '二', '三', '四', '五', '六'];

        str = str.replace(/yyyy|YYYY/, this.getFullYear());
        str = str.replace(/yy|YY/, (this.getYear() % 100) > 9 ? (this.getYear() % 100).toString() : '0' + (this.getYear() % 100));

        str = str.replace(/MM/, (this.getMonth() + 1) > 9 ? (this.getMonth() + 1).toString() : '0' + (this.getMonth() + 1));
        str = str.replace(/M/g, this.getMonth());

        str = str.replace(/w|W/g, Week[this.getDay()]);

        str = str.replace(/dd|DD/, this.getDate() > 9 ? this.getDate().toString() : '0' + this.getDate());
        str = str.replace(/d|D/g, this.getDate());

        str = str.replace(/hh|HH/, this.getHours() > 9 ? this.getHours().toString() : '0' + this.getHours());
        str = str.replace(/h|H/g, this.getHours());
        str = str.replace(/mm/, this.getMinutes() > 9 ? this.getMinutes().toString() : '0' + this.getMinutes());
        str = str.replace(/m/g, this.getMinutes());

        str = str.replace(/ss|SS/, this.getSeconds() > 9 ? this.getSeconds().toString() : '0' + this.getSeconds());
        str = str.replace(/s|S/g, this.getSeconds());

        return str;
    }
    $('#save').click(function() {
        commitData("draft");
        return false;
    });
    $('#save_and_publish').click(function() {
        commitData("published");
        return false;
    });
    $('#return').click(function() {
        location.href = "/console/survey_list";
    });
    var commitData = function(status) {
        var postData = {
            _xsrf: $.cookie("_xsrf")
        };
        // postData.type = type;
        var url = '';
        url = '/rest/mgr/survey/commit';
        if (id != "") {
            postData.id = id;
        }
        postData.sur_status = status;
        postData.sur_title = $('#sur_title').val();
        postData.sur_content = $('#sur_content').val();
        postData.sur_image = $('#upload-images').val();
        postData.quizs = [];
        $('#quiz-table tbody tr').each(function(row){
            var args = getOneQuiz($(this));
            postData.quizs.push(args);
        });
        postData.quizs = JSON.stringify(postData.quizs);
        $.ajax({
            type: "POST",
            url: url,
            data: postData,
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '添加失败！');
                }
                location.href = "/console/survey_list";
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    }

    $("#published").datepicker({
        format: 'yyyy-mm-dd'
    }).on('changeDate', function(ev) {
        $('.datepicker').hide();
    });

    var quizTypes = {
        text: "单行填空题",
        textarea: "多行填空题",
        select: "单选题",
        checkbox: "多选题"
    };
    var initQuizModal = function(args){
        if(!args){
            $('#new-quiz-id').val('');
            $('#new-quiz-title').val('');
            $('#new-quiz-type').val('');
            $('#new-quiz-sort').val(1);
            $('#new-quiz-opts').val('');
            $('#new-quiz-opts-section').hide();
            $('#new-quiz-opt-items').html(''); 
        }else{
            $('#new-quiz-id').val(args.id);
            $('#new-quiz-title').val(args.title);
            $('#new-quiz-type').val(args.type);
            $('#new-quiz-sort').val(args.sort);
            $('#new-quiz-opt-items').html(''); 
            for(var i = 0; i < args.opts.length; i++){
                var id = args.opts[i].id, sort = args.opts[i].sort, title = args.opts[i].title;
                var html = '<div class="row m-b-3 opt-row" id="{id}"><div class="col-md-8 opt-div"><input class="opt-title form-control" type="text" value="{title}"/></div><div class="col-md-2"><input class="opt-sort form-control" type="text" value="{sort}"/></div><div class="col-md-2"><button class="btn btn-danger btn-sm" type="button" onclick="$._removeQuizOpt(\'{id}\')">删除</button></div></div>';
                html = html.replace(/\{id\}/igm, id).replace('{sort}', sort).replace('{title}', title);
                $('#new-quiz-opt-items').append(html); 
            }
            if(args.type != 'text' && args.type != 'textarea'){
                $('#new-quiz-opts-section').show();
            }else{
                $('#new-quiz-opts-section').hide();
            }
        }
        $('#new-quiz-modal').modal('show');
    };

    $('#btn-add-quiz').click(function(){initQuizModal()});
    $('#new-quiz-type').change(function(){
        var v = $(this).val();
        if(v == 'text' || v == 'textarea'){
            $('#new-quiz-opts-section').hide();
        }else{
            $('#new-quiz-opts-section').show();
        }
    });
    var getOneQuiz = function(t){ //row dom
        var args = {};
        args.id = t.attr('id'),
        args.title = $('.quiz-title', t).text();
        args.sort = $('.quiz-sort', t).text();
        args.required = $('.quiz-required input', t).val();
        args.type = $('.quiz-type input', t).val();
        var opts = [];
        $('.opt-row', t).each(function(i){
            opts.push({
                id: $(this).attr('id'),
                sort: $('.opt-sort', this).text(),
                title: $('.opt-title', this).text()
            });
        });
        args.opts = opts;
        return args;
    };
    var updateQuizTable = function(id, title, type, sort, required, opts){
        var optRowHtml = '<div class="opt-row" id="{id}"><span class="opt-sort hidden">{sort}</span>{index}.<span class="opt-title">{title}</span></div>', optHtml = '';
        opts = opts.sort(function(a, b){
            return a.sort > b.sort ? 1 : 0;
        });
        for(var i = 0; i < opts.length; i++){
            optHtml += optRowHtml.replace('{id}', opts[i].id).replace('{sort}', opts[i].sort).replace('{title}', opts[i].title).replace('{index}', i + 1);
        }
        var typeName = quizTypes[type];
        var requiredName = (required == 1 ? '是' : '否');
        var html = '<td class="quiz-sort">{sort}</td><td class="quiz-title">{title}</td><td class="quiz-type">{type_name}<input type="hidden" value="{type}"</td><td class="quiz-opts">{opts}</td><td class="quiz-required">{requiredName}<input type="hidden" value="{required}"</td><td><button type="button" class="btn btn-warning btn-xs" onclick="$._editQuizRow(this)">修改</button> <button type="button" class="btn btn-danger btn-xs" onclick="$._removeQuizRow(this)">删除</button></td>';
        html = html.replace('{id}', id).replace('{sort}', sort).replace('{title}', title).replace('{opts}', optHtml).replace('{type}', type).replace('{type_name}', typeName).replace('{requiredName}', requiredName).replace('{required}', required);
        if(!id){
            id = Math.uuid();
        }
        if($('#' + id).length){
            $('#' + id).html(html);
        }else{
            $('#quiz-table tbody').append('<tr id="' + id + '">' + html + '</tr>');
        }
    };
    $._editQuizRow = function(target){
        var t = $(target).parent().parent();
        var args = getOneQuiz(t);
        initQuizModal(args);
    };
    $._removeQuizRow = function(target){
        var t = $(target).parent().parent();
        if(confirm('确定删除吗？')){
            t.remove();
        }
    };
    $('#new-quiz-save-btn').click(function(){
        var id = $('#new-quiz-id').val(),
            title = $('#new-quiz-title').val(),
            type = $('#new-quiz-type').val(),
            sort = $('#new-quiz-sort').val() || 1,
            required = $('#new-quiz-required').val(),
            optDoms = $('#new-quiz-opt-items .opt-row');
        if(!title) return alert('必须填写问题标题');
        if(!type) return alert('必须选择问题类型');
        if(!optDoms.length && type != 'text' && type != 'textarea') return alert('必须填写问题选项');
        var opts = [];
        for(var i = 0; i < optDoms.length; i++){
            var t = optDoms.eq(i);
            opts.push({
                id: t.attr('id'),
                sort: $('.opt-sort', t).val(),
                title: $('.opt-title', t).val()
            });
        }
        updateQuizTable(id, title, type, sort, required, opts);
        $('#new-quiz-modal').modal('hide');
    });
    $._removeQuizOpt = function(id){
        if(confirm('确定删除吗？')){
            $('#new-quiz-modal #' + id).remove();
        }
    };
    $('#new-quiz-opt-btn').click(function(){
        var title = $('#new-quiz-opt-title').val(),
            sort = $('#new-quiz-opt-sort').val() || 1,
            id = Math.uuid();
        if(!title) return alert('必须填写选项说明');
        var html = '<div class="row m-b-3 opt-row" id="{id}"><div class="col-md-8 opt-div"><input class="opt-title form-control" type="text" value="{title}"/></div><div class="col-md-2"><input class="opt-sort form-control" type="text" value="{sort}"/></div><div class="col-md-2"><button class="btn btn-danger btn-sm" type="button" onclick="$._removeQuizOpt(\'{id}\')">删除</button></div></div>';
        html = html.replace(/\{id\}/igm, id).replace('{sort}', sort).replace('{title}', title);
        $('#new-quiz-opt-items').append(html); 
        $('#new-quiz-opt-title').val('');
        $('#new-quiz-opt-sort').val('');
    });

    $('#btn-fetch-content').click(function() {
        var url = $('#data_source').val();
        if (!url) {
            return alert('链接不能为空！');
        }
        $.ajax({
            type: "POST",
            url: '/rest/mgr/fetch/weixin',
            data: {
                url: url
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error || '失败！');
                }
                $('#title').val(data.title);
                $('#sur_content').summernote("code", data.content);
                $('#published').val(data.date);
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    });

});