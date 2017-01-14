$(document).ready(function(){
	var serverslist= $('#serversList');//系统管理页面里集群机器信息列表
	var serversStatusinfo = getServerStatusInfo();
	var servers = serversStatusinfo["servers"];
	var count = 0;
    for (count = 0; count < servers.length; count++){
      	serverslist.append(serversListFormat(servers[count]["serverId"], count));
    }
    for (count = 0; count < servers.length; count++){
      	for (var i = 0; i < servers[count]["disks"].length; i++){
	        var serverid = '#diskinfo' + servers[count]["serverId"];
	        var disklist = $(serverid);
	        disklist.append(diskContentFormat(servers[count]["disks"][i]["diskId"], i, count));
      	}
    }
    $(".menu-item.system").click(function(){
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
    
    function serversListFormat(serverId, i) {
	    if (servers[i]["serverStatus"] == "Connected"){
	      return '<div class="info-box"><span style = "color:green" class="info-box-icon "><i class="fa fa-fw fa-tv" title="服务器名称:'+ serverId+'"></i></span>' +
	              '<div class="info-box-content" style="color: black"> ' +
	              '<span class="info-box-text">'+ serverId + '</span> ' +
	              '<div class="info-box-number" id="diskinfo'+ serverId + '">' +
	              '<button type="button" class="btn btn-primary btn-sm col-md-offset-10 pull-right" id="serverRestart"><i class="fa fa-refresh"></i>立即重启</button>'+
	              '</div>' +
	              '</div>'+
	      '</div>';
	    }else{
	      return '<div class="info-box"><span style = "color:darkslategray" class="info-box-icon"><i class="fa fa-fw fa-tv" title="服务器名称:'+ serverId+'"></i></span>  ' +
	              '<div class="info-box-content" style="color: black"> ' +
	              '<span class="info-box-text">'+ serverId + '</span>' +
	              '<div class="info-box-number" id="diskinfo'+ serverId +'">' +
	              '<button type="button" class="btn btn-primary btn-sm col-md-offset-10 pull-right" id="serverRestart"><i class="fa fa-refresh"></i>立即重启</button>'+
	              '</div>' +
	              '</div>'+
	      '</div>';
	    }
	}
    
    
    function getServerStatusInfo(){
    	var url = $SCRIPT_ROOT + '/cluster/info';
    	var serverStatusInfo={};
      	$.ajaxSetup({async:false});
    	$.getJSON(url, null, function (data) {
      		serverStatusInfomat = data;
    	});
    	return serverStatusInfomat;
	}
    
    
    function diskContentFormat(diskId , i, count){
	    if (servers[count]["disks"][i]["diskStatus"] == "health") {
	      // return '<a class="btn btn-app" rel="tooltip" title="存储设备名称: 166.111.131.144:/few/fe<br>状态: 在线" data-html="true">  <i class="glyphicon glyphicon-tasks text-success"></i>块名称</a>';
	      return ' <i class="glyphicon glyphicon-tasks text-success" title="磁盘编号:'+ diskId + '"></i>'
	    }else{
	      //  return '<a class="btn btn-app" rel="tooltip" title="存储设备名称: 166.111.131.144:/few/fe<br>状态: 在线" data-html="true">  <i class="glyphicon glyphicon text-danger"></i>块名称</a>';
	      return ' <i class="glyphicon glyphicon-tasks text-danger" title="磁盘编号:'+ diskId + '"></i>'
	    }
	  }   
})