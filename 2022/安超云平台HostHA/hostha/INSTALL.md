## 计算节点高可用项目

### 制作包

```shell
bash build-rpm.sh 

```

### 安装

```shell
yum localinstall hostha-0.0.1.dev1-1.el7.noarch.rpm 

# 安装pip 后安装consul
pip install python-consul==0.7.2
yum -y install fping
```

### 配置

#### 注册服务
```shell
openstack user create --domain Default --password PASSWORD cloudultra
openstack role add --project service --user cloudultra admin
openstack service create --name cloudultra cloudultra

openstack endpoint create --region RegionOne cloudultra public http://10.10.10.10:13306/v1.0
openstack endpoint create --region RegionOne cloudultra internal http://10.10.10.10:13306/v1.0
openstack endpoint create --region RegionOne cloudultra admin http://10.10.10.10:13306/v1.0
```

#### 创建数据库
```sql
CREATE DATABASE hostha;
GRANT ALL PRIVILEGES ON hostha.* TO 'hostha'@'localhost' \
    IDENTIFIED BY 'PASSWORD';
GRANT ALL PRIVILEGES ON hostha.* TO 'hostha'@'%' \
    IDENTIFIED BY 'PASSWORD';
```
#### 调整配置
/etc/hostha/hostha.conf
```ini
[database]
connection = mysql+pymysql://hostha:PASSWORD@10.0.51.171/hostha

```
#### 初始化表结构
```shell
hostha-db-manage --config-file /etc/hostha/hostha.conf upgrade head
```

### 配置consul服务

#### 获取consul
```shell
wget https://releases.hashicorp.com/consul/0.9.2/consul_0.9.2_linux_amd64.zip
unzip consul_0.9.2_linux_amd64.zip
mv consul /usr/bin/
```

#### 配置service文件
```shell
cat << EOF > /usr/lib/systemd/system/consul.service
[Unit]
Description=consul service
After=syslog.target network.target
[Service]
Type=simple
PIDFile=/tmp/consuldaemon
ExecStart=/usr/bin/consuldaemon start
ExecReload=/usr/bin/consuldaemon restart
ExecStop=/usr/bin/consuldaemon stop
[Install]
WantedBy=multi-user.target
EOF
```

#### 配置脚本
/usr/bin/consuldaemon 内容如下
```shell
#!/bin/bash

#!/bin/bash

function fence() {
    echo $(date "+%Y-%m-%d %H:%M:%S")" Fence host, try fence the node" >> /var/log/consul/consul.log
    systemctl stop openstack-nova-compute.service
    #systemctl disable openstack-nova-compute.service
    shutdown now
}

# Check all interfaces arp list and ping one by one, if all interface
# are not reachable, then should be error
function checknetwork() {
    workable=0
    i=0
    Error=""
    AddrsPort=($(getAddrs))
    for v in ${AddrsPort[@]}
    do
        dat=$(date "+%Y-%m-%d %H:%M:%S")
        ipaddr=$(echo $v | awk -F":" '{print $1}')
        ifname=$(ip addr | grep $ipaddr | awk -F" " '{print $7}')
        if [ "$ifname" = "" ];then
            Error=$Error$dat" can't get the ifname if "$ipaddr";"
            continue
        fi
        Linkstatus=$(ethtool $ifname | xargs echo | sed 's/.*Link detected: \(no\|yes\).*/\1/g')
        if [ "$Linkstatus" = "no" ];then
            Error=$Error$dat" Link of Interface "$ifname" is DOWN;"
            continue
        fi
        localippool=$(arp -n -i $ifname |  grep "ether" | awk -F" " '{print $1}')
        if [ "$localippool" = "" ];then
            Error=$Error$dat" arp list of Interface "$ifname" is empty;"
            continue
        fi
        aliveNumber=$(fping $localippool -I $ifname | grep "is alive" | wc -l)
        if [ "$aliveNumber" = "" ];then
            Error=$Error$dat" no reachable host get for Interface "$ifname";"
            continue
        else
            workable=$(expr  $workable + 1)
        fi
    done

    echo $workable";"$Error
}

function getAgentMode() {
    info=`consul info -http-addr=$1`
    echo $(echo $info | sed 's/.*server = \(.*\) runtime:.*/\1/g')
}

function getServers() {
    # if the client is down, the servers will be -10, other two clients 3 + 3 =6, 6+(-10) <0
    # in this situation, will not fence the host
    servers=-10
    info=`consul info -http-addr=$1`
    is_server=$(echo $info | sed 's/.*server = \(.*\) runtime:.*/\1/g')
    if [ "$is_server" = "false" ];then
        servers=$(echo $info | sed 's/.*known_servers = \([0-9]\) server.*/\1/g')
    fi
    echo $servers
}

function getAddrs() {
    declare -a addrs
    if [ -e $configPatch_m ];then
        addr_m=$(cat /etc/consul.d/management | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        addrs[0]=$addr_m
    fi
    if [ -e $configPatch_t ];then
        addr_t=$(cat /etc/consul.d/tenant | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        addrs[1]=$addr_t
    fi

    if [ -e $configPatch_s ];then
        addr_s=$(cat /etc/consul.d/storage | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        addrs[2]=$addr_s
    fi

    echo ${addrs[*]}
}

# like [httpaddr:port,retry-jion], [192.168.20.51:8700,192.168.20.52 192.168.20.53:8700,192.168.20.52]
function getJoinAddrs() {
    declare -a addrs
    if [ -e $configPatch_m ];then
        addr_m=$(cat /etc/consul.d/management | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        retryJoin_m=$(cat /etc/consul.d/management | awk -F'\"retry_join\":' '{print $2}' | sed -e '/^$/d' | xargs echo | sed 's/\[\|\]//g')
        addrs[0]=$addr_m,$retryJoin_m
    fi
    if [ -e $configPatch_t ];then
        addr_t=$(cat /etc/consul.d/tenant | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        retryJoin_t=$(cat /etc/consul.d/tenant | awk -F'\"retry_join\":' '{print $2}' | sed -e '/^$/d' | xargs echo | sed 's/\[\|\]//g')
        addrs[1]=$addr_t,$retryJoin_t
    fi

    if [ -e $configPatch_s ];then
        addr_s=$(cat /etc/consul.d/storage | awk -F'\"http\":' '{print $2}' | sed -e '/^$/d' | sed 's/\"//g' | sed 's/,//g' | xargs echo | sed 's/ /:/g')
        retryJoin_s=$(cat /etc/consul.d/storage | awk -F'\"retry_join\":' '{print $2}' | sed -e '/^$/d' | xargs echo | sed 's/\[\|\]//g')
        addrs[2]=$addr_s,$retryJoin_s
    fi

    echo ${addrs[*]}
}

function consulLeave() {
    leave=`consul leave -http-addr=$1`
}

function consulJoin() {
    httpaddr=$(echo $1 | awk -F',' '{print $1}')
    joinaddr=$(echo $1 | awk -F',' '{print $2}')
    Join=`consul Join -http-addr=$httpaddr $joinaddr`
}

tenantCmd='consul agent -config-dir /etc/consul.d/tenant >/dev/null 2>&1 &'
storageCmd=$(echo $tenantCmd | sed 's/tenant/storage/g')
managementCmd=$(echo $tenantCmd | sed 's/tenant/management/g')

configPatch_s="/etc/consul.d/storage"
configPatch_t="/etc/consul.d/tenant"
configPatch_m="/etc/consul.d/management"

process_s='ps aux | grep -w consul | grep storage | grep -v grep | wc -l'
process_t=$(echo $process_s | sed 's/storage/tenant/g')
process_m=$(echo $process_s | sed 's/storage/management/g')

# 2 initial value
# 1 online
# 0 offline
online_s=2
online_t=2
online_m=2

function checkAlive() {
if [ -e $configPatch_s ];then
    if [ $(eval $process_s) = 0 ];then
        if [ "$online_s" != "0" ];then
            echo $(date "+%Y-%m-%d %H:%M:%S")" storage consul is offline" >> /var/log/consul/storage.log
            online_s=0
        fi
        eval $storageCmd
        sleep 0.5
    else
        # only online from offline need log
        if [ "$online_s" != "1" ];then
            echo $(date "+%Y-%m-%d %H:%M:%S")" storage consul is online" >> /var/log/consul/storage.log
            online_s=1
        fi
    fi
fi

if [ -e $configPatch_t ];then
    if [ $(eval $process_t) = 0 ];then
        if [ "$online_t" != "0" ];then
            online_t=0
            echo $(date "+%Y-%m-%d %H:%M:%S")" tenant consul is offline" >>/var/log/consul/tenant.log
        fi
        eval $tenantCmd
        sleep 0.5
    else
        # only online from offline need log
        if [ "$online_t" != "1" ];then
            echo  $(date "+%Y-%m-%d %H:%M:%S")" tenant consul is online" >>/var/log/consul/tenant.log
            online_t=1
        fi
    fi
fi

if [ -e $configPatch_m ];then
    if [ $(eval $process_m) = 0 ];then
        if [ "$online_m" != "0" ];then
            online_m=0
            echo $(date "+%Y-%m-%d %H:%M:%S")" management consul is offline" >>/var/log/consul/management.log
        fi
        eval $managementCmd
        sleep 0.5
    else
        # only online from offline need log
        if [ "$online_m" != "1" ];then
            echo $(date "+%Y-%m-%d %H:%M:%S")" management consul is online" >>/var/log/consul/management.log
            online_m=1
        fi
    fi
fi

}

function getPID() {
    # maybe execute for multiple times, so wen get the list
    if [ -e "/var/log/consul/consuldaemonpid" ];then
        PID=$(cat /var/log/consul/consuldaemonpid)
        # double check if the system has the PID
        PID_SYS=$(ps aux | grep 'consuldaemon start' | grep -v grep | awk -F' ' '{print $2}')
        if [ "$PID" = "$PID_SYS" ];then
            echo $PID
        else
            removePID
            echo ""
        fi
    else
        echo ""
    fi
}

function removePID() {
    $(rm -rf /var/log/consul/consuldaemonpid)
}

function writePID() {
    $(echo $$ > /var/log/consul/consuldaemonpid)
}

consulAddrs=($(getAddrs))

function consulStop() {
    if [ $(eval $process_m) = 1 ];then
        $(consulLeave ${consulAddrs[0]})
         echo $(date "+%Y-%m-%d %H:%M:%S")" management consul is leave" >>/var/log/consul/management.log
    fi

    if [ $(eval $process_t) = 1 ];then
        $(consulLeave ${consulAddrs[1]})
        echo $(date "+%Y-%m-%d %H:%M:%S")" tenant consul is leave" >>/var/log/consul/tenant.log
    fi

    if [ $(eval $process_s) = 1 ];then
        $(consulLeave ${consulAddrs[2]})
        echo $(date "+%Y-%m-%d %H:%M:%S")" storage consul is leave" >> /var/log/consul/storage.log
    fi
}

function consulKillStop() {
    process_s="ps aux | grep -w consul | grep storage | grep -v grep | awk -F' ' '{print \$2}'"
    process_t=$(echo $process_s | sed 's/storage/tenant/g')
    process_m=$(echo $process_s | sed 's/storage/management/g')

    kill -9 $(eval $process_s) $(eval $process_t) $(eval $process_m)
}


# SIGNAL process
#trap "consulStop;exit" 2 20
trap "exit" 2 20

function startDaemon() {
    PID=$(getPID)
    if [ "$PID" != "" ];then
        echo "deamon already running with PID: "$PID
        exit 0
    fi

    # check all network down times to ignor the wrong action for fence
    networkfailedtimes=0

    while true;do
        PID=$(getPID)
        if [ "$PID" = "" ];then
            writePID
        fi

        checkAlive

        aliveServers=0
        for v in ${consulAddrs[@]}
        do
            if [ "$(getAgentMode $v)" = "true" ];then
                break
            fi
            aliveServers=$(expr  $aliveServers + $(getServers $v))
        done
        # all known servers are 0, then should fence internally for client mode
        # since any client error will mark it's aliveServers= -10, so we will never fence this host. 
        if [ "$aliveServers" = "0" ];then
            if [ "$InitServers" != "0" ];then
                echo $(date "+%Y-%m-%d %H:%M:%S")" All servers are lost connection, try check network connecting" >> /var/log/consul/consul.log
                result=$(checknetwork)
                workline=$(echo $result | awk -F";" '{print $1}')
                echo $result | awk -F";" 'BEGIN{i=2} {while(i<NF){print $i;i++} }' >> /var/log/consul/consul.log
                #echo "Fence needed"
                if [ "$workline" = "0" ];then
                    # 2 * sleep(5s) = 10s, max is 15s
                    if [ "$networkfailedtimes" == "1" ];then
                        echo $(date "+%Y-%m-%d %H:%M:%S")" networkfailedtimes = "$networkfailedtimes" Now try to fence internal" >> /var/log/consul/consul.log
                        fence
                    else
                        echo $(date "+%Y-%m-%d %H:%M:%S")" networkfailedtimes = "$networkfailedtimes" less than 1, will plus 1 and recheck" >> /var/log/consul/consul.log
                        networkfailedtimes=$(expr $networkfailedtimes + 1)
                    fi
                else
                    networkfailedtimes=0
                    # here we need try rejoin the cluster, since servers may recovery
                    echo $(date "+%Y-%m-%d %H:%M:%S")" try rejoin to servers" >> /var/log/consul/consul.log
                    joinaddrs=($(getJoinAddrs))
                    for j in ${joinaddrs[@]}
                    do
                        consulJoin $j
                    done
                fi
            fi
        elif [ "$InitServers" = "0" ];then
            if [ "$aliveServers" -gt "0" ];then
                InitServers=$aliveServers
            fi
        fi
        #echo "do not need fence, servers:"$aliveServers" InitServers:"$InitServers
        sleep 5
    done
}

function term() {
    PID=$(getPID)
    if [ "$PID" != "" ];then
        kill -n 20 $PID
        removePID
    fi
}

# Indicate that if the service at the start time, we do not connected any servers, never fence
InitServers=0
if [ ! -d "/var/log/consul" ];then
    mkdir /var/log/consul
fi

if [ "$#" = "1" ];then
    if [ $1 = "start" ]
    then
        startDaemon
    elif [ $1 = "stop" ]
    then
        term
        sleep 1
        consulKillStop
        exit 0
    elif [ $1 = "restart" ]
    then
        term
        sleep 1
        consulStop
        sleep 1
        startDaemon
    elif [ $1 = "leave" ]
    then
        term
        sleep 1
        consulStop
        exit 0
    fi
else
    echo "must give the params like start/stop/restart"
fi


```

/usr/bin/fence 内容如下
```shell
#!/bin/bash

parse_payload(){
#value=`echo $1 | sed 's/.*Payload:\(.*\),NodeFilter.*/\1/'`
value=`echo $1 | awk -F"\",\"" '{print $3}' | awk -F"\":\"" '{print $2}'`
echo $value
}

read message

if [ "$message" = "[]" ]; then
    exit 0
fi

echo $(date "+%Y-%m-%d %H:%M:%S")" received message: "$message >> /var/log/consul.log

payload=$(parse_payload $message)

de_payload=$(echo $payload | base64 --decode)
echo $(date "+%Y-%m-%d %H:%M:%S")" message payload: "$de_payload >> /var/log/consul.log

# de_payload should be the format as:
#   fence@serverhostname@timestamp

cmd=$(echo $de_payload | awk -F'@' '{print $1}')
timestamp=$(echo $de_payload | awk -F'@' '{print $3}')
timenow=$(date +%s)
timegap=$(expr $timenow - $timestamp)
node=`echo $message | awk -F'"NodeFilter":' '{print $2}' |awk -F'"' '{print $2}'`
hostname=`hostname`

# only the time gap less then 120 seconds we assume that it is valid
if [ "$timegap" -lt 120 ]; then
  if [ "$hostname" = "$node" ];  then
    if [ "$cmd" = "fence" ]; then
        echo $(date "+%Y-%m-%d %H:%M:%S")" received the fence event, try fence the node" >> /var/log/consul.log
        systemctl stop openstack-nova-compute.service
        #systemctl disable openstack-nova-compute.service
        shutdown now
    elif [ "$cmd" = "enable-nova" ]; then
        systemctl enable openstack-nova-compute.service
        systemctl start openstack-nova-compute.service
    fi
  else
    echo node is $node, ignore >> /var/log/consul.log
  fi
else
    echo $(date "+%Y-%m-%d %H:%M:%S")" received the fence event, but the timegap is "$timegap", exceed the 120s, ignor the event" >> /var/log/consul.log
fi

```

```shell
chmod +x /usr/bin/consuldaemon
chmod +x /usr/bin/fence

```


#### 配置监控网络
```shell
mkdir /etc/consul.d/
mkdir /var/log/consul/
```
管理网络 /etc/consul.d/management 内容如下
```json
{
    "bootstrap_expect": 3,
    "bind_addr": "37.47.10.10",
    "datacenter": "management",
    "data_dir": "/tmp/consul_m",
    "log_level": "INFO",
    "node_name": "node01",
    "server": true,
    "watches": [
        {
            "type": "event",
            "name": "fence",
            "handler": "/usr/bin/fence"
        }
    ],
    "addresses": {
        "rpc": "37.47.10.10",
        "https": "37.47.10.10",
        "dns": "37.47.10.10",
        "http": "37.47.10.10"
    },
    "ports": {
        "http": 8500,
        "rpc": 8400,
        "serf_lan": 8301,
        "serf_wan": 8302,
        "server": 8300
    },
    "enable_script_checks": false,
    "retry_join": ["37.47.10.10"]
}

```

存储网络 /etc/consul.d/storage 内容如下
```json
{
    "bootstrap_expect": 3,
    "bind_addr": "6.150.12.10",
    "datacenter": "storage",
    "data_dir": "/tmp/consul_storage",
    "log_level": "INFO",
    "node_name": "node01",
    "server": true,
    "watches": [
        {
            "type": "event",
            "name": "fence",
            "handler": "/usr/bin/fence"
        }
    ],
    "addresses": {
        "rpc": "6.150.12.10",
        "https": "6.150.12.10",
        "dns": "6.150.12.10",
        "http": "6.150.12.10"
    },
    "ports": {
        "http": 8500,
        "rpc": 8400,
        "serf_lan": 8301,
        "serf_wan": 8302,
        "server": 8300
    },
    "enable_script_checks": false,
    "retry_join": ["6.150.12.10"]
}

```


业务网络 /etc/consul.d/tenant 内容如下
```json
{
    "bootstrap_expect": 3,
    "bind_addr": "5.150.12.10",
    "datacenter": "tenant",
    "data_dir": "/tmp/consul_tenant",
    "log_level": "INFO",
    "node_name": "node01",
    "server": true,
    "watches": [
        {
            "type": "event",
            "name": "fence",
            "handler": "/usr/bin/fence"
        }
    ],
    "addresses": {
        "rpc": "5.150.12.10",
        "https": "5.150.12.10",
        "dns": "5.150.12.10",
        "http": "5.150.12.10"
    },
    "ports": {
        "http": 8500,
        "rpc": 8400,
        "serf_lan": 8301,
        "serf_wan": 8302,
        "server": 8300
    },
    "enable_script_checks": false,
    "retry_join": ["5.150.12.10"]
}

```

bootstrap_expect 为三节点（控制节点,默认3）

bind_addr 为当前控制节点配置文件对应管理网/存储网/租户网的IP地址 

node_name 当前控制节点的hostname 

addresses 为当前控制节点配置文件对应管理网/存储网/租户网的IP地址，与bind_addr一致 

retry_join 第一个控制节点管理网/存储网/租户网的IP地址

非server节点节点去掉 '"bootstrap_expect": 3 ', '"server": true'

#### 所有节点启动consul 并验证
```shell
systemctl enable consul
systemctl start consul

## 如下说明consul服务启动成功
[root@node01 ~]# consul members -http-addr=37.47.10.10:8500
Node    Address           Status  Type    Build  Protocol  DC
node01  37.47.10.10:8301  alive   server  0.9.2  2         management
node02  37.47.10.13:8301  alive   server  0.9.2  2         management
node03  37.47.10.16:8301  alive   server  0.9.2  2         management
node04  37.47.10.19:8301  alive   client  0.9.2  2         management
You have new mail in /var/spool/mail/root
[root@node01 ~]# consul members -http-addr=5.150.12.10:8500                                                                                                                                    
Node    Address           Status  Type    Build  Protocol  DC
node01  5.150.12.10:8301  alive   server  0.9.2  2         tenant
node02  5.150.12.13:8301  alive   server  0.9.2  2         tenant
node03  5.150.12.16:8301  alive   server  0.9.2  2         tenant
node04  5.150.12.19:8301  alive   client  0.9.2  2         tenant
[root@node01 ~]# consul members -http-addr=6.150.12.10:8500
Node    Address           Status  Type    Build  Protocol  DC
node01  6.150.12.10:8301  alive   server  0.9.2  2         storage
node02  6.150.12.13:8301  alive   server  0.9.2  2         storage
node03  6.150.12.16:8301  alive   server  0.9.2  2         storage
node04  6.150.12.19:8301  alive   client  0.9.2  2         storage


```


### hostha服务

#### 调整hostha配置
/etc/hostha/hostha.conf 
```ini
[DEFAULT]
use_stderr=0
debug=1
host = 0.0.0.0
port = 12307
region = regionOne
auth_strategy = keystone

[keystone_authtoken]
auth_version = v3
auth_type = password
auth_uri = http://37.47.10.206:6000/v3
auth_url = http://37.47.10.206:45357
identity_uri = http://37.47.10.206:45357/
user_domain_name = default
project_domain_name = default
project_name = service
username = cloudultra
password = cloudadmin@Passw0rd
memcached_servers = 37.47.10.206:12211

[database]
connection = mysql+pymysql://hostha:Passw0rd@37.47.10.206:3306/hostha

[oslo_messaging_notifications]
driver = messagingv2

[oslo_messaging_rabbit]
rabbit_userid = openstack
rabbit_password = openstack
rabbit_hosts = 37.47.10.206:5671


[compute_ha]
host_check_method = consul
# ['37.47.10.10', '5.150.12.10','6.150.12.10'] 为第一个server节点对应的管理 租户 存储网，与/etc/consul.d/下配置文件里ip对应
# ['37.47.10.13', '5.150.12.13', '6.150.12.13']为第二个server节点对应的管理
consul_servers=[['37.47.10.10', '5.150.12.10','6.150.12.10'],['37.47.10.13', '5.150.12.13', '6.150.12.13'],['37.47.10.16', '5.150.12.16', '6.150.12.19']]
consul_ports=[8500, 8500, 8500]  #对应的端口
host_check_interval=10
host_check_retry=3
multiple_recovery=true

```

#### 控制节点启动服务
```shell
systemctl enable hostha-hostha hostha-api
systemctl start hostha-hostha hostha-api
```

#### 验证api功能
##### 参考docs目录下api文档



#### 验证hostha功能
##### 录入节点信息
参考api
##### 断某一个节点的存储网络，预期 节点被关机，其上vm被疏散
##### 断某一个节点掉电，预期 节点上vm被疏散
##### 其他各种场景的验证 ...