/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

/**
 * 看板可视编辑器。
 * 全局变量名：window.dashboardFactory.dashboardEditor
 * 
 * 加载时依赖：
 *   dashboardFactory.js
 * 
 * 运行时依赖:
 *   jquery.js
 *   dashboardFactory.js
 *   chartFactory.js
 */
(function(global)
{
	/**看板工厂*/
	var dashboardFactory = (global.dashboardFactory || (global.dashboardFactory = {}));
	var editor = (dashboardFactory.dashboardEditor || (dashboardFactory.dashboardEditor = {}));
	var i18n = (editor.i18n || (editor.i18n = {}));
	
	i18n.insertInsideChartOnChartEleDenied = "图表元素内不允许再插入图表元素";
	i18n.selectElementForSetChart = "请选择要设置/替换的图表元素";
	i18n.canEditOnlyTextElement = "仅可编辑纯文本元素";
	i18n.selectedElementRequired = "请选择要操作的元素";
	i18n.selectedNotChartElement = "选定元素不是图表元素";
	i18n.noSelectableNextElement="没有可选择的下一个元素";
	i18n.noSelectablePrevElement="没有可选择的上一个元素";
	i18n.noSelectableChildElement="没有可选择的子元素";
	i18n.noSelectableParentElement="没有可选择的父元素";
	i18n.imgEleRequired = "不是图片元素";
	i18n.hyperlinkEleRequired = "不是超链接元素";
	i18n.videoEleRequired = "不是视频元素";
	i18n.labelEleRequired = "不是文本标签元素";
	
	//参考org.datagear.web.controller.DashboardController.DASHBOARD_BUILTIN_RENDER_CONTEXT_ATTR_EDIT_HTML_INFO
	var DASHBOARD_BUILTIN_RENDER_CONTEXT_ATTR_EDIT_HTML_INFO = (editor.DASHBOARD_BUILTIN_RENDER_CONTEXT_ATTR_EDIT_HTML_INFO = "DG_EDIT_HTML_INFO");
	
	var BODY_CLASS_VISUAL_EDITOR = (editor.BODY_CLASS_VISUAL_EDITOR = "dg-show-ve");
	
	//参考org.datagear.web.controller.DashboardController.DashboardShowForEdit.ELEMENT_ATTR_VISUAL_EDIT_ID
	var ELEMENT_ATTR_VISUAL_EDIT_ID = (editor.ELEMENT_ATTR_VISUAL_EDIT_ID = "dg-visual-edit-id");
	
	var ELEMENT_CLASS_SELECTED = (editor.ELEMENT_CLASS_SELECTED = "dg-show-ve-selected");
	
	var ELEMENT_CLASS_NEW_INSERT = (editor.ELEMENT_CLASS_NEW_INSERT = "dg-show-ve-new-insert");
	
	var BODY_CLASS_ELEMENT_BOUNDARY = (editor.BODY_CLASS_ELEMENT_BOUNDARY = "dg-show-ve-boundary");
	
	var INSERT_ELE_FORMAT_FLAG = (editor.INSERT_ELE_FORMAT_FLAG = "<!--dg-format-flag-->");
	
	dashboardFactory._initSuperByDashboardEditor = dashboardFactory.init;
	dashboardFactory.init = function(dashboard)
	{
		dashboardFactory._initSuperByDashboardEditor(dashboard);
		editor.init(dashboard);
	};
	
	/**
	 * 初始化可视编辑器。
	 */
	editor.init = function(dashboard)
	{
		this.dashboard = dashboard;
		
		this._initStyle();
		this._initEditHtmlIframe();
		this._initInteraction();
	};
	
	///初始化样式。
	editor._initStyle = function()
	{
		this._setPageStyle();
	};
	
	//初始化编辑HTML的iframe
	editor._initEditHtmlIframe = function()
	{
		var editHtmlInfo = this._editHtmlInfo();
		var editBodyHtml = this._unescapeEditHtml(editHtmlInfo.bodyHtml);
		this._editIframe(editBodyHtml);
	};
	
	//初始化交互控制
	editor._initInteraction = function()
	{
		$(function()
		{
			$(document.body).addClass(BODY_CLASS_VISUAL_EDITOR);
			
			$(document.body).on("click", function(event)
			{
				editor._removeElementClassNewInsert();
				
				var target = $(event.target);
				var veEle = (target.attr(ELEMENT_ATTR_VISUAL_EDIT_ID) ? target :
									target.closest("["+ELEMENT_ATTR_VISUAL_EDIT_ID+"]"));
				
				if(veEle.length == 0)
				{
					editor.deselectElement();
				}
				else
				{
					if(!editor._isSelectableElement(veEle))
					{
						editor.deselectElement();
					}
					else if(editor._isSelectedElement(veEle))
					{
						//再次点击选中元素，不取消选择
					}
					else
					{
						editor.selectElement(veEle);
					}
				}
				
				if(editor.clickCallback)
					editor.clickCallback(event);
			});
			
			$(window).on("beforeunload", function()
			{
				editor.beforeunloadCallback();
			});
		});
	};
	
	//获取当前编辑HTML
	editor.editedHtml = function()
	{
		var editHtmlInfo = this._editHtmlInfo();
		var editBodyHtml = this._editBodyHtml();
		
		//将占位标签还原为原始标签
		var placeholderSources = (editHtmlInfo.placeholderSources || {});
		for(var placeholder in placeholderSources)
		{
			var source = placeholderSources[placeholder];
			editBodyHtml = editBodyHtml.replace(placeholder, source);
		}
		
		//删除末尾的：" dg-visual-edit-id='...'>"
		var eidRegex0 = /\s?dg\-visual\-edit\-id\=["'][^"']*["']\s*>/gi;
		editBodyHtml = editBodyHtml.replace(eidRegex0, ">");
		
		//删除中间的：" dg-visual-edit-id='...'"
		var eidRegex1 = /\s?dg\-visual\-edit\-id\=["'][^"']*["']/gi;
		editBodyHtml = editBodyHtml.replace(eidRegex1, "");
		
		//删除插入元素后又删除元素遗留的多余格式符
		var insertFormatRegex0 = /\n\<\!\-\-dg\-format\-flag\-\-\>\n\s*(\n\<\!\-\-dg\-format\-flag\-\-\>\n)+/gi;
		editBodyHtml = editBodyHtml.replace(insertFormatRegex0, "\n");
		
		//删除插入元素时的格式符
		var insertFormatRegex1 = /\n\<\!\-\-dg\-format\-flag\-\-\>\n/gi;
		editBodyHtml = editBodyHtml.replace(insertFormatRegex1, "\n");
		
		var editedHtml = editHtmlInfo.beforeBodyHtml + editBodyHtml + editHtmlInfo.afterBodyHtml;
		return this._unescapeEditHtml(editedHtml);
	};
	
	/**
	 * 是否在指定changeFlag后有修改。
	 *
	 * @param changeFlag 待比较的变更标识
	 */
	editor.isChanged = function(changeFlag)
	{
		return (this.changeFlag() != changeFlag);
	};
	
	/**
	 * 获取/设置变更标识。
	 *
	 * @param set 可选，要设置的变更标识，格式为：true 自增，数值 设置明确值
	 */
	editor.changeFlag = function(set)
	{
		if(this._changeFlag == null)
			this._changeFlag = 0;
		
		if(set == true)
		{
			this._changeFlag++;
		}
		else if(chartFactory.isNumber(set))
		{
			this._changeFlag = set;
		}
		else
		{
			return this._changeFlag;
		}
	};
	
	//提示信息
	editor.tipInfo = function(msg)
	{
		alert(msg);
	};
	
	//页面点击回调函数，格式为：function(event){}
	editor.clickCallback = function(event)
	{
		
	};
	
	/**
	 * 选择元素回调函数。
	 * 
	 * @param ele JQ元素
	 */
	editor.selectElementCallback = function(ele)
	{
		
	};
	
	/**
	 * 取消选择元素回调函数。
	 * 
	 * @param ele JQ元素
	 */
	editor.deselectElementCallback = function(ele)
	{
		
	};
	
	//页面卸载前回调函数，比如：保存编辑HTML
	editor.beforeunloadCallback = function()
	{
		
	};
	
	/**
	 * 获取/设置元素边界线启用禁用/状态。
	 *
	 * @param enable 可选，true 启用；false 禁用。
	 * @returns 是否已启用 
	 */
	editor.enableElementBoundary = function(enable)
	{
		var body = $(document.body);
		
		if(arguments.length == 0)
			return body.hasClass(BODY_CLASS_ELEMENT_BOUNDARY);
		
		if(enable)
			body.addClass(BODY_CLASS_ELEMENT_BOUNDARY);
		else
			body.removeClass(BODY_CLASS_ELEMENT_BOUNDARY);
	};
	
	/**
	 * 是否未选中任何元素。
	 */
	editor.isNonSelectedElement = function()
	{
		var selected = this._selectedElement();
		return (selected.length == 0);
	};
	
	/**
	 * 获取元素的可视编辑ID。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.getElementVisualEditId = function(ele)
	{
		ele = this._currentElement(ele, true);
		return this._getVisualEditId(ele);
	};
	
	/**
	 * 选中指定元素。
	 * 
	 * @param eleOrVisualEditId 元素、元素可编辑ID
	 * @returns true 已选择，false 未选择
	 */
	editor.selectElement = function(eleOrVisualEditId)
	{
		var ele = eleOrVisualEditId;
		
		if(chartFactory.isString(ele))
			ele = $("["+ELEMENT_ATTR_VISUAL_EDIT_ID+"='"+ele+"']");
		
		this._removeElementClassNewInsert();
		
		this.deselectElement();
		
		if(ele && ele.length > 0)
		{
			this._selectElement(ele);
			
			if(this.selectElementCallback)
				this.selectElementCallback(ele);
			
			return true;
		}
		
		return false;
	};
	
	/**
	 * 取消选中元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.deselectElement = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		this._removeElementClassNewInsert();
		
		if(ele.length > 0)
		{
			this._deselectElement(ele);
			
			if(this.deselectElementCallback)
				this.deselectElementCallback(ele);
		}
	};
	
	/**
	 * 选中下一个可编辑元素。
	 * 如果元素时<body>，将选中其第一个可编辑子元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素、或者<body>元素
	 * @param tip 可选，未选择时是否给出提示，默认为：true
	 * @returns true 已选择，false 未选择
	 */
	editor.selectNextElement = function(ele, tip)
	{
		//(true)、(false)
		if(arguments.length == 1 && (ele === true || ele === false))
		{
			tip = ele;
			ele = undefined;
		}
		
		tip = (tip == null ? true : tip);
		
		this._removeElementClassNewInsert();
		
		ele = this._currentElement(ele);
		
		if(ele.is("body"))
			return this.selectFirstChildElement(ele, tip);
		
		var target = ele;
		while((target = target.next()))
		{
			if(target.length == 0 || this._isSelectableElement(target))
			{
				break;
			}
		}
		
		if(target.length == 0)
		{
			if(tip)
				this.tipInfo(i18n.noSelectableNextElement);
			
			return false;
		}
		
		return this.selectElement(target);
	};
	
	/**
	 * 选中前一个可编辑元素。
	 * 如果元素时<body>，将选中其第一个可编辑子元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素、或者<body>元素
	 * @param tip 可选，未选择时是否给出提示，默认为：true
	 * @returns true 已选择，false 未选择
	 */
	editor.selectPrevElement = function(ele, tip)
	{
		//(true)、(false)
		if(arguments.length == 1 && (ele === true || ele === false))
		{
			tip = ele;
			ele = undefined;
		}
		
		tip = (tip == null ? true : tip);
		
		this._removeElementClassNewInsert();
		
		ele = this._currentElement(ele);
		
		if(ele.is("body"))
			return this.selectFirstChildElement(ele, tip);
		
		var target = ele;
		while((target = target.prev()))
		{
			if(target.length == 0 || this._isSelectableElement(target))
			{
				break;
			}
		}
		
		if(target.length == 0)
		{
			if(tip)
				this.tipInfo(i18n.noSelectablePrevElement);
			return false;
		}
		
		return this.selectElement(target);
	};
	
	/**
	 * 选中第一个可编辑子元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素、或者<body>元素
	 * @param tip 可选，未选择时是否给出提示，默认为：true
	 * @returns true 已选择，false 未选择
	 */
	editor.selectFirstChildElement = function(ele, tip)
	{
		//(true)、(false)
		if(arguments.length == 1 && (ele === true || ele === false))
		{
			tip = ele;
			ele = undefined;
		}
		
		tip = (tip == null ? true : tip);
		
		this._removeElementClassNewInsert();
		
		ele = this._currentElement(ele);
		var firstChild = $("> *:first", ele);
		
		var target = firstChild;
		while(true)
		{
			if(target.length == 0 || this._isSelectableElement(target))
			{
				break;
			}
			
			target = target.next();
		}
		
		if(target.length == 0)
		{
			if(tip)
				this.tipInfo(i18n.noSelectableChildElement);
			return false;
		}
		
		return this.selectElement(target);
	};
	
	/**
	 * 选中可编辑上级元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素、或者<body>元素
	 * @param tip 可选，未选择时是否给出提示，默认为：true
	 * @returns true 已选择，false 未选择
	 */
	editor.selectParentElement = function(ele, tip)
	{
		//(true)、(false)
		if(arguments.length == 1 && (ele === true || ele === false))
		{
			tip = ele;
			ele = undefined;
		}
		
		tip = (tip == null ? true : tip);
		
		this._removeElementClassNewInsert();
		
		ele = this._currentElement(ele);
		
		if(ele.is("body"))
		{
			if(tip)
				this.tipInfo(i18n.noSelectableParentElement);
			return false;
		}
		
		var target = ele;
		while((target = target.parent()))
		{
			if(target.length == 0 || target.is("body") || this._isSelectableElement(target))
			{
				break;
			}
		}
		
		if(target.is("body") || target.length == 0)
		{
			if(tip)
				this.tipInfo(i18n.noSelectableParentElement);
			return;
		}
		
		return this.selectElement(target);
	};
	
	editor._isSelectableElement = function($ele)
	{
		if(!$ele.attr(ELEMENT_ATTR_VISUAL_EDIT_ID))
			return false;
		
		var tagName = ($ele[0].tagName || "").toLowerCase();
		
		if(tagName == "")
			return false;
		
		if(tagName == "body")
			return false;
		
		if(tagName == "script" || tagName == "style" || tagName == "template")
			return false;
		
		if($ele.is(":hidden"))
			return false;
		
		//没有尺寸的也忽略
		var w = $ele.outerWidth(), h = $ele.outerHeight();
		if(w == null || w <= 0 || h == null || h <= 0)
			return false;
		
		return true;
	};
	
	/**
	 * 是否是图表元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.isChartElement = function(ele)
	{
		ele = this._currentElement(ele);
		return (this.dashboard.renderedChart(ele) != null);
	};
	
	/**
	 * 是否是网格布局条目元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.isGridItemElement = function(ele)
	{
		ele = this._currentElement(ele, true);
		var parent = ele.parent();
		var display = (parent.css("display") || "");
		
		return /^(grid|inline-grid)$/i.test(display);
	};
	
	/**
	 * 是否是弹性布局条目元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.isFlexItemElement = function(ele)
	{
		ele = this._currentElement(ele, true);
		var parent = ele.parent();
		var display = (parent.css("display") || "");
		
		return /^(flex|inline-flex)$/i.test(display);
	};
	
	/**
	 * 校验网格布局元素。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertGridLayout = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 是否可以插入填满父元素的网格布局元素。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.canInsertFillParentGridLayout = function(insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		var insertParentEle = this._getInsertParentElement(refEle, insertType);
		
		if(!insertParentEle.is("body"))
			return false;
		
		var canInsert = true;
		
		//只有还未插入任何可选择元素时，才可以插入填满父容器元素
		insertParentEle.children().each(function()
		{
			if(editor._isSelectableElement($(this)))
				canInsert = false;
		});
		
		return canInsert;
	};
	
	/**
	 * 插入网格布局元素。
	 * 
	 * @param gridAttr 网格设置，格式为：{ rows: 数值或数值字符串, columns: 数值或数值字符串, fillParent: 布尔值或布尔值字符串 }
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertGridLayout = function(gridAttr, insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		var rows = (!chartFactory.isNumber(gridAttr.rows) ? parseInt(gridAttr.rows) : gridAttr.rows);
		var columns = (!chartFactory.isNumber(gridAttr.columns) ? parseInt(gridAttr.columns) : gridAttr.columns);
		
		//不能使用"<div />"，生成的源码格式不对
		var div = $("<div></div>");
		
		var styleStr = "display:grid;";
		var insertParentEle = this._getInsertParentElement(refEle, insertType);
		
		if(gridAttr.fillParent === "true" || gridAttr.fillParent === true)
			styleStr += "position:absolute;left:0;top:0;right:0;bottom:0;";
		else if(insertParentEle.is("body"))
			styleStr += "width:100%;height:300px;";
		else
			styleStr += "width:100%;height:100%;";
		
		if(rows > 0)
			styleStr += "grid-template-rows:repeat("+rows+", 1fr);";
		if(columns > 0)
			styleStr += "grid-template-columns:repeat("+columns+", 1fr);";
		
		div.attr("style", styleStr);
		
		for(var i=0; i<rows; i++)
		{
			for(var j=0; j<columns; j++)
				this._insertElement(div, $("<div></div>"), "append");
		}
		
		this.insertElement(div, insertType, refEle);
	};
	
	/**
	 * 校验insertDiv操作。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertDiv = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 插入div元素。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertDiv = function(insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		//不能使用"<div />"，生成的源码格式不对
		var div = $("<div></div>");
		
		var styleStr = "";
		var insertParentEle = this._getInsertParentElement(refEle, insertType);
		
		if(insertParentEle.is("body"))
			styleStr = "width:100%;height:100px;";
		else
			styleStr = "width:100px;height:100px;";
		
		div.attr("style", styleStr);
		
		this.insertElement(div, insertType, refEle);
	};
	
	/**
	 * 校验insertImage操作。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertImage = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 插入图片元素。
	 * 
	 * @param imgAttr 图片设置，格式为：{ src: "", width: ..., height: ... }
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertImage = function(imgAttr, insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		var img = $("<img>");
		
		this.insertElement(img, insertType, refEle);
		this.setImageAttr(imgAttr, img);
	};
	
	/**
	 * 元素是否是图片。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.isImage = function(ele)
	{
		ele = this._currentElement(ele);
		return ele.is("img");
	};
	
	/**
	 * 获取图片元素属性。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.getImageAttr = function(ele)
	{
		ele = this._currentElement(ele);
		
		var attrObj = {};
		
		if(!this.isImage(ele))
			return attrObj;
		
		ele = this._editElement(ele);
		
		var eleStyle = this.getElementStyle(ele);
		
		attrObj.src = (ele.attr("src") || "");
		attrObj.width = eleStyle.width;
		attrObj.height = eleStyle.height;
		
		return attrObj;
	};
	
	/**
	 * 设置图片元素属性。
	 * 
	 * @param imgAttr 图片设置，格式为：{ src: "", width: ..., height: ... }
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.setImageAttr = function(imgAttr, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.isImage(ele))
		{
			this.tipInfo(i18n.imgEleRequired);
			return;
		}
		
		var eleStyle = { width: imgAttr.width, height: imgAttr.height };
		
		this._setElementAttr(ele, "src", (imgAttr.src || ""));
		this._setElementStyle(ele, eleStyle);
	};
	
	/**
	 * 校验insertHyperlink操作。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertHyperlink = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 插入超链接元素。
	 * 
	 * @param hyperlinkAttr 超链接设置，格式为：{ content: "...", href: "...", target: "..." }
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertHyperlink = function(hyperlinkAttr, insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		var a = $("<a></a>");
		
		this.insertElement(a, insertType, refEle);
		this.setHyperlinkAttr(hyperlinkAttr, a);
	};
	
	/**
	 * 元素是否是超链接。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.isHyperlink = function(ele)
	{
		ele = this._currentElement(ele);
		return ele.is("a");
	};
	
	/**
	 * 获取超链接元素属性。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.getHyperlinkAttr = function(ele)
	{
		ele = this._currentElement(ele);
		
		var attrObj = {};
		
		if(!this.isHyperlink(ele))
			return attrObj;
		
		ele = this._editElement(ele);
		
		attrObj.content = $.trim(ele.html());
		attrObj.href = (ele.attr("href") || "");
		attrObj.target = (ele.attr("target") || "");
		
		return attrObj;
	};
	
	/**
	 * 设置超链接元素属性。
	 * 
	 * @param hyperlinkAttr 超链接设置，格式为：{ content: "...", href: "...", target: "..." }
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.setHyperlinkAttr = function(hyperlinkAttr, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.isHyperlink(ele))
		{
			this.tipInfo(i18n.hyperlinkEleRequired);
			return;
		}
		
		this._setElementText(ele, (hyperlinkAttr.content || hyperlinkAttr.href || ""));
		this._setElementAttr(ele, "href", (hyperlinkAttr.href || ""));
		if(hyperlinkAttr.target)
			this._setElementAttr(ele, "target", hyperlinkAttr.target);
		else
			this._removeElementAttr(ele, "target");
	};
	
	/**
	 * 校验insertVideo操作。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertVideo = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 插入视频元素。
	 * 
	 * @param videoAttr 视频设置，格式为：{ src: "", width: ..., height: ... }
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertVideo = function(videoAttr, insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		var ele = $("<video controls=\"controls\"></video>");
		
		this.insertElement(ele, insertType, refEle);
		this.setVideoAttr(videoAttr, ele);
	};
	
	/**
	 * 是否是视频元素。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.isVideo = function(ele)
	{
		ele = this._currentElement(ele);
		return ele.is("video");
	};
	
	/**
	 * 获取视频元素属性。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.getVideoAttr = function(ele)
	{
		ele = this._currentElement(ele);
		
		var attrObj = {};
		
		if(!this.isVideo(ele))
			return attrObj;
		
		ele = this._editElement(ele);
		
		var eleStyle = this.getElementStyle(ele);
		
		attrObj.src = (ele.attr("src") || "");
		attrObj.width = eleStyle.width;
		attrObj.height = eleStyle.height;
		
		return attrObj;
	};
	
	/**
	 * 设置视频元素属性。
	 * 
	 * @param videoAttr 视频设置，格式为：{ src: "", width: ..., height: ... }
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.setVideoAttr = function(videoAttr, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.isVideo(ele))
		{
			this.tipInfo(i18n.videoEleRequired);
			return;
		}
		
		var eleStyle = { width: videoAttr.width, height: videoAttr.height };
		
		this._setElementAttr(ele, "src", (videoAttr.src || ""));
		this._setElementStyle(ele, eleStyle);
	};
	
	/**
	 * 校验insertLabel操作。
	 * 
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.checkInsertLabel = function(insertType, refEle)
	{
		return true;
	};
	
	/**
	 * 插入标签元素。
	 * 
	 * @param labelAttr 标签设置，格式为：{ content: "" }
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertLabel = function(labelAttr, insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		var ele = $("<label></label>");
		ele.html(labelAttr.content || "");
		
		this.insertElement(ele, insertType, refEle);
	};
	
	/**
	 * 是否是标签元素。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.isLabel = function(ele)
	{
		ele = this._currentElement(ele);
		return ele.is("label");
	};
	
	/**
	 * 获取标签元素属性。
	 * 
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.getLabelAttr = function(ele)
	{
		ele = this._currentElement(ele);
		
		var attrObj = {};
		
		if(!this.isLabel(ele))
			return attrObj;
		
		ele = this._editElement(ele);
		
		attrObj.content = $.trim(ele.html());
		
		return attrObj;
	};
	
	/**
	 * 设置标签元素属性。
	 * 
	 * @param labelAttr 标签设置，格式为：{ content: "..." }
	 * @param ele 可选，参考insertElement函数的refEle参数
	 */
	editor.setLabelAttr = function(labelAttr, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.isLabel(ele))
		{
			this.tipInfo(i18n.labelEleRequired);
			return;
		}
		
		this._setElementText(ele, (labelAttr.content || ""));
	};
	
	/**
	 * 校验insertChart操作。
	 * 
	 * @param insertType 可选，参考insertChart函数的insertType参数
	 * @param refEle 可选，参考insertChart函数的refEle参数
	 */
	editor.checkInsertChart = function(insertType, refEle)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		//图表元素内部不允许再插入图表元素
		if(this.isChartElement(refEle) && (insertType == "append" || insertType == "prepend"))
		{
			this.tipInfo(i18n.insertInsideChartOnChartEleDenied);
			return false;
		}
		else
			return true;
	};
	
	//插入图表元素时的默认元素样式
	editor.defaultInsertChartEleStyle = "";
	
	/**
	 * 插入图表。
	 * 
	 * @param chartWidgets 要插入的图表部件对象、数组
	 * @param insertType 可选，参考insertElement函数的insertType参数
	 * @param refEle 可选，参考insertElement函数的refEle参数
	 */
	editor.insertChart = function(chartWidgets, insertType, refEle)
	{
		if(!chartWidgets || chartWidgets.length == 0)
			return;
		
		chartWidgets = (!$.isArray(chartWidgets) ? [ chartWidgets ] : chartWidgets);
		
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		
		//图表元素内部不允许再插入图表元素
		if(!this.checkInsertChart(insertType, refEle))
			return;
		
		var styleStr = "";
		var insertParentEle = this._getInsertParentElement(refEle, insertType);
		
		if(insertParentEle.is("body"))
			styleStr = this.defaultInsertChartEleStyle;
		else
			styleStr = "width:100%;height:100%;";
		
		for(var i=0; i<chartWidgets.length; i++)
		{
			var chartWidget = chartWidgets[i];
			
			var chartDiv = $("<div></div>");
			
			//先设style，与源码模式一致
			if(styleStr)
				chartDiv.attr("style", styleStr);
			
			chartDiv.attr(chartFactory.elementAttrConst.WIDGET, chartWidget.id)
						.html("<!--"+chartWidget.name+"-->");
			
			this.insertElement(chartDiv, insertType, refEle);
		}
		
		this.dashboard.loadUnsolvedCharts();
	};
	
	editor._getInsertParentElement = function(refEle, insertType)
	{
		var insertParentEle = null;
		
		if(refEle.is("body"))
			insertParentEle = refEle;
		else if("after" == insertType || "before" == insertType)
			insertParentEle = refEle.parent();
		else
			insertParentEle = refEle;
		
		return insertParentEle;
	};
	
	/**
	 * 校验bindChart操作。
	 *
	 * @param ele 可选，要绑定的图表元素，默认为：当前选中图表元素
	 */
	editor.checkBindChart = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		return true;
	};
	
	/**
	 * 绑定或替换图表。
	 * 
	 * @param chartWidget 要绑定的新图表部件对象
	 * @param ele 可选，要绑定的图表元素，默认为：当前选中图表元素
	 */
	editor.bindChart = function(chartWidget, ele)
	{
		if(!chartWidget)
			return;
		
		ele = this._currentElement(ele, true);
		
		if(!this.checkBindChart(ele))
			return;
		
		if(this.isChartElement(ele))
		{
			this.dashboard.removeChart(ele);
		}
		
		this._setElementAttr(ele, chartFactory.elementAttrConst.WIDGET, chartWidget.id);
		this.dashboard.loadChart(ele);
	};
	
	/**
	 * 校验unbindChart操作。
	 *
	 * @param ele 可选，要解绑的图表元素，默认为：当前选中图表元素
	 */
	editor.checkUnbindChart = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		if(!this.isChartElement(ele))
		{
			this.tipInfo(i18n.selectedNotChartElement);
			return false;
		}
		
		return true;
	};
	
	/**
	 * 解绑图表。
	 * 
	 * @param ele 可选，要解绑的图表元素，默认为：当前选中图表元素
	 */
	editor.unbindChart = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkUnbindChart(ele))
			return;
		
		this.dashboard.removeChart(ele);
		this._removeElementAttr(ele, chartFactory.elementAttrConst.WIDGET);
	};
	
	/**
	 * 插入元素。
	 * 
	 * @param insertEle 要插入的jq元素、HTML文本，不要使用"<div />"的格式，可能导致编辑HTML代码格式不对
	 * @param insertType 可选，插入类型："after"、"before"、"append"、"prepend"，默认为："after"
	 * @param refEle 插入参照元素，默认为：当前选中元素，或者<body>
	 * @param sync 可选，是否将插入操作同步至编辑iframe中，默认为：true
	 */
	editor.insertElement = function(insertEle, insertType, refEle, sync)
	{
		refEle = this._currentElement(refEle);
		insertType = this._trimInsertType(refEle, insertType);
		sync = (sync == null ? true : sync);
		
		if(chartFactory.isString(insertEle))
			insertEle = $(insertEle);
		
		this._addVisualEditIdAttr(insertEle);
		
		this._insertElement(refEle, insertEle, insertType);
		
		if(sync)
		{
			var editEle = this._editElement(refEle);
			var insertEleClone = insertEle.clone();
			this._insertElement(editEle, insertEleClone, insertType);
		}
		
		insertEle.addClass(ELEMENT_CLASS_NEW_INSERT);
		$("*", insertEle).addClass(ELEMENT_CLASS_NEW_INSERT);
		
		this._hasElementClassNewInsert = true;
		
		this.changeFlag(true);
	};
	
	/**
	 * 获取元素文本内容。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.getElementText = function(ele)
	{
		ele = this._editElement(this._currentElement(ele));
		return $.trim(ele.text());
	};
	
	/**
	 * 校验setElementText操作。
	 *
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.checkSetElementText = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		var firstChild = $("> *:first-child", ele);
		
		if(firstChild.length > 0)
		{
			this.tipInfo(i18n.canEditOnlyTextElement);
			return false;
		}
		
		return true;
	};
	
	/**
	 * 设置元素文本内容。
	 * 
	 * @param text 要设置的文本内容
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.setElementText = function(text, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkSetElementText(ele))
			return;
		
		this._setElementText(ele, text);
	};
	
	/**
	 * 校验deleteElement操作。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.checkDeleteElement = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		return true;
	};
	
	/**
	 * 删除元素。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.deleteElement = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkDeleteElement(ele))
			return;
		
		var iframeEle = this._editElement(ele);
		
		//应先删除元素包含的所有图表
		var chartEles = this._getChartElements(ele);
		chartEles.each(function()
		{
			editor.dashboard.removeChart(this);
		});
		
		var selEle = (this._isSelectedElement(ele) ? ele : this._selectedElement(ele));
		this.deselectElement(selEle);
		
		ele.remove();
		iframeEle.remove();
		
		this.changeFlag(true);
	};
	
	/**
	 * 校验setElementStyle操作。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.checkSetElementStyle = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		return true;
	};
	
	/**
	 * 设置元素样式。
	 * 
	 * @param styleObj 要设置的样式对象，格式为：{ 'color': '...', 'background-color': '...' }
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.setElementStyle = function(styleObj, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkSetElementStyle(ele))
			return;
		
		var so = this._spitStyleAndOption(styleObj);
		
		this._setElementStyle(ele, so.style);
		this._setElementClass(ele, so.option.className);
		
		var chartEles = this._getChartElements(ele);
		chartEles.each(function()
		{
			if(so.option.syncChartTheme)
			{
				var thisEle = $(this);
				var chartTheme = editor._evalElementChartThemeByStyleObj(thisEle, ele, so.style);
				editor.setElementChartTheme(chartTheme, thisEle);
			}
			else
			{
				var renderedChart = editor.dashboard.renderedChart(this);
				editor._resizeChart(renderedChart);
			}
		});
	};
	
	editor._resizeChart = function(chart)
	{
		if(!chart)
			return;
		
		try
		{
			chart.resize();
		}
		catch(e){}
	};
	
	/**
	 * 获取元素样式对象。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.getElementStyle = function(ele)
	{
		ele = this._editElement(this._currentElement(ele, true));
		return this._getElementStyleObj(ele);
	};
	
	/**
	 * 设置全局样式（body）。
	 * 
	 * @param styleObj 要设置的样式对象，格式为：{ 'color': '...', 'background-color': '...' }
	 */
	editor.setGlobalStyle = function(styleObj)
	{
		var so = this._spitStyleAndOption(styleObj);
		var body = $(document.body);
		
		this._setElementStyle(body, so.style);
		this._setElementClass(body, so.option.className);
		
		if(so.style.color)
		{
			this._setPageStyle(
			{
				selectedBorderColor: so.style.color
			});
		}
		
		if(so.option.syncChartTheme)
		{
			var chartTheme = this._evalElementChartThemeByStyleObj($(document.body), $(document.body), so.style);
			this.setGlobalChartTheme(chartTheme);
		}
	};
	
	/**
	 * 获取全局样式对象（body）。
	 */
	editor.getGlobalStyle = function()
	{
		var ele = this._editElement($(document.body));
		return this._getElementStyleObj(ele);
	};
	
	editor._spitStyleAndOption = function(styleObj)
	{
		var optionObj =
		{
			syncChartTheme: (styleObj.syncChartTheme == true || styleObj.syncChartTheme == "true"),
			className: styleObj.className
		};
		
		var plainStyleObj = $.extend({}, styleObj);
		plainStyleObj.syncChartTheme = undefined;
		plainStyleObj.className = undefined;
		
		var re =
		{
			style: plainStyleObj,
			option: optionObj
		};
		
		return re;
	};
	
	editor._evalElementChartThemeByStyleObj = function(chartEle, styleEle, styleObj)
	{
		var nowTheme = this._getElementChartTheme(chartEle);
		var styleTheme = {};
		
		var color = styleObj.color;
		var bgColor = styleObj['background-color'];
		var fontSize = styleObj['font-size'];
		
		if(color || bgColor || fontSize != null)
		{
			if(color)
				styleTheme.color = color;
			
			//只有之前设置了图表背景色且不是透明的才需要同步
			if(bgColor && nowTheme && nowTheme.backgroundColor
					&& nowTheme.backgroundColor != "transparent")
				styleTheme.backgroundColor = bgColor;
			
			if(bgColor && bgColor != "transparent")
				styleTheme.actualBackgroundColor = bgColor;
			
			//从元素的css中取才能获取字体尺寸像素数
			if(fontSize != null && fontSize != "")
				styleTheme.fontSize = styleEle.css("font-size");
		}
		
		if(!nowTheme)
		{
			return styleTheme;
		}
		else
		{
			nowTheme.color = (styleTheme.color ? styleTheme.color : undefined);
			nowTheme.backgroundColor = (styleTheme.backgroundColor ? styleTheme.backgroundColor : undefined);
			nowTheme.actualBackgroundColor = (styleTheme.actualBackgroundColor ? styleTheme.actualBackgroundColor : undefined);
			nowTheme.fontSize = (styleTheme.fontSize != null ? styleTheme.fontSize : undefined);
			
			return nowTheme;
		}
	};
	
	/**
	 * 校验setElementChartTheme操作。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.checkSetElementChartTheme = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		return true;
	};
	
	/**
	 * 设置元素或其所有子图表元素的图表主题。
	 * 
	 * @param chartTheme 要设置的图表主题对象，格式为：{ 'color': '...', 'backgroundColor': '...', ... }
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.setElementChartTheme = function(chartTheme, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkSetElementChartTheme(ele))
			return;
		
		var chartEles = this._getChartElements(ele);
		chartEles.each(function()
		{
			var thisEle = $(this);
			
			editor._setElementChartTheme(thisEle, chartTheme);
			var chart = editor.dashboard.renderedChart(thisEle);
			chart.destroy();
			chart.init();
		});
	};
	
	/**
	 * 获取元素图表主题。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.getElementChartTheme = function(ele)
	{
		ele = this._editElement(this._currentElement(ele, true));
		return this._getElementChartTheme(ele);
	};
	
	/**
	 * 设置全局图表主题。
	 * 
	 * @param chartTheme 要设置的图表主题对象，格式为：{ 'color': '...', 'backgroundColor': '...', ... }
	 */
	editor.setGlobalChartTheme = function(chartTheme)
	{
		this._setElementChartTheme($(document.body), chartTheme);
		
		this.dashboard.destroy();
		this.dashboard.render();
	};
	
	/**
	 * 获取全局图表主题。
	 */
	editor.getGlobalChartTheme = function()
	{
		var ele = this._editElement($(document.body));
		return this._getElementChartTheme(ele);
	};
	
	/**
	 * 校验setElementChartOptions操作。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.checkSetElementChartOptions = function(ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this._checkNotEmptyElement(ele))
			return false;
		
		return true;
	};
	
	/**
	 * 设置元素或其所有子图表元素的图表选项。
	 * 
	 * @param chartOptions 要设置的图表选项对象、字符串，格式为：{ ... }、"{ ... }"、"变量名"
	 * @param ele 可选，元素，默认为：当前选中元素
	 */
	editor.setElementChartOptions = function(chartOptions, ele)
	{
		ele = this._currentElement(ele, true);
		
		if(!this.checkSetElementChartOptions(ele))
			return;
		
		var chartEles = this._getChartElements(ele);
		chartEles.each(function()
		{
			var thisEle = $(this);
			
			editor._setElementChartOptions(thisEle, chartOptions);
			var chart = editor.dashboard.renderedChart(thisEle);
			chart.destroy();
			chart.init();
		});
	};
	
	/**
	 * 获取元素图表选项的字符串格式。
	 * 
	 * @param ele 可选，元素，默认为：当前选中元素
	 * @oaram asString 可选，是否以字符串形式返回，默认为：true
	 */
	editor.getElementChartOptions = function(ele, asString)
	{
		ele = this._editElement(this._currentElement(ele, true));
		asString = (asString == null ? true : asString);
		
		return this._getElementChartOptions(ele);
	};
	
	/**
	 * 设置全局图表选项。
	 * 
	 * @param chartOptions 要设置的全局图表选项对象、字符串，格式为：{ ... }、"{ ... }"、"变量名"
	 */
	editor.setGlobalChartOptions = function(chartOptions)
	{
		this._setElementChartOptions($(document.body), chartOptions);
		
		this.dashboard.destroy();
		this.dashboard.render();
	};
	
	/**
	 * 获取全局图表选项的字符串格式。
	 * 
	 * @oaram asString 可选，是否以字符串形式返回，默认为：true
	 */
	editor.getGlobalChartOptions = function(asString)
	{
		asString = (asString == null ? true : asString);
		
		var ele = this._editElement($(document.body));
		return this._getElementChartOptions(ele);
	};
	
	editor._setElementChartOptions = function(ele, chartOptions, sync)
	{
		if(!chartOptions)
		{
			this._removeElementAttr(ele, chartFactory.elementAttrConst.OPTIONS, sync);
			return;
		}
		
		var attrValue = "";
		
		if(chartFactory.isString(chartOptions))
		{
			if(this._isJsonString(chartOptions))
			{
				chartOptions = chartFactory.evalSilently(chartOptions, {});
				attrValue = this._serializeForAttrValue(chartOptions);
			}
			else
			{
				//chartOptions允许是某个图表选项对象的变量名
				attrValue = chartOptions;
			}
		}
		else
			attrValue = this._serializeForAttrValue(chartOptions);
		
		attrValue = (attrValue ? attrValue : "{}");
		
		this._setElementAttr(ele, chartFactory.elementAttrConst.OPTIONS, attrValue, sync);
	};
	
	editor._getElementChartOptions = function(ele)
	{
		var optionsStr = ele.attr(chartFactory.elementAttrConst.OPTIONS);
		return optionsStr;
	};
	
	/**
	 * 校验元素不为空。
	 *
	 * @param ele
	 */
	editor._checkNotEmptyElement = function(ele)
	{
		if(this._isEmptyElement(ele))
		{
			this.tipInfo(i18n.selectedElementRequired);
			return false;
		}
		
		return true;
	};
	
	editor._getElementChartTheme = function(ele)
	{
		var themeStr = ele.attr(chartFactory.elementAttrConst.THEME);
		
		if(!themeStr)
			return null;
		
		return chartFactory.evalSilently(themeStr, {});
	};
	
	editor._setElementChartTheme = function(ele, chartTheme, sync)
	{
		chartTheme = $.extend(true, {}, chartTheme); 
		
		if(chartFactory.isString(chartTheme.graphColors))
			chartTheme.graphColors = this._spitIgnoreEmpty(chartTheme.graphColors);
		if(chartFactory.isString(chartTheme.graphRangeColors))
			chartTheme.graphRangeColors = this._spitIgnoreEmpty(chartTheme.graphRangeColors);
		
		var mergedChartTheme = (this.getElementChartTheme(ele) || {});
		
		for(var p in chartTheme)
		{
			var v = chartTheme[p];
			
			if(v == null || v == "" || ($.isArray(v) && v.length == 0))
				delete mergedChartTheme[p];
			else
				mergedChartTheme[p] = v;
		}
		
		//确保fontSize为数值
		if(mergedChartTheme.fontSize != null && !chartFactory.isNumber(mergedChartTheme.fontSize))
		{
			var fontSize = parseInt(mergedChartTheme.fontSize);
			if(isNaN(fontSize))
				delete mergedChartTheme.fontSize;
			else
				 mergedChartTheme.fontSize = fontSize;
		}
		
		var trim = {};
		
		for(var p in mergedChartTheme)
		{
			var v = mergedChartTheme[p];
			
			if(v == null)
				;
			else if(chartFactory.isString(v))
			{
				if(v != "")
					trim[p] = v;
			}
			else if($.isArray(v))
			{
				if(v.length > 0)
					trim[p] = v;
			}
			else
				trim[p] = v;
		}
		
		var attrValue = this._serializeForAttrValue(trim);
		
		if(attrValue == "{}")
			this._removeElementAttr(ele, chartFactory.elementAttrConst.THEME, sync);
		else
			this._setElementAttr(ele, chartFactory.elementAttrConst.THEME, attrValue, sync);
	};
	
	editor._setElementStyle = function(ele, styleObj, sync)
	{
		styleObj = (styleObj || {});
		sync = (sync == null ? true : sync);
		
		this._setElementStyleNoSync(ele, styleObj);
		
		if(sync)
		{
			var editEle = this._editElement(ele);
			this._setElementStyleNoSync(editEle, styleObj);
		}
		
		this.changeFlag(true);
	};
	
	editor._setElementClass = function(ele, className, sync)
	{
		className = (className || "");
		sync = (sync == null ? true : sync);
		
		var editEle = this._editElement(ele);
		var removeClassName = editEle.attr("class");
		
		if(removeClassName)
			ele.removeClass(removeClassName);
		if(sync)
		{
			if(!className)
				editEle.removeAttr("class");
			else
				editEle.removeClass(removeClassName);
		}
		
		if(className)
		{
			ele.addClass(className);
			if(sync)
				editEle.addClass(className);
		}
	};
	
	editor._setElementStyleNoSync = function(ele, styleObj)
	{
		//这里不能采用整体设置"style"属性的方式，因为"style"属性可能有很多不支持编辑的、或者动态生成的css属性，
		//它们应该被保留，且不能同步至对应的编辑元素上
		
		var nowStyleObj = chartFactory.styleStringToObj(chartFactory.elementStyle(ele) || "");
		
		for(var name in styleObj)
		{
			var value = styleObj[name];
			
			if(value == null || value == "")
				delete nowStyleObj[name];
			else
			{
				if(name == "background-image")
				{
					//不是"url(...)"格式
					if(/^url\(/i.test(value) != true)
						value = "url(" + value +")"
				}
				
				nowStyleObj[name] = value;
			}
		}
		
		if($.isEmptyObject(nowStyleObj))
			ele.removeAttr("style");
		else
			chartFactory.elementStyle(ele, nowStyleObj);
	};
	
	editor._getElementStyleObj = function(ele)
	{
		var newStyleObj = {};
		
		var styleObj = chartFactory.styleStringToObj(chartFactory.elementStyle(ele));
		
		//先处理复合css，因为它们应是低优先级
		for(var p in styleObj)
		{
			if(p == "inset")
			{
				this._resolveSetStyleInset(newStyleObj, styleObj[p]);
			}
			else if(p == "background")
			{
				this._resolveSetStyleBackground(newStyleObj, styleObj[p]);
			}
		}
		
		for(var p in styleObj)
		{
			if(this._editableElementStyles[p] && styleObj[p])
				newStyleObj[p] = styleObj[p];
		}
		
		newStyleObj.className = (ele.attr("class") || "");
		
		return newStyleObj;
	};
	
	//将css的background属性转换为background-color、background-image等属性
	editor._resolveSetStyleBackground = function(styleObj, background)
	{
		if(!background)
			return;
		
		var ary = background.split(" ");
		var beforePositionSizeSplitter = true;
		var bgPositionCount = 0, bgSizeCount = 0;
		
		for(var i=0; i<ary.length; i++)
		{
			var v = ary[i];
			
			// "background-position / background-size"
			if("/" == v)
			{
				beforePositionSizeSplitter = false;
			}
			else if(/^url\(/i.test(v))
			{
				styleObj["background-image"] = v;
			}
			else if(/^(\#|rgb)/.test(v))
			{
				styleObj["background-color"] = v;
			}
			else if(/^(no\-repeat|repeat|repeat\-x|repeat\-y)$/i.test(v))
			{
				styleObj["background-repeat"] = v;
			}
			else if(beforePositionSizeSplitter && bgPositionCount < 2 && (/^(left|right|top|bottom|center)$/i.test(v) || /^\d/.test(v)))
			{
				styleObj["background-position"] = (bgPositionCount == 0 ? v : styleObj["background-position"]+" "+v);
				bgPositionCount++;
			}
			else if(!beforePositionSizeSplitter && bgSizeCount < 2 && (/^(auto|cover|contain)$/i.test(v) || /^\d/.test(v)))
			{
				styleObj["background-size"] = (bgSizeCount == 0 ? v : styleObj["background-size"]+" "+v);
				bgSizeCount++;
			}
			// 颜色单词
			else if(i == 0 && !styleObj["background-color"] && /^[a-zA-Z]/.test(v))
			{
				styleObj["background-color"] = v;
			}
		}
	};
	
	//将css的inset属性转换为top、left、right、bottom属性
	editor._resolveSetStyleInset = function(styleObj, inset)
	{
		if(!inset)
			return;
		
		var ary = inset.split(" ");
		
		if(ary.length == 0)
			return;
		
		if(ary.length == 1)
		{
			ary[1] = ary[0];
			ary[2] = ary[0];
			ary[3] = ary[0];
		}
		else if(ary.length == 2)
		{
			ary[2] = ary[0];
			ary[3] = ary[1];
		}
		else if(ary.length == 3)
		{
			ary[3] = ary[1];
		}
		
		styleObj["top"] = ary[0];
		styleObj["right"] = ary[1];
		styleObj["bottom"] = ary[2];
		styleObj["left"] = ary[3];
	};
	
	editor._editableElementStyles =
	{
		"color": true,
		"background-color": true,
		"background-image": true,
		"background-position": true,
		"background-size": true,
		"background-repeat": true,
		"border-width": true,
		"border-color": true,
		"border-style": true,
		"border-radius": true,
		"box-shadow": true,
		"display": true,
		"width": true,
		"height": true,
		"padding": true,
		"margin": true,
		"box-sizing": true,
		"position": true,
		"left": true,
		"top": true,
		"right": true,
		"bottom": true,
		"z-index": true,
		"flex-direction": true,
		"flex-wrap": true,
		"justify-content": true,
		"align-items": true,
		"order": true,
		"flex-grow": true,
		"flex-shrink": true,
		"flex-basis": true,
		"align-self": true,
		"align-content": true,
		"grid-template-columns": true,
		"grid-template-rows": true,
		"grid-column-gap": true,
		"grid-row-gap": true,
		"grid-template-areas": true,
		"grid-auto-flow": true,
		"justify-items": true,
		"grid-auto-columns": true,
		"grid-auto-rows": true,
		"grid-column-start": true,
		"grid-column-end": true,
		"grid-row-start": true,
		"grid-row-end": true,
		"grid-area": true,
		"justify-self": true,
		"font-family": true,
		"font-size": true,
		"font-weight": true,
		"text-align": true
	};
	
	//设置元素文本内容
	editor._setElementText = function(ele, text, sync)
	{
		text = (text || "");
		sync = (sync == null ? true : sync);
		
		ele.text(text);
		
		if(sync)
		{
			var editEle = this._editElement(ele);
			editEle.text(text);
		}
		
		this.changeFlag(true);
	};
	
	//设置元素属性
	editor._setElementAttr = function(ele, name, value, sync)
	{
		sync = (sync == null ? true : sync);
		
		ele.attr(name, value);
		
		if(sync)
		{
			var editEle = this._editElement(ele);
			editEle.attr(name, value);
		}
		
		this.changeFlag(true);
	};
	
	//删除元素属性
	editor._removeElementAttr = function(ele, name, sync)
	{
		sync = (sync == null ? true : sync);
		
		ele.removeAttr(name);
		
		if(sync)
		{
			var editEle = this._editElement(ele);
			editEle.removeAttr(name);
		}
		
		this.changeFlag(true);
	};
	
	editor._currentElement = function(currentEle, excludeBody)
	{
		excludeBody = (excludeBody == null ? false : excludeBody);
		
		currentEle = (this._isEmptyElement(currentEle) ? this._selectedElement() : currentEle);
		
		if(!excludeBody)
			currentEle = (this._isEmptyElement(currentEle) ? $(document.body) : currentEle);
		
		return $(currentEle);
	};
	
	editor._addVisualEditIdAttr = function($ele)
	{
		$ele.attr(ELEMENT_ATTR_VISUAL_EDIT_ID, this._nextVisualEditId());
		
		var children = $ele.children();
		
		if(children.length < 1)
			return;
			
		children.each(function()
		{
			editor._addVisualEditIdAttr($(this));
		});
	};
	
	editor._insertElement = function(refEle, insertEle, insertType)
	{
		if(insertType == "after")
		{
			refEle.after(insertEle);
			
			refEle.after("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
		}
		else if(insertType == "before")
		{
			refEle.before(insertEle);
			
			refEle.before("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
		}
		else if(insertType == "append")
		{
			var innerHtml = refEle.prop("innerHTML");
			if(!innerHtml || innerHtml.charAt(innerHtml.length-1) != '\n')
				refEle.append("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
			
			refEle.append(insertEle);
			
			refEle.append("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
		}
		else if(insertType == "prepend")
		{
			var innerHtml = refEle.prop("innerHTML");
			if(!innerHtml || innerHtml.charAt(0) != '\n')
				refEle.prepend("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
			
			refEle.prepend(insertEle);
			
			refEle.prepend("\n"+INSERT_ELE_FORMAT_FLAG+"\n");
		}
	};
	
	editor._trimInsertType = function(refEle, insertType)
	{
		insertType = (!insertType ? "after" : insertType);
		insertType = (insertType == "after" || insertType == "before"
						|| insertType == "append" || insertType == "prepend" ? insertType : "after");
		
		if(refEle.is("body"))
		{
			if(insertType == "after")
				insertType = "append";
			else if(insertType == "before")
				insertType = "prepend";
		}
		
		return insertType;
	};
	
	//获取元素本身、子孙元素中所有的图表元素
	editor._getChartElements = function(ele)
	{
		var chartEles = [];
		
		if(ele.attr(chartFactory.elementAttrConst.WIDGET))
			chartEles.push(ele[0]);
		
		$("["+chartFactory.elementAttrConst.WIDGET+"]", ele).each(function()
		{
			chartEles.push(this);
		});
		
		return $(chartEles);
	};
	
	editor._selectedElement = function(context)
	{
		if(context == null)
			return $("."+ELEMENT_CLASS_SELECTED);
		else
			return $("."+ELEMENT_CLASS_SELECTED, context);
	};
	
	editor._isSelectedElement = function($ele)
	{
		return $ele.hasClass(ELEMENT_CLASS_SELECTED);
	};
	
	editor._selectElement = function($ele)
	{
		$ele.addClass(ELEMENT_CLASS_SELECTED);
	};
	
	editor._deselectElement = function($ele)
	{
		$ele.removeClass(ELEMENT_CLASS_SELECTED);
	};
	
	editor._removeElementClassNewInsert = function()
	{
		if(this._hasElementClassNewInsert)
		{
			$("."+ELEMENT_CLASS_NEW_INSERT).removeClass(ELEMENT_CLASS_NEW_INSERT);
			this._hasElementClassNewInsert = false;
		}
	};
	
	editor._isEmptyElement = function(ele)
	{
		return (ele == null || ele.length == 0);
	};
	
	editor._getVisualEditId = function($ele)
	{
		return $ele.attr(ELEMENT_ATTR_VISUAL_EDIT_ID);
	};
	
	editor._nextVisualEditId = function()
	{
		return chartFactory.uid();
	};
	
	/**
	 * 设置编辑页面样式。
	 *
	 * @param options 可选，格式为：{ selectedBorderColor: "..." }
	 */
	editor._setPageStyle = function(options)
	{
		options = $.extend(
		{
			selectedBorderColor: $(document.body).css("color")
		},
		options);
		
		chartFactory.styleSheetText("dg-show-ve-style",
			  "\n"
			+ "."+BODY_CLASS_VISUAL_EDITOR+"."+BODY_CLASS_ELEMENT_BOUNDARY+" *["+ELEMENT_ATTR_VISUAL_EDIT_ID+"]{\n"
			+ "  box-shadow: inset 0 0 1px 1px " + options.selectedBorderColor + ";"
			+ "\n}"
			+ "\n"
			+ "."+BODY_CLASS_VISUAL_EDITOR+" ."+ELEMENT_CLASS_SELECTED+",\n"
			+ "."+BODY_CLASS_VISUAL_EDITOR+"."+BODY_CLASS_ELEMENT_BOUNDARY+" ."+ELEMENT_CLASS_SELECTED+"{\n"
			+ "  box-shadow: inset 0 0 3px 3px " + options.selectedBorderColor + " !important;"
			+ "\n}"
			+ "\n"
			+ "."+BODY_CLASS_VISUAL_EDITOR+" ."+ELEMENT_CLASS_NEW_INSERT+",\n"
			+ "."+BODY_CLASS_VISUAL_EDITOR+"."+BODY_CLASS_ELEMENT_BOUNDARY+" ."+ELEMENT_CLASS_NEW_INSERT+"{\n"
			+ "  box-shadow: inset 0 0 1px 1px " + options.selectedBorderColor + ";"
			+ "\n}");
	};
	
	//获取编辑HTML信息
	//结构参考：org.datagear.web.controller.DashboardController.DashboardShowForEdit.EditHtmlInfo
	editor._editHtmlInfo = function()
	{
		return this.dashboard.renderContextAttr(DASHBOARD_BUILTIN_RENDER_CONTEXT_ATTR_EDIT_HTML_INFO);
	};
	
	//反转义编辑HTML（转义操作由后台执行）
	editor._unescapeEditHtml = function(editHtml)
	{
		return (editHtml ? editHtml.replace(/<\\\//g, "</") : editHtml);
	};
	
	editor._spitIgnoreEmpty = function(str, splitter)
	{
		splitter = (splitter ? splitter : ",");
		
		var ary = [];
		
		if(!str)
			return ary;
		
		ary = str.split(splitter);
		
		var re = [];
		
		for(var i=0; i<ary.length; i++)
		{
			var ele = $.trim(ary[i]);
			if(ele)
				re.push(ele);
		}
		
		return re;
	};
	
	editor._serializeForAttrValue = function(obj)
	{
		if(obj == null)
			return null;
		
		var type = typeof(obj);
		
		if(type == "string")
			return "'" + obj.replace(/\'/g, "\\'") + "'";
		else if(type == "number")
			return obj.toString();
		else if(type == "boolean")
			return obj.toString();
		else if($.isArray(obj))
		{
			var str = "[";
			
			for(var i=0; i<obj.length; i++)
			{
				if(i > 0)
					str += ",";
				
				str += this._serializeForAttrValue(obj[i]);
			}
			
			str += "]";
			
			return str;
		}
		else if($.isPlainObject(obj))
		{
			var str = "{";
			
			for(var p in obj)
			{
				if(str != "{")
					str += ",";
				
				var v = this._serializeForAttrValue(obj[p]);
				
				if(v != null)
					str += this._serializeForAttrValue(p) + ":" + v;
			}
			
			str += "}";
			
			return str;
		}
		else
			return obj.toString();
	};
	
	/**
	 * 获取编辑iframe，也可设置其HTML。
	 * 
	 * 这里的editBodyHtml应只使用"<body>...</body>"，因为渲染iframe页面时，如果"<body>"前、"</body>"后里有不合规的元素，
	 * 可能会被渲染至<body></body>内，导致【结果HTML】还原不对。
	 * 
	 * @param editBodyHtml 
	 */
	editor._editIframe = function(editBodyHtml)
	{
		var id = (this._editIframeId != null ? this._editIframeId
					: (this._editIframeId = chartFactory.uid()));
		
		var iframe = $("#" + id);
		
		if(iframe.length == 0)
		{
			iframe = $("<iframe class='dg-edit-html-ifm' style='display:none;'></iframe>")
				.attr("name", id).attr("id", id).appendTo(document.body);
		}
		
		iframe = iframe[0];
		
		if(editBodyHtml != null)
		{
			var editIframeBodyHtml = this._toEditIframeBodyHtml(editBodyHtml);
			
			var editDoc = this._editDocument();
			editDoc.open();
			editDoc.write("<!DOCTYPE html><html><head></head><body>");
			editDoc.write(editIframeBodyHtml);
			editDoc.write("</body></html>");
			editDoc.close();
			
			this.changeFlag(true);
		}
		
		return iframe;
	};
	
	//将"<body>...</body>"转换为"<div>...</div>"，使得可以直接使用：$(document.body).html("...");
	editor._toEditIframeBodyHtml = function(editBodyHtml)
	{
		var startTagRegex = /^\s*<body/i;
		var endTagRegex = /\/body>\s*$/i;
		
		var editIframeBodyHtml = editBodyHtml.replace(startTagRegex, "<div");
		editIframeBodyHtml = editIframeBodyHtml.replace(endTagRegex, "/div>");
		
		return editIframeBodyHtml;
	};
	
	//将由editor._toEditIframeBodyHtml()转换的"<div>...</div>"恢复为"<body>...</body>"
	editor._fromEditIframeBodyHtml = function(editIframeBodyHtml)
	{
		var startTagRegex = /^\s*<div/i;
		var endTagRegex = /\/div>\s*$/i;
		
		var editBodyHtml = editIframeBodyHtml.replace(startTagRegex, "<body");
		editBodyHtml = editBodyHtml.replace(endTagRegex, "/body>");
		
		return editBodyHtml;
	};
	
	/**
	 * 获取编辑iframe的document对象。
	 */
	editor._editDocument = function(iframe)
	{
		iframe = (iframe == null ? this._editIframe() : iframe);
		
		return (iframe.contentDocument || iframe.contentWindow.document);
	};
	
	//获取编辑HTML的<body>...</body>内容
	editor._editBodyHtml = function()
	{
		var editDoc = this._editDocument();
		var editIframeBodyHtml = $(editDoc.body).html();
		
		return this._fromEditIframeBodyHtml(editIframeBodyHtml);
	};
	
	/**
	 * 获取编辑iframe中的元素。
	 * 
	 * @param $ele 展示元素
	 */
	editor._editElement = function($ele)
	{
		var editDoc = this._editDocument();
		
		if($ele.is("body"))
		{
			// <body>被转换为了<div>，参考editor._toEditIframeBodyHtml()函数
			return $("> div", editDoc.body);
		}
		
		var editId = (this._getVisualEditId($ele) || "");
		return $("["+ELEMENT_ATTR_VISUAL_EDIT_ID+"='"+editId+"']", editDoc.body);
	};
	
	editor._evalTopWindowSize = function()
	{
		var topWindow = window;
		while(topWindow.parent  && topWindow.parent != topWindow)
			topWindow = topWindow.parent;
		
		var size =
		{
			width: $(topWindow).width(),
			height: $(topWindow).height()
		};
		
		return size;
	};
	
	editor._isJsonString = function(str)
	{
		return chartFactory.isJsonString(str);
	};
	
	/**
	 * 获取元素节点路径信息。
	 */
	editor.getElementPath = function(ele)
	{
		ele = $(ele);
		
		var paths = [];
		
		while(true)
		{
			if(ele.length == 0)
				break;
			
			var isBody =  ele.is("body");
			
			if(!this._isSelectableElement(ele) && !isBody)
				continue;
			
			var editEle = this._editElement(ele);
			var pathInfo =
			{
				tagName: (ele[0].tagName || "").toLowerCase(),
				selected: this._isSelectedElement(ele),
				id: editEle.attr("id"),
				className: editEle.attr("class"),
				visualEditId: editEle.attr(ELEMENT_ATTR_VISUAL_EDIT_ID)
			};
			
			var displayName = pathInfo.tagName;
			if(pathInfo.id)
				displayName += "#"+pathInfo.id;
			else if(pathInfo.className)
				displayName += "."+pathInfo.className;
			
			pathInfo.displayName = displayName;
			
			paths.push(pathInfo);
			
			if(isBody)
				break;
			else
				ele = ele.parent();
		}
		
		return paths.reverse();
	};
})
(this);