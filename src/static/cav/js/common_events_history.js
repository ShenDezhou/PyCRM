$(function() {
    var start_id = $('#list-items li:last-child').attr('data-id') || '';
    var updateMore = function() {
        $('#btn-check-more').hide();
        $.ajax({
            type: "GET",
            cache: false,
            url: '/rest/common/events_history',
            data: {
                _xsrf: $.cookie("_xsrf"),
                start_id: start_id
            },
            success: function(data) {
                if (data.events && data.events.length) {
                    if(start_id == '' || data.events.length == 10){
                        $('#btn-check-more').show();
                    }
                    var events = data.events;
                    start_id = events[data.events.length - 1].id;
                    var html = '', tpl = $('#tpl-list-item').html();
                    for(var i = 0; i < events.length; i++){
                        var n = tpl;
                        for(var k in events[i]){
                            var reg = new RegExp('\{' + k + '\}', 'igm');
                            var v = events[i][k];
                            if(k == 'pictures'){
                                if(events[i][k]){
                                    v = '/assets/ticket/image/' + events[i][k].split(',')[0];
                                }else{
                                    v = '/static/cav/img/default-u.png'; 
                                }
                            }else if(k == 'activity_end_date'){
                                if(events[i]['activity_start_date'] == events[i]['activity_end_date']){
                                    v = '';
                                }
                            }else if(k == 'general_place'){
                                v = v || '--';
                            }else if(k == 'sign_up_status'){
                                v = events[i].event_time_status ? events[i].event_time_status : events[i].sign_up_status;
                            }
                            n = n.replace(reg, v);
                        }
                        

                        html += n;
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