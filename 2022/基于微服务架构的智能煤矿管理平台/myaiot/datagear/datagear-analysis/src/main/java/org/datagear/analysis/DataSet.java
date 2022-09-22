/*
 * Copyright 2018 datagear.tech
 *
 * Licensed under the LGPLv3 license:
 * http://www.gnu.org/licenses/lgpl-3.0.html
 */

package org.datagear.analysis;

import java.io.Serializable;
import java.util.List;

/**
 * 数据集。
 * 
 * @author datagear@163.com
 *
 */
public interface DataSet extends Identifiable, Serializable
{
	/**
	 * 获取名称。
	 * 
	 * @return
	 */
	String getName();

	/**
	 * 是否是易变模型。
	 * <p>
	 * 即{@linkplain #getResult(DataSetQuery)}返回数据的结构并不是固定不变、可由{@linkplain #getProperties()}描述的。
	 * </p>
	 * 
	 * @return
	 */
	boolean isMutableModel();

	/**
	 * 获取属性列表。
	 * <p>
	 * 属性列表描述{@linkplain #getResult(DataSetQuery)}返回的{@linkplain DataSetResult#getData()}的对象结构。
	 * </p>
	 * 
	 * @return 属性列表，返回空列表则表示无属性
	 */
	List<DataSetProperty> getProperties();

	/**
	 * 获取指定名称的属性，没有则返回{@code null}。
	 * 
	 * @param name
	 * @return
	 */
	DataSetProperty getProperty(String name);

	/**
	 * 获取参数列表。
	 * 
	 * @return 参数列表，返回空列表则表示无参数
	 */
	List<DataSetParam> getParams();

	/**
	 * 获取指定名称的参数，没有则返回{@code null}。
	 * 
	 * @param name
	 * @return
	 */
	DataSetParam getParam(String name);

	/**
	 * 获取{@linkplain DataSetResult}。
	 * <p>
	 * 如果{@linkplain #isMutableModel()}为{@code false}，那么返回结果中的数据项属性不应超出{@linkplain #getProperties()}的范围，
	 * 避免暴露底层数据源不期望暴露的数据；
	 * 如果{@linkplain #isMutableModel()}为{@code true}，则返回结果中的数据项属性不受{@linkplain #getProperties()}范围限制。
	 * </p>
	 * <p>
	 * 如果返回结果中的数据项属性在{@linkplain #getProperties()}中有对应，当数据项属性值为{@code null}时，应使用{@linkplain DataSetProperty#getDefaultValue()}的值。
	 * </p>
	 * <p>
	 * 返回结果中的数据项属性值应已转换为与{@linkplain #getProperties()}的{@linkplain DataSetProperty#getType()}类型一致。
	 * </p>
	 * 
	 * @param query
	 * @return
	 * @throws DataSetException
	 */
	DataSetResult getResult(DataSetQuery query) throws DataSetException;
}
