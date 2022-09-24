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
	<@spring.message code='module.dashboardGlobalRes' />
	<#include "../include/html_request_action_suffix.ftl">
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-form horizontal page-form-db-g-r">
	<form id="${pid}form" class="flex flex-column" :class="{readonly: pm.isReadonlyAction}">
		<div class="page-form-content flex-grow-1 px-2 py-1 overflow-y-auto">
			<div class="field grid">
				<label for="${pid}savePath" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					title="<@spring.message code='dashboardGlobalRes.upload.savePath.desc' />">
					<@spring.message code='savePath' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}savePath" v-model="fm.savePath" type="text" class="input w-full"
		        		name="savePath" required maxlength="200" autofocus>
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}resourceContent" class="field-label col-12 mb-2">
					<@spring.message code='resourceContent' />
				</label>
		        <div class="field-input col-12">
		        	<div id="${pid}resourceContent" class="code-editor-wrapper input p-component p-inputtext w-full">
						<div id="${pid}codeEditor" class="code-editor"></div>
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
<#include "../include/page_code_editor.ftl">
<script>
(function(po)
{
	po.submitUrl = "/dashboardGlobalRes/"+po.submitAction;
	
	po.beforeSubmitForm = function(action)
	{
		action.options.data.resourceContent = po.getCodeText(po.codeEditor);
	};
	
	var formModel = $.unescapeHtmlForJson(<@writeJson var=formModel />);
	po.setupForm(formModel, { closeAfterSubmit: false });
	
	po.vueMounted(function()
	{
		var fm = po.vueFormModel();
		
		var resourceEditorOptions =
		{
			value: "",
			matchBrackets: true,
			matchTags: true,
			autoCloseTags: true,
			mode: po.evalCodeModeByName(fm.savePath)
		};
		
		po.codeEditor = po.createCodeEditor(po.elementOfId("${pid}codeEditor"), resourceEditorOptions);
		po.setCodeTextTimeout(po.codeEditor, fm.resourceContent);
	});
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>