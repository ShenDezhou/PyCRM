$(function() {
    var start_id = $('#list-items li:last-child').attr('data-id') || '';
    var updateMore = function() {
        $('#btn-check-more').hide();
        $.ajax({
            type: "GET",
            cache: false,
            url: '/rest/common/articles',
            data: {
                _xsrf: $.cookie("_xsrf"),
                start_id: start_id
            },
            success: function(data) {
                if (data.articles && data.articles.length) {
                    if(data.articles.length == 10){
                        $('#btn-check-more').show();
                    }
                    start_id = data.articles[data.articles.length - 1].id;
                    var html = '';
                    for(var i = 0; i < data.articles.length; i++){
                        html += '<li class="media media-" data-id="' + data.articles[i].id + '">' + 
                                    '<a href="/page/article/' + data.articles[i].id + '" target="article" class="pull-left">' + 
                                        (data.articles[i]['pictures'] ? 
                                            ('<img class="media-object" src="/assets/ticket/image/' + data.articles[i]['pictures'].split(',')[0] + '" alt=""/>')
                                            :
                                            ('<img src="/static/cav/img/default-u.png" alt="" style="max-width:128px"/>')) +
                                    '</a>' + 
                                    '<div class="media-body">' + 
                                        '<a href="/page/article/' + data.articles[i].id + '" target="article">' + 
                                            '<h4 class="media-heading">' + data.articles[i].title + '</h4> ' + 
                                            '<i class="text-muted">' + (data.articles[i].published+'').split(' ')[0] + '</i>' + 
                                        '</a>' + 
                                    '</div>' + 
                                '</li>';
                    }
                    $(html).appendTo($('#list-items'));
                }
            },
            error: function() {
                $('#btn-check-more').show();
            },
            dataType: 'json'
        });
    };
    $('#btn-check-more').click(updateMore);
    updateMore();
});