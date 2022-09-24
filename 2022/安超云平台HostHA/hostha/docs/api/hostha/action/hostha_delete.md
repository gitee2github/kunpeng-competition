# 删除ha_host记录

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
DELETE /v1.0/host_ha/{hostname}
```

### 请求正文

## 响应

### 成功响应

成功状态码：204

## 示例

curl demo
```
curl -g -i -X DELETE http://controller01:12306/v1.0/host_ha/hostname1 -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN"
```