var version = {
	suffix:"VT",	
	oDataTable:null,
	bindEvents : function(){
		//绑定用户类型的change事件
	},
	initTable : function(){
		// 前两列固定列
		var columns = [
		     {
				id : 'datetime',
				name : '备份失败日期'
			},{
				id :'ip',
				name: '备份失败IP'
			}
		];
		this.oDataTable = DataTable.init({
			id : 'versionTable',
			columns : columns,
			bPaginate : false 
		});
		return true;
	
	},
	run : function(data){
		version.oDataTable.fnClearTable();
		version.oDataTable.fnAddData(data);
		 $('#versionModal').modal('show');
	},
};



function loadFullBackupPic(url,game){
    $.ajax({
        mimeType: 'textml; charset=utf-8', // ! Need set mimeType only when run from local file
        url: url,
        dataType: "json",
        type: 'GET',
        success: function(json){
	var dateTimeList = new Array();
	var successNumList = new Array();
	var failNumList = new Array();

        for(var i in json){
	   dateTimeList.push(json[i].datetime);
	   successNumList.push(json[i].success.length);
	   failNumList.push(json[i].fail.length);
	}



$(function () {
    $('#fullBackupPic').highcharts({
        chart: {
        },
	legend:{
	    itemHiddenStyle:{
		color:'white'
	    }
	},
        title: {
            text: "完整备份" 
        },
        subtitle: {
            text: game
        },
        xAxis: {
            categories: dateTimeList 
        },
        yAxis: {
            title: {
                text: 'num' 
            }
        },
	plotOptions :{
	    series: {
		cursor: 'pointer',
		events: {
		    click: function(){


         var day = new Date();
         var curdate=day.getFullYear()+"-"+((day.getMonth()+1)<10?"0":"")+(day.getMonth()+1)+"-"+((day.getDate()+1)<10?"0":"")+(day.getDate()+1);
         var defautdate = day.getFullYear()+"-"+((day.getMonth()+1)<10?"0":"")+(day.getMonth()+1)+"-"+((day.getDate()-2)<10?"0":"")+(day.getDate()-2);
         var startdateoption = document.getElementById("startDate");
         var startdate = startdateoption.value;
         var enddateoption = document.getElementById("endDate");
         var enddate = enddateoption.value;
         if (startdate=="")
         {
                startdate=defautdate
         }
         if (enddate=="")
         {
                enddate=curdate
         }	





			$.ajax({
				url: '/api/getFullBackup/?game='+game+'&startdate='+startdate+'&enddate='+enddate,
				mimeType: 'textml; charset=utf-8', // ! Need set mimeType only when run from local file
				dataType: "json",
				type: 'GET',
				success: function(json){			   	
				var result = [];
				for(var i in json){
				   var failList= json[i].fail;
				   var datetime = json[i].datetime;
				   for(ip in failList){
					var temp = {'datetime':datetime,'ip':failList[ip]}
					result.push(temp)
				   }
				}

				//for(date in datetime){
				//	var temp={'datetime':datetime[date]}
				//	result.push(temp)
				//}
				//var result = [];
				//var fail_ip = data.fail;
				
				//for(ip in fail_ip){
				//	var temp = {'ip':fail_ip[ip]}
				//	result.push(temp);
				//}
				version.initTable();
			 	version.run(result);	
	

			  }
			
			})
		    }
		}
	    }
	},
        series: [{
            name: "success",
            data: successNumList 
        }, {
            name: 'fail',
            data: failNumList
        }]
    });
});









	},
        error: function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
            //debugger;
        },
        async: false
    });
}
