# 更新cloudultra配置

## 请求

### 请求方法

```
PATCH /v1.0/configuration
```

### 请求正文

已有配置项说明

在请求正文中可以指定以下参数：

| id | group | name       | value |    说明     |
|----|------------|----------------|-----------|-------------|
|  1 | host_ha | check_interval           | 20        | 物理机ha检查间隔|
|  2 | host_ha | check_retry              | 4         | 每次检查重试|


更新参数
group 组名  string
name 配置名 string
value 值   string


## 响应

### 成功响应

成功状态码：202

成功返回数据：无

### 失败响应

失败状态码：

* 400：非法的正文数据
* 401：没有权限
* 404：资源未找到
* 500：内部错误
* 503：服务不可用

## 示例

请求提交正文数据示例：

curl demo
```
curl -g -i -X PATCH http://controller:12306/v1.0/configuration -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN" -d '{"group": "host_ha","name": "recovery_enabled","value": "0"}'
```
