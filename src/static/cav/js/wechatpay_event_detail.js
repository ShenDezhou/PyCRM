$(function() {
    function js_yyyy_mm_dd_hh_mm_ss () {
      now = new Date();
      year = "" + now.getFullYear();
      month = "" + (now.getMonth() + 1); if (month.length == 1) { month = "0" + month; }
      day = "" + now.getDate(); if (day.length == 1) { day = "0" + day; }
      hour = "" + now.getHours(); if (hour.length == 1) { hour = "0" + hour; }
      minute = "" + now.getMinutes(); if (minute.length == 1) { minute = "0" + minute; }
      second = "" + now.getSeconds(); if (second.length == 1) { second = "0" + second; }
      return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
    };
    var remark = $("#pay_remark").val();
    $._wechatpayquery = function(event_id, who) {
        var postData = {
            _xsrf: $.cookie("_xsrf"),
            event_id: event_id,
            id_who: who
        };
        $.ajax({
            type: "POST",
            url: '/wechatpay/orderQuery',
            data: postData,
            success: function(data) {

            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
    $._wechatpay = function(event_id, who, money, cash, nocash) {
        var postData = {
            _xsrf: $.cookie("_xsrf"),
            event_id: event_id,
            paid_start_time: js_yyyy_mm_dd_hh_mm_ss(),
            paid_type: "微信支付",
            id_who: who,
            paid_money: parseFloat(money) * 100,
            paid_remark: remark,
            cash: parseFloat(cash) * 100,
            nocash: parseFloat(nocash) * 100
        };
        if (confirm("你确定要支付吗?")) {
            alert(JSON.stringify(postData));
        
            $.ajax({
                type: "POST",
                url: '/wechatpay/orderPrepay',
                data: postData,
                success: function(data) {
                    WeixinJSBridge.invoke(
                           'getBrandWCPayRequest', data,
                           function(res){     
                               alert(JSON.stringify(res));
                               if(res.err_msg == "get_brand_wcpay_request:ok" ) {}     // 使用以上方式判断前端返回,微信团队郑重提示：res.err_msg将在用户支付成功后返回    ok，但并不保证它绝对可靠。 
                           }
                    ); 
                    //  alert('生成订单成功。' + JSON.stringify(data));
                    //  function onBridgeReady(){
                    //    WeixinJSBridge.invoke(
                    //        'getBrandWCPayRequest', data,
                    //        function(res){     
                    //            if(res.err_msg == "get_brand_wcpay_request:ok" ) {}     // 使用以上方式判断前端返回,微信团队郑重提示：res.err_msg将在用户支付成功后返回    ok，但并不保证它绝对可靠。 
                    //        }
                    //    ); 
                    // }
                    // if (typeof WeixinJSBridge == "undefined"){
                    //    if( document.addEventListener ){
                    //        document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
                    //    }else if (document.attachEvent){
                    //        document.attachEvent('WeixinJSBridgeReady', onBridgeReady); 
                    //        document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
                    //    }
                    // } else {
                    //    onBridgeReady();
                    // } 


                //     function jsApiCall(param){
                //         var _this = this;
                //         alert(JSON.stringify(param));
                //         WeixinJSBridge.invoke(
                //                 'getBrandWCPayRequest',
                //                 param,
                //                 function(res){
                // //                            WeixinJSBridge.log(res.err_msg);
                //                     alert(res.err_code+res.err_desc+res.err_msg);
                // //                            alert('么么哒');

                //                     _this.$http.post('/wechatpay/orderNotify', {"id":param.id,"paid_end_time":js_yyyy_mm_dd_hh_mm_ss(),"paid_number":param.paid_money}).then(function(str) {
                // //                                alert(str.data+'/////////////');
                // //                         var str = JSON.parse(str.data);
                // //                         if(str.resp_code == 100){
                // // //                                alert(7987987987897)
                // //                             _this.$route.router.go({'name':'toBeShipped'});
                // //                         }else{
                // // //                                    alert(JSON.stringify(str));
                // //                             _this.$route.router.go({'name':'payfail',params:{
                // //                                 "orderN":str.order.order_id,
                // //                                 "time":str.order.time,
                // //                                 "allPrice":str.order.all_price
                // //                             }})
                // //                         }
                //                     },function(err){
                //                         alert('出错了'+err);
                //                         console.log(err)
                //                     })

                //                 }
                //         );
                //     };

                //     function callpay(){
                //         if (typeof WeixinJSBridge == "undefined"){
                //             if( document.addEventListener ){
                //                 document.addEventListener('WeixinJSBridgeReady', this.jsApiCall, false);
                //             }else if (document.attachEvent){
                //                 document.attachEvent('WeixinJSBridgeReady', this.jsApiCall);
                //                 document.attachEvent('onWeixinJSBridgeReady', this.jsApiCall);
                //             }
                //         }else{
                //             this.jsApiCall(param);
                //         }
                //     };

                //     callpay();
                },
                error: function() {
                    alert('网络错误！');
                },
                dataType: 'json'
            });

        }
    };
    


});