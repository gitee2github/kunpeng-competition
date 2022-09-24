# 创建ha_host记录

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
POST /v1.0/host_ha
```

### 请求正文
```json
{
	"hostname": "hostname1",
	"host_ha_enabled": 1,
	"vm_ha_enabled": 1,
	"ipmi_ip": "ipmi_ip2",
	"ipmi_password": "ipmi_password1",
	"ipmi_user": "ipmi_user1"
}
```

## 响应

### 成功响应

成功状态码：202


## 示例



curl demo
```
curl -g -i -X POST http://controller01:12306/v1.0/host_ha -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN" -d '
{
	"hostname": "hostname1",
	"host_ha_enabled": 1,
	"vm_ha_enabled": 1,
	"ipmi_ip": "ipmi_ip2",
	"ipmi_password": "ipmi_password1",
	"ipmi_user": "ipmi_user2"
}'
```