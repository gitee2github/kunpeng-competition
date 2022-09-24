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
	<@spring.message code='module.dataSetResDirectory' />
	<#include "../include/html_request_action_suffix.ftl">
</title>
</head>
<body class="p-card no-border">
<#include "../include/page_obj.ftl">
<div id="${pid}" class="page page-form horizontal">
	<form id="${pid}form" class="flex flex-column" :class="{readonly: pm.isReadonlyAction}">
		<div class="page-form-content flex-grow-1 px-2 py-1 overflow-y-auto">
			<div class="field grid">
				<label for="${pid}directory" class="field-label col-12 mb-2 md:col-3 md:mb-0"
					 title="<@spring.message code='dataSetResDirectory.directory.desc' />">
					<@spring.message code='directory' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-inputtext id="${pid}directory" v-model="fm.directory" type="text" class="input w-full"
		        		name="directory" required maxlength="300" autofocus>
		        	</p-inputtext>
		        </div>
			</div>
			<div class="field grid">
				<label for="${pid}desc" class="field-label col-12 mb-2 md:col-3 md:mb-0">
					<@spring.message code='desc' />
				</label>
		        <div class="field-input col-12 md:col-9">
		        	<p-textarea id="${pid}desc" v-model="fm.desc" rows="10" class="input w-full"
		        		name="desc" maxlength="500">
		        	</p-textarea>
		        </div>
			</div>
		</div>
		<div class="page-form-foot flex-grow-0 pt-3 text-center">
			<p-button type="submit" label="<@spring.message code='save' />"></p-button>
		</div>
	</form>
</div>
<#include "../include/page_form.ftl">
<script>
(function(po)
{
	po.submitUrl = "/dataSetResDirectory/"+po.submitAction;
	
	var formModel = $.unescapeHtmlForJson(<@writeJson var=formModel />);
	po.setupForm(formModel);
	
	po.vueMount();
})
(${pid});
</script>
</body>
</html>