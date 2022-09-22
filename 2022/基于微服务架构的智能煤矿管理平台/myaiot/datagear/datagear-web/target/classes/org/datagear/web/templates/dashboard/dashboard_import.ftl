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
	<@spring.message code='module.dashboard' />
	<#include "../include/html_request_action_suffix.ftl">
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-form horizontal">
	<form id="${pid}form" class="flex flex-column" :class="{readonly: pm.isReadonlyAction}">
		<div class="page-form-content flex-grow-1 px-2 py-1 overflow-y-auto">
			<div class="field grid">
				<label for="${pid}file" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='dashboard.import.file.desc' />">
					<@spring.message code='file' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<div id="${pid}file" class="fileupload-wrapper flex align-items-center mt-1" v-if="!pm.isReadonlyAction">
			        	<p-fileupload mode="basic" name="file" :url="pm.uploadFileUrl"
			        		@upload="onUploaded" @select="uploadFileOnSelect" @progress="uploadFileOnProgress"
			        		:auto="true" choose-label="<@spring.message code='select' />" class="mr-2">
			        	</p-fileupload>
						<#include "../include/page_fileupload.ftl">
		        	</div>
		        	<div class="validate-msg">
		        		<input name="dashboardFileName" required type="text" class="validate-proxy" />
		        	</div>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}zipFileNameEncoding" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='dashboard.import.zipFileNameEncoding.desc' />">
					<@spring.message code='zipFileEncoding' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-dropdown id="${pid}zipFileNameEncoding" v-model="fm.zipFileNameEncoding"
		        		:options="pm.availableCharsetNames" class="input w-full">
		        	</p-dropdown>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}name" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='dashboardName' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}name" v-model="fm.name" type="text" class="input w-full"
		        		name="name" required maxlength="100">
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}template" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='dashboard.import.templateName.desc' />">
					<@spring.message code='templateFileName' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}template" v-model="fm.template" type="text" class="input w-full"
		        		name="template" required maxlength="200">
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}ownerProject" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='ownerProject' />
				</label>
				<div class="field-input col-12 md:col-9">
					<div class="p-inputgroup">
						<div class="p-input-icon-right flex-grow-1">
							<i class="pi pi-times cursor-pointer opacity-60" @click="onDeleteAnalysisProject" v-if="!pm.isReadonlyAction">
							</i>
							<p-inputtext id="${pid}ownerProject" v-model="fm.analysisProject.name" type="text" class="input w-full h-full border-noround-right"
								readonly="readonly" name="analysisProject.name" maxlength="200">
							</p-inputtext>
						</div>
						<p-button type="button" label="<@spring.message code='select' />"
							@click="onSelectAnalysisProject" class="p-button-secondary"
							v-if="!pm.isReadonlyAction">
						</p-button>
					</div>
				</div>
			</div>
			<div class="field grid">
				<label class="field-label col-12 mb-2 md:col-3 md:mb-0">
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<div class="desc text-color-secondary text-sm">
			        	<@spring.message code='dashboard.import.notice' />
						<br>
						<@spring.message code='dashboard.import.notice.1' />
						<br>
						<@spring.message code='dashboard.import.notice.2' />
						<br>
						<@spring.message code='dashboard.import.notice.3' />
					</div>
		        </div>
			</div>
		</div>
		<div class="page-form-foot flex-grow-0 pt-3 text-center">
			<p-button type="submit" label="<@spring.message code='save' />"></p-button>
		</div>
	</form>
</div>
<#include "../include/page_form.ftl">
<#include "../include/page_boolean_options.ftl">
<script>
(function(po)
{
	po.submitUrl = "/dashboard/"+po.submitAction;
	
	var availableCharsetNames = $.unescapeHtmlForJson(<@writeJson var=availableCharsetNames />);
	
	var formModel = $.unescapeHtmlForJson(<@writeJson var=formModel />);
	formModel.analysisProject = (formModel.analysisProject == null ? {} : formModel.analysisProject);
	po.setupForm(formModel);
	
	po.vuePageModel(
	{
		availableCharsetNames: availableCharsetNames,
		uploadFileUrl: po.concatContextPath("/dashboard/uploadImportFile")
	});
	
	po.vueMethod(
	{
		onUploaded: function(e)
		{
			var fm = po.vueFormModel();
			var response = $.getResponseJson(e.xhr);
			
			po.uploadFileOnUploaded(e);
			fm.name = response.dashboardName;
			fm.template = response.template;
			fm.dashboardFileName = response.dashboardFileName;
		},
		
		onDeleteAnalysisProject: function()
		{
			var fm = po.vueFormModel();
			fm.analysisProject = {};
		},
		
		onSelectAnalysisProject: function()
		{
			po.handleOpenSelectAction("/analysisProject/select", function(analysisProject)
			{
				var fm = po.vueFormModel();
				fm.analysisProject = analysisProject;
			});
		}
	});
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>