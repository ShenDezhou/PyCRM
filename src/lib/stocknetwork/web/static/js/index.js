$(function(){
	//登录页面
	var ifUser = sessionStorage.getItem("user");
	if(ifUser){//判断一下如果用户已经登录，则不显示登录页面
		$('body').css("overflow","auto");
		$("#loginCon").css("display","none");
	}else{
		
		function csvJSON1(csv){	
		  	var lines=csv.split("\n");			
		  	var result = [];
		  	var headers= ["time","username","weight"];//区分用户登录次数，加上weight
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
		function getuser(){
			var defer = $.Deferred();
			$.ajax({
				type:"get",
				url:"xueqiu.user",
				success:function(data){
					defer.resolve(data);
				}
			});
			return defer.promise();
		}//获取所有登录过的用户
		
		$.when(getuser()).done(function(data){
			var jsonData = csvJSON1(data);
			var arr1 = [];//从jsonData中把用户的手机号提取出来。当作用户名
			for (var i=0;i<jsonData.length;i++) {
				arr1.push(jsonData[i]['username'])
			}
			function arrSort1(array){			  
		        var count = 1;  
		        var yuansu= new Array();//存放数组array的不重复的元素比
		        var sum = new Array(); //存放数组array中每个不同元素的出现的次数  
		        var results = [];//同时存放元素出现次数和元素
		        for (var i = 0; i < array.length; i++) {   
		            for(var j=i+1;j<array.length;j++)  
		            {  
		                if (array[i] == array[j]) {  
		                    count++;//用来计算与当前这个元素相同的个数  
		                    array.splice(j, 1); //没找到一个相同的元素，就要把它移除掉，  
		                    j--;   
		                }  
		            }  
		            yuansu[i] = array[i];//将当前的元素存入到yuansu数组中  
		            sum[i] = count;  //并且将有多少个当前这样的元素的个数存入sum数组中  
		            count =1;  //再将count重新赋值，进入下一个元素的判断  
		        }  
		        for (var i=0;i<yuansu.length;i++) {
		        	results.push(yuansu[i]+':'+sum[i]);
		        }
		        if(results.length>=100){
		        	results.sort();
        			results.reverse();
        			results=results.slice(0,100);//如果要显示的用户过多。则只显示登录次数最多的前100名用户
		        }
				return results;
			}//数组排序
			var arr2 = arrSort1(arr1);
			var wordData = [];//用来存放最后生成词云的数据
		  	var headers= ["text","weight"];
		  	for(var i=0;i<arr2.length;i++){
			  	var obj = {};
			  	var currentline=arr2[i].split(":");
			  	for(var j=0;j<headers.length;j++){
				  	obj[headers[j]] = currentline[j];
			  	}
			  	wordData.push(obj);			
		  	}//把数据写成词云需要的数据格式
	    	$("#wordCloud").jQCloud(wordData);//初始化词云
	  });
		
		$("#login").click(function(){
			var localTime = new Date().toString().split(" ");//获取当前时间并写成固定的格式传参
	    	var timeData = localTime[0]+" "+localTime[1]+" "+localTime[2]+" "+localTime[4]+" "+localTime[3];
			var user_name = $("#userPhone").val();
			if(user_name){
				var a = /^((\(\d{3}\))|(\d{3}\-))?13\d{9}|14[57]\d{8}|15\d{9}|18\d{9}$/ ; 
				if( user_name.length!=11||!user_name.match(a) ) { 
					alert("请输入正确的手机号码!"); //判断用户输入是否为手机号
				} else{
					$.ajax({
						type:"get",
						url:"http://114.215.101.25/append?file=xueqiu.user",
						data:{
							time:timeData,
							username:user_name
						}
					});
					$('body').css("overflow","auto");
					$("#loginCon").css("display","none");
					$("#userPhone").val("");
					sessionStorage.setItem("user",user_name);//若符合登录条件。则登录并保存用户名
				}
			}else{
				alert('请输入手机号或点击下方用户名');
			}
		})
	}
	
		
	
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
	
	function arrSort(array){			  
        var count = 1;  
        var yuansu= new Array();//存放数组array的不重复的元素比如 
        var sum = new Array(); //存放数组array中每个不同元素的出现的次数  
        var results = [];//同时存放元素出现次数和元素
        for (var i = 0; i < array.length; i++) {   
            for(var j=i+1;j<array.length;j++)  
            {  
                if (array[i] == array[j]) {  
                    count++;//用来计算与当前这个元素相同的个数  
                    array.splice(j, 1); //没找到一个相同的元素，就要把它移除掉，  
                    j--;   
                }  
            }  
            yuansu[i] = array[i];//将当前的元素存入到yuansu数组中  
            sum[i] = count;  //并且将有多少个当前这样的元素的个数存入sum数组中  
            count =1;  //再将count重新赋值，进入下一个元素的判断  
        }  
        for (var i=0;i<yuansu.length;i++) {
        	results.push(sum[i]+':'+yuansu[i]);
        }
        results.sort();
        results.reverse();
        var sortArr = [];//存放按出现次数多少排序后的数组元素
		for (var i=0;i<results.length;i++) {
			var ele = results[i].split(':');
			sortArr.push(ele[1]);
		}
		return sortArr;
	}//数组排序

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
	} //获取用户对股票喜欢或不喜欢
	
	
	function getData(dataCon){
		$("#bottom").append(xihao(i));//DOM添加页面下方两个按钮
		content(dataCon);	//页面加载完成后显示第一支随机股票	
		
		var userName = sessionStorage.getItem("user");//获取当前登录用户的id
		var length = dataCon.length;
		var i=0;
		$(".xihao").click(function(){
			var localTime = new Date().toString().split(" ");
    		var timeData = localTime[0]+" "+localTime[1]+" "+localTime[2]+" "+localTime[4]+" "+localTime[3];
			var thisId = $(this).attr("id");
			if(thisId == "like"){
				var interest = "1";
			}else if(thisId == "dislike"){
				var interest = "0";
			}//1代表喜欢，0代表不喜欢
			var urlCon = $("#url a span").html();
			var encodeUrl=encodeURIComponent(urlCon);//当前URL
			$.ajax({
				type:"GET",
				url:"http://114.215.101.25/append?file=xueqiu.like",
				data:{
					time:timeData,
					username:userName,
					url:encodeUrl,
					taste:interest
				}
			});
			i++;									
			if(i>=3){
				setTimeout(function(){
					window.location.href="table.html";
				},500);	//看完三支股票之后，延迟500毫秒跳转页面		
			}
			content(dataCon);//重新添加一支随机股票的信息		
		})
		
		
		function xihao(i){
			var likebutton = '<div id="dislike" class="xihao no">不喜欢</div><div id="like" class="xihao yes">喜欢</div>';
			return likebutton;
		}
		function content(dataCon){
			var length = dataCon.length;
			var random = parseInt(Math.random()*length);
			$("#url a span").html(dataCon[random].url);
			$("#url a")[0].href = dataCon[random].url;
			$("#c_city span").html(dataCon[random]["城市"]);
			$("#city span").html(dataCon[random]["city"]);
			$("#c_industry span").html(dataCon[random]["行业"]);
			$("#industry span").html(dataCon[random]["industry"]);
			$("#name span").html(dataCon[random]["名称"]);
			$("#jianjie span").html(dataCon[random]["简介"]);
			$("#time span").html(dataCon[random]["time"]);
			$.when(userLike()).done(function(data){
				var jsonData = csvJSON(data);
				if(jsonData){
					$("#count").html("喜欢这支股票的用户还有：");
					$("#gupiaos").html("你可能还喜欢：");
//					console.log(jsonData);
					var currentUrl = $("#url a span").html();
					var urlArr = [];//此数组乘放xueqiu.like文件里包含这支股票的所有信息
					for (var i=0;i<jsonData.length;i++) {
						var fileUrl = jsonData[i]['url'];
						if(fileUrl == currentUrl){
							urlArr.push(jsonData[i]);
						}
					}//把文件里所有包含当前股票信息的数据获取出来
					var likeArr = [];//此数组乘放有多少人喜欢当前显示的股票
					var dislikeArr = [];//此数组乘放有多少人不喜欢当前显示的股票
					var likeUser = [];//此数组乘放喜欢这支股票的其余用户
					for (var i=0;i<urlArr.length;i++) {
						if(urlArr[i]['interest']=="1"){
							likeArr.push(urlArr[i]);
							likeUser.push(urlArr[i]['username']);
						}else if(urlArr[i]['interest']=="0"){
							dislikeArr.push(urlArr[i]);
						}
					}
					$("#likeCount").html(likeArr.length);
					$("#dislikeCount").html(dislikeArr.length);
					if(likeUser.length != 0){
						var html1 = "";
						var gupiaos = [];//此数组乘放喜欢这支股票的所有用户的信息
						for (var i=0;i<likeUser.length;i++) {
							html1 += '<span>'+likeUser[i]+'</span>';
							var gupiao= [];
							for(var j=0;j<jsonData.length;j++){
								if(likeUser[i]==jsonData[j]["username"]){
									gupiaos.push(jsonData[j]);
								}
							}
						}
						if(gupiaos.length != 0){
							
							var like_gupiao = [];//此数组用来乘放喜欢这支股票的用户还喜欢哪些股票的url
							for (var k=0;k<gupiaos.length;k++) {
								if(gupiaos[k]["interest"]=="1"){
									like_gupiao.push(gupiaos[k]["url"]);
								}
							}
							if(like_gupiao.length!=0){
								if(like_gupiao.length>=50){
									like_gupiao=arrSort(like_gupiao).slice(0,50);
								}
								var html2="";
								for (var i=0;i<like_gupiao.length;i++) {
									html2+='<a href="'+like_gupiao[i]+'"><span>'+like_gupiao[i]+',</span></a>';
								}
							}else{
								var html2 = "";
								html2='<span>无统计</span>';
							}
						}
						else{
							var html2 = "";
							html2='<span>无统计</span>';
						}
					}else{
						var html1 = "";
						html1 = '<span>无统计</span>';
						var html2 = "";
						html2='<span>无统计</span>';
					}
					$("#count").append(html1);
					$("#gupiaos").append(html2);
				}
			})
		}
	}
	var datas = sessionStorage.getItem("tableData");
	var jsonData = JSON.parse(datas);
	if(jsonData){
		getData(jsonData);
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
		}
		
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
		}
		$.when(Ajax1()).done(function(data){
			var data1 = csvJSON(data);
			$.when(Ajax2()).done(function(data){
				var data2 = csvJSON(data);						
				function extend(obj1,obj2){
					for(var i=0;i<obj2.length;i++){
						for(var key in obj2[i]){ 
						    if(obj1[i].hasOwnProperty(key)){continue};//有相同的属性则略过 
						    obj1[i][key]=obj2[i][key]; 
						} 
					} 
					return obj1;
				}
				var datas = extend(data1,data2);
				sessionStorage.setItem("tableData",JSON.stringify(datas));
				getData(datas);
			});
		});
	}
})