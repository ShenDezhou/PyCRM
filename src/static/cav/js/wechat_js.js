$(function(){

    $.ajax({
        type: "POST",
        cache: false,
        url: '/rest/wechat/jssign',
        data: {
            _xsrf: $.cookie("_xsrf"),
            url: location.href
        },
        success: function(data) {

            wx.config({
                debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                appId: data.appid, // 必填，公众号的唯一标识
                timestamp: data.timestamp, // 必填，生成签名的时间戳
                nonceStr: data.nonceStr, // 必填，生成签名的随机串
                signature: data.signature,// 必填，签名，见附录1
                jsApiList: [
                    'onMenuShareTimeline',
                    'onMenuShareAppMessage',
                    'onMenuShareQQ',
                    'onMenuShareWeibo'
                ] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
            });

            wx.ready(function () {
                // 在这里调用 API
                // 
                var title = pageTitle || $('title').text(),
                    link = pageUrl || location.href,
                    imgUrl = pageIcon || (location.protocol + '//' + location.hostname + '/static/cav/img/logo2.png'),
                    desc = pageDesc;

                if(imgUrl.indexOf('http') != 0){
                    imgUrl = location.protocol + '//' + location.hostname + imgUrl;
                }

                wx.onMenuShareTimeline({
                    title: title, // 分享标题
                    link: link, // 分享链接
                    imgUrl: imgUrl, // 分享图标
                    success: function () {
                        // 用户确认分享后执行的回调函数
                        // alert('1');
                    },
                    cancel: function () {
                        // 用户取消分享后执行的回调函数
                        // alert('2');
                    }
                });
                
                wx.onMenuShareAppMessage({
                    title: title, // 分享标题
                    desc: desc, // 分享描述
                    link: link, // 分享链接
                    imgUrl: imgUrl, // 分享图标
                    type: '', // 分享类型,music、video或link，不填默认为link
                    dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
                    success: function () {
                        // 用户确认分享后执行的回调函数
                    },
                    cancel: function () {
                        // 用户取消分享后执行的回调函数
                    }
                });
                
                wx.onMenuShareQQ({
                    title: title, // 分享标题
                    desc: desc, // 分享描述
                    link: link, // 分享链接
                    imgUrl: imgUrl, // 分享图标
                    success: function () {
                       // 用户确认分享后执行的回调函数
                    },
                    cancel: function () {
                       // 用户取消分享后执行的回调函数
                    }
                });

                wx.onMenuShareWeibo({
                    title: title, // 分享标题
                    desc: desc, // 分享描述
                    link: link, // 分享链接
                    imgUrl: imgUrl, // 分享图标
                    success: function () {
                       // 用户确认分享后执行的回调函数
                    },
                    cancel: function () {
                        // 用户取消分享后执行的回调函数
                    }
                });

              });
        },
        error: function() {
            
        },
        dataType: 'json'
    }); 
});