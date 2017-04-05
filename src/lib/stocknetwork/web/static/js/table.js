$(function(){
	//CSV格式转化成json格式
	function csvJSON(csv){	
	  	var lines=csv.split("\n");
	  	var currentline=lines[0].split("\t");
	  	if(currentline[0][0]=="h"){
	  		if(currentline.length==5){ //xueqiu.url.types
				var headers= ["url","城市","city","行业","industry"];
			}else if(currentline.length==4){//xueqiu.crumb
				var headers= ["url","名称","简介","time"];
			}
	  	}else{
	  		var headers= ["time","username","url","interest"];
	  	}			
	  	var result = [];
	  	for(var i=0;i<lines.length-1;i++){
		  	var obj = {};
		  	var currentline=lines[i].split("\t");
		  	for(var j=0;j<headers.length;j++){
			  	obj[headers[j]] = currentline[j];
		  	}
		  	result.push(obj);			
	  	}
	  	return result; //JSON
	}
	
	
	
	function initTable(datas){
		function updateFilter(){
			var filter = $("#filter-field").val();	
			$("#example-table-filters").tabulator("setFilter", filter, $("#filter-type").val(), $("#filter-value").val());
		}

		$("#filter-field, #filter-type").change(updateFilter);
		$("#filter-value").keyup(updateFilter);

		$("#filter-clear").click(function(){
			$("#filter-field").val("");
			$("#filter-type").val("=");
			$("#filter-value").val("");

			$("#example-table-filters").tabulator("clearFilter");
		});
	
		$("#example-table-filters").tabulator({
//					height:"328px",
			fitColumns:true,
			pagination:true,
			paginationSize:30,
			columns:[
			{title:"URL", field:"url", sorter:"string", width:200, onClick:function(e, cell, val, data){window.location.href = data.url} },
			{title:"城市", field:"城市", sorter:"string", width:64},
			{title:"City", field:"city", sorter:"string",width:100},
			{title:"行业", field:"行业",width:100, sorter:"string",width:65},
			{title:"Industry", field:"industry", sorter:"string",width:96},
			{title:"名称", field:"名称", sorter:"string", width:200,onClick:function(e, cell, val, data){
				var height = cell.height();	
				cell.css({"height":"auto","overflow":"visible","white-space":"pre-wrap"});
				var brother = cell.parent().siblings();
				for (var i=0;i<brother.length;i++) {
					var sib = brother.eq(i).children().eq(5);
					sib.css({"height":26,"overflow":"hidden","white-space":"nowrap"})
				}//表格内数据过多隐藏显示。点击是显示全部
			}},
			{title:"简介", field:"简介", sorter:"string",onClick:function(e, cell, val, data){
				var height = cell.height();	
				cell.css({"height":"auto","overflow":"visible","white-space":"pre-wrap"});
				var brother = cell.parent().siblings();
				for (var i=0;i<brother.length;i++) {
					var sib = brother.eq(i).children().eq(6);
					sib.css({"height":26,"overflow":"hidden","white-space":"nowrap"})
				}
			}},
			{title:"time", field:"time",width:100, sorter:"string",onClick:function(e, cell, val, data){
				var height = cell.height();	
				cell.css({"height":"auto","overflow":"visible","white-space":"pre-wrap"});
				var brother = cell.parent().siblings();
				for (var i=0;i<brother.length;i++) {
					var sib = brother.eq(i).children().eq(7);
					sib.css({"height":26,"overflow":"hidden","white-space":"nowrap"})
				}
			}},
			],
		});

		$("#example-table-filters").tabulator("setData", datas);
		$("#example-table-pagination").tabulator("setPage", 1);

		$(window).resize(function(){
			$("#example-table-filters").tabulator("redraw");
		});
		var tableRows = $(".tabulator-row.tabulator-selectable").length;
		var rowHeight = $(".tabulator-row.tabulator-selectable").height();
		$(".tabulator-tableHolder").height(tableRows*rowHeight);
		$(".tabulator-tableHolder").css("min-height",0);
	}
	
	
	//获取用户喜好
	function userLike(){
		var defer = $.Deferred();
		$.ajax({
			type:"get",
			url:"xueqiu.like",
			success:function(data){					
				defer.resolve(data);
			}
		});
		return defer.promise();
	}
	$.when(userLike()).done(function(data){
		var jsonData = csvJSON(data);
		if(jsonData){
			var userId = sessionStorage.getItem("user");//获取用户名
			var currentTime = decodeURI(jsonData[0]["time"]);//以后如果需要时间的话要用decodeURI解码
			var userArr = [];
			for (var i=0;i<jsonData.length;i++) {
				if(jsonData[i]["username"]==userId){
					userArr.push(jsonData[i]);
				}
			}//筛选当前用户的记录信息
			var dislikeArr = [];
			for (var i=0;i<userArr.length;i++) {
				if(userArr[i]['interest']=="0"){
					var urldis = userArr[i]['url'];
					dislikeArr.push(urldis);
				}
			}//从当前用户的记录信息中选出用户不喜欢的url
			function filter(data,arrUrl){
				for (var i=0;i<data.length;i++) {
					for (var j=0;j<arrUrl.length;j++){
						if(data[i]['url']==arrUrl[j]){
							data.splice(i,1);
						}
					}
				}
			}//把用户不喜欢的url与所有数据中的URL做对比、删除不喜欢

			var localdata = sessionStorage.getItem("tableData");
			var table_data=JSON.parse(localdata);				
			var filterData = table_data;
			if(table_data){	
				console.log(table_data.length);
				filter(filterData,dislikeArr);
				console.log(filterData.length);
				initTable(filterData);
			}else{		
				function Ajax1(){
					var defer = $.Deferred();
					$.ajax({			
						url:'xueqiu.url.types.utf8',
						type:'GET', 
						scriptCharset: 'utf-8', 
						success:function(msg){
							defer.resolve(msg);
						}
					});
					return defer.promise();
				}//获取xueqiu.url.types里面的数据
				
				function Ajax2(){
					var defer = $.Deferred();
					$.ajax({			
						url:'xueqiu.crumb.utf8',
						type:'GET', 
						scriptCharset: 'utf-8', 
						success:function(msg){
							defer.resolve(msg);
						}
					});
					return defer.promise();
				}//获取xueqiu.crumb里面的数据
				$.when(Ajax1()).done(function(data){			
					var table_data1 = csvJSON(data);
					$.when(Ajax2()).done(function(data){
						var table_data2 = csvJSON(data);					
						function extend(obj1,obj2){
							for(var i=0;i<obj2.length;i++){
								for(var key in obj2[i]){ 
								    if(obj1[i].hasOwnProperty(key)){continue};//有相同的属性则略过 
								    obj1[i][key]=obj2[i][key]; 
								} 
							} 
							return obj1;
						}//把获取到的两条数据合并成一条数据以便显示到页面上
						
						var table_data = extend(table_data1,table_data2);
						var filterData = table_data;
						console.log(table_data.length);
						filter(filterData,dislikeArr);
						console.log(filterData.length);
						initTable(filterData);
//							initTable(table_data);
					})
				})
			}	
		}
	})
})