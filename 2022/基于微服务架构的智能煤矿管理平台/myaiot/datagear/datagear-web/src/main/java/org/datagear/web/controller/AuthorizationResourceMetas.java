/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

package org.datagear.web.controller;

import java.io.Serializable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import org.datagear.management.domain.Authorization;
import org.datagear.management.domain.Schema;

/**
 * 授权资源元信息。
 * <p>
 * {@linkplain AuthorizationController}使用此类提供的元信息绘制授权页面。
 * </p>
 * 
 * @author datagear@163.com
 *
 */
public class AuthorizationResourceMetas
{
	private static final ConcurrentMap<String, ResourceMeta> RESOURCEMETA_MAP = new ConcurrentHashMap<String, ResourceMeta>();

	/**
	 * 注册{@linkplain ResourceMeta}。
	 * 
	 * @param resourceMeta
	 */
	public static void register(ResourceMeta resourceMeta)
	{
		RESOURCEMETA_MAP.put(resourceMeta.getResourceType(), resourceMeta);
	}

	/**
	 * 注册用于支持分享功能的{@linkplain ResourceMeta}。
	 * 
	 * @param resourceType
	 */
	public static void registerForShare(String resourceType)
	{
		PermissionMeta read = PermissionMeta.valueOfRead();
		ResourceMeta resourceMeta = new ResourceMeta(resourceType, PermissionMeta.valuesOf(read));
		resourceMeta.setEnableSetEnable(false);
		resourceMeta.setAuthModuleLabel("module.share");

		resourceMeta.setAuthPrincipalLabel("authorization.default.share.principal");
		resourceMeta.setAuthPrincipalTypeLabel("authorization.default.share.principalType");

		register(resourceMeta);
	}

	/**
	 * 获取{@linkplain ResourceMeta}。
	 * <p>
	 * 没有，则返回{@code null}。
	 * </p>
	 * 
	 * @param resourceType
	 * @return
	 */
	public static ResourceMeta get(String resourceType)
	{
		return RESOURCEMETA_MAP.get(resourceType);
	}

	static
	{
		// 数据源授权资源元信息
		{
			PermissionMeta read = PermissionMeta.valueOfRead(Schema.PERMISSION_TABLE_DATA_READ);
			read.setPermissionLabelDesc("schema.auth.permission.read.desc");

			PermissionMeta edit = PermissionMeta.valueOfEdit(Schema.PERMISSION_TABLE_DATA_EDIT);
			edit.setPermissionLabelDesc("schema.auth.permission.edit.desc");

			PermissionMeta delete = PermissionMeta.valueOfDelete(Schema.PERMISSION_TABLE_DATA_DELETE);
			delete.setPermissionLabelDesc("schema.auth.permission.delete.desc");

			PermissionMeta none = PermissionMeta.valueOfNone();
			none.setPermissionLabelDesc("schema.auth.permission.none.desc");

			ResourceMeta resourceMeta = new ResourceMeta(Schema.AUTHORIZATION_RESOURCE_TYPE,
					PermissionMeta.valuesOf(read, edit, delete, none));

			register(resourceMeta);
		}
	}

	private AuthorizationResourceMetas()
	{
		super();
	}

	/**
	 * 授权资源元信息。
	 * 
	 * @author datagear@163.com
	 *
	 */
	public static class ResourceMeta implements Serializable
	{
		private static final long serialVersionUID = 1L;

		/** 资源类型 */
		private String resourceType;

		/** 资源权限元信息 */
		private PermissionMeta[] permissionMetas;

		/** 是否开启设置启用/禁用功能 */
		private boolean enableSetEnable = true;

		private String authModuleLabel = "module.authorization";
		
		private String authResourceLabel = "authorization.resource";

		private String authResourceTypeLabel = "authorization.resourceType";

		private String authPrincipalLabel = "authorization.principal";

		private String authPrincipalTypeLabel = "authorization.principalType";

		private String authPermissionLabel = "authorization.permission";

		private String authEnabledLabel = "isEnabled";

		public ResourceMeta()
		{
			super();
		}

		public ResourceMeta(String resourceType, PermissionMeta... permissionMetas)
		{
			super();
			this.resourceType = resourceType;
			this.permissionMetas = permissionMetas;
		}

		public String getResourceType()
		{
			return resourceType;
		}

		public void setResourceType(String resourceType)
		{
			this.resourceType = resourceType;
		}

		public PermissionMeta[] getPermissionMetas()
		{
			return permissionMetas;
		}

		public void setPermissionMetas(PermissionMeta[] permissionMetas)
		{
			this.permissionMetas = permissionMetas;
		}

		public boolean isEnableSetEnable()
		{
			return enableSetEnable;
		}

		public void setEnableSetEnable(boolean enableSetEnable)
		{
			this.enableSetEnable = enableSetEnable;
		}

		public String getAuthModuleLabel()
		{
			return authModuleLabel;
		}

		public void setAuthModuleLabel(String authModuleLabel)
		{
			this.authModuleLabel = authModuleLabel;
		}

		public String getAuthResourceLabel()
		{
			return authResourceLabel;
		}

		public void setAuthResourceLabel(String authResourceLabel)
		{
			this.authResourceLabel = authResourceLabel;
		}

		public String getAuthResourceTypeLabel()
		{
			return authResourceTypeLabel;
		}

		public void setAuthResourceTypeLabel(String authResourceTypeLabel)
		{
			this.authResourceTypeLabel = authResourceTypeLabel;
		}

		public String getAuthPrincipalLabel()
		{
			return authPrincipalLabel;
		}

		public void setAuthPrincipalLabel(String authPrincipalLabel)
		{
			this.authPrincipalLabel = authPrincipalLabel;
		}

		public String getAuthPrincipalTypeLabel()
		{
			return authPrincipalTypeLabel;
		}

		public void setAuthPrincipalTypeLabel(String authPrincipalTypeLabel)
		{
			this.authPrincipalTypeLabel = authPrincipalTypeLabel;
		}

		public String getAuthPermissionLabel()
		{
			return authPermissionLabel;
		}

		public void setAuthPermissionLabel(String authPermissionLabel)
		{
			this.authPermissionLabel = authPermissionLabel;
		}

		public String getAuthEnabledLabel()
		{
			return authEnabledLabel;
		}

		public void setAuthEnabledLabel(String authEnabledLabel)
		{
			this.authEnabledLabel = authEnabledLabel;
		}

		/**
		 * 是否只有一个权限。
		 * 
		 * @return
		 */
		public boolean isSinglePermission()
		{
			return (this.permissionMetas != null && this.permissionMetas.length == 1);
		}

		public PermissionMeta getSinglePermissionMeta()
		{
			return this.permissionMetas[0];
		}
	}

	/**
	 * 授权资源权限值元信息。
	 * 
	 * @author datagear@163.com
	 *
	 */
	public static class PermissionMeta implements Serializable
	{
		public static final String[] DEFAULT_SUB_LABELS = { "READ", "EDIT", "DELETE", "NONE" };

		private static final long serialVersionUID = 1L;

		/** 权限值 */
		private int permission;

		/** 权限标签I18N关键字 */
		private String permissionLabel;

		/** 可选，权限标签描述I18N关键字 */
		private String permissionLabelDesc = "authorization.default.permission.desc";

		public PermissionMeta()
		{
			super();
		}

		public PermissionMeta(int permission, String permissionLabel)
		{
			super();
			this.permission = permission;
			this.permissionLabel = permissionLabel;
		}

		public int getPermission()
		{
			return permission;
		}

		public void setPermission(int permission)
		{
			this.permission = permission;
		}

		public String getPermissionLabel()
		{
			return permissionLabel;
		}

		public void setPermissionLabel(String permissionLabel)
		{
			this.permissionLabel = permissionLabel;
		}

		public String getPermissionLabelDesc()
		{
			return permissionLabelDesc;
		}

		public void setPermissionLabelDesc(String permissionLabelDesc)
		{
			this.permissionLabelDesc = permissionLabelDesc;
		}

		public static PermissionMeta valueOf(int permission, String permissionLabel)
		{
			return new PermissionMeta(permission, permissionLabel);
		}

		public static PermissionMeta valueOfRead()
		{
			return valueOfRead(Authorization.PERMISSION_READ_START);
		}

		public static PermissionMeta valueOfRead(int permission)
		{
			return new PermissionMeta(permission, "authorization.permission.READ");
		}

		public static PermissionMeta valueOfEdit()
		{
			return valueOfEdit(Authorization.PERMISSION_EDIT_START);
		}

		public static PermissionMeta valueOfEdit(int permission)
		{
			return new PermissionMeta(permission, "authorization.permission.EDIT");
		}

		public static PermissionMeta valueOfDelete()
		{
			return valueOfDelete(Authorization.PERMISSION_DELETE_START);
		}

		public static PermissionMeta valueOfDelete(int permission)
		{
			return new PermissionMeta(permission, "authorization.permission.DELETE");
		}

		public static PermissionMeta valueOfNone()
		{
			return valueOfNone(Authorization.PERMISSION_NONE_START);
		}

		public static PermissionMeta valueOfNone(int permission)
		{
			return new PermissionMeta(permission, "authorization.permission.NONE");
		}

		public static PermissionMeta[] valuesOf(PermissionMeta... permissionMetas)
		{
			return permissionMetas;
		}
	}
}