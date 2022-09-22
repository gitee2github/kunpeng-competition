/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

package org.datagear.management.service.impl;

import java.util.Map;

import org.apache.ibatis.session.SqlSessionFactory;
import org.datagear.management.domain.DashboardShareSet;
import org.datagear.management.service.DashboardShareSetService;
import org.datagear.management.util.dialect.MbSqlDialect;
import org.mybatis.spring.SqlSessionTemplate;

/**
 * {@linkplain DashboardShareSetService}实现类。
 * 
 * @author datagear@163.com
 *
 */
public class DashboardShareSetServiceImpl extends AbstractMybatisEntityService<String, DashboardShareSet>
		implements DashboardShareSetService
{
	protected static final String SQL_NAMESPACE = DashboardShareSet.class.getName();

	private DashboardSharePasswordCrypto dashboardSharePasswordCrypto;

	public DashboardShareSetServiceImpl()
	{
		super();
	}

	public DashboardShareSetServiceImpl(SqlSessionFactory sqlSessionFactory, MbSqlDialect dialect,
			DashboardSharePasswordCrypto dashboardSharePasswordCrypto)
	{
		super(sqlSessionFactory, dialect);
		this.dashboardSharePasswordCrypto = dashboardSharePasswordCrypto;
	}

	public DashboardShareSetServiceImpl(SqlSessionTemplate sqlSessionTemplate, MbSqlDialect dialect,
			DashboardSharePasswordCrypto dashboardSharePasswordCrypto)
	{
		super(sqlSessionTemplate, dialect);
		this.dashboardSharePasswordCrypto = dashboardSharePasswordCrypto;
	}

	public DashboardSharePasswordCrypto getDashboardSharePasswordEncoder()
	{
		return dashboardSharePasswordCrypto;
	}

	public void setDashboardSharePasswordEncoder(DashboardSharePasswordCrypto dashboardSharePasswordCrypto)
	{
		this.dashboardSharePasswordCrypto = dashboardSharePasswordCrypto;
	}

	@Override
	public void save(DashboardShareSet entity)
	{
		if (!super.update(entity))
			super.add(entity);
	}

	@Override
	protected void add(DashboardShareSet entity, Map<String, Object> params)
	{
		entity = entity.clone();
		entity.setPassword(this.dashboardSharePasswordCrypto.encrypt(entity.getPassword()));

		super.add(entity, params);
	}

	@Override
	protected boolean update(DashboardShareSet entity, Map<String, Object> params)
	{
		entity = entity.clone();
		entity.setPassword(this.dashboardSharePasswordCrypto.encrypt(entity.getPassword()));

		return super.update(entity, params);
	}

	@Override
	protected DashboardShareSet getByIdFromDB(String id, Map<String, Object> params)
	{
		DashboardShareSet entity = super.getByIdFromDB(id, params);

		if (entity != null)
			entity.setPassword(this.dashboardSharePasswordCrypto.decrypt(entity.getPassword()));

		return entity;
	}

	@Override
	protected String getSqlNamespace()
	{
		return SQL_NAMESPACE;
	}
}
