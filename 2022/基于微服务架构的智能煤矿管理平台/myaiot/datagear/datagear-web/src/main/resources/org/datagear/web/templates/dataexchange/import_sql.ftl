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
	<@spring.message code='module.importData' />
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-manager page-dataexchange page-import-data-sql">
	<#include "include/import_head.ftl">
	<div class="page-content">
		<div class="page-form">
			<form id="${pid}form" action="#">
				<div class="page-form-content p-2 overflow-y-auto"
					:class="pm.steps.activeIndex == 0 ? '' : 'hidden'">
					<div class="field grid">
						<label for="${pid}exceptionResolve" class="field-label col-12 mb-2 md:col-3 md:mb-0">
							<@spring.message code='dataExchange.exceptionResolve' />
						</label>
						<div class="field-input col-12 md:col-9">
							<p-selectbutton id="${pid}exceptionResolve" v-model="fm.importOption.exceptionResolve"
								:options="pm.exceptionResolveOptions" option-label="name" option-value="value" class="input w-full">
					       	</p-selectbutton>
						</div>
					</div>
				</div>
				<div class="page-form-content p-2 overflow-y-auto"
					:class="pm.steps.activeIndex == 1 ? '' : 'hidden'">
					<#include "include/import_table_head.ftl">
					<div class="subdataexchange-table-wrapper pt-2">
						<p-datatable :value="fm.subDataExchanges" :scrollable="true" scroll-height="flex"
							v-model:selection="pm.selectedSubDataExchanges" selection-mode="multiple"
							:sortable="false" dataKey="id" striped-rows class="table-sm">
							<p-column selection-mode="multiple" :frozen="true" class="col-check"></p-column>
							<p-column field="number" header="<@spring.message code='givenNumber' />" :frozen="true" class="col-version">
							</p-column>
							<p-column field="fileDisplayName" header="<@spring.message code='fileName' />" class="col-name"></p-column>
							<p-column field="fileSize" header="<@spring.message code='fileSize' />" class="col-version"></p-column>
							<p-column field="dependentNumber" header="<@spring.message code='dependentNumber' />" class="col-version">
								<template #body="slotProps">
									<p-inputtext v-model="slotProps.data.dependentNumber" class="w-full"
										:disabled="pm.dataExchangeStatus != pm.DataExchangeStatusEnum.edit"
										placeholder="<@spring.message code='none' />">
									</p-inputtext>
								</template>
							</p-column>
							<p-column header="<@spring.message code='importProgress' />" class="col-last" style="min-width:20rem;">
								<template #body="slotProps">
									<div v-html="slotProps.data.status"></div>
								</template>
							</p-column>
						</p-datatable>
					</div>
				</div>
				<#include "include/import_foot.ftl">
			</form>
		</div>
	</div>
</div>
<#include "../include/page_form.ftl">
<#include "../include/page_simple_form.ftl">
<#include "../include/page_format_time.ftl">
<#include "include/dataexchange_js.ftl">
<#include "include/import_js.ftl">
<script>
(function(po)
{
	po.submitUrl = "/dataexchange/"+encodeURIComponent(po.schemaId)+"/import/sql/doImport";
	
	po.checkSubmitSubDataExchange = function(subDataExchange)
	{
		return true;
	};
	
	var formModel = $.unescapeHtmlForJson(<@writeJson var=formModel />);
	po.setupDataExchangeForm(formModel);
	
	po.setupDataExchange();
	po.setupImportHead("<@spring.message code='dataImport.importSqlData' />");
	po.setupImportTableHead(
			po.concatContextPath("/dataexchange/"+encodeURIComponent(po.schemaId)+"/import/sql/uploadImportFile"),
			function(response)
			{
				po.addSubDataExchangesForFileInfos(response);
			},
			{
				uploadFileLabelDesc: "<@spring.message code='dataImport.uploadFile.sql.desc' />",
			});
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>