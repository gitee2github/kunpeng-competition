# 查询vm_evacuation

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
GET /v1.0/vm_evacuation 
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
  {"vm_name": "vnname", "finished_at": "2021-12-29T02:39:51", "host_op_id": 1, "des_host": "node4", 
    "retry_count": 1, "vm_uuid": "uuid1", "result": 1, "origin_state": "1", "message": "succ", 
    "started_at": "2021-12-29T02:39:31", "id": 1, "src_host": "node03"}]}
```

curl demo
```
curl -g -i -X GET http://node01:12307/v1.0/vm_evacuation -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN"
```