# 更新host配置

## 请求

### 请求方法

```
PATCH /v1.0/host_ha
```

### 请求正文

在请求正文中可以指定以下参数：
| Field         | Type         | Null | Key | Default | Extra          |   说明   |
|---------------|--------------|------|-----|---------|----------------|----------|
| id            | int(11)      | NO   | PRI | NULL    | auto_increment |          |
| hostname      | varchar(255) | NO   |     | NULL    |                |  主机名  |
| task         | varchar(255)  | YES  |     | NULL    |                |  任务情况|
| host_ha_enabled| int(11)     | YES  |     | NULL    |                | 启用物理机ha|
| ipmi_ip       | varchar(255) | YES  |     | NULL    |                | ipmi管理ip|
| ipmi_user     | varchar(255) | YES  |     | NULL    |                | ipmi用户 |
| ipmi_password | varchar(255) | YES  |     | NULL    |                | ipmi密码 |

host_ha_enabled vm_ha_enabled ：1启用 0禁用


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
curl -g -i -X PATCH http://controller:12306/v1.0/host_ha -H "Content-Type: application/json" -H "Accept: application/json" -H "X-Auth-Token: $TOKEN" -d '{"hostname":"controller", "host_ha_enabled": 1}'
```
