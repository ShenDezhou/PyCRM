$(function() {
    var s = window.screen;
    var width = q.width = s.width / 2;
    var height = q.height = s.height;
    var letters = Array(256).join(1).split('');
    var _div = document.getElementById("main");
    _div.style.left = (width - 960) / 2 + "px"; //给主页面left定位;
    var draw = function() {
        q.getContext('2d').fillStyle = 'rgba(0,0,0,.05)';
        q.getContext('2d').fillRect(0, 0, width, height);
        q.getContext('2d').fillStyle = '#0F0';
        letters.map(function(y_pos, index) {
            text = Math.random()>0.5?String.fromCharCode(0x3040 + Math.random() * 96) : String.fromCharCode(0x31F0 + Math.random() * 96);
            x_pos = index * 10;
            q.getContext('2d').fillText(text, x_pos, y_pos);
            letters[index] = (y_pos > 758 + Math.random() * 1e4) ? 0 : y_pos + 10;
        });
    };
    setInterval(draw, 33);


});
