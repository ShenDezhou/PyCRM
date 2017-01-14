/**
 * Created by jiang on 16-6-29.
 */
$(document).ready(function () {
   
    var table = $('#volumeList');
    var vCapacity;
    var getCData = function(data){
        vCapacity = data.from;
    };
    var clientList = ["nfs", "samba", "iscsi", "swift"];
    var clientIndex = {"nfs" : 0, "samba" : 1, "iscsi" : 2, "swift" : 3};


    var clusterinfo = getClusterInfo();

    //alert("Data:" + clusterinfo["cluster"][0]["hostname"]);

    var serversinfo = clusterinfo["cluster"];
    /*
     if (serversinfo[0]["hostname"] == '127.0.0.1'){
     serversinfo[0]["hostname"] = "localhost";
     }
     for(i=0; i < serversinfo[0]["cpus"].length; i++){
     serversinfo[0]["cpus"][i]["name"] = 'cpu'+i;
     }
     */
    var serversStatusinfo = getServerStatusInfo();

    var servers = serversStatusinfo["servers"];
    //alert (servers[0]["serverId"]);
    var serverslist= $('#serversList');
    var volumeData = {{ volumeData|safe}};
    //console.log(volumeData);
    var globalVolumeData = {};
    //初始化全局数据,name->status
    for (i = 0; i < volumeData.length; i++){
        var tmpName = volumeData[i]["name"];
        globalVolumeData[tmpName] = volumeData[i]["status"];
    }
    jQuery(document).ready(function ($) {
        $("[rel='tooltip']").tooltip();

        //创建volume--------------------------------
        $("#volumeCForm").submit(function( event ) {
            //创建volume
            event.preventDefault();
            var volume_name = $('#cVolumeName').val();
            var volume_capacity = vCapacity;
            var Redundancy = $('#Redundancy').val();

            $.getJSON($SCRIPT_ROOT + '/volume/add', {
                name : volume_name,
                capacity : volume_capacity,
                redundancy_ratio : Redundancy
            }, function (data) {
                var result = data["success"];
                var message = data["message"];
                var volumeIData = message;
                if (result){
                    alert("添加成功");
                    //判断是否为唯一一个volume
                    if (Object.keys(globalVolumeData).length == 0){
                        $("#noVolume").css('display','none');
                    }
                    var toString = Object.prototype.toString;
                    //console.log(volumeIData);
                    //console.log(toString.call(volumeIData));
                    addSingleVolume(volumeIData, Object.keys(globalVolumeData).length);
                    globalVolumeData[volume_name] = "Started";
                    //添加新条目到table
                    var formatData = [];
                    var tmp = {};
                    tmp["volumeName"] = volumeIData["name"];
                    if (volumeIData["status"] == "Started"){
                        tmp["status"] = "<span class=\"label label-success\">运行中</span>";
                    } else{
                        tmp["status"] = "<span class=\"label label-danger\">停止</span>";
                    }
                    tmp["capacity"] = volumeIData["capacity"];
                    if (volumeIData["nfs"]){
                        tmp["NFS"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
                    } else{
                        tmp["NFS"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
                    }
                    if (volumeIData["samba"]){
                        tmp["Samba"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
                    } else{
                        tmp["Samba"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
                    }
                    if (volumeIData["iscsi"]){
                        tmp["iSCSI"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
                    } else{
                        tmp["iSCSI"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
                    }
                    if (volumeIData["swift"]){
                        tmp["Swift"] = "<span style='color:green'><i class='fa fa-fw fa-circle'></i></span>";
                    } else{
                        tmp["Swift"] = "<span style='color:red'><i class='fa fa-fw fa-circle-o'></i></span>";
                    }
                    formatData.push(tmp);
                    table.bootstrapTable('append', formatData);


                } else {
                    alert("添加失败:" + message);
                }
            });

            $("#addVolumeM").modal("hide");
        });
        $("#vCapacity").ionRangeSlider({
            min: 1,
            max: 20,
            from: 3,
            postfix: "TB",
            onStart : function(data){
                getCData(data);
            },
            onChange : getCData,
            onFinish : getCData

        });
        $("#tabs").tab();
        $('.nav-stacked').click(function (e) {
            var target = $(e.target).attr("href");
            //判断状态确定删除键是否可以使用
            //var volumeID = $('.nav-stacked .active').text();
            var volumeID = target.replace("#tabContent","");
            if (globalVolumeData[volumeID] == "Started"){
                $('#removeVolume').prop("disabled", true);
            } else {
                $('#removeVolume').prop("disabled", false);
            }
            var rwSpeedIDt = '#' + volumeID + 'rwSpeed';
            setTimeout(function(){$(rwSpeedIDt).highcharts().reflow();}, 1);
        });
        $('.nav-tabs').click(function (e) {
            var target = $(e.target).attr("href");
            //判断状态确定删除键是否可以使用
            //var volumeID = $('.nav-stacked .active').text();
            var tabPage = target.replace("#","");
            if (tabPage == "volumeM"){
                var currentVolume = $('.nav-stacked .active').text();
                setTimeout(function(){$("#" + currentVolume + "rwSpeed").highcharts().reflow();}, 1);
            }

            if (tabPage == "monitorM"){

                setTimeout(function (){
                    for (var i = 0; i < serversinfo.length; i++){
                        $("#CPU"+serversinfo[i]["hostname"]).highcharts().reflow();
                    }

                },1);
                setTimeout(function (){
                    for (var i = 0; i < serversinfo.length; i++){
                        $("#Mem"+serversinfo[i]["hostname"]).highcharts().reflow();
                    }
                },1);
                setTimeout(function (){
                    for (var i = 0; i < serversinfo.length; i++){
                        for (var j = 0; j < serversinfo[i]["disks"].length; j++){
                            $("#monitorPieChart"+ i + "disk" + j).highcharts().reflow();
                        }
                    }
                },1);

            }
        });
        $("#removeConfirm").click(function(){
            //alert("当前存储卷!" + $('.nav-stacked .active').text());
            //删除当前的volume
            var volumeID = $('.nav-stacked .active').text();
            $.getJSON($SCRIPT_ROOT + '/volume/remove', {
                name: volumeID
            }, function (data) {
                var result = data["success"];
                var message = data["message"];
                if (result){
                    //删除成功
                    //alert("删除成功!");
                    //console.log(volumeID);
                    //删除系统概要表格列
                    table.bootstrapTable('removeByUniqueId', volumeID);
                    //删除nva tab以及对应的content
                    var volumeTab = $('#tabList' + volumeID);

                    var volumeContent = $('#tabContent' + volumeID);


                    volumeTab.remove();
                    volumeContent.remove();
                    delete globalVolumeData[volumeID];
                    if (Object.keys(globalVolumeData).length > 0){
                        //显示第一个为active
                        //alert("set active");
                        var firstVolume = Object.keys(globalVolumeData)[0];
                        if (globalVolumeData[firstVolume] == "Started"){
                            $('#removeVolume').prop("disabled", true);
                        }
                        $('.nav-stacked a[href="#tabContent' + firstVolume + '"]').tab('show');
                    } else {
                        $("#noVolume").css('display','block');
                        $('#removeVolume').prop("disabled", true);
                    }
                } else {
                    //删除失败
                    alert(message);
                }
            });
            $("#removeConfirmM").modal("hide");
        });
    });


    $(function () {
        /*----------------------------------系统概要tab-----------------------------------*/
        /*添加数据到volumeList*/
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
        }
        table.bootstrapTable('append', formatData);




        var donutData = [
            {label: "已使用", data: parseFloat({{used}}), color: "#0073b7"},
        {label: "未使用", data: parseFloat({{available}}), color: "#00c0ef"}
        ];
        $.plot("#sysUsage", donutData, {
            series: {
                pie: {
                    show: true,
                    radius: 1,
                    innerRadius: 0.5,
                    label: {
                        show: true,
                        radius: 2 / 3,
                        formatter: labelFormatter,
                        threshold: 0.1
                    }

                }
            },
            legend: {
                show: false
            }
        });
        /*------test------*/
        $.plot("#volumeUsage", donutData, {
            series: {
                pie: {
                    show: true,
                    radius: 1,
                    innerRadius: 0.4,
                    label: {
                        show: true,
                        radius: 2 / 3,
                        formatter: labelFormatter,
                        threshold: 0.1
                    }

                }
            },
            legend: {
                show: false
            }
        });
        /*---------------*/
        /*------------------------------------------存储卷管理tab------------------------*/
        var volumeTabs = $('#volumeTabs');
        var volumeContent = $('#volumeContent');
        var removeButton = $('#removeVolume');

        for (i = 0; i < volumeData.length; i++) {
            if (i == 0) {
                $("#noVolume").css('display', 'none');
            }
            addSingleVolume(volumeData[i], i);
        }
        $("[data-toggle='toggle']").bootstrapToggle();

        /*
         for (var subi = 0; subi < volumeData.length; subi++){
         const initVTableID = volumeData[subi]["volumeName"] + "ClientTable";
         for (var subj = 0; subj < clientList.length; subj++){
         var initClientID  = volumeData[subi]["volumeName"] + clientList[subj] + "Client";
         const initClientOb = $("#" + initClientID);
         const cur_row = subj;
         initClientOb.change(function() {
         if (initClientOb.prop("checked")){
         alert("checked");
         } else {
         alert("unchecked");//-------------------------------------------------to do

         $('#' + initVTableID).bootstrapTable('updateCell', {index:cur_row, field:"address", value:"--"});
         $('#' + initVTableID).bootstrapTable('updateCell', {index:cur_row, field:"username", value:"--"});
         $('#' + initVTableID).bootstrapTable('updateCell', {index:cur_row, field:"password", value:"--"});
         $("[data-toggle='toggle']").bootstrapToggle();

         }
         });
         }
         }
         */
        var nfsClient = $('#test1nfsClient');
        //console.log(nfsClient);
        nfsClient.change(function() {
            if (nfsClient.prop("checked")){
                alert("checked");
            } else {
                alert("unchecked");//-------------------------------------------------to do
            }
        });
        /*--------------------------tabcontent-----------------*/

        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        $('#rwSpeed').highcharts({
            credits: {
                enabled: false
            },
            chart: {
                type: 'line',
                animation: false, // don't animate in old IE
                events: {
                    load: function (event) {
                        var series = this.series[0];
                        var series1 = this.series[1];
                        setInterval(function () {
                            var x = (new Date()).getTime(), // current time
                                y = Math.random();//y get from background
                            series.addPoint([x, y], true, true);
                            series1.addPoint([x, Math.random()], true, true);
                        }, 1000);
                    }
                }
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150,
                minPadding: 0,
                maxPadding: 0
            },
            yAxis: {
                title: {
                    text: 'MB/s'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
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
            title : {
                text : ""
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
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -19; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 1000,
                            y: Math.random()
                        });
                    }
                    return data;
                }())
            }, {
                name: '写',
                data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;

                    for (i = -19; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 1000,
                            y: Math.random()
                        });
                    }
                    return data;
                }()),
                color : '#6FDB4B'
            }]
        });

        /*    System Manager table-------------------------*/
        var count = 0;
        for (count = 0; count < servers.length; count++){
            serverslist.append(serversListFormat(servers[count]["serverId"], count));
        }
        for (count = 0; count < servers.length; count++){
            for (var i = 0; i < servers[count]["disks"].length; i++){
                //alert("done");
                var serverid = '#diskinfo' + servers[count]["serverId"];
                var disklist = $(serverid);
                //diskContentFormat(servers[count]["disks"][i]["diskId"], i, count)
                disklist.append(diskContentFormat(servers[count]["disks"][i]["diskId"], i, count));
            }
        }


        /*　System Moniter ---------------------------------*/





        var SystemMoni = $('#ServersMoni');

        for (count = 0; count < serversinfo.length; count++){
            SystemMoni.append(monitorinfoFormat(serversinfo[count]["hostname"], count));
            // SystemMoni.append(monitorinfoFormat("localhost", count));


            Highcharts.setOptions({
                global: {
                    useUTC: false
                },
                colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
            });
            var CPUid = '#CPU' + serversinfo[count]["hostname"];
            //var CPUid = '#CPU' + 'localhost';
            //var test = createSeries(0);
            //alert(test.length);
            //alert(test[0]["name"]);
            // alert(CPUid);
            // alert(getSeries(count) +"hello");
            $(CPUid).highcharts( {
                credits: {
                    enabled: false
                },
                chart: {
                    // renderTo: 'container',
                    type: 'line',
                    animation: false, // don't animate in old IE
                    events: {
                        load: function (event) {

                            var series = this.series;
                            /*   var series1 = this.series[1];
                             var series2 = this.series[2];
                             var series3 = this.series[3];
                             var series4 = this.series[4];
                             var series5 = this.series[5];
                             var series6 = this.series[6];
                             var series7 = this.series[7];
                             */
                            var cnt = count;
                            setInterval(function ( ) {
                                var x = (new Date()).getTime();
                                // current time
                                /*    for(var i = 0; i < serversinfo[count]["cpus"].length; i++)
                                 {
                                 var x = (new Date()).getTime();
                                 var y = Math.random();//y get from background
                                 series[i].addPoint([x, y],true,true);
                                 }*/
                                var url = $SCRIPT_ROOT + '/monitor/info';
                                $.getJSON(url, null, function (data) {
                                    for (var i = 0; i < series.length; i++)
                                    {
                                        series[i].addPoint([x, parseInt(data["cluster"][cnt]["cpus"][i]["usage"][19])], true, true);
                                    }
                                });

                            }, 1000);
                        }

                    }
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
                title : {
                    text : ""
                },
                legend: {
                    enabled: true
                },
                exporting: {
                    enabled: false
                },
                series : createSeries(count)

            });


            var memId = '#Mem' + serversinfo[count]["hostname"];
            //var CPUid = '#CPU' + 'localhost';
            //var test = createSeries(0);
            //alert(test.length);
            //alert(test[0]["name"]);
            // alert(CPUid);
            // alert(getSeries(count) +"hello");
            $(memId).highcharts( {
                credits: {
                    enabled: false
                },
                chart: {
                    // renderTo: 'container',
                    type: 'spline',
                    animation: false, // don't animate in old IE
                    events: {
                        load: function (event) {
                            var series = this.series;
                            var cnt = count;
                            setInterval(function ( ) {
                                var x = (new Date()).getTime();
                                // current time
                                /*    for(var i = 0; i < serversinfo[count]["cpus"].length; i++)
                                 {
                                 var x = (new Date()).getTime();
                                 var y = Math.random();//y get from background
                                 series[i].addPoint([x, y],true,true);
                                 }*/
                                var url = $SCRIPT_ROOT + '/monitor/info';
                                $.getJSON(url, null, function (data) {
                                    series[0].addPoint([x, parseFloat(data["cluster"][cnt]["memory"]["usage"][19])], true, true);
                                });
                            }, 1000);
                        }
                    }
                },
                xAxis: {
                    type: 'datetime',
                    tickPixelInterval: 150,
                    minPadding: 0,
                    maxPadding: 0
                },
                yAxis: {
                    title: {
                        text: '内存使用率(%, '+ getMemsize(count)+'G)'
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
                title : {
                    text : ""
                },
                legend: {
                    enabled: true
                },
                exporting: {
                    enabled: false
                },
                series : createMemSeries(count)
            });


            var monitorPieChart = $('#PieChart' + serversinfo[count]["hostname"]);

            monitorPieChart.append(getMonitorPieChartDiv(count));

            //alert(serversinfo[count]["disks"].length)
            for (var i = 0; i < serversinfo[count]["disks"].length; i++) {

                //  alert("i:" + i);
                Highcharts.setOptions({
                    colors: ['#ED561B','#058DC7','#64E572', '#FF9655', '#FFF263', '#6AF9C4']
                });
                //alert(parseFloat(serversinfo[count]["disks"][i]["usage"]));

                $('#monitorPieChart'+count+ "disk"+ i).highcharts({

                    credits:{
                        enabled:false
                    },
                    exporting:{
                        enabled:false
                    },
                    chart: {
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false
                    },
                    title: {
                        text: serversinfo[count]["disks"][i]["name"] + "使用率"
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false,
                                color: '#000000',
                                connectorColor: '#000000',
                                format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                            },
                            showInLegend: true

                        }
                    },

                    series:[{
                        type:'pie',
                        name:serversinfo[count]["disks"][i]["name"],
                        data: [
                            //     ['used', 40],
                            //     ['unused',60]
                            ['使用', parseFloat(serversinfo[count]["disks"][i]["usage"]) * 100],
                            ['未使用', 100 - parseFloat(serversinfo[count]["disks"][i]["usage"]) * 100]
                        ]
                    }]
                    //createDiskPie(count, i)
                });

            }
            Highcharts.setOptions({
                colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
            });
        }
    });

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
            for (i = -19; i <= 0; i++){
                data.push({
                    "x": time + i * 1000,
                    "y": parseFloat(serversinfo[serverId]["memory"]["usage"][i + 19])
                });
            }
            return data;
        }();
        series.push({
            "name": "memory",
            "data": data
        });
        //  alert(cpuId);
        // alert(serversinfo[serverId]["cpus"][7]["name"] + "hello");
        // alert(series);
        //alert(series.length);
        return series;
    }


    function  getSeries(serverId) {
        return serversinfo[serverId]["cpus"].length;
    }

    function getData(serverId, cpuId){


    }
    function createSeries (serverId) {
        /*  var series =  [{
         name: 'Jiang',
         data: (function () {
         var data = [], time = (new Date()).getTime(), i;
         for (i = -19; i <= 0; i++) {
         data.push(
         {
         x: time + i * 1000,
         y: 2
         }
         )
         }
         return data;
         }())
         },
         {
         name: 'long',
         data: (function () {
         var data = [], time = (new Date()).getTime(), i;
         for (i = -19; i <= 0; i++) {
         data.push(
         {
         x: time + i * 1000,
         y: 2
         }
         )
         }
         return data;
         }())
         }

         ];
         return series;
         */
        var series = new Array();
        var time = (new Date()).getTime();
        for (var cpuId = 0; cpuId < serversinfo[serverId]["cpus"].length; cpuId++){

            var data = function () {
                var data = [],  i;
                for (i = -19; i <= 0; i++){
                    data.push({
                        "x": time + i * 1000,
                        "y": parseInt(serversinfo[serverId]["cpus"][cpuId]["usage"][i + 19])
                    });
                }
                return data;
            }();
            series.push({
                "name": serversinfo[serverId]["cpus"][cpuId]["name"],
                "data": data

            });
            //  alert(cpuId);

        }
        // alert(serversinfo[serverId]["cpus"][7]["name"] + "hello");
        // alert(series);
        //alert(series.length);
        return series;


    }

    function getServerStatusInfo(){
        var url = $SCRIPT_ROOT + '/cluster/info';

        var serverStatusInfo={

        };
        $.ajaxSetup({async:false});
        $.getJSON(url, null, function (data) {

            // alert(data["cluster"][0]["hostname"]);
            serverStatusInfomat = data;
        });
        return serverStatusInfomat;
        //
    }
    function getClusterInfo() {

        var url = $SCRIPT_ROOT + '/monitor/info';

        var clusterinfomat={
            cluster: [{
                hostname:"tfs00"
            }
            ]
        };
        $.ajaxSetup({async:false});
        $.getJSON(url, null, function (data) {

            // alert(data["cluster"][0]["hostname"]);
            clusterinfomat = data;
        });
        return clusterinfomat;
    }


    function monitorinfoFormat(serverId, i) {
        return '<div class="col-md-12">'+
            '<div class= "box-header with-border monitorTitle">' +
            '<h3 class ="box-title" id="serverid">机器名称：' + serverId + '</h3>' +
            '</div>' +

            '<div class= "col-md-6">' +
            '<div class="box box-primary">' +
            '<div class="box-header with-border">' +
            '<i class="fa fa-bar-chart-o"></i>' +
            '<h3 class="box-title">CPU使用率</h3>' +
            '</div>' +
            '<div class="box-body" id="rwCPU'+ serverId+ '">' +
            '<div id="CPU'+ serverId+ '" style="height: 250px; width: 100%"></div>' +
            '</div>' +
            '</div>' +
            '</div>'+

            '<div class= "col-md-6">' +
            '<div class="box box-primary">' +
            '<div class="box-header with-border">' +
            '<i class="fa fa-bar-chart-o"></i>' +
            '<h3 class="box-title">内存使用率</h3>' +
            '</div>' +
            '<div class="box-body" id="rwMem'+ serverId+ '">' +
            '<div id="Mem' + serverId + '" style="height: 250px; width: 100%"></div>' +
            '</div>' +
            '</div>' +
            '</div>'+
            /**
             '<div class= "col-md-6">' +
             '<div class="box box-primary">' +
             '<div class="box-header with-border">' +
             '<i class="fa fa-bar-chart-o"></i>' +
             '<h3 class="box-title">网络I/O</h3>' +
             '</div>' +
             '<div class="box-body" id="rwNet'+ serverId+ '">' +
             '<div id="Net' + serverId + '" style="height: 180px; width:100%"></div>' +
             '</div>' +
             '</div>' +
             '</div>'+

             '<div class= "col-md-6">' +
             '<div class="box box-primary">' +
             '<div class="box-header with-border">' +
             '<i class="fa fa-bar-chart-o"></i>' +
             '<h3 class="box-title">磁盘I/O</h3>' +
             '</div>' +
             '<div class="box-body" id="rwNet'+ serverId+ '">' +
             '<div id="Iodisk' + serverId + '" style="height: 180px; width: 100%"></div>' +
             '</div>' +
             '</div>' +
             '</div>'+
             **/

            '<div class= "col-md-12">' +
            '<div class="box box-primary">' +
            '<div class="box-header with-border">' +
            '<i class="fa fa-bar-chart-o"></i>' +
            '<h3 class="box-title">磁盘使用率</h3>' +
            '</div>' +
            '<div class="box-body" id="DiskUsage'+ serverId+ '">' +
            '<div id="PieChart' + serverId + '" style=" width: 100%">'+

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









    function serversListFormat(serverId, i) {
        if (servers[i]["serverStatus"] == "Connected"){
            return '<div class="info-box"><span style = "color:green" class="info-box-icon "><i class="fa fa-fw fa-tv" title="服务器名称:'+ serverId+'"></i></span>' +
                '<div class="info-box-content" style="color: black"> ' +
                '<span class="info-box-text">'+ serverId + '</span> ' +
                '<div class="info-box-number" id="diskinfo'+ serverId + '">' +
                '<button type="button" class="btn btn-primary btn-sm col-md-offset-10 pull-right" id="serverRestart"><i class="fa fa-refresh"></i>立即重启</button>'+
                '</div>' +
                '</div>'
            '</div>';
        }else{
            return '<div class="info-box"><span style = "color:darkslategray" class="info-box-icon"><i class="fa fa-fw fa-tv" title="服务器名称:'+ serverId+'"></i></span>  ' +
                '<div class="info-box-content" style="color: black"> ' +
                '<span class="info-box-text">'+ serverId + '</span>' +
                '<div class="info-box-number" id="diskinfo'+ serverId +'">' +
                '<button type="button" class="btn btn-primary btn-sm col-md-offset-10 pull-right" id="serverRestart"><i class="fa fa-refresh"></i>立即重启</button>'+
                '</div>' +
                '</div>'
            '</div>';
        }
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


    function addSingleVolume(volumeData, i){
        var removeButton = $('#removeVolume');
        var volumeTabs = $('#volumeTabs');
        var volumeContent = $('#volumeContent');
        var read_seri = [];
        var write_seri = [];
        for (var rw_i = 0; rw_i < volumeData["read"].length; rw_i++){
            read_seri.push(parseFloat(volumeData["read"][rw_i]));
            write_seri.push(parseFloat(volumeData["write"][rw_i]));
        }
        volumeTabs.append(volumeTabFormat(volumeData["name"], i));
        volumeContent.append(volumeContentFormat(volumeData, i));
        // 初始化启动停止功能
        const vStartButton = $('#' + volumeData["name"] + "Start");
        const vStopButton = $('#' + volumeData["name"] + "Stop");
        const vRestartButton = $('#' + volumeData["name"] + "Restart");
        const cVolumeName = volumeData["name"];
        const table = $("#volumeList");
        vRestartButton.click(
            function (){
                $.getJSON($SCRIPT_ROOT + '/volume/self/restart', {
                    volume_name: cVolumeName
                }, function (data) {
                    var status = data["success"];
                    if (status){
                        //restart成功,按钮变灰
                        alert("重启成功!");
                        vStartButton.prop("disabled", true);
                        vStopButton.prop("disabled", false);
                        //不能删除
                        removeButton.prop("disabled", true);
                        globalVolumeData[cVolumeName] = "Started";
                        //改变table状态
                        var rowData = table.bootstrapTable('getRowByUniqueId', cVolumeName);
                        rowData["status"] = "<span class=\"label label-success\">运行中</span>";
                        table.bootstrapTable('updateByUniqueId', {id: cVolumeName, row:rowData});
                    } else {
                        alert("启动失败: " + data["message"]);
                    }
                });
            }
        );
        vStartButton.click(
            //
            function (){
                $.getJSON($SCRIPT_ROOT + '/volume/self/start', {
                    volume_name: cVolumeName
                }, function (data) {
                    var status = data["success"];
                    if (status){
                        //start成功,按钮变灰
                        alert("启动成功!");
                        vStartButton.prop("disabled", true);
                        vStopButton.prop("disabled", false);
                        vRestartButton.prop("disabled", false);
                        //不能删除
                        removeButton.prop("disabled", true);
                        globalVolumeData[cVolumeName] = "Started";
                        //更改前面Table的状态

                        var rowData = table.bootstrapTable('getRowByUniqueId', cVolumeName);
                        rowData["status"] = "<span class=\"label label-success\">运行中</span>";
                        table.bootstrapTable('updateByUniqueId', {id: cVolumeName, row:rowData});
                    } else {
                        alert("启动失败: " + data["message"]);
                    }
                });
            }
        );
        vStopButton.click(
            //
            function (){
                $.getJSON($SCRIPT_ROOT + '/volume/self/stop', {
                    volume_name: cVolumeName
                }, function (data) {
                    var status = data["success"];
                    if (status){
                        //start成功,按钮变灰
                        alert("停止成功!");
                        vStartButton.prop("disabled", false);
                        vStopButton.prop("disabled", true);
                        vRestartButton.prop("disabled", true);
                        //删除变可点击
                        removeButton.prop("disabled", false);
                        globalVolumeData[cVolumeName] = "Stopped";
                        //更改Table的状态
                        var rowData = table.bootstrapTable('getRowByUniqueId', cVolumeName);
                        rowData["status"] = "<span class=\"label label-danger\">停止</span>";
                        table.bootstrapTable('updateByUniqueId', {id: cVolumeName, row:rowData});
                    } else {
                        alert("停止失败: " + data["message"]);
                    }
                });
            }
        );

        //存储设备

        var bricksBox = $("#" + cVolumeName + "Bricks");
        var bricksI = volumeData["bricks"];
        for (var i = 0; i < bricksI.length; i++){
            //alert(bricksI[i]);
            var spliceB = bricksI[i]["address"].split('/');
            var brickName = spliceB[spliceB.length - 1];
            var formatBrick = '<a class="btn btn-app" rel="tooltip" title="地址: ' + bricksI[i]["address"] + '状态: ' + bricksI[i]["online"] + '使用: ' + bricksI[i]["usage"] + '" data-html="true"> <i class="fa fa-database text-success"></i>' + brickName + ' </a>';
            bricksBox.append(formatBrick);
        }

        //快照初始化

        var snapShotTable = $('#' + cVolumeName + "Snapshot");
        snapShotTable.bootstrapTable();
        var snapShotData = volumeData["snapshots"];
        //console.log(snapShotData);
        var tmpTabSR = [];
        for (var sI = 0; sI < snapShotData.length; sI++){
            var snapshot = snapShotData[sI];
            var tmpTabSD = {};
            tmpTabSD["snapshotName"] = snapshot["Snapshot"];
            tmpTabSD["createTime"] = snapshot["Created"];
            tmpTabSD["snapshotOp"] = '<button type="button" class="btn btn-success btn-sm" style="margin-right: 10px"><i class="fa fa-reply"></i></button> <button type="button" class="btn btn-danger btn-sm" style="margin-left: 10px"><i class="fa fa-times"></i></button>';
            tmpTabSR.push(tmpTabSD);
        }
        snapShotTable.bootstrapTable('append', tmpTabSR);



        //初始化表格----------------------
        var vClientTableID = '#' + volumeData["name"] + 'ClientTable';
        $(vClientTableID).bootstrapTable();
        $(vClientTableID).on('check.bs.table', function (e, row, $element) {
            alert(row["client"]);
        });
        $(vClientTableID).on('uncheck.bs.table', function (e, row, $element) {
            alert(row["client"]);
        });
        for (var j = 0; j < 4; j++){
            var clientString = clientList[j];
            if (volumeData[clientString]){
                //start
                var tmpTabClientInfo = clientString + "Info";
                var tmpTabCR = [];
                var tmpTabCD = {};
                var metaDataClient = volumeData[tmpTabClientInfo];
                //nfs开启
                var ckClientID = volumeData["name"] + clientString + "Client";
                //tmpTabCD["ck"] = '<input id="' + ckClientID +'" type="checkbox" checked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
                tmpTabCD["ck"] = true;
                tmpTabCD["client"] = clientString;
                tmpTabCD["address"] = metaDataClient["address"];
                tmpTabCD["username"] = metaDataClient["username"];
                tmpTabCD["password"] = metaDataClient["password"];
                tmpTabCR.push(tmpTabCD);
                $(vClientTableID).bootstrapTable('append', tmpTabCR);
            } else {
                //off
                var tmpTabClientInfo = clientString + "Info";
                var tmpTabCR = [];
                var tmpTabCD = {};
                var metaDataClient = volumeData[tmpTabClientInfo];
                //nfs开启
                var ckClientID = volumeData["name"] + clientString + "Client";
                //tmpTabCD["ck"] = '<input id="' + ckClientID +'" type="checkbox" unchecked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
                tmpTabCD["ck"] = false;
                tmpTabCD["client"] = clientString;
                tmpTabCD["address"] = "--";
                tmpTabCD["username"] = "--";
                tmpTabCD["password"] = "--";
                tmpTabCR.push(tmpTabCD);
                $(vClientTableID).bootstrapTable('append', tmpTabCR);

            }
        }
        //初始化bricks
        var brickContainer = $('#' + volumeData["name"] + "Bricks");

        //初始化饼图----------------------
        var volumeUsageID = '#' + volumeData["name"] + 'Usage';
        var usage = volumeData["usage"];
        var usageData = [
            {label: "已使用", data: usage, color: "#0073b7"},
            {label: "未使用", data: 100 - usage, color: "#00c0ef"}
        ];
        $.plot(volumeUsageID, usageData, {
            series: {
                pie: {
                    show: true,
                    radius: 1,
                    innerRadius: 0.4,
                    label: {
                        show: true,
                        radius: 2 / 3,
                        formatter: labelFormatter,
                        threshold: 0.1
                    }

                }
            },
            legend: {
                show: false
            }
        });
        //初始化曲线图
        var rwSpeedID = '#' + volumeData["name"] + 'rwSpeed';
        $(rwSpeedID).highcharts({
            credits: {
                enabled: false
            },
            chart: {
                type: 'line',
                animation: false, // don't animate in old IE
                events: {
                    load: function (event) {
                        var series = this.series[0];
                        var series1 = this.series[1];
                        setInterval(function () {
                            const x = (new Date()).getTime(); // current time
                            //y = getWrite("vol1");//y get from background
                            $.getJSON($SCRIPT_ROOT + '/volume/perf', {
                                volume_name: volumeData["name"]
                            }, function (data) {
                                var result = data["success"];
                                var message = data["message"];
                                var toString = Object.prototype.toString;
                                //console.log(message);
                                //console.log(toString.call(message));
                                if (result){
                                    //return parseFloat(message);
                                    var y = message[0];
                                    var y_1 = message[1];
                                    series.addPoint([x, y], true, true);
                                    series1.addPoint([x, y_1], true, true);
                                } else {
                                    //console.log("get write performance failed: " + message);
                                    series.addPoint([x, 0], true, true);
                                    series1.addPoint([x, 0], true, true);
                                }
                            });

                        }, 3000);
                    }
                }
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150,
                minPadding: 0,
                maxPadding: 0
            },
            yAxis: {
                title: {
                    text: 'MB/s'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
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
            title : {
                text : ""
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
                    var len = read_seri.length;
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        j = -len;

                    for (; j < 0; j += 3) {
                        data.push({
                            x: time + j * 1000,
                            y: read_seri[len + j]
                        });
                    }
                    //console.log(volumeData[i]["write"].length);
                    return data;
                }())
            }, {
                name: '写',
                data: (function () {
                    var len = write_seri.length;
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        j = -len;

                    for (; j < 0; j += 3) {
                        data.push({
                            x: time + j * 1000,
                            y: write_seri[len + j]
                        });
                    }
                    //console.log(volumeData[i]["write"].length);
                    return data;
                }()),
                color : '#6FDB4B'
            }]
        });
        //初始化clinetTable
        var clientData = [];
        var tmpClientData = {};
        //NFS
        if (volumeData["nfs"]){
            var nfsData = volumeData["nfsInfo"];
            //nfs开启
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'nfsClient" type="checkbox" checked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "nfs";
            tmpClientData["address"] = nfsData["address"];
            tmpClientData["username"] = nfsData["username"];
            tmpClientData["password"] = nfsData["password"];
        } else {
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'nfsClient" type="checkbox" unchecked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "nfs";
            tmpClientData["address"] = "--";
            tmpClientData["username"] = "--";
            tmpClientData["password"] = "--";
        }
        clientData.push(tmpClientData);
        tmpClientData = {};
        //Samba
        if (volumeData["samba"]){
            var sambaData = volumeData["sambaInfo"];
            //nfs开启
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'sambaCient" type="checkbox" checked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "samba";
            tmpClientData["address"] = sambaData["address"];
            tmpClientData["username"] = sambaData["username"];
            tmpClientData["password"] = sambaData["password"];
        } else {
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'sambaCient" type="checkbox" unchecked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "samba";
            tmpClientData["address"] = "--";
            tmpClientData["username"] = "--";
            tmpClientData["password"] = "--";
        }
        clientData.push(tmpClientData);
        tmpClientData = {};
        //iSCSI
        if (volumeData["iscsi"]){
            var iscsiData = volumeData["iscsiInfo"];
            //nfs开启
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'iscsiClient" type="checkbox" checked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "iscsi";
            tmpClientData["address"] = iscsiData["address"];
            tmpClientData["username"] = iscsiData["username"];
            tmpClientData["password"] = iscsiData["password"];
        } else {
            tmpClientData["ck"] = '<input id="' + volumeData["name"] +'iscsiClient" type="checkbox" unchecked data-toggle="toggle" data-on="On" data-off="Off" data-onstyle="success" data-offstyle="danger" data-size="mini">';
            tmpClientData["client"] = "iscsi";
            tmpClientData["address"] = "--";
            tmpClientData["username"] = "--";
            tmpClientData["password"] = "--";
        }
        clientData.push(tmpClientData);
        tmpClientData = {};
        //swift
        if (volumeData["swift"]){
            var swiftData = volumeData["swiftInfo"];
            //nfs开启
            tmpClientData["ck"] = "<input id=\" " + volumeData["name"] +"swiftClient\" type=\"checkbox\" checked data-toggle=\"toggle\" data-on=\"On\" data-off=\"Off\" data-onstyle=\"success\" data-offstyle=\"danger\" data-size=\"mini\">";
            tmpClientData["client"] = "swift";
            tmpClientData["address"] = swiftData["address"];
            tmpClientData["username"] = swiftData["username"];
            tmpClientData["password"] = swiftData["password"];
        } else {
            tmpClientData["ck"] = "<input id=\" " + volumeData["name"] +"swiftClient\" type=\"checkbox\" unchecked data-toggle=\"toggle\" data-on=\"On\" data-off=\"Off\" data-onstyle=\"success\" data-offstyle=\"danger\" data-size=\"mini\">";
            tmpClientData["client"] = "swift";
            tmpClientData["address"] = "--";
            tmpClientData["username"] = "--";
            tmpClientData["password"] = "--";
        }
        clientData.push(tmpClientData);
        //console.log(clientData);
        //$clientTable.bootstrapTable('append', clientData);
        if (i == 0){
            //console.log("don1");
            $('#table_test').bootstrapTable('append', clientData);

        }
        //console.log("done2");

        if (i == 0 && volumeData["status"] == "Stopped") {
            removeButton.prop("disabled", false);
        }
    }

    function labelFormatter(label, series) {
        return '<div style="font-size:13px; text-align:center; padding:2px; color: #fff; font-weight: 600;">'
            + label
            + "<br>"
            + Math.round(series.percent) + "\%</div>";
    }
    function volumeTabFormat(volumeName, i){
        if (i == 0){
            return '<li role="presentation" id ="tabList' + volumeName + '" class ="active"><a href="#tabContent' + volumeName + '" data-toggle="tab">' + volumeName + '</a></li>';
        }else {
            return '<li role="presentation" id ="tabList' + volumeName + '"><a href="#tabContent' + volumeName + '" data-toggle="tab">' + volumeName + '</a></li>';
        }

    }
    function volumeContentFormat(volumeData, i){
        if (i == 0){
            return '<div id="tabContent' + volumeData["name"] + '" class="tab-pane active">' + contentFirstRow(volumeData) + contentSecondRow(volumeData) + contentThirdRow(volumeData["name"]) + contentForthRow(volumeData["name"]) + '</div>';
        } else {
            return '<div id="tabContent' + volumeData["name"] + '" class="tab-pane">' + contentFirstRow(volumeData) + contentSecondRow(volumeData) + contentThirdRow(volumeData["name"]) + contentForthRow(volumeData["name"]) + '</div>';
        }
    }

    function contentFirstRow(volumeData){
        var firstRow = '<div class="row"><div class="col-md-3">' + formatUsage(volumeData["name"]) + '</div>' + '<div class="col-md-9">' + formatRWSpeed(volumeData["name"]) + '</div></div>';
        return firstRow;
    }

    function formatUsage(volumeName){
        return '<div class="box box-primary"><div class="box-header with-border"><i class="fa fa-bar-chart-o"></i><h3 class="box-title">存储卷容量</h3><div class="box-tools pull-right"><button type="button" class="btn btn-box-tool" data-widget="collapse"><i class="fa fa-minus"></i></button></div></div><div class="box-body"><div id="' + volumeName + 'Usage" style="height: 150px; width:100%"></div></div></div>'
    }

    function formatRWSpeed(volumeName){
        return '<div class="box box-primary"><div class="box-header with-border"><i class="fa fa-bar-chart-o"></i><h3 class="box-title">IO读写速度</h3><div class="box-tools pull-right"><button type="button" class="btn btn-box-tool" data-widget="collapse"><i class="fa fa-minus"></i></button></div></div><div class="box-body" id="rwBox"><div id="' + volumeName + 'rwSpeed" style="height: 150px; width: 100%"></div></div></div>';
    }

    function contentSecondRow(volumeData){
        return '<div class="row"><div class="col-md-5">' + formatOperation(volumeData["name"], volumeData["status"]) + '</div><div class="col-md-7">' + formatClientTable(volumeData["name"]) + '</div></div>';
    }

    function formatOperation(volumeName, status){
        if (status == 'Started'){
            return '<div class="box box-primary"><div class="box-header with-border"><h3 class="box-title">存储卷操作</h3></div><div class="box-body table-responsive no-padding" style="color: black;height: 158px"><div class="row" style="text-align: center;margin-top: 39px;width: 100%"><button class="btn btn-app" id="' + volumeName +'Start" disabled><i class="fa fa-play"></i> 启动</button><button class="btn btn-app" id="' + volumeName + 'Restart"><i class="fa fa-repeat"></i> 重启</button><button class="btn btn-app" id="' + volumeName + 'Stop"><i class="fa fa-pause"></i> 停止</button></div></div></div>';

        } else {
            return '<div class="box box-primary"><div class="box-header with-border"><h3 class="box-title">存储卷操作</h3></div><div class="box-body table-responsive no-padding" style="color: black;height: 158px"><div class="row" style="text-align: center;margin-top: 39px;width: 100%"><button class="btn btn-app" id="' + volumeName +'Start"><i class="fa fa-play"></i> 启动</button><button class="btn btn-app" id="' + volumeName + 'Restart" disabled><i class="fa fa-repeat"></i> 重启</button><button class="btn btn-app" id="' + volumeName + 'Stop" disabled><i class="fa fa-pause"></i> 停止</button></div></div></div>';

        }
    }

    function formatClientTable(volumeName){
        return '<table data-toggle="table" data-unique-id="client" id="' + volumeName + 'ClientTable"><thead><tr><th data-align="center" data-field="ck" data-checkbox = "true"></th><th data-align="center" data-field="client">客户端</th><th data-align="center" data-field="address">网址</th><th data-align="center" data-field="username">用户名</th><th data-align="center" data-field="password">密码</th></tr></thead><tbody></tbody></table>';
    }

    function contentThirdRow(volumeName){
        return '<div class="row"><div class="box"><div class="box-header"><h3 class="box-title">存储设备</h3><div class="box-body" id="' + volumeName + 'Bricks"></div></div></div></div>';
    }

    function contentForthRow(volumeName){
        return '<div class="row"><div class="box box-primary"><div class="box-header"><i class="ion ion-clipboard"></i><h3 class="box-title">快照</h3></div><div class="box-body"><table data-toggle="table" id="' + volumeName + 'Snapshot" data-unique-id="snapshotName"><thead><tr><th data-align="center" data-field="snapshotName">快照名称</th><th data-align="center" data-field="createTime">创建时间</th><th data-align="center" data-field="snapshotOp">操作</th></tr></thead><tbody></tbody></div><div class="box-footer clearfix no-border"><button id="' + volumeName + 'Create" type="button" class="btn btn-default pull-right"><i class="fa fa-plus"></i>添加快照</button></div></div></div></div>';
    }
    function formatBrick(brickData){
        var address = brickData["address"];
        var strList = address.splice('/');
        var name = strList[strList.length - 1];
        return '<a class="btn btn-app" rel="tooltip" title="存储设备名称: ' + brickData["address"] + '状态: ' + brickData["online"] + '" data-html="true"><i class="fa fa-database text-danger"></i>' + name + '</a>';
    }

    function appendNewVolume(newVolumeData, i){
        var volumeTabs = $('#volumeTabs');
        var volumeContent = $('#volumeContent');
        var removeButton = $('#removeVolume');
        volumeTabs.append(volumeTabFormat(newVolumeData["volumeName"], i));
    }


})