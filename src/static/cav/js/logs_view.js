/**
 * Created by Jason on 9/28/16.
 */
$(function() {
    var Logs = function(file_name) {
        var url = '/rest/logs/view';
        var logs = $("#logs");
        $.ajax({
                type: "GET",
                url: url,
                cache: false,
                data: {
                    "file_name": file_name
                },
                success: function(data) {
                    console.log(typeof(data));
                    var html='';
                    for (item in data['logs']) {
                        html += '<div style="font-style: normal;color:white;font-family:' + '\'Courier New\';'+'width: auto">' +
                                data['logs'][item] + '</div>';
                        console.log(data['logs'][item])
                    }
                    logs.replaceWith(html)
                    ("#click").click();
                },
                dataType: "json"
            }
        )
    };
    $("#click").click();
    var web = $("#web_log");
    var mysql = $("#mysql");
    var mysql_error = $("#error");
    var mysql_slow = $("#mysql-slow");
    web.click(function() {
        mysql.css('background-color',"black");
        web.css('background-color',"red");
        mysql_error.css('background-color',"black");
        mysql_slow.css('background-color',"black");
        Logs('web_log')
    });
    mysql.click(function() {
        mysql.css('background-color',"red");
        web.css('background-color',"black");
        mysql_error.css('background-color',"black");
        mysql_slow.css('background-color',"black");
        Logs('mysql')
    });
    mysql_slow.click(function() {
        mysql.css('background-color',"black");
        web.css('background-color',"black");
        mysql_error.css('background-color',"black");
        mysql_slow.css('background-color',"red");
        Logs('mysql_slow')
    });
    mysql_error.click(function() {
        mysql.css('background-color',"black");
        web.css('background-color',"black");
        mysql_error.css('background-color',"red");
        mysql_slow.css('background-color',"black");
        Logs('mysql_error')
    });
});
