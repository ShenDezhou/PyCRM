$(function() {
    var uploadedDocFiles = $.uploadedDocFiles = [];
    var deleteImage = function(){
        if(confirm("你确定删除该文件吗？")){
            var src = $("a.doc-file", $(this).parent()).attr('href');
            for(var i = 0; i < uploadedDocFiles.length; i++){
                if(src.indexOf(uploadedDocFiles[i]) >= 0){
                    uploadedDocFiles = uploadedDocFiles.slice(0, i).concat(uploadedDocFiles.slice(i + 1));
                    refreshDocPreviews();
                    break;
                }
            }
        }
    };

    $.initPreviewDocForNews = function(images){
        uploadedDocFiles = images;
        refreshDocPreviews();
    };

    $.appendDocUploadedFile = function(file){
        uploadedDocFiles.push(file);
        refreshDocPreviews();
    };

    var refreshDocPreviews = function(){
        $('#upload-docs').val(uploadedDocFiles.join(","));
        var html = '';
        for(var i = 0; i < uploadedDocFiles.length; i++){
            html += '<div class="col-md-12"><a class="doc-file" href="/assets/news/doc/' + uploadedDocFiles[i] + '">' + uploadedDocFiles[i].split('/')[1] + '</a><a class="btn btn-danger btn-sm btn-bitbucket"><i class="fa fa-fw fa-trash-o"></i>删除</a></div>';
        }
        $('#upload-doc-previews').html(html);
        $('#upload-doc-previews a').click(deleteImage);
    };


    // $('#doc-files').on('filesuccessremove', function(event) {
    // });
});