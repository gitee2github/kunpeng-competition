<#--
 *
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 *
-->
<#include "../include/page_import.ftl">
<#include "../include/html_doctype.ftl">
<html>
<head>
<#include "../include/html_head.ftl">
<title>
	<#include "../include/html_app_name_prefix.ftl">
	<@spring.message code='module.exportData' />
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-manager page-export-data">
	<div class="page-header grid grid-nogutter align-items-center pb-2">
		<div class="col-12 flex align-items-center mb-1">
			<i class="pi pi-database text-color-secondary text-sm"></i>
			<div class="text-color-secondary text-sm ml-1">${schema.title}</div>
		</div>
		<div class="col-12">
			<label class="text-lg font-bold">
				<@spring.message code='dataExport.selectDataType' />
			</label>
		</div>
	</div>
	<div class="page-content">
		<form id="${pid}form">
			<div class="pl-5 pt-4 pb-2">
				<div class="field-radiobutton">
					<p-radiobutton id="${pid}vsc" name="dataType" value="csv" v-model="fm.dataType"></p-radiobutton>
					<label for="${pid}vsc" style="min-width:8rem;"><@spring.message code='dataExport.dataType.csv' /></label>
					<label for="${pid}vsc" class="ml-3 text-sm text-color-secondary"><@spring.message code='dataExport.dataType.csv.desc' /></label>
				</div>
				<div class="field-radiobutton pt-2">
					<p-radiobutton id="${pid}excel" name="dataType" value="excel" v-model="fm.dataType"></p-radiobutton>
					<label for="${pid}excel" style="min-width:8rem;"><@spring.message code='dataExport.dataType.excel' /></label>
					<label for="${pid}excel" class="ml-3 text-sm text-color-secondary"><@spring.message code='dataExport.dataType.excel.desc' /></label>
				</div>
				<div class="field-radiobutton pt-2">
					<p-radiobutton id="${pid}sql" name="dataType" value="sql" v-model="fm.dataType"></p-radiobutton>
					<label for="${pid}sql" style="min-width:8rem;"><@spring.message code='dataExport.dataType.sql' /></label>
					<label for="${pid}sql" class="ml-3 text-sm text-color-secondary"><@spring.message code='dataExport.dataType.sql.desc' /></label>
				</div>
				<div class="field-radiobutton pt-2">
					<p-radiobutton id="${pid}json" name="dataType" value="json" v-model="fm.dataType"></p-radiobutton>
					<label for="${pid}json" style="min-width:8rem;"><@spring.message code='dataExport.dataType.json' /></label>
					<label for="${pid}json" class="ml-3 text-sm text-color-secondary"><@spring.message code='dataExport.dataType.json.desc' /></label>
				</div>
			</div>
			<div class="pt-3 text-center">
				<p-button type="submit" label="<@spring.message code='confirm' />"></p-button>
			</div>
		</form>
	</div>
</div>
<#include "../include/page_form.ftl">
<#include "../include/page_simple_form.ftl">
<script>
(function(po)
{
	po.schemaId = "${schema.id}";
	po.queries = ($.unescapeHtmlForJson(<@writeJson var=queries />) || []);
	po.submitUrl = function()
	{
		var fm = po.vueFormModel();
		var url="/dataexchange/"+encodeURIComponent(po.schemaId)+"/export/" + fm.dataType;
		
		$.each(po.queries, function(i, query)
		{
			url = $.addParam(url, "query", query, true);
		});
		
		return url;
	}
	
	if(po.isAjaxRequest)
	{
		po.setupForm({ dataType: "csv" },
		{
			closeAfterSubmit: false,
			success: function(response)
			{
				po.element().parent().html(response);
			}
		});
	}
	//新窗口打开
	else
	{
		po.setupForm({ dataType: "csv" },
		{
			closeAfterSubmit: false
		});
		
		po.submitForm = function(url, options)
		{
			options.target = "_self";
			po.open(url, options);
		};
	}
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>