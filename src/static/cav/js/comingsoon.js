
var handleCountdownTimer = function() {
    var e = new Date;
    e = new Date(2018, 1, 1);
    $("#timer").countdown({ 
        labels: ['年', '月', '周', '日', '小时', '分钟', '秒'],
        labels1: ['年', '月', '周', '日', '小时', '分钟', '秒'],
        until: e 
    }) };
var ComingSoon = function() { 
    "use strict";
    return { init: function() { handleCountdownTimer() } } }();

$(function(){
    ComingSoon.init();
});