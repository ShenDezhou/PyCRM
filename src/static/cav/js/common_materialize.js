$(function() {
    var i = $('#menu i');
    $('#menu').click(function() {
        if (i.text() == 'menu') {
            i.text('done');
        } else {
            i.text('menu');
        }
    });

    $('#format').click(function() {
        i.text('menu');
        $('.fixed-action-btn').closeFAB();
        // return false;
    });

    $('#publish').click(function() {
        i.text('menu');
        $('.fixed-action-btn').closeFAB();
        // return false;
    });

    $('#edit').click(function() {
        i.text('menu');
        $('.fixed-action-btn').closeFAB();
        // return false;
    });
});
