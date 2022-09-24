/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

package org.datagear.web.controller;

import java.sql.Connection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.datagear.connection.DriverEntity;
import org.datagear.connection.DriverEntityManager;
import org.datagear.management.domain.Schema;
import org.datagear.management.domain.User;
import org.datagear.management.service.SchemaGuardService;
import org.datagear.management.service.impl.SaveSchemaUrlPermissionDeniedException;
import org.datagear.meta.SimpleTable;
import org.datagear.meta.Table;
import org.datagear.meta.TableType;
import org.datagear.persistence.Order;
import org.datagear.persistence.PagingData;
import org.datagear.persistence.PagingQuery;
import org.datagear.util.IDUtil;
import org.datagear.util.JdbcUtil;
import org.datagear.web.util.KeywordMatcher;
import org.datagear.web.util.OperationMessage;
import org.datagear.web.util.WebUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * 模式管理控制器。
 * 
 * @author datagear@163.com
 *
 */
@Controller
@RequestMapping("/schema")
public class SchemaController extends AbstractSchemaConnTableController
{
	public static final String COOKIE_PAGINATION_SIZE = "SCHEMA_PAGINATION_PAGE_SIZE";

	@Autowired
	private DriverEntityManager driverEntityManager;

	@Autowired
	private SchemaGuardService schemaGuardService;

	public SchemaController()
	{
		super();
	}

	public DriverEntityManager getDriverEntityManager()
	{
		return driverEntityManager;
	}

	public void setDriverEntityManager(DriverEntityManager driverEntityManager)
	{
		this.driverEntityManager = driverEntityManager;
	}

	public SchemaGuardService getSchemaGuardService()
	{
		return schemaGuardService;
	}

	public void setSchemaGuardService(SchemaGuardService schemaGuardService)
	{
		this.schemaGuardService = schemaGuardService;
	}

	@RequestMapping("/add")
	public String add(org.springframework.ui.Model model,
			@RequestParam(value = "copyId", required = false) String copyId)
	{
		Schema schema = new Schema();

		Schema sourceSchema = null;

		if (!isEmpty(copyId))
		{
			sourceSchema = getSchemaService().getById(copyId);

			if (sourceSchema != null)
			{
				schema.setTitle(sourceSchema.getTitle());
				schema.setUrl(sourceSchema.getUrl());
				schema.setUser(sourceSchema.getUser());
				schema.setDriverEntity(sourceSchema.getDriverEntity());
			}
		}

		setFormModel(model, schema, REQUEST_ACTION_ADD, SUBMIT_ACTION_SAVE_ADD);

		return "/schema/schema_form";
	}

	@RequestMapping(value = "/saveAdd", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public ResponseEntity<OperationMessage> saveAdd(HttpServletRequest request, HttpServletResponse response,
			@RequestBody Schema schema)
	{
		User user = WebUtils.getUser();

		if (isBlank(schema.getTitle()) || isBlank(schema.getUrl()))
			throw new IllegalInputException();

		schema.setId(IDUtil.randomIdOnTime20());
		schema.setCreateTime(new Date());
		schema.setCreateUser(user.cloneNoPassword());

		getSchemaService().add(user, schema);

		return optSuccessDataResponseEntity(request, schema);
	}

	@RequestMapping("/edit")
	public String edit(HttpServletRequest request, HttpServletResponse response, org.springframework.ui.Model model,
			@RequestParam("id") String id)
	{
		User user = WebUtils.getUser();
		Schema schema = getByIdForEdit(getSchemaService(), user, id);
		
		setFormModel(model, schema, REQUEST_ACTION_EDIT, SUBMIT_ACTION_SAVE_EDIT);
		return "/schema/schema_form";
	}

	@RequestMapping(value = "/saveEdit", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public ResponseEntity<OperationMessage> saveEdit(HttpServletRequest request, HttpServletResponse response,
			@RequestBody Schema schema)
	{
		if (isBlank(schema.getTitle()) || isBlank(schema.getUrl()))
			throw new IllegalInputException();

		User user = WebUtils.getUser();

		Schema old = getSchemaService().getById(schema.getId());

		boolean updated = getSchemaService().update(user, schema);

		// 如果URL或者用户变更了，则需要清除缓存
		if (updated && old != null
				&& (!schema.getUrl().equals(old.getUrl()) || !schema.getUser().equals(old.getUser())))
			getTableCache().invalidate(schema.getId());

		return optSuccessDataResponseEntity(request, schema);
	}

	@RequestMapping("/view")
	public String view(HttpServletRequest request, HttpServletResponse response, org.springframework.ui.Model model,
			@RequestParam("id") String id)
	{
		User user = WebUtils.getUser();
		Schema schema = getByIdForView(getSchemaService(), user, id);
		schema.clearPassword();

		setFormModel(model, schema, REQUEST_ACTION_VIEW, SUBMIT_ACTION_NONE);
		return "/schema/schema_form";
	}

	@RequestMapping(value = "/delete", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public ResponseEntity<OperationMessage> delete(HttpServletRequest request, HttpServletResponse response,
			@RequestBody String[] ids)
	{
		User user = WebUtils.getUser();

		for (int i = 0; i < ids.length; i++)
		{
			String id = ids[i];

			boolean deleted = getSchemaService().deleteById(user, id);

			// 清除缓存
			if (deleted)
				getTableCache().invalidate(id);
		}

		return optSuccessResponseEntity(request);
	}

	@RequestMapping(value = "/query")
	public String query(HttpServletRequest request, HttpServletResponse response, org.springframework.ui.Model model)
	{
		model.addAttribute(KEY_REQUEST_ACTION, REQUEST_ACTION_QUERY);
		setReadonlyActionOnRoleDataAnalyst(model, WebUtils.getUser());
		return "/schema/schema_tree";
	}

	@RequestMapping(value = "/select")
	public String select(HttpServletRequest request, HttpServletResponse response, org.springframework.ui.Model model)
	{
		setSelectAction(request, model);
		return "/schema/schema_table";
	}

	@RequestMapping(value = "/queryData", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public List<Schema> queryData(HttpServletRequest request, HttpServletResponse response,
			@RequestBody(required = false) PagingQuery pagingQueryParam) throws Exception
	{
		User user = WebUtils.getUser();
		final PagingQuery pagingQuery = inflatePagingQuery(request, pagingQueryParam);

		List<Schema> schemas = getSchemaService().query(user, pagingQuery);
		processForUI(request, schemas);

		return schemas;
	}

	@RequestMapping(value = "/pagingQueryData", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public PagingData<Schema> pagingQueryData(HttpServletRequest request, HttpServletResponse response,
			@RequestBody(required = false) PagingQuery pagingQueryParam) throws Exception
	{
		User user = WebUtils.getUser();
		final PagingQuery pagingQuery = inflatePagingQuery(request, pagingQueryParam);

		PagingData<Schema> pagingData = getSchemaService().pagingQuery(user, pagingQuery);
		processForUI(request, pagingData.getItems());

		return pagingData;
	}

	@RequestMapping(value = "/testConnection", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public ResponseEntity<OperationMessage> testConnection(HttpServletRequest request, HttpServletResponse response,
			@RequestBody Schema schema) throws Exception
	{
		if (isBlank(schema.getTitle()) || isBlank(schema.getUrl()))
			throw new IllegalInputException();

		User user = WebUtils.getUser();

		if (!this.schemaGuardService.isPermitted(user, schema.getUrl()))
			throw new SaveSchemaUrlPermissionDeniedException();

		// 用户选定驱动程序时
		if (!isEmpty(schema.getDriverEntity()) && !isEmpty(schema.getDriverEntity().getId()))
		{
			DriverEntity driverEntity = this.driverEntityManager.get(schema.getDriverEntity().getId());
			schema.setDriverEntity(driverEntity);
		}

		Connection cn = null;

		try
		{
			cn = getSchemaConnection(schema);
		}
		finally
		{
			JdbcUtil.closeConnection(cn);
		}

		return optSuccessDataResponseEntity(request, "schema.testConnection.ok");
	}

	@RequestMapping(value = "/list", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public List<Schema> list(HttpServletRequest request, HttpServletResponse response,
			@RequestBody PagingQuery pagingQueryParam)
	{
		PagingQuery pagingQuery = inflatePagingQuery(request, pagingQueryParam, COOKIE_PAGINATION_SIZE);

		User user = WebUtils.getUser();

		pagingQuery.setOrders(Order.valueOf("title", Order.ASC));

		List<Schema> schemas = getSchemaService().query(user, pagingQuery);
		processForUI(request, schemas);

		return schemas;
	}

	@RequestMapping(value = "/{schemaId}/pagingQueryTable", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public PagingData<SimpleTable> pagingQueryTable(HttpServletRequest request, HttpServletResponse response,
			org.springframework.ui.Model springModel, @PathVariable("schemaId") String schemaId,
			@RequestBody PagingQuery pagingQueryParam) throws Throwable
	{
		final PagingQuery pagingQuery = inflatePagingQuery(request, pagingQueryParam, COOKIE_PAGINATION_SIZE);

		List<SimpleTable> tables = new ReturnSchemaConnExecutor<List<SimpleTable>>(request, response, springModel,
				schemaId, true)
		{
			@Override
			protected List<SimpleTable> execute(HttpServletRequest request, HttpServletResponse response,
					org.springframework.ui.Model springModel, Schema schema) throws Throwable
			{
				Connection cn = getConnection();

				List<SimpleTable> tables = getDbMetaResolver().getSimpleTables(cn);
				return TableType.filterUserDataTables(cn, getDbMetaResolver(), tables);
			}

		}.execute();

		sortByTableName(tables);

		List<SimpleTable> keywordTables = findByKeyword(tables, pagingQuery.getKeyword());

		PagingData<SimpleTable> pagingData = new PagingData<>(pagingQuery.getPage(), keywordTables.size(),
				pagingQuery.getPageSize());

		keywordTables = keywordTables.subList(pagingData.getStartIndex(), pagingData.getEndIndex());

		pagingData.setItems(keywordTables);

		return pagingData;
	}

	@RequestMapping(value = "/{schemaId}/table/{tableName}", produces = CONTENT_TYPE_JSON)
	@ResponseBody
	public Table getTable(HttpServletRequest request, HttpServletResponse response,
			org.springframework.ui.Model springModel, @PathVariable("schemaId") String schemaId,
			@PathVariable("tableName") String tableName,
			@RequestParam(value = "reload", required = false) Boolean forceReload) throws Throwable
	{
		if (Boolean.TRUE.equals(forceReload))
			getTableCache().invalidate(schemaId, tableName);

		ReturnSchemaConnTableExecutor<Table> executor = new ReturnSchemaConnTableExecutor<Table>(request, response,
				springModel, schemaId, tableName, true)
		{
			@Override
			protected Table execute(HttpServletRequest request, HttpServletResponse response,
					org.springframework.ui.Model springModel, Schema schema, Table table) throws Exception
			{
				return table;
			}
		};

		return executor.execute();
	}

	/**
	 * 处理展示。
	 * 
	 * @param request
	 * @param schemas
	 */
	protected void processForUI(HttpServletRequest request, List<Schema> schemas)
	{
		if (schemas != null && !schemas.isEmpty())
		{
			for (Schema schema : schemas)
			{
				// 清除密码，避免传输至客户端引起安全问题。
				schema.clearPassword();
			}
		}
	}

	/**
	 * 将{@linkplain SimpleTable}数组按照{@linkplain SimpleTable#getName()}排序。
	 * 
	 * @param tables
	 */
	public static void sortByTableName(List<SimpleTable> tables)
	{
		Collections.sort(tables, TABLE_SORT_BY_NAME_COMPARATOR);
	}

	/**
	 * 根据表名称关键字查询{@linkplain TableInfo}列表。
	 * 
	 * @param tables
	 * @param tableNameKeyword
	 * @return
	 */
	public static List<SimpleTable> findByKeyword(List<SimpleTable> tables, String tableNameKeyword)
	{
		return KeywordMatcher.<SimpleTable> match(tables, tableNameKeyword, new KeywordMatcher.MatchValue<SimpleTable>()
		{
			@Override
			public String[] get(SimpleTable t)
			{
				return new String[] { t.getName() };
			}
		});
	}

	public static Comparator<SimpleTable> TABLE_SORT_BY_NAME_COMPARATOR = new Comparator<SimpleTable>()
	{
		@Override
		public int compare(SimpleTable o1, SimpleTable o2)
		{
			return o1.getName().compareTo(o2.getName());
		}
	};
}
