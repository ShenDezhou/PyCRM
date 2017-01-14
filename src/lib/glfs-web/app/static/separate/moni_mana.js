$(document).ready(function(){
		
	var clusterinfo = JSON.parse(localStorage.getItem('clusterinfo'));
	if(!clusterinfo){
		clusterinfo = test();
	}
	
	function test(){
		var url = $SCRIPT_ROOT + '/monitor/info';
	    $.ajaxSetup({async:false});
	    $.getJSON(url, null, function (data) {
	    	clusterinfo = data;
	      	localStorage.setItem('clusterinfo', JSON.stringify(data));
	    });
	    return clusterinfo;
	}
	
	setInterval( function () {
		getClusterInfo();
    }, 1000);
	var serversinfo = clusterinfo["cluster"];
    var serversStatusinfo = getServerStatusInfo();
    var servers = serversStatusinfo["servers"];
    var cluster_info_wr = JSON.parse(localStorage.getItem('write_reads'));
    console.log(cluster_info_wr)
    
    
    function highcarts_reflow(num){
	    setTimeout(function(){
	        $("#CPU"+serversinfo[num]["hostname"]).highcharts().reflow();	        
	    },180);
	    setTimeout(function (){
	        $("#Mem"+serversinfo[num]["hostname"]).highcharts().reflow();
	    },180);
	    setTimeout(function (){
	        $("#RW"+serversinfo[num]["hostname"]).highcharts().reflow();
	    },180);
	    setTimeout(function (){
	        $("#NETWORK"+serversinfo[num]["hostname"]).highcharts().reflow();
	    },180);
	    setTimeout(function (){
	        for (var j = 0; j < serversinfo[num]["disks"].length; j++){
	          $("#monitorPieChart"+ num + "disk" + j).highcharts().reflow();
	        }
	    },180);
    }	//初始化曲线图，使曲线图适应父层框的大小    
       
      
    $('.menu-item.monitor').click(function (e) {//监控管理
    	$(".menu-item.volume .fa.fa-chevron-down").removeClass("fa-chevron-UP");
		$("#volumeMNav").stop().animate({
			height:"0"
		},500)
		
		//	    左侧监控管理折叠菜单
		if($(this).width()>100){
			var monitorMNav_show = $("#monitorMNav").css("height");
			var show_height = Math.round($("#monitorMNav li:eq(0)").outerHeight()*serversinfo.length);
			$(".menu-item.monitor .fa.fa-chevron-down").toggleClass("fa-chevron-UP");
			if (monitorMNav_show == "0px") {
				$("#monitorMNav").stop().animate({
				 	height:show_height+6+"px"
				},500)
			}else{
				$("#monitorMNav").stop().animate({
				 	height:"0"
				 },500)
			};
		};
		
		
		var li_named = $("#monitorMNav li").attr("data-selected");
		if(li_named == null){
			highcarts_reflow(0);
			$("#monitorMNav li:first-child").css({"background":"#1e282c","color":"#fff"}).siblings().css({"background":"","color":""});
		}else{
			var li_selected = $("#monitorMNav li[data-selected='true']").attr("data-number");
			highcarts_reflow(li_selected);
		}	    
	});//$('.monitor_1').click监控管理点击函数结束	
	
	$("#slidebar_nav").click(function(){
		var monitorMNav_show = $("#monitorMNav").css("height");
		var show_height = Math.round($("#monitorMNav li:eq(0)").outerHeight()*serversinfo.length);
		if(monitorMNav_show != "0px"){
			$(".menu-item.monitor .fa.fa-chevron-down").css("visibility","hidden");
			$("#monitorMNav").stop().animate({
			 	height:"0"
			},500)
		}else if($('.menu-item.monitor').width()<100&&monitorMNav_show == "0px"){
			$(".menu-item.monitor .fa.fa-chevron-down").css("visibility","visible");
		}else{
			$(".menu-item.monitor .fa.fa-chevron-down").css("visibility","hidden");
		}
		
		var volumeMNav_hei = $("#volumeMNav").css("height");
		var hei_length = $("#volumeTabs li").length;
		var V_list_show_height = Math.round($("#volumeTabs li:eq(0)").outerHeight()*hei_length);
		var Vshow_height = Math.round($("#volumeTabs li:eq(0)").outerHeight()*hei_length+$("#volumeMNav div:eq(0)").outerHeight()*2);
		if(volumeMNav_hei != "0px"){
			$(".menu-item.volume .fa.fa-chevron-down").css("visibility","hidden");
			$("#volumeMNav").stop().animate({
			 	height:"0"
			},500)
		}else if($('.menu-item.volume').width()<100&&volumeMNav_hei == "0px"){
			$(".menu-item.volume .fa.fa-chevron-down").css("visibility","visible");
		}else{
			$(".menu-item.volume .fa.fa-chevron-down").css("visibility","hidden");
		}		
	})
   
    /*　System Moniter ---------------------------------*/
    var SystemMoni = $('#ServersMoni');                       
    var html = "";
    var count = 0;
    for (count = 0; count < serversinfo.length; count++) {
    	html+='<li data-label="'+serversinfo[count]["hostname"]+'" data-number="'+count+'">'+serversinfo[count]["hostname"]+'</li>';
    }  //根据获取到的机器的数量，动态添加相应个数的li，用作下拉菜单的选项     
    $("#monitorMNav").html(html);//将下拉菜单添加到页面上 	
	var monitor_navs = $("#monitorMNav").find("li");
	monitor_navs.on('click', function (e) {
		var $this = $(this);
		$(this).attr("data-selected","true").siblings().attr("data-selected","false");
		$(this).css({"background":"#1e282c","color":"#fff"}).siblings().css({"background":"","color":""});
		var cunt=$this.attr("data-number");//给获取到的机器一个编号，依次是0、1、2...,并获取出来
    	SystemMoni.html("");//SystemMoni添加元素之前先把内容清空
    	SystemMoni.append(monitorinfoFormat(serversinfo[cunt]["hostname"], count));
    	//调用monitorinfoFormat函数，将相应编号的机器信息添加到页面上   	
    	highcarts_reflow(cunt);   	
      	runhighChart(cunt);		
		e.preventDefault;
	});
	
	$("#placeholder").text(serversinfo[0]["hostname"]);//页面刚加载完成时，下拉菜单中显示的获取到的第一台机器的名称
	//页面加载完成时,首先添加获取到的第一台机器的信息到页面上
	SystemMoni.append(monitorinfoFormat(serversinfo[0]["hostname"], count));
	runhighChart(0);
	function runhighChart(COUNT){
		
		//折线图的全局变量设置
	    Highcharts.setOptions({
	        global : {
	            useUTC : false
	        },
	        lang: {
		        rangeSelectorZoom: '时间长度' 
		    },
		    colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
	    });
	      
	    //////////cpu使用率折线图////////
	    var CPUid = '#CPU' + serversinfo[COUNT]["hostname"];
	     $(CPUid).highcharts({
		    credits: {
		        enabled: false
		    },
	        chart: {
	        	backgroundColor:"#ECF0F5",
	          	type: 'line',
	          	reflow:true,
	          	animation: false, // don't animate in old IE
	          	events: {
	              	load: function (event) {
	                	var series = this.series;
	                	var cnt = COUNT;
	                	setInterval(function () {
	                  		var x = (new Date()).getTime();	
	                    	var data_string = localStorage.getItem("clusterinfo");
    						if (!data_string){
    							alert("No use");
    						}
    						var data = JSON.parse(data_string);
	                    	for (var i = 0; i < series.length; i++){
	                      		series[i].addPoint([x, parseFloat(data["cluster"][cnt]["cpus"][i]["usage"][29])], true, true);
	                    	}	              
	                  	},2000);//计时器结束
	           		}//load结束
	          	}//event结束
	        },//chart结束
	        title:{
		    	text:""
		    },
	        xAxis: {
	          	type: 'datetime',
	          	tickPixelInterval: 150,
	          	minPadding: 0,
	          	maxPadding: 0
	        },
	        yAxis: {
	        	title: {
		      		text: 'CPU已使用率(%)'
		    	},
	          	plotLines: [{
	            	value: 0,
	            	width: 2,
	            	color: '#808080'
	          	}],
			  	opposite: false,
	          	max: 100,
	          	min: 0
	        },
          	tooltip: {
            	formatter: function () {
	            	return '<b>' + this.series.name + '</b><br/>' +
	                    Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
	                    Highcharts.numberFormat(this.y, 2);
	          	},
	          	crosshairs: true
	        },
          	plotOptions: {
	          	series: {	
	            	dataLabels: {
	             		allowOverlap: true
	            	}
	          	}
	        },
          	legend: {
            	enabled: true
	        },
          	exporting: {
            	enabled: false
        	},
          	series : createSeries(COUNT)	
	    });//CPUid highchart结束


	      
		//////内存使用率折线图
	      
	    var memId = '#Mem' + serversinfo[COUNT]["hostname"];
	    $(memId).highcharts( {
	        credits: {
	        	enabled: false
	        },
	        chart: {
	        	backgroundColor:"#ECF0F5",
	            type: 'spline',
	            reflow:true,
	            animation: false, // don't animate in old IE
	            events: {
	                load: function (event) {
	                    var series = this.series;
	                    var cnt = COUNT;
	                    setInterval(function ( ) {
		                    var x = (new Date()).getTime();
		                    var data_string = localStorage.getItem('clusterinfo');
			      			var data = JSON.parse(data_string);
			      			var Length = data["cluster"][cnt]["memory"]["usage"].length-1;
		                    series[0].addPoint([x, parseFloat(data["cluster"][cnt]["memory"]["usage"][Length])], true, true);	
	                    }, 2000);
	                }
	            }
	        },	
	        title:{
		    	text:""
		    },
          	xAxis: {
            	type: 'datetime',
            	tickPixelInterval: 150,
            	minPadding: 0,
            	maxPadding: 0
          	},
            yAxis: {
                title: {
                  text: '内存使用率(%, '+getMemsize(COUNT)+'G)'
                },
                plotLines: [{
                  value: 0,
                  width: 2,
                  color: '#808080'
                }]
            },
          	tooltip: {
                formatter: function () {
                  return '<b>' + this.series.name + '</b><br/>' +
                          Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                          Highcharts.numberFormat(this.y, 3);
                },
                crosshairs: true
            },
            plotOptions: {
                series: {
                  dataLabels: {
                    allowOverlap: true
                  }
                }
            },
            legend: {
            	enabled: true
	        },
            exporting: {
                enabled: false
            }, 
			series : createMemSeries(COUNT)
	    });//内存使用率折线图结束
	
		/////////磁盘读写速度diskio折线图	   	    		
	    var RWid = '#RW' + serversinfo[COUNT]["hostname"];
		$(RWid).highcharts('StockChart', {
	    	credits: {
			   enabled: false
			},
	        chart : {
	        	backgroundColor:"#ECF0F5",
	        	type:"line",
	        	reflow:true,
	        	animation: false,
	            events : {
	            	load: function (event) {
	            		var Series = this.series;
	            		var cnt = COUNT;
		                setInterval(function () { 
		                  	var data_string = localStorage.getItem('clusterinfo');
	    					if (!data_string){
	    						alert("No use");
	    					}
	    					var data = JSON.parse(data_string);
		                    var Length = data["cluster"][cnt]["init_disk_write_data"].length-1;
		                    var valueTimeWrite = data["cluster"][cnt]["init_disk_write_data"][Length];
		                    var JsonDataWrite = eval('(' + valueTimeWrite + ')'); 
		                    var valueTimeRead = data["cluster"][cnt]["init_disk_read_data"][Length];
		                    var JsonDataRead = eval('(' + valueTimeRead + ')');
		                    var jsCurrentTime = (new Date()).getTime();
		                    var timeMius = jsCurrentTime - parseInt(JsonDataRead.time);
		                    //var x = jsCurrentTime - timeMius;
		                    var x = (new Date()).getTime();
		                    Series[0].addPoint([x, parseFloat(JsonDataRead.data)], true, true);
		                    Series[1].addPoint([x, parseFloat(JsonDataWrite.data)], true, true);
		                  },2000);//计时器结束
		           	}//load结束
	            }
	        },
	        yAxis: {
		    	title: {
		      		text: 'MB/s'
		    	},
		    	opposite: false,
		    	plotLines: [{
			      	value: 0,
			      	width: 1,
			      	color: '#808080'
		    	}]
		  	},
	        rangeSelector: {
	            buttons: [{
	                count: 1,
	                type: 'minute',
	                text: '1分钟'
	            }, {
	                count: 5,
	                type: 'minute',
	                text: '5分钟'
	            }, {
	                type: 'all',
	                text: '1小时'
	            }],
	            inputEnabled: false,
	            selected: 0
	        },
	        tooltip: {
	    		formatter: function () {
	                var s = '<b style="font-weight:300;">' + Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '</b>';
	                $.each(this.points, function () {
	                	if(this.y>=(1024*1024)){
	                		var number = (this.y/(1024*1024)).toFixed(2)+"MB/s";
	                	}else if(this.y<(1024*1024)){
	                		var number = (this.y/1024).toFixed(2)+"KB/s";
	                	}else if(this.y<=0){
	                	    this.y = 0;
	                		var number = "0KB/s";
	                	}
	                    s += '<br/><span style="font-weight:800;color:'+this.series.color+';">'+this.series.name+'</span>: <b>'+number+'</b>';
	                });
	
	                return s;
	            },
	            shared: true,
	            useHTML: true,
	            shared: true
			}, 
	        plotOptions: {
		    	series: {
		      		dataLabels: {
		        		allowOverlap: true
		      		}
		    	}
		  	},
			legend: {
			   enabled: true
			},
	        exporting: {
	            enabled: false
	        },
	        series: [{
	        	name: '读',
	        	data: (function () {
	        		var valueTime = cluster_info_wr[COUNT]["init_disk_read_data"][20];
	          		var JsonData = eval('(' + valueTime + ')'); 
	          		var data = [],time = parseInt(JsonData.time),j;
	          		for (j = -359; j < 0; j += 1) {
	          			var valueTime = cluster_info_wr[COUNT]["init_disk_read_data"][j + 359];
	          			var JsonData = eval('(' + valueTime + ')'); 
	            		data.push([
	               			time + j * 1000,
	               			parseInt(JsonData.data)
	            		]);
	          		}
	          		return data;
	        	}())
	      		}, {
	        	name: '写',
	        	data: (function () {
	        		var valueTime = cluster_info_wr[COUNT]["init_disk_write_data"][20];
	          		var JsonData = eval('(' + valueTime + ')'); 
	          		var data = [], time = parseInt(JsonData.time),j;	
	          		for (j = -359; j < 0; j += 1) {
	          			var valueTime = cluster_info_wr[COUNT]["init_disk_write_data"][j + 359];
	          			var JsonData = eval('(' + valueTime + ')'); 
	            		data.push([
	               			time + j * 1000,
	               			parseInt(JsonData.data)
	            		]);
	          		}
	         	return data;
	        	}()),
	        	color : '#6FDB4B'
	      	}]
	    });
    		   													
			
		///////networkio读写速度图 		
		var NETid = '#NETWORK' + serversinfo[COUNT]["hostname"];    		
		$(NETid).highcharts('StockChart', {
	    	credits: {
			   enabled: false
			},
	        chart : {
	        	backgroundColor:"#ECF0F5",
	        	type:"line",
	        	reflow:true,
	        	animation: false,
	            events : {
	                load: function (event) {
		                var Series = this.series;
	            		var cnt = COUNT;
		                setInterval(function () {
		                  	var data_string = localStorage.getItem('clusterinfo');
	    					if (!data_string){
	    						alert("No use");
	    					}
	    					var data = JSON.parse(data_string);
		                    var Length = data["cluster"][cnt]["init_network_in_data"].length-1;
		                    var valueTimeIn = data["cluster"][cnt]["init_network_in_data"][Length];
		                    var JsonDataIn = eval('(' + valueTimeIn + ')'); 
		                    var valueTimeOut = data["cluster"][cnt]["init_network_out_data"][Length];
		                    var JsonDataOut = eval('(' + valueTimeOut + ')');
		                    var jsCurrentTime = (new Date()).getTime();
		                    var timeMius = jsCurrentTime - parseInt(JsonDataOut.time);
		                    //var x = jsCurrentTime - timeMius;
		                    var x = (new Date()).getTime();
		                    Series[0].addPoint([x, parseFloat(JsonDataIn.data)], true, true);
		                    Series[1].addPoint([x, parseFloat(JsonDataOut.data)], true, true);
		                  },2000);//计时器结束
		           	}//load结束
	            }
	        },
	        yAxis: {
		    	title: {
		      		text: 'MB/s'
		    	},
		    	opposite: false,
		    	plotLines: [{
			      	value: 0,
			      	width: 1,
			      	color: '#808080'
		    	}]
		  	},
	        rangeSelector: {
	            buttons: [{
	                count: 1,
	                type: 'minute',
	                text: '1分钟'
	            }, {
	                count: 5,
	                type: 'minute',
	                text: '5分钟'
	            }, {
	                type: 'all',
	                text: '1小时'
	            }],
	            inputEnabled: false,
	            selected: 0
	        },
	        tooltip: {
	    		formatter: function () {
	                var s = '<b style="font-weight:300;">' + Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '</b>';
	                $.each(this.points, function () {
	                	if(this.y>=(1024*1024)){
	                		var number = (this.y/(1024*1024)).toFixed(2)+"MB/s";
	                	}else if(this.y<(1024*1024)){
	                		var number = (this.y/1024).toFixed(2)+"KB/s";
	                	}else if(this.y<=0){
	                	    this.y = 0;
	                		var number = "0KB/s";
	                	}
	                    s += '<br/><span style="font-weight:800;color:'+this.series.color+';">'+this.series.name+'</span>: <b>'+number+'</b>';
	                });		
	                return s;
	            },
	            shared: true,
	            useHTML: true,
	            shared: true
			}, 
	        plotOptions: {
		    	series: {
		      		dataLabels: {
		        		allowOverlap: true
		      		}
		    	}
		  	},
		  	legend: {
			   enabled: true
			},
	        title : {
	            text : ''
	        },
	        exporting: {
	            enabled: false
	        },
	        series: [{
		        name: '入流量',
		        data: (function () {
		        	var valueTime = cluster_info_wr[COUNT]["init_network_in_data"][20];
		            var JsonData = eval('(' + valueTime + ')'); 
		          	var data = [],time = parseInt(JsonData.time),j;		
		          	for (j = -359; j < 0; j += 1) {
		          		var valueTime = cluster_info_wr[COUNT]["init_network_in_data"][j+359];
		                var JsonData = eval('(' + valueTime + ')'); 
	            		data.push([
	               			time + j * 1000,
	               			parseInt(JsonData.data)
	            		]);
	          		}
		          	return data;
		        	}())
		      	}, {
	        	name: '出流量',
	        	data: (function () {
	        		var valueTime = cluster_info_wr[COUNT]["init_network_out_data"][20];
		            var JsonData = eval('(' + valueTime + ')'); 
	          		var data = [],time = parseInt(JsonData.time),j;			
	          		for (j = -359; j < 0; j += 1) {
	          			var valueTime = cluster_info_wr[COUNT]["init_network_out_data"][20];
		            	var JsonData = eval('(' + valueTime + ')'); 
	            		data.push([
	               			time + j * 1000,
	               			parseInt(JsonData.data)
	            		]);
	          		}
	          		return data;
	        	}()),
	        	color : '#6FDB4B'
	      	}]
	    });
    									
	
		//磁盘使用率折线图
        var monitorPieChart = $('#PieChart' + serversinfo[COUNT]["hostname"]);
        monitorPieChart.append(getMonitorPieChartDiv(COUNT));
        for (var i = 0; i < serversinfo[COUNT]["disks"].length; i++) {
			//console.log(parseFloat(serversinfo[COUNT]["disks"][i]["usage"]));
          	Highcharts.setOptions({
	            colors: ['#ED561B','#058DC7','#64E572','#FF9655', '#FFF263', '#6AF9C4']
	        });
	        $('#monitorPieChart'+COUNT+"disk"+ i).highcharts({
	            credits:{
	              enabled: false
	            }, 
	            exporting:{
	              enabled:false
	            },
	            chart: {
	              backgroundColor:"#ECF0F5",
	              plotBackgroundColor: null,
	              plotBorderWidth: null,
	              plotShadow: false,
	            },
	            title: {
	              text: serversinfo[COUNT]["disks"][i]["name"] + "使用率"
	            },
	            tooltip: {
	              pointFormat: '{series.name}: <b>{point.percentage:.2f}%</b>'
	            },
	            plotOptions: {
	              	pie: {
	                	allowPointSelect: true,
	                	cursor: 'pointer',
	                	dataLabels: {
		                  	enabled: false,
		                  	color: '#000000',
		                  	connectorColor: '#000000',
		                  	format: '<b>{point.name}</b>: {point.perce+ntage:.2f} %'
	                	},
	                	showInLegend: true	
	              	}
	            },
	            legend: {
	                enabled: true
	            },
	            series:[{
	              	type:'pie',
	              	name:serversinfo[COUNT]["disks"][i]["name"],
	              	data: [
	               		{name:'使用',
						 y:parseFloat(serversinfo[COUNT]["disks"][i]["usage"])},
	                	{name:'未使用', 
						 y:100 - parseFloat(serversinfo[COUNT]["disks"][i]["usage"])}
	              	]
	            }]
	        }); //磁盘使用率折线图结束
	    }//disk循环结束
	    Highcharts.setOptions({
	        colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
	    });
	}//runhighchart函数结束

    function getServerStatusInfo(){
    	var url = $SCRIPT_ROOT + '/cluster/info';
    	var serverStatusInfo={};
    	$.ajaxSetup({async:false});
    	$.getJSON(url, null, function (data) {
      		serverStatusInfomat = data;
      		localStorage.setItem('init_write_reads', JSON.stringify(data["init_write_reads"]));
			localStorage.setItem('write_reads', JSON.stringify(data["write_reads"]));
    	});
    	return serverStatusInfomat;
	}
            
    function getClusterInfo() {
	    var url = $SCRIPT_ROOT + '/monitor/info';
	    var clusterinfomat={
	      cluster: [{
	        hostname:"tfs00"
	      }
	      ]
	    };
	    //$.ajaxSetup({async:false});
	    $.getJSON(url, null, function (data) {
	      clusterinfomat = data;
	      localStorage.setItem('clusterinfo', JSON.stringify(data));
	    });
	    return clusterinfomat;
	}
       
       
    function getMemsize(serverId){
	  return serversinfo[serverId]["memory"]["size"];
	}
    
    function createDiskPie(serverId,diskId){
	    var series = new Array();
	    var data = function(){
	      var data= [], i;
	      data.push(['Used', parseFloat(serversinfo[serverId]["disks"][diskId]["usage"])]);
	      return data;
	    }();
	    series.push({
	      "type": 'pie',
	      "name": serversinfo[serverId]["disks"][diskId]["name"],
	      "data":data
	    });
	    return series;
	}
    
    function createMemSeries(serverId) {
	    var series = new Array();
	    var time = (new Date()).getTime();
	    var data = function () {
	      var data = [],  i;
	      for (i = -29; i <= 0; i++){
	          data.push([
	            time + i * 1000,
	            parseInt(serversinfo[serverId]["memory"]["usage"][i + 29])
	          ]);
	        }
	        return data;
	    }();
	    series.push({
	      "name": "memory",
	      "data": data
	    });
	    return series;
    }
    
    function  getSeries(serverId) {
	    return serversinfo[serverId]["cpus"].length;
	}
    
    function createSeries (serverId) {
	    var series = new Array();
	    var time = (new Date()).getTime();
	    for (var cpuId = 0; cpuId < serversinfo[serverId]["cpus"].length; cpuId++){
	      var data = function () {
	        var data = [],  i;
	        for (i = -29; i <= 0; i++){
	          data.push([
	            time + i * 1000,
	            parseInt(serversinfo[serverId]["cpus"][cpuId]["usage"][i + 29])
	          ]);
	        }
	        return data;
	      }();
	      series.push({
	        "name": serversinfo[serverId]["cpus"][cpuId]["name"],
	        "data": data
	
	      });
	    }
	    return series;
    }
    
    function monitorinfoFormat(serverId, i) {
	    return '<div class="col-md-12">'+
	            '<div class= "box-header with-border monitorTitle">' +
	            '<h3 class ="box-title" id="serverid">机器名称:' + serverId + '</h3>' +
	            '</div>' +
	            '<div class= "col-md-6">' +
	            '<div class="box box-primary">' +
	            '<div class="box-header with-border">' +
	            '<i class="fa fa-bar-chart-o"></i>' +
	            '<h3 class="box-title">CPU使用率</h3>' +
	            '</div>' +
	            '<div class="box-body" id="rwCPU'+ serverId+ '" >' +
	            '<div id="CPU'+ serverId+ '"style="height: 300px"></div>' +
	            '</div>' +
	            '</div>' +
	            '</div>'+
	            '<div class= "col-md-6">' +
	            '<div class="box box-primary">' +
	            '<div class="box-header with-border">' +
	            '<i class="fa fa-bar-chart-o"></i>' +
	            '<h3 class="box-title">内存使用率</h3>' +
	            '</div>' +
	            '<div class="box-body" id="rwMem'+ serverId+ '" >' +
	            '<div id="Mem' + serverId + '" style="height: 300px"></div>' +
	            '</div>' +
	            '</div>' +
	            '</div>'+
	            '<div class="col-md-12"><div class="box box-primary"><div class="box-header with-border">'+
	            '<i class="fa fa-bar-chart-o"></i>'+
	            '<h3 class="box-title">磁盘性能</h3>'+
	            '</div>'+
	            '<div class="box-body" id="rwSpeed'+ serverId+ '" >'+
	            '<div id="RW'+ serverId+ '"style="height: 300px"></div>'+
	            '</div>'+
	            '</div></div>'+
	            '<div class="col-md-12"><div class="box box-primary"><div class="box-header with-border">'+
	            '<i class="fa fa-bar-chart-o"></i>'+
	            '<h3 class="box-title">网络性能</h3>'+
	            '</div>'+
	            '<div class="box-body" id="networkSpeed'+ serverId+ '" >'+
	            '<div id="NETWORK'+ serverId+ '"style="height: 300px"></div>'+
	            '</div>'+
	            '</div></div>'+
	            '<div class= "col-md-12">' +
	            '<div class="box box-primary">' +
	            '<div class="box-header with-border">' +
	            '<i class="fa fa-bar-chart-o"></i>' +
	            '<h3 class="box-title">磁盘使用率</h3>' +
	            '</div>' +
	            '<div class="box-body" id="DiskUsage'+ serverId+ '" >' +
	            '<div id="PieChart' + serverId + '" style="height: 100%" >'+
	            '</div>' +
	            '</div>' +
	            '</div>' +
	            '</div>'+
	            '</div>';
	}
    
    function getMonitorPieChartDiv(serverId) {
	    var monitorPieChartDiv = "";
	    for (var i = 0; i < serversinfo[serverId]["disks"].length; i ++) {
	
	      monitorPieChartDiv = monitorPieChartDiv + '<div class = "pieChartShow" id="monitorPieChart'+serverId+'disk'+ i +'"></div>';
	    }
	
	    return monitorPieChartDiv;
	}
      
      
      
      
        
})//ready函数结束
