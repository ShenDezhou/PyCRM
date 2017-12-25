$(function() {
    var uploadedFiles = $.uploadedFiles = [];
    var deleteImage = function(){
        if(confirm("你确定删除该图片吗？")){
            var src = $("img", $(this).parent()).attr('src');
            for(var i = 0; i < uploadedFiles.length; i++){
                if(src.indexOf(uploadedFiles[i]) >= 0){
                    uploadedFiles = uploadedFiles.slice(0, i).concat(uploadedFiles.slice(i + 1));
                    refreshPreviews();
                    break;
                }
            }
        }
    };

    $.initPreviewImageForTicket = function(images){
        uploadedFiles = images;
        refreshPreviews();
    };

    $.appendUploadedFile = function(file){
        uploadedFiles.push(file);
        refreshPreviews();
    };

    var refreshPreviews = function(){
        $('#upload-images').val(uploadedFiles.join(","));
        var html = '';
        for(var i = 0; i < uploadedFiles.length; i++){
            html += '<div class="col-md-3 preview-box"><img src="' + $.get_file_url(uploadedFiles[i], "/assets/ticket/image/") + '"/><a class="btn btn-danger btn-sm btn-bitbucket"><i class="fa fa-fw fa-trash-o"></i>删除</a></div>';
        }
        $('#upload-image-previews').html(html);
        $('#upload-image-previews .preview-box a').click(deleteImage);
    };

    // $('#ticket-files').on('fileuploaded', function(event, data, previewId, index) {
    //     var form = data.form,
    //         files = data.files,
    //         extra = data.extra,
    //         response = data.response,
    //         reader = data.reader;
    //     for (var i = 0; i < response.files.length; i++) {
    //         uploadedFiles.push(response.files[i].url);
    //     }
    //     refreshPreviews();
    // });
});
