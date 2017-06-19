#!/bin/env python
#encoding: utf-8
#author: Lion
import  paramiko,threading,time
import configparser,re,copy,sys
config_file='WorkShow.conf'
SeverGroups=[]
ServerInfo={}
CMD_exec_fail_server=[]
ThreadPoolCounts=10
def read_config(choice,config_file=config_file,groups='all'):
    c=configparser.ConfigParser()
    title = ['host', 'port', 'user', 'password', 'usekey']
    try:
        c.read(config_file)
        if choice=='groups':
            global SeverGroups
            SeverGroups.clear()
            SeverGroups = c.sections()
        else:
            global ServerInfo
            ServerInfo.clear()
            if groups=='all':
                groups=SeverGroups
            else:
                groups=groups
            for i in groups:
                opts = c.options(i)
                for h in opts:
                    ServerInfo[h] = dict(zip(title, c.get(i, h).split('===')))
    except configparser.ParsingError as e:
        print("文件%s格式错误.\a\n\t" % (config_file))
class ssh_client():
    def __init__(self):
        self.ssh=paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.session=[]
        self.command_log={}
        self.error_log={}
    def concat_log(self,host,response,status):
        Datetime=time.strftime('%Y-%m-%d %H:%M:%S')
        msg="---------------------------------"+host+"--------------------------------"+\
            "\n"+response+"\n"+\
            "命令执行状态："+status+"\t\t执行命令失败主机总数："+str(len(CMD_exec_fail_server))+\
            "\t\t时间："+Datetime+"\n"+ \
            "---------------------------------" + host + "--------------------------------\n"
        return msg
    def command(self,host_info,CMD):
        session=self.ssh.connect(host_info['host'], int(host_info['port']),
                                 host_info['user'], host_info['password'])
        #self.session.append(session)
        stdin,stdout,stderr = self.ssh.exec_command(CMD)
        result = stdout.read()
        err_result=stderr.read()
        if result and not err_result:
            response=result.decode()
            self.command_log[host_info['host']]=response
            print(self.concat_log(host_info['host'],response, '成功'))
        else:
            CMD_exec_fail_server.append(host_info['host'])
            response = err_result.decode()
            print(response)
            self.command_log[host_info['host']] = response
            print(self.concat_log(host_info['host'],response,'失败'))
        #self.session.clear()
        self.ssh.close()
    def sftp(self,host_info,local_path,remote_path,method):
        transport=paramiko.Transport((host_info['host'], int(host_info['port'])))
        transport.connect(username=host_info['user'],password=host_info['password'])
        Sftp=paramiko.SFTPClient.from_transport(transport)
        try:
            if method=='upload':
                print('%s starting uploading...' %(host_info['host']))
                Sftp.put(local_path,remote_path)
            elif method=='download':
                print('%s starting downloading...' %(host_info['host']))
                local_path=local_path+'_'+host_info['host']
                Sftp.get(remote_path,local_path)
            else:
                print(method+' option is a unknow argument')
                raise EOFError
        except Exception as e:
            print(e)
if __name__=='__main__':
    read_config('groups')
    read_config('serverinfo')
    while True:
        Cmd=input('WorkShow#').strip(' ')
        start = time.clock()
        ThreadPool = []
        if Cmd=='':
            continue
        elif Cmd=='upload':
            Local_file_Path=input('input the local file path:')
            Remote_Path=input('input the remote host file path:')
            start = time.clock()
            for i in ServerInfo:
                t = threading.Thread(target=a.sftp, args=(ServerInfo[i],Local_file_Path,Remote_Path,'upload'))
                t.start()
                ThreadPool.append(t)
            for T in ThreadPool:
                T.join()
                # print(str(a.command_log))
            end = time.clock()
            print("程序运行用时：%s" % (end - start))
        elif Cmd=='download':
            Local_file_Path=input('input the local file path:')
            Remote_Path=input('input the remote host file path:')
            start = time.clock()
            for i in ServerInfo:
                t = threading.Thread(target=a.sftp, args=(ServerInfo[i],Local_file_Path,Remote_Path,'download'))
                t.start()
                ThreadPool.append(t)
            for T in ThreadPool:
                T.join()
            end = time.clock()
            print("程序运行用时：%s" % (end - start))
        elif Cmd == 'exit':
            sys.exit()
        elif Cmd=='config':
            print('''selg {grounps}\t\t\t\t选择分组\nselser {servers}\t\t\t选择指定服务器\nshow selected\t\t\t\t显示已选择的服务器\nshow all\t\t\t\t显示所有服务器\nexit\t\t\t\t\t退出配置模式\nshow failed\t\t\t\t显示失败的服务器''')
            while True:
                Selection=input('config:')
                if re.search("^ *[Ee][Xx][Ii][Tt] *$", Selection):
                    break
                elif re.search("^ *[sS][Ee][Ll][Gg].*$", Selection):
                    print(Selection)
                    T_grounps=Selection.split(' ')
                    T_grounps=T_grounps[1].split(',')
                    read_config(T_grounps)
                    Servers=[]
                    for s in ServerInfo.keys():
                        Servers.append(s)
                    print(ServerInfo)
                elif re.search("^ *[sS][Ee][Ll][Ss][Ee][Rr].*$", Selection):
                    print('start select server')
                    T_servers = Selection.split(' ')
                    T_servers = T_servers[1].split(',')
                    read_config('groups')
                    read_config('serverinfo')
                    Tmp_data=copy.deepcopy(ServerInfo)
                    for server in Tmp_data.keys():
                        if server not in T_servers:
                            ServerInfo.pop(server)
                    Servers = []
                    for s in ServerInfo.keys():
                        Servers.append(s)
                    print(Servers)
                elif re.search("^ *[sS][Hh][Oo][Ww] *[Aa][Ll][Ll] *$", Selection):
                    print('show all server')
                    Tmp_ServerInfo=copy.deepcopy(ServerInfo)
                    read_config('groups')
                    read_config('serverinfo')
                    print(str(SeverGroups)+'\n'+str(ServerInfo))
                    ServerInfo=Tmp_ServerInfo
                elif re.search("^ *[sS][Hh][Oo][Ww] *[Ss][Ee][Ll].*$", Selection):
                    print('show selected')
                    print(ServerInfo)
                elif re.search("^ *[sS][Hh][Oo][Ww] *[Ff][Aa][Ii][Ll][Ee][Dd].*$", Selection):
                    print('show failed')
                    print(CMD_exec_fail_server)
        else:
            CMD_exec_fail_server.clear()
            for i in ServerInfo:
                a = ssh_client()
                t=threading.Thread(target=a.command,args=(ServerInfo[i],Cmd))
                t.start()
                ThreadPool.append(t)
            for T in ThreadPool:
                T.join()
        end = time.clock()
        print("程序运行用时：%s" % (end - start))
