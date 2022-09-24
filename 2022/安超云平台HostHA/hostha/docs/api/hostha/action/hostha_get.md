# 查询hahost配置

该操作要求客户端具备管理员权限。

## 请求

### 请求方式

```
GET /v1.0/host_ha
```

### 请求正文

无。

## 响应

### 成功响应

成功状态码：200

成功返回数据：

| Field         | Type         | Null | Key | Default | Extra          |   说明   |
|---------------|--------------|------|-----|---------|----------------|----------|
| id            | int(11)      | NO   | PRI | NULL    | auto_increment |          |
| hostname      | varchar(255) | NO   |     | NULL    |                |  主机名  |
| task         | varchar(255)  | YES  |     | NULL    |                |  任务情况|
| host_ha_enabled| int(11)     | YES  |     | NULL    |                | 启用物理机ha|
| vm_ha_enabled | int(11)      | YES  |     | NULL    |                | 启用此物理机上vm ha|
| mgmt_ip       | varchar(255) | YES  |     | NULL    |                | 管理ip地址|
| store_ip      | varchar(255) | YES  |     | NULL    |                | 存储ip地址|
| ipmi_ip       | varchar(255) | YES  |     | NULL    |                | ipmi管理ip|
| ipmi_user     | varchar(255) | YES  |     | NULL    |                | ipmi用户 |
| ipmi_password | varchar(255) | YES  |     | NULL    |                | ipmi密码 |

host_ha_enabled vm_ha_enabled ：1启用 0禁用

### 失败响应

失败状态码：

* 404：资源未找到
* 401：没有权限
* 500：内部错误
* 503：服务不可用

## 示例

成功返回信息示例：

```json
{"hosts": [
        {"vm_ha_enabled": 1, "ipmi_user": null, "task": null, "mgmt_ip": "172.16.28.168", "store_ip": "172.16.28.168",
         "hostname": "controller", "host_ha_enabled": 0, "ipmi_ip": null, "ipmi_password": null, "id": 4},
        {"vm_ha_enabled": 1, "ipmi_user": null, "task": "", "mgmt_ip": "172.16.28.152", "store_ip": "172.16.28.152",
         "hostname": "compute", "host_ha_enabled": 0, "ipmi_ip": null, "ipmi_password": null, "id": 7}]}
```

curl demo
```
 
```