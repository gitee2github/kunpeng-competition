<#--
 *
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 *
-->
<#--
数据集文件源输入项

依赖：

-->
<#assign DirectoryFileDataSetEntity=statics['org.datagear.management.domain.DirectoryFileDataSetEntity']>
<div class="field grid">
	<label for="${pid}fileSourceType" class="field-label col-12 mb-2 md:col-3 md:mb-0">
		<@spring.message code='fileType' />
	</label>
	<div class="field-input col-12 md:col-9">
      	<p-selectbutton v-model="fm.fileSourceType" :options="pm.fileSourceTypeOptions"
       		option-label="name" option-value="value" @change="onFileSourceTypeChange" class="input w-full">
       	</p-selectbutton>
	</div>
</div>
<div class="field grid" v-if="fm.fileSourceType == '${DirectoryFileDataSetEntity.FILE_SOURCE_TYPE_UPLOAD}'">
	<label for="${pid}displayName" class="field-label col-12 mb-2 md:col-3 md:mb-0">
		<@spring.message code='uploadFile' />
	</label>
	<div class="field-input col-12 md:col-9">
		<p-inputtext id="${pid}displayName" v-model="fm.displayName" type="text" class="input w-full"
			name="displayName" required readonly>
		</p-inputtext>
       	<div id="${pid}fileName" class="fileupload-wrapper flex align-items-center mt-1" v-if="!pm.isReadonlyAction">
        	<p-fileupload mode="basic" name="file" :url="pm.uploadFileUrl"
        		@upload="onUploaded" @select="uploadFileOnSelect" @progress="uploadFileOnProgress"
        		:auto="true" choose-label="<@spring.message code='select' />" class="mr-2">
			</p-fileupload>
			<#include "../../include/page_fileupload.ftl">
		</div>
	</div>
</div>
<div class="field grid" v-if="fm.fileSourceType == '${DirectoryFileDataSetEntity.FILE_SOURCE_TYPE_SERVER}'">
	<label for="${pid}dataSetResDirectory" class="field-label col-12 mb-2 md:col-3 md:mb-0"
		title="<@spring.message code='dataSet.directoryOnServer.desc' />">
		<@spring.message code='directoryOnServer' />
	</label>
       <div class="field-input col-12 md:col-9">
       	<div class="p-inputgroup">
        	<div class="p-input-icon-right flex-grow-1">
				<i class="pi pi-times cursor-pointer opacity-60" @click="onDeleteDataSetResDirectory" v-if="!pm.isReadonlyAction">
				</i>
				<p-inputtext id="${pid}dataSetResDirectory" v-model="fm.dataSetResDirectory.directory" type="text" class="input w-full h-full border-noround-right"
					name="dataSetResDirectory.directory" required readonly>
				</p-inputtext>
			</div>
        	<p-button type="button" label="<@spring.message code='select' />" @click="onSelectDataSetResDirectory"
        		v-if="!pm.isReadonlyAction">
        	</p-button>
		</div>
	</div>
</div>
<div class="field grid" v-if="fm.fileSourceType == '${DirectoryFileDataSetEntity.FILE_SOURCE_TYPE_SERVER}'">
	<label for="${pid}dataSetResFileName" class="field-label col-12 mb-2 md:col-3 md:mb-0"
		title="<@spring.message code='dataSet.fileInDirectory.desc' />">
		<@spring.message code='fileInDirectory' />
	</label>
       <div class="field-input col-12 md:col-9">
       	<div class="p-inputgroup">
        	<p-inputtext id="${pid}dataSetResFileName" v-model="fm.dataSetResFileName" type="text" class="input"
        		name="dataSetResFileName" required  maxlength="1000">
        	</p-inputtext>
        	<p-button type="button" label="<@spring.message code='select' />" @click="onSelectDataSetResFileName"
        		aria:haspopup="true" aria-controls="${pid}dsrFilesPanel"
        		v-if="!pm.isReadonlyAction">
        	</p-button>
			<p-overlaypanel ref="${pid}dsrFilesPanelEle" append-to="body"
				:show-close-icon="false" @show="onDsrFilesPanelShow" id="${pid}dsrFilesPanel" class="dsr-files-panel">
				<div class="pb-2">
					<label class="text-lg font-bold">
						<@spring.message code='selectFile' />
					</label>
				</div>
				<div class="panel-content-size-xxs overflow-auto p-2">
					<p-tree :value="pm.dsrFileNodes"
						selection-mode="single" v-model:selection-keys="pm.dsrSelectedNodeKeys"
						@node-expand="onDsrFileNodeExpand" @node-select="onDsrFileNodeSelect"
						:loading="pm.dsrLoading" class="h-full overflow-auto">
					</p-tree>
				</div>
				<div class="pt-3 text-center">
					<p-button type="button" @click="onConfirmDataSetResFileName" label="<@spring.message code='confirm' />"></p-button>
				</div>
			</p-overlaypanel>
		</div>
	</div>
</div>
<script>
(function(po)
{
	po.loadDsrFiles = function(node)
	{
		var subPath = (node && node.path ? node.path : "");
		
		var fm = po.vueFormModel();
		var pm = po.vuePageModel();
		
		pm.dsrLoading = true;
		po.ajax("/dataSetResDirectory/listFiles",
		{
			data: { id: fm.dataSetResDirectory.id, subPath: subPath },
			success: function(response)
			{
				var nodes = po.dsrFileInfosToNodes(subPath, response);
				
				if(node)
					node.children = nodes;
				else
					pm.dsrFileNodes = nodes;
				
				pm.dsrSelectedNodeKeys = null;
				pm.dsrSelectedNode = null;
			},
			complete: function()
			{
				pm.dsrLoading = false;
			}
		});
	};
	
	po.dsrFileInfosToNodes = function(subPath, fileInfos)
	{
		var re = [];
		
		$.each(fileInfos, function(idx, fi)
		{
			var myPath = (subPath ? subPath + "/" : "") + fi.name;
			
			re.push(
			{
				key: myPath,
				label: fi.name + (fi.directory ? "" : " ("+fi.size+")"),
				icon: (fi.directory ? "pi pi-folder" : "pi pi-file"),
				leaf: (fi.directory ? false : true),
				children: null,
				fileInfo: fi,
				path: myPath
			});
		});
		
		return re;
	};
	
	po.vuePageModel(
	{
		fileSourceTypeOptions:
		[
			{name: "<@spring.message code='dataSet.FILE_SOURCE_TYPE_UPLOAD' />", value: "${DirectoryFileDataSetEntity.FILE_SOURCE_TYPE_UPLOAD}"},
			{name: "<@spring.message code='dataSet.FILE_SOURCE_TYPE_SERVER' />", value: "${DirectoryFileDataSetEntity.FILE_SOURCE_TYPE_SERVER}"}
		],
		uploadFileUrl: po.concatContextPath("/dataSet/uploadFile"),
		dsrFileNodes: null,
		dsrSelectedNodeKeys: null,
		dsrSelectedNode: null,
		dsrLoading: false
	});
	
	po.vueRef("${pid}dsrFilesPanelEle", null);
	
	po.vueMethod(
	{
		onFileSourceTypeChange: function()
		{
			
		},
		
		onUploaded: function(e)
		{
			var fm = po.vueFormModel();
			var response = $.getResponseJson(e.xhr);
			
			po.uploadFileOnUploaded(e);
			fm.fileName = response.fileName;
			fm.displayName = response.displayName;
		},
		
		onSelectDataSetResDirectory: function(e)
		{
			po.handleOpenSelectAction("/dataSetResDirectory/select", function(dsrd)
			{
				var fm = po.vueFormModel();
				fm.dataSetResDirectory = dsrd;
			});
		},
		
		onDeleteDataSetResDirectory: function(e)
		{
			var fm = po.vueFormModel();
			fm.dataSetResDirectory = {};
		},
		
		onSelectDataSetResFileName: function(e)
		{
			var fm = po.vueFormModel();
			
			if(!fm.dataSetResDirectory || !fm.dataSetResDirectory.id)
				return;
			
			po.vueUnref("${pid}dsrFilesPanelEle").show(e);
		},
		
		onDsrFilesPanelShow: function(e)
		{
			po.loadDsrFiles();
		},
		
		onDsrFileNodeExpand: function(node)
		{
			if(node.children == null)
				po.loadDsrFiles(node);
		},
		
		onDsrFileNodeSelect: function(node)
		{
			var pm = po.vuePageModel();
			pm.dsrSelectedNode = node;
		},
		
		onConfirmDataSetResFileName: function(e)
		{
			var fm = po.vueFormModel();
			var pm = po.vuePageModel();
			
			if(!pm.dsrSelectedNode || pm.dsrSelectedNode.fileInfo.directory)
			{
				$.tipInfo("<@spring.message code='pleaseSelectOneFile' />");
				return;
			}
			
			fm.dataSetResFileName = pm.dsrSelectedNode.path;
			po.vueUnref("${pid}dsrFilesPanelEle").hide();
		}
	});
})
(${pid});
</script>
