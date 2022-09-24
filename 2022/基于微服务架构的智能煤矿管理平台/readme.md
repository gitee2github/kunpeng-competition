# Asp.Net用户登录认证示例

## 引用框架或类库

1. SpringCloud
2. Redis
3. easy-captcha—[GITHUB]([GitHub - pig-mesh/easy-captcha: https://github.com/whvcse/EasyCaptcha增强JAVA11](https://github.com/pig-mesh/easy-captcha))
4. hutool5.1
5. mybatis-spring-boot-starter2.1.4
6. mysql

## 说明

1. 开发数据库mysql
   
   rm-2vcy3wg9z88lf5ub9eo.mysql.cn-chengdu.rds.aliyuncs.com:3306
   
   只读权限用户
   
   username:commit_to_kunpeng
   
   password:kunpeng2022

2. Redis
   
   IP:112.74.34.69
   
   密码:Kribug@959999

3. ~~请使用DataStudio(OpenGauss官方提供客户端)或者gsql创建test数据库~~（直接提供开发环境数据库）

4. ~~请修改appsettings.json中的ConnectionStrings配置链接~~

5. ~~程序运行时不会自动创建用户表和用户数据，请打开项目目录中Scripts，依次执行 schema.sql,data.sql用来初始化用户表和用户数据（默认用户和密码均为test）~~

6. ~~可以在vs中运行本示例~~