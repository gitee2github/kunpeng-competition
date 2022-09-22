<#--
 *
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 *
-->
<#--
导入页头片段
-->
<div class="page-header grid grid-nogutter align-items-center pb-2">
	<div class="col-12 flex align-items-center mb-1">
		<i class="pi pi-database text-color-secondary text-sm"></i>
		<div class="text-color-secondary text-sm ml-1">${schema.title}</div>
	</div>
	<div class="col-12">
		<div class="grid">
			<label class="text-lg font-bold col-5 md:col-3">
				{{pm.importHeadTitle}}
			</label>
			<div class="col-7 md:col-9 inline-steps">
				<#include "../../include/page_steps.ftl">
			</div>
		</div>
	</div>
</div>
<script>
(function(po)
{
	po.stepsItems =
	[
		{ label: "<@spring.message code='set' />" },
		{ label: "<@spring.message code='import' />" }
	];
	
	po.setupImportHead = function(title)
	{
		po.vuePageModel(
		{
			importHeadTitle: title
		});
		
		po.setupSteps(po.stepsItems);
	};
})
(${pid});
</script>