# 查询cloudultra配置

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
GET /v1.0/configuration
```

### 请求正文

无。

## 响应

### 成功响应

成功状态码：200

成功返回数据：

| id | name | name       | value |    说明     |
|----|------------|----------------|-----------|-------------|
|  1 | host_ha | check_interval    | 20        | 物理机ha检查间隔|
|  2 | host_ha | check_retry       | 4         | 每次检查重试|


### 失败响应

失败状态码：

* 404：资源未找到
* 401：没有权限
* 500：内部错误
* 503：服务不可用

## 示例

成功返回信息示例：

```json
{"configurations": [
  {"group": "host_ha", "name": "check_interval", "value": "5", "id": 1},
  {"group": "host_ha", "name": "check_retry", "value": "3", "id": 4}]
}
```
curl 请求demo
```
curl -g -i -X GET http://controller:12306/v1.0/configuration -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN"
```