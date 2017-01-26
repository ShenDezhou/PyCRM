$(document).ready(function(){			
	$(".menu-item.abstract").click(function(){
    	var monitorMNav_hide = $("#monitorMNav").css("height");
    	if(monitorMNav_hide != "0px"){
    		$(".menu-item.monitor .fa.fa-chevron-down").removeClass("fa-chevron-UP");
    		$("#monitorMNav").stop().animate({
    			height:"0"
    		},500)
    	}
    	$(".menu-item.volume .fa.fa-chevron-down").removeClass("fa-chevron-UP");
		$("#volumeMNav").stop().animate({
			height:"0"
		},500)    	
    })
	
		
	function get_volumedata() {
	    var url = $SCRIPT_ROOT + '/overview/volumeData';
		$.ajaxSetup({async:false});
	    $.getJSON(url, null, function (data) {
	      volume_Data = data;
	    });
	    return volume_Data;
	}//获取volume_Data
	
	
	var volumeData = get_volumedata();
	var table = $('#volumeList');//系统概要里磁盘卷信息列表
	
	function getSysCapacity() {
    	var url = $SCRIPT_ROOT + '/overview/capacity';
//		$.ajaxSetup({async:false});
    	$.getJSON(url, null, function (data) {
      	totalCapacity = data[0];
      	availableCapacity = data[1];
      	volume_numsCapacity = data[2];
      	usedCapacity = data[3];
      	$("#sysTotal").html(totalCapacity+"GB");
      	$("#sysFree").html(availableCapacity+"GB");
      	$("#volumeNumber").html(volume_numsCapacity);
      	var html_option = "";
				$.each(data[4],function(i,n){
					html_option += '<option value="'+data[4][i]+'">'+data[4][i]+'%</option>';
				})
     	  $("#Redundancy").append(html_option);
    	});
  	}
	getSysCapacity();
	   
    /*添加数据到volumeList，即磁盘卷信息列表*/
	var formatData = [];
	for (var i = 0; i < volumeData.length; i++){
    var tmp = {};
    tmp["volumeName"] = volumeData[i]["name"];
    if (volumeData[i]["status"] == "Started"){
      tmp["status"] = "<span class=\"label label-success\">运行中</span>";
    } else{
      tmp["status"] = "<span class=\"label label-danger\">停止</span>";
    }
    tmp["capacity"] = volumeData[i]["capacity"];
    if (volumeData[i]["nfs"]){
      tmp["NFS"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
    } else{
      tmp["NFS"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
    }
    if (volumeData[i]["samba"]){
      tmp["Samba"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
    } else{
      tmp["Samba"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
    }
    if (volumeData[i]["iscsi"]){
      tmp["iSCSI"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
    } else{
      tmp["iSCSI"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
    }
    if (volumeData[i]["swift"]){
      tmp["Swift"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
    } else{
      tmp["Swift"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
    }
    formatData.push(tmp);
	}//for循环结束
	table.bootstrapTable('append', formatData);//在磁盘卷列表里添加信息
	var donutData = [
    	{label: "已使用", data: parseFloat(usedCapacity), color: "#0073b7"},
    	{label: "未使用", data: parseFloat(availableCapacity), color: "#00c0ef"}
  	];
  
 	//  系统概要里系统容量饼状图
//	$.plot("#sysUsage", donutData, {
//    series: {
//      pie: {
//        show: true,
//        radius: 1,
//        innerRadius: 0.5,
//        label: {
//          show: true,
//          radius: 2 / 3,
//          formatter: labelFormatter,
//          threshold: 0.1
//        }
//      }
//    },
//    legend: {
//      show: false
//    }
//  });//plot结束
    
    $('#sysUsage').highcharts({
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
          text:""
        },
        tooltip: {
          //pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
   		  enabled: false
        },
        colors: ['#ED561B','#00C0EF','#64E572','#FF9655', '#FFF263', '#6AF9C4'],
        plotOptions: {
          	pie: {
          		size:290,
            	allowPointSelect: true,
            	cursor: 'pointer',
				innerSize:"50%",
            	dataLabels: {
                  	enabled: true,
					distance:-40,
                  	connectorColor: '#000000',
                  	format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                  	style:{
	            		color:"#fff",
	            		fontWeight:"lighter",
	            		textShadow:"none"
	            	}
            	}
          	}
        },
        series:[{
          	type:'pie',
          	//name:"系统容量",
          	data: [
           		['使用', parseFloat(usedCapacity)],
            	['未使用', parseFloat(availableCapacity)]
          	]
        }]
    });
    
    
    function labelFormatter(label, series) {
    	return '<div style="font-size:13px; text-align:center; padding:2px; color: #fff; font-weight: 600;">'
            + label
            + "<br>"
            + Math.round(series.percent) + "\%</div>";
  	}
    
    
    var cluster_info = JSON.parse(localStorage.getItem('init_write_reads'));
    clusterInfo = cluster_info[0];
    console.log(clusterInfo);
    
	Highcharts.setOptions({
        global : {
            useUTC : false
        },
        lang: {
	        rangeSelectorZoom: '时间长度' 
	    }
//	    colors: ['#ED561B', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
    });
	$('#sum_diskio_speed').highcharts('StockChart', {
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
	                setInterval(function () {
	                  	var x = (new Date()).getTime()-333000;	
	                    var data_string = localStorage.getItem("clusterinfo")
    					if (!data_string){
    						alert("No use");
    					}
    					var data = JSON.parse(data_string);
    					var Length = data["cluster"][0]["init_disk_read_sum"].length-1;
    					var valueTimeRead = data["cluster"][0]["init_disk_read_sum"][Length];
		                var JsonDataRead = eval('(' + valueTimeRead + ')'); 
		                var valueTimeWrite = data["cluster"][0]["init_disk_write_sum"][Length];
		               	var JsonDataWrite = eval('(' + valueTimeWrite + ')');
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
                		var number = (this.y/(1024*1024)).toFixed(2)+"MB";
                	}else if(this.y<(1024*1024)){
                		var number = (this.y/1024).toFixed(2)+"KB";
                	}else if(this.y==0){
                		var number = "0KB";
                	}
                    s += '<br/><span style="font-weight:800;color:'+this.series.color+';">'+this.series.name+'</span>: <b>'+number+'</b>';
                });

                return s;
            },
            valueDecimals: 2,
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
        name: '读',
        data: (function () {
        	var valueTime = clusterInfo["init_network_in_sum"][20];
	      	var JsonData = eval('(' + valueTime + ')'); 
          	var data = [],time = parseInt(JsonData.time),j;
         	for (j = -359; j < 0; j += 1) {
         		var valueTime = clusterInfo["init_network_in_sum"][j+359];
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
          var valueTime = clusterInfo["init_disk_write_sum"][20];
	      var JsonData = eval('(' + valueTime + ')'); 
          var data = [], time = parseInt(JsonData.time),j;
          for (j = -359; j < 0; j += 1) {
          	var valueTime = clusterInfo["init_disk_write_sum"][j+359];
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
    
    
//  var read_seri1 = [];
//  var write_seri1 = [];
//  for (var rw_i = 0; rw_i < clusterInfo["init_network_in_sum"].length; rw_i++){
//    	read_seri1.push(parseFloat(clusterInfo["init_network_in_sum"][rw_i]));
//    	write_seri1.push(parseFloat(clusterInfo["init_network_out_sum"][rw_i]));
//  }
	
	$('#sum_networkio_speed').highcharts('StockChart', {
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
	    		var Series = this.series;
	                setInterval(function () {
	                  var x = (new Date()).getTime()-333000;	
	                    var data_string = localStorage.getItem("clusterinfo")
    					if (!data_string){
    						alert("No use");
    					}
    					var data = JSON.parse(data_string);
    					var Length = data["cluster"][0]["init_network_in_sum"].length-1; 
    					var valueTimeIn = data["cluster"][0]["init_network_in_sum"][Length];
		                var JsonDataIn = eval('(' + valueTimeIn + ')'); 
		                var valueTimeOut = data["cluster"][0]["init_network_out_sum"][Length];
		               	var JsonDataOut = eval('(' + valueTimeOut + ')');
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
                		var number = (this.y/(1024*1024)).toFixed(2)+"MB";
                	}else if(this.y<(1024*1024)){
                		var number = (this.y/1024).toFixed(2)+"KB";
                	}else if(this.y==0){
                		var number = "0KB";
                	}
                    s += '<br/><span style="font-weight:800;color:'+this.series.color+';">'+this.series.name+'</span>: <b>'+number+'</b>';
                });
                return s;
            },
            valueDecimals: 2,
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
          //var len = read_seri1.length;
          var valueTime = clusterInfo["init_network_in_sum"][20];
	      var JsonData = eval('(' + valueTime + ')'); 
          var data = [],time = parseInt(JsonData.time),j;
          for (j = -359; j < 0; j += 1) {
          	var valueTime = clusterInfo["init_network_in_sum"][j+359];
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
          //var len = write_seri1.length;
          var valueTime = clusterInfo["init_network_out_sum"][20];
	      var JsonData = eval('(' + valueTime + ')'); 
          var data = [],time = parseInt(JsonData.time),j;
          for (j = -359; j < 0; j += 1) {
          	var valueTime = clusterInfo["init_network_out_sum"][j+359];
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
   
    
})
