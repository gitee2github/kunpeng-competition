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
	<@spring.message code='module.schema' />
	<#include "../include/html_request_action_suffix.ftl">
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-form horizontal">
	<form id="${pid}form" class="flex flex-column" :class="{readonly: pm.isReadonlyAction}">
		<div class="page-form-content flex-grow-1 px-2 py-1 overflow-y-auto">
			<div class="field grid">
				<label for="${pid}name" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='name' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}name" v-model="fm.title" type="text" class="input w-full"
		        		name="title" required maxlength="100" autofocus>
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}url" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='schema.url.desc' />">
					<@spring.message code='url' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<div class="p-inputgroup">
			        	<p-inputtext id="${pid}url" v-model="fm.url" type="text" class="input"
			        		name="url" required maxlength="2000" placeholder="jdbc:">
			        	</p-inputtext>
			        	<p-button type="button" label="<@spring.message code='help' />" @click="onBuildSchemaUrl"
			        		class="p-button-secondary"
			        		v-if="!pm.isReadonlyAction">
			        	</p-button>
		        	</div>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}user" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='schema.username.desc' />">
					<@spring.message code='username' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}user" v-model="fm.user" type="text" class="input w-full"
		        		name="user" maxlength="200" autocomplete="off">
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid" v-if="!pm.isReadonlyAction">
				<label for="${pid}password" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='schema.password.desc' />">
					<@spring.message code='password' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-password id="${pid}password" v-model="fm.password" class="input w-full"
		        		input-class="w-full" toggle-mask :feedback="false"
		        		name="password" maxlength="100" autocomplete="new-password">
		        	</p-password>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}driverEntity" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='schema.driverEntity.desc' />">
					<@spring.message code='module.driverEntity' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<div class="p-inputgroup">
		        		<div class="p-input-icon-right flex-grow-1">
			        		<i class="pi pi-times cursor-pointer opacity-60" @click="onDeleteDriverEntity" v-if="!pm.isReadonlyAction">
			        		</i>
				        	<p-inputtext id="${pid}driverEntity" v-model="fm.driverEntity.displayName" type="text" class="input w-full h-full border-noround-right"
				        		readonly="readonly" name="driverEntity.displayName" maxlength="200">
				        	</p-inputtext>
			        	</div>
			        	<p-button type="button" label="<@spring.message code='select' />"
			        		@click="onSelectDriverEntity" class="p-button-secondary"
			        		v-if="!pm.isReadonlyAction">
			        	</p-button>
		        	</div>
		        </div>
			</div>
			<div class="field grid" v-if="pm.isReadonlyAction">
				<label for="${pid}createUser" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='createUser' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}createUser" v-model="fm.createUser.nameLabel" type="text" class="input w-full" readonly="readonly">
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid" v-if="pm.isReadonlyAction">
				<label for="${pid}createTime" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='createTime' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}createTime" v-model="fm.createTime" type="text" class="input w-full" readonly="readonly">
		        	</p-inputtext>
		        </div>
			</div>
		</div>
		<div class="page-form-foot flex-grow-0 pt-3 text-center h-opts">
			<p-button type="button" :label="pm.testActionBtnLabel" @click="onTest"
				:disabled="pm.inTestAction?true:false" class="p-button-secondary">
			</p-button>
			<p-button type="submit" label="<@spring.message code='save' />"></p-button>
		</div>
	</form>
</div>
<#include "../include/page_form.ftl">
<script>
(function(po)
{
	po.submitUrl = "/schema/"+po.submitAction;

	po.inTestAction = function(boolVal)
	{
		var pm = po.vuePageModel();
		
		if(boolVal === undefined)
			return (pm.inTestAction == true);
		
		pm.inTestAction = boolVal;
		pm.testActionBtnLabel = (boolVal ? "<@spring.message code='testing' />" : "<@spring.message code='test' />");
	};
	
	po.beforeSubmitForm = function(action)
	{
		if(!po.inTestAction())
			return;
		
		action.url = "/schema/testConnection";
		action.options.defaultSuccessCallback = false;
	};
	
	po.vuePageModel(
	{
		inTestAction: false,
		testActionBtnLabel: "<@spring.message code='test' />"
	});
	
	var formModel = $.unescapeHtmlForJson(<@writeJson var=formModel />);
	formModel.driverEntity = (formModel.driverEntity == null ? {} : formModel.driverEntity);
	
	po.setupForm(formModel,
	{
		complete: function()
		{
			if(po.inTestAction())
				po.inTestAction(false);
		}
	},
	{
		invalidHandler: function()
		{
			if(po.inTestAction())
				po.inTestAction(false);
		}
	});
	
	po.vueMethod(
	{
		onBuildSchemaUrl: function()
		{
			var fm = po.vueFormModel();
			
			po.open("/schemaUrlBuilder/build",
			{
				data: {url: fm.url},
				contentType: $.CONTENT_TYPE_FORM,
				pageParam:
				{
					submitSuccess: function(url)
					{
						var fm = po.vueFormModel();
						fm.url = url;
					}
				}
			});
		},
		onDeleteDriverEntity: function()
		{
			var fm = po.vueFormModel();
			fm.driverEntity = {};
		},
		
		onSelectDriverEntity: function()
		{
			po.handleOpenSelectAction("/driverEntity/select", function(driverEntity)
			{
				var fm = po.vueFormModel();
				fm.driverEntity = driverEntity;
			});
		},
		
		onTest: function(e)
		{
			po.inTestAction(true);
			po.form().submit();
		}
	});
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>