<#--
 *
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 *
-->
<#assign HtmlChartWidgetEntity=statics['org.datagear.management.domain.HtmlChartWidgetEntity']>
<#include "../include/page_import.ftl">
<#include "../include/html_doctype.ftl">
<html>
<head>
<#include "../include/html_head.ftl">
<title>
	<#include "../include/html_app_name_prefix.ftl">
	<@spring.message code='module.chart' />
	<#include "../include/html_request_action_suffix.ftl">
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-manager page-table page-search-ap-aware">
	<div class="page-header grid grid-nogutter align-items-center pb-2">
		<div class="col-12 mb-1">
			<#include "../include/page_current_analysis_project.ftl">
		</div>
		<div class="col-12" :class="pm.isSelectAction ? 'md:col-6' : 'md:col-4'">
			<#include "../include/page_search_form_filter.ftl">
		</div>
		<div class="h-opts col-12 text-right" :class="pm.isSelectAction ? 'md:col-6' : 'md:col-8'">
			<p-button label="<@spring.message code='confirm' />" @click="onSelect" v-if="pm.isSelectAction"></p-button>
			
			<p-splitbutton label="<@spring.message code='add' />" @click="onAdd" :model="pm.addBtnItems" v-if="!pm.isReadonlyAction"></p-splitbutton>
			<p-button label="<@spring.message code='edit' />" @click="onEdit" v-if="!pm.isReadonlyAction"></p-button>
			<p-splitbutton label="<@spring.message code='show' />" @click="onShow" :model="pm.showBtnItems" v-if="!pm.isSelectAction"></p-splitbutton>
			<p-button label="<@spring.message code='share' />" @click="onShare" v-if="!pm.isReadonlyAction"></p-button>
			<p-button label="<@spring.message code='view' />" @click="onView" :class="{'p-button-secondary': pm.isSelectAction}"></p-button>
			<p-button label="<@spring.message code='delete' />" @click="onDelete" class="p-button-danger" v-if="!pm.isReadonlyAction"></p-button>
		</div>
	</div>
	<div class="page-content">
		<p-datatable :value="pm.items" :scrollable="true" scroll-height="flex"
			:paginator="pm.paginator" :paginator-template="pm.paginatorTemplate"
			:rows="pm.rowsPerPage" :current-page-report-template="pm.pageReportTemplate"
			:rows-per-page-options="pm.rowsPerPageOptions" :loading="pm.loading"
			:lazy="true" :total-records="pm.totalRecords" @page="onPaginator($event)"
			sort-mode="multiple" :multi-sort-meta="pm.multiSortMeta" @sort="onSort($event)"
			v-model:selection="pm.selectedItems" :selection-mode="pm.selectionMode" dataKey="id" striped-rows>
			<p-column :selection-mode="pm.selectionMode" :frozen="true" class="col-check"></p-column>
			<p-column field="id" header="<@spring.message code='id' />" class="col-id"></p-column>
			<p-column field="name" header="<@spring.message code='name' />" :sortable="true" class="col-name"></p-column>
			<p-column field="htmlChartPlugin.id" header="<@spring.message code='type' />" :sortable="true" style="min-width:8em;">
				<template #body="{data}">
					<div v-html="formatChartPlugin(data)"></div>
				</template>
			</p-column>
			<p-column field="updateInterval" header="<@spring.message code='updateInterval' />" :sortable="true" style="min-width:8em;max-width:15em;">
				<template #body="{data}">
					{{formatInterval(data)}}
				</template>
			</p-column>
			<p-column field="analysisProject.name" header="<@spring.message code='ownerProject' />" :sortable="true" class="col-owner-project"></p-column>
			<p-column field="createUser.realName" header="<@spring.message code='createUser' />" :sortable="true" class="col-user"></p-column>
			<p-column field="createTime" header="<@spring.message code='createTime' />" :sortable="true" class="col-datetime col-last"></p-column>
		</p-datatable>
	</div>
	<#include "../include/page_copy_to_clipboard.ftl">
</div>
<#include "../include/page_manager.ftl">
<#include "../include/page_table.ftl">
<script>
(function(po)
{
	po.serverURL = "${serverURL}";
	
	po.buildShowURL = function(id)
	{
		return po.concatContextPath("/chart/show/"+encodeURIComponent(id)+"/");
	};
	
	po.setupAjaxTable("/chart/pagingQueryData",
	{
		multiSortMeta: [ {field: "createTime", order: -1} ]
	});
	
	po.vuePageModel(
	{
		addBtnItems:
		[
			{
				label: "<@spring.message code='copy' />",
				command: function()
				{
					po.handleOpenOfAction("/chart/copy", {width: "70vw"});
				}
			}
		],
		showBtnItems:
		[
			{
				label: "<@spring.message code='copyShowUrl' />",
				command: function()
				{
					po.executeOnSelect(function(entity)
	 				{
						po.copyToClipboard(po.serverURL + po.buildShowURL(entity.id));
	 				});
				}
			}
		]
	});
	
	po.vueMethod(
	{
		formatInterval: function(data)
		{
			var interval = data.updateInterval;
			
			if(interval < 0)
				return "<@spring.message code='noUpdate' />";
			else if(interval == 0)
				return "<@spring.message code='realtime' />";
			else
				return "<@spring.message code='xxxMilliseconds' />".replace("{0}", interval);
		},
		formatChartPlugin: function(data)
		{
			return $.toChartPluginHtml(data.htmlChartPlugin, po.contextPath);
		},
		onAdd: function()
		{
			po.handleAddAction("/chart/add", {width: "70vw"});
		},
		
		onEdit: function()
		{
			po.handleOpenOfAction("/chart/edit", {width: "70vw"});
		},
		
		onView: function()
		{
			po.handleOpenOfAction("/chart/view", {width: "70vw"});
		},

		onShare: function()
		{
			po.executeOnSelect(function(entity)
			{
				po.openTableDialog("/authorization/${HtmlChartWidgetEntity.AUTHORIZATION_RESOURCE_TYPE}/"+encodeURIComponent(entity.id)+"/query");
			});
		},
		
		onDelete: function()
		{
			po.handleDeleteAction("/chart/delete");
		},
		
		onSelect: function()
		{
			po.handleSelectAction();
		},
		
		onShow: function(e)
		{
			po.executeOnSelect(function(entity)
			{
				window.open(po.buildShowURL(entity.id), entity.id);
			});
		}
	});
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>