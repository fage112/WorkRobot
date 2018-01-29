# WorkShow
一个由python编写的自动化运维程序，依赖paramiko库，通过ssh协议来连接linux,unix服务器批量执行命令，
支持通过sftp协议批量上传和下载文件

使用方法
程序使用前需要先配置配置文件WorkShow.conf,配置文件的格式为
[服务器组]
hostname=host===port===user===password===UseKey
hostname:主机名
host:	 ip地址
port:	 端口
user：	 账号
password：密码
UseKey：  使用秘钥
运行程序后需要选择命令模式；
命令模式有三种：
1、upload,上传文件模式
2、download,文件下载模式
3、config，配置程序需要控制的机器清单
4、exit,退出程序