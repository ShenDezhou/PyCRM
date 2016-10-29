var TABLE_LANG = {
    "emptyTable": "暂无数据",
    "info": "当前显示 _START_ 到 _END_ 条记录, 共 _TOTAL_ 条",
    "infoEmpty": "当前 0 到 0 / 共 0 条",
    "infoFiltered": "",
    "infoPostFix": "",
    "thousands": ",",
    "lengthMenu": "每页显示&nbsp; _MENU_ &nbsp;条",
    "loadingRecords": "正在加载...",
    "processing": "正在处理...",
    "search": "搜索:",
    "zeroRecords": "暂无数据",
    "paginate": {
        "first": "首页",
        "last": "末页",
        "next": "下一页",
        "previous": "上一页"
    },
    "aria": {
        "sortAscending": ": 顺序排序",
        "sortDescending": ": 反序排序"
    }
};

function save_dt_view (oSettings, oData) {
    localStorage.setItem( 'DataTables_'+window.location.href, JSON.stringify(oData) );
}
function load_dt_view (oSettings) {
    return JSON.parse( localStorage.getItem('DataTables_'+window.location.href) );
}
function reset_dt_view() {
    localStorage.removeItem('DataTables_'+window.location.href);
}

var personInfoTitle = function(){
    var output = "";       
    output += "<tr><td style='width:90px;'>姓名</td><td class='fullname'></td></tr>";
    output += "<tr><td>性别</td><td class='gender'></td></tr>";
    output += "<tr><td>出生日期</td><td class='birthday'></td></tr>";
    output += "<tr><td>毕业院校</td><td class='school'></td></tr>";
    output += "<tr><td>入学年份</td><td class='school_start'></td></tr>";
    output += "<tr><td>所在城市</td><td class='city'></td></tr>";
    output += "<tr><td>微信号</td><td class='wechatid'></td></tr>";
    output += "<tr><td>微信群</td><td class='weixin_group'></td></tr>";
    output += "<tr><td>电话号码</td><td class='cellphone'></td></tr>";
    output += "<tr><td>电话号码1</td><td class='cellphone1'></td></tr>";
    output += "<tr><td>电话号码2</td><td class='cellphone2'></td></tr>";
    output += "<tr><td>E-mail</td><td class='email'></td></tr>";
    output += "<tr><td>E-mail1</td><td class='email1'></td></tr>";
    output += "<tr><td>E-mail2</td><td class='email2'></td></tr>";
    output += "<tr><td>地址</td><td class='address'></td></tr>";
    output += "<tr><td>职位</td><td class='position'></td></tr>";
    output += "<tr><td>个人背景简介</td><td class='person_info'></td></tr>";
    output += "<tr><td>院系</td><td class='school_department'></td></tr>";
    output += "<tr><td>学号</td><td class='school_number'></td></tr>";
    return output;
};

var willAndExpect = function(){
    var output = "";
    output += "<tr><td>联合会普通会员推荐人1</td><td class='first_normal_recommend'></td></tr>";
    output += "<tr><td>联合会普通会员推荐人2</td><td class='second_normal_recommend'></td></tr>";
    output += "<tr><td>联合会理事会员推荐人</td><td class='first_advanced_recommend'></td></tr>";
    output += "<tr><td>期望获取哪些服务或资源</td><td class='expects'></td></tr>";
    output += "<tr><td>可提供哪些服务或资源</td><td class='wills'></td></tr>";
    return output;
};

var orgInfoTitle = function(){
    var output = "";
    output += "<tr><td style='width:90px;'>公司名</td><td class='org_name'></td></tr>";
    output += "<tr><td>企业法人/责任人</td><td class='representative'></td></tr>";
    output += "<tr><td>所属行业</td><td class='industry'></td></tr>";
    output += "<tr><td>是否高新企业</td><td class='high_tech'></td></tr>";
    output += "<tr><td>公司简介</td><td class='general_description'></td></tr>";
    output += "<tr><td>业务范围</td><td class='domain_description'></td></tr>";
    output += "<tr><td>公司网址</td><td class='website'></td></tr>";
    output += "<tr><td>办公地址</td><td class='office_address'></td></tr>";
    output += "<tr><td>注册地址</td><td class='reg_address'></td></tr>";
    output += "<tr><td>备注</td><td class='comments'></td></tr>";
    return output;
};

var isIE = function(ver){
    var b = document.createElement('b');
    b.innerHTML = '<!--[if IE ' + ver + ']><i></i><![endif]-->';
    return b.getElementsByTagName('i').length === 1;
};

$.get_file_url = function(path, rel_path){
    return rel_path + path;
};
function getQueryString(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]);
        return null;
}

$.showLoading = function(msg){
    msg = msg || '正在加载...';
    if(!$._showLoadingDiv){
        $._showLoadingDiv = $('<div class="overlay" style="position:fixed;left:0;top:0;z-index:99999;width:100%;height:100%;background:rgba(228, 228, 228, 0.3);">' + 
                                '<div class="form-loading-container">' + 
                                    '<div class="form-loading-icon"></div>' +
                                    '<div class="form-loading-text"></div>' +
                                '</div>' +
                                '</div>').appendTo('body');
    }else{
        $._showLoadingDiv.css('display', '');
    }
    $('.form-loading-text', $._showLoadingDiv).text(msg);
};
$.hideLoading = function(){
    if($._showLoadingDiv){
        $._showLoadingDiv.css('display', 'none');
        $('.form-loading-text', $._showLoadingDiv).text('');
    }
};