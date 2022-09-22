# 查询host_evacuation 

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
GET /v1.0/host_evacuation 
```

### 请求正文

无。

## 响应

### 成功响应

成功状态码：200


## 示例

成功返回信息示例：

```json
{"records": [
  {"started_at": "2021-12-29T02:39:31", "finished_at": "2021-12-29T02:39:51", "hostname": "node03", "id": 1}]}
```

curl demo
```
curl -g -i -X GET http://node01:12307/v1.0/host_evacuation -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN"
```