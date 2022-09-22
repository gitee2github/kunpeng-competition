/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

package org.datagear.web.security;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.datagear.web.util.accesslatch.IpLoginLatch;
import org.datagear.web.util.accesslatch.UsernameLoginLatch;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationFailureHandler;

/**
 * {@linkplain AuthenticationFailureHandler}自定义实现。
 * 
 * @author datagear@163.com
 *
 */
public class AuthenticationFailureHandlerImpl extends SimpleUrlAuthenticationFailureHandler
{
	private IpLoginLatch ipLoginLatch;

	private UsernameLoginLatch usernameLoginLatch;

	private String loginUsernameParam;

	public AuthenticationFailureHandlerImpl(String defaultFailureUrl, IpLoginLatch ipLoginLatch,
			UsernameLoginLatch usernameLoginLatch, String loginUsernameParam)
	{
		super(defaultFailureUrl);
		super.setUseForward(true);
		this.ipLoginLatch = ipLoginLatch;
		this.usernameLoginLatch = usernameLoginLatch;
		this.loginUsernameParam = loginUsernameParam;
	}

	public IpLoginLatch getIpLoginLatch()
	{
		return ipLoginLatch;
	}

	public void setIpLoginLatch(IpLoginLatch ipLoginLatch)
	{
		this.ipLoginLatch = ipLoginLatch;
	}

	public UsernameLoginLatch getUsernameLoginLatch()
	{
		return usernameLoginLatch;
	}

	public void setUsernameLoginLatch(UsernameLoginLatch usernameLoginLatch)
	{
		this.usernameLoginLatch = usernameLoginLatch;
	}

	public String getLoginUsernameParam()
	{
		return loginUsernameParam;
	}

	public void setLoginUsernameParam(String loginUsernameParam)
	{
		this.loginUsernameParam = loginUsernameParam;
	}

	@Override
	public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
			AuthenticationException exception) throws IOException, ServletException
	{
		onAuthenticationFailure(request, response, exception, true);
	}

	public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
			AuthenticationException exception, boolean accessLatch) throws IOException, ServletException
	{
		if (accessLatch)
			this.accessFailure(request, response, exception);

		super.onAuthenticationFailure(request, response, exception);
	}

	public int getIpLoginLatchRemain(HttpServletRequest request)
	{
		return this.ipLoginLatch.remain(request);
	}

	public int getUsernameLoginLatchRemain(HttpServletRequest request)
	{
		return this.usernameLoginLatch.remain(getLoginUsername(request));
	}

	protected String getLoginUsername(HttpServletRequest request)
	{
		return request.getParameter(this.loginUsernameParam);
	}

	protected void accessFailure(HttpServletRequest request, HttpServletResponse response,
			AuthenticationException exception)
	{
		this.ipLoginLatch.access(request);

		String loginUsername = request.getParameter(this.loginUsernameParam);
		this.usernameLoginLatch.access(loginUsername);
	}
}
