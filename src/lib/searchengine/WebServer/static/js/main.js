/**
 * Created by billcao on 16/7/8.
 */
$('#container').on('focus', '#search_input', function () {
    var $weuiSearchBar = $('#search_bar');
    $weuiSearchBar.addClass('weui_search_focusing');
}).on('blur', '#search_input', function () {
    var $weuiSearchBar = $('#search_bar');
    $weuiSearchBar.removeClass('weui_search_focusing');
    if ($(this).val()) {
        $('#search_text').hide();
    } else {
        $('#search_text').show();
    }
}).on('input', '#search_input', function () {
    var $searchShow = $("#search_show");
    if ($(this).val()) {
        $searchShow.show();
    } else {
        $searchShow.hide();
    }
}).on('touchend', '#search_cancel', function () {
    $("#search_show").hide();
    $('#search_input').val('');
}).on('touchend', '#search_clear', function () {
    $("#search_show").hide();
    $('#search_input').val('');
});


$('#view_more').click(function () {
    var offset = $('#article_offset');
    $.ajax({
        url: '/article/view/' + offset.val(),
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            data.forEach(function (element) {
                $('#article_list').append('<a href="' + element.link + '" class="weui_media_box weui_media_appmsg">' +
                    '<div class="weui_media_hd"><img class="weui_media_appmsg_thumb" src="' + element.src +
                    '"/></div><div class="weui_media_bd">' +
                    '<h4 class="weui_media_title">' + element.title +
                    '</h4><p class="weui_media_desc">' + element.desc + '</p></div></a>'
                )
            });
            offset.val(parseInt(offset.val()) + 10);
        },
        error: function (data) {
            console.error(data)
        }
    });
    return false;
});