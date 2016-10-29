$(function() {
	var detail_table = null;
    var checked = false;
   
	$.stats_show_detail = function(activity_id , type, status_type){
        status_type = status_type || '';
        if (detail_table == null) {
            detail_table = $('#detail_list_table').DataTable({
                responsive: true,
                "dom": '<"clear">frtip',
                "processing": true,
                "serverSide": true,
                "searching": true,
                "bStateSave": true,
                "fnStateSave": function(oSettings, oData) { save_dt_view(oSettings, oData); },
                "fnStateLoad": function(oSettings) { return load_dt_view(oSettings); },
                "tableTools": {
                    "sSwfPath": "/static/lte/plugins/data-tables/extensions/TableTools/swf/copy_csv_xls_pdf.swf",
                    "aButtons": [{
                        "sExtends": "xls",
                        "sButtonText": "导出Excel",
                        "sFileName": "列表.xls"
                    }]
                },
                "ajax": "/rest/mgr/discussion/visit/table?activity_id="+activity_id+"&type="+type+'&status_type='+status_type,
                "columns": [{
                    "data": "name",
                    "mRender": function(data, something, full) {
                        return "<a class='btn btn-link btn-xs' target='_blank' href='" + full['link'] + "'>"+data+"</a>";
                    }
                }, {
                    "data": "fullname",
                    "mRender": function(data, something, full) {
                        return "<a class='btn btn-link btn-xs' target='_blank' href='" + full['auth_link'] + "'>"+data+"</a>";
                    }
                }, {
                    "data": "visit_count"
                },{
                    "data": "first_visited"
                },{
                    "data": "last_visited"
                },{
                    "data": "link",
                    "mRender": function(data, something, full) {
                        return "<a class='btn btn-link btn-xs' target='_blank' href='" + data + "'>"+data+"</a>";
                    }
                }],
                "columnDefs": [],
                "aaSorting": [4, 'desc'],
                "language": TABLE_LANG
            });
        } else {
            detail_table.ajax.url("/rest/mgr/activity/sign_up_or_register/table?activity_id="+activity_id+"&type="+type+'&status_type='+status_type).load();
        }
    };
    $.stats_show_detail(getQueryString("activity"),"discussion");

    var personInfo = function(person_info) {
        var output = "<tr><td>人员类型</td><td class='person_type'></td></tr><tr><td>公司名称</td><td class='org_name'></td></tr>"+personInfoTitle();
      
        var tables = '';
        tables += '<table id="person_info_table" class="table table-bordered display responsive nowrap table-striped"><tbody></tbody></table>';
        $('#div_person').html(tables);         
        $('#person_info_table tbody').html(output);
        for (var key in person_info)
        {
            if(key=='gender')
            {
                if(person_info[key]==2)
                    $('#person_info_table .' + key).html('女士');
                else
                    $('#person_info_table .' + key).html('先生');
            }
            else
                $('#person_info_table .' + key).html(person_info[key]);
        }
        if( person_info['attachment'])
        {
            $('#images').show();
            var images = person_info['attachment'].split(',');
            var image_output = "";
            for (var i = 0; i < images.length; i++) {
                image_output += "<tr><td><img width='500px' height='300px' src='" + $.get_file_url(images[i],'/assets/ticket/image/') + "'></td></tr>";
            }
            $('#image_table tbody').html(image_output);
        }
        else
        {
            $('#images').hide();
        }

    };
    $.getPersonDetailInfo=function(person_id) {
        $.ajax({
            type: "get",
            cache: false,
            url: '/rest/mgr/person/detail',
            data: {
                person_id: person_id
            },
            success: function(data) {
                if (data.error) {
                    return alert(data.error);
                }
                personInfo(data);
                $("#modal-person-detail").modal("show");
            },
            error: function() {
                alert('网络错误！');
            },
            dataType: 'json'
        });
    };
});