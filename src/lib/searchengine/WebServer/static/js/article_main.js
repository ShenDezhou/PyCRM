/**
 * Created by billcao on 16/7/15.
 */
var i = $('#menu i');

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function (from, to) {
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

$(document).ready(function () {
    $('.modal-trigger').leanModal();
});

$('#menu').click(function () {
    if (i.text() == 'menu') {
        i.text('done');
    } else {
        i.text('menu');
    }
});

$('#format').click(function () {
    i.text('menu');
    $('.fixed-action-btn').closeFAB();
    return false;
});

$('#publish').click(function () {
    i.text('menu');
    $('.fixed-action-btn').closeFAB();
    return false;
});

$('#edit').click(function () {
    i.text('menu');
    $('.fixed-action-btn').closeFAB();
    return false;
});

function tag_add(tag) {
    var isOK = false;
    $.ajax({
        url: '/keyword',
        type: 'POST',
        dataType: 'text',
        data: {
            article_id: article_id,
            keyword: tag
        },
        async: false,
        success: function (data) {
            $('#article').mark(tag);
            isOK = (data == 'success');
        },
        error: function () {
            isOK = false;
        }
    });
    return isOK;
}

function tag_delete(tag) {
    var isOK = false;
    if (confirm('确认删除 ' + tag + '吗?')) {
        $.ajax({
            url: '/keyword',
            type: 'DELETE',
            dataType: 'text',
            data: {
                article_id: article_id,
                keyword: tag
            },
            async: false,
            success: function () {
                var index = tags.indexOf(tag);
                tags.remove(index);
                $('#article').unmark().mark(tags);
                isOK = true;
            },
            error: function () {
                isOK = false;
            }
        });
        return isOK;
    } else {
        return false;
    }
}
