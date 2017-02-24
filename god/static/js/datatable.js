var DataTable = function() {
    var oDataTable = null;
    return {
	/**
	 * DataTable.init({ id:'#serverDataTable', columns:[{ id:'startTime',
	 * name:'开始时间', sort:true },{ id:'endTime', name:'开始时间' }] });
	 */
	init : function(conf) {
	    var tableHtml = [];
	    var columns = [];
	    // 若已存在表格，清掉
	    if ($("#" + conf.id + " div").length) {
		$("#" + conf.id + " div").html("");
	    }
	    tableHtml
		    .push('<table class="table table-bordered table-hover" id="'
			    + conf.id + '_table"><thead><tr>');
	    $.each(conf.columns, function(index, data) {
		tableHtml.push('<th><strong>' + data.name + '</strong></th>');
		columns.push({
		    'mDataProp' : data.id,
		    'bSortable' : data.sort ? true : false,
		    'mRender' : data.mRender || function(data, type, full) {
		    	return data
		    }
		});
	    });
	    tableHtml.push('</tr></thead></table>');
	    // 画出table
	    $("#" + conf.id).html(tableHtml.join(""));
	    if (columns.length === 0) {
		return;
	    }
	    // 初始化table
	    oDataTable = $("#" + conf.id + "_table")
		    .dataTable(
			    {
				"bStateSave" : true, // 缓存 ,
				"bDestroy" : true,
				"sDom" : "T<'clear'f><'row'r><'table-scrollable't><'row-fluid'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",// l-每页显示数量,f-过滤输入,t-表单,i-信息,p-翻页
				"bScrollCollapse" : true,
				"oTableTools" : {
				    "sSwfPath" : "assets/plugins/data-tables/media/swf/copy_csv_xls_pdf.swf",
				    "aButtons" : [ {
					"sExtends" : "copy",
					"sButtonText" : "导出",
					"sButtonClass" : "btn default btn-ext"
				    } ]
				},
				"aoColumns" : columns,
		         //解决checkbox样式失效
		         "fnDrawCallback": function () {       
				     App.initUniform();        
				 },
				"iDisplayLength" : conf.iDisplayLength ? conf.iDisplayLength: 100,
				"bPaginate": conf.bPaginate==false ? false : true   //开关，是否显示分页器		
			    });
	    $('#' + conf.id + '_table_wrapper .dataTables_filter input').addClass("form-control input-medium"); // modify
	    $('#' + conf.id + '_table_wrapper .dataTables_length select').addClass("form-control input-xsmall"); // modify
	    $('#' + conf.id + '_table_wrapper .dataTables_length select').select2();
	    $('#sample_2_column_toggler input[type="checkbox"]').change(function(){
	    	debugger
            /* Get the DataTables object again - this is not a recreation, just a get of the object */
            var iCol = parseInt($(this).attr("data-column"));
            var bVis = this.oDataTable.fnSettings().aoColumns[iCol].bVisible;
            this.oDataTable.fnSetColumnVis(iCol, (bVis ? false : true));
      });
	    
	    return oDataTable;
	},
	/**
	 * DataTable.query({
	 * url:'operating.do?method=querySingleServerDataList', 
	 * params:{ 
	 * 	a:1,
	 *  b:'test', 
	 * } } );
	 */
	query : function(conf) {
	    // 请求模版参数
	    $.Ajax(conf.url, conf.params, null, function(data) {
		oDataTable.fnClearTable();
		// 重新添加数据
		oDataTable.fnAddData(data.root);
	    });
	}
    };
}();
