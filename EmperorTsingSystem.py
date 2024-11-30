import json, os, hashlib, base64

class EmperorTsingSystem:
    '''秦始皇系统的主要逻辑'''
    
    def __init__(self,path):
        '''初始化资源'''
        
        self.info=[None,None,None]
        self.path=path
        self.logged=False
    
    
    def _read_data(self):
        '''读取文件数据'''
        
        with open(self.path,"r",encoding="utf-8") as f:
            return json.load(f)
    
    
    def _check_pwd(self,index,pwd,data):
        '''检查密码'''
        
        encoded_salt=data[3][index]
        encoded_pwd=data[1][index]
        
        salt=base64.b64decode(encoded_salt)
        stored_pwd=base64.b64decode(encoded_pwd)
    
        
        hashed_pwd=hashlib.scrypt(pwd.encode("utf-8"),salt=salt,n=16384,r=8,p=1,dklen=64)
        
        return stored_pwd==hashed_pwd
    
    
    def _create_pwd(self,pwd):
        '''为新用户处理密码'''
        
        salt=os.urandom(16)
        hashed_pwd=hashlib.scrypt(pwd.encode("utf-8"),salt=salt,n=16384,r=8,p=1,dklen=64)
        
        encoded_pwd=base64.b64encode(hashed_pwd).decode("utf-8")
        encoded_salt=base64.b64encode(salt).decode("utf-8")
    
        
        return [encoded_pwd,encoded_salt]
    
    
    def log_out(self):
        '''登出'''
        
        self.info=[None,None,None]
        self.logged=False
        
        print("期待您的下次使用！")
        
        return True
    
    
    def _create_user(self,info,data):
        '''创建新用户'''
        
        data[0].append(info[2])
        data[1].append(info[0])
        data[2].append(0)
        data[3].append(info[1])
        data[4].append(True)
        
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(data,f)
        
        return True
    
    
    def log_in(self,name,pwd):
        '''用户登录'''
        
        data=self._read_data()
        
        if name not in data[0] or len(pwd) < 8 or len(pwd) > 64:
            print("用户名或密码错误！")
            return False
        
        index=data[0].index(name)
        
        if self._check_pwd(index,pwd,data):
            self.info[0]=name
            self.info[1]=data[2][index]
            self.info[2]=index
            self.logged=True
            
            print(f"欢迎，{self.info[0]}！")
            
            return True
        else:
            print("用户名或密码错误！")
            return False
    
    
    def register_in(self,name,pwd1,pwd2):
        '''用户注册'''
        
        data=self._read_data()
        
        if any(name==n.lower() for n in data[0]):
            print("用户名已被占用！")
            return False
        if pwd1!=pwd2:
            print("两次输入的密码不一致！")
            return False
        if len(pwd1)>64 or len(pwd1)<8:
            print("密码的长度应在8-64位之间！")
            return False
        info=self._create_pwd(pwd1)
        info.append(name)
        self._create_user(info,data)
        print("注册成功！")
        return True
    
    
    def change_pwd(self,pwd,pwd1,pwd2):
        '''改密码'''
        
        data=self._read_data()
        
        if not self._check_pwd(self.info[2],pwd,data):
            print("密码错误！")
            return False
        if pwd1!=pwd2:
            print("两次输入的密码不一致！")
            return False
        if len(pwd1) < 8 or len(pwd1) > 64:
            print("密码的长度应在8-64位之间！")
            return False
        
        new=self._create_pwd(pwd1)
        data[1][self.info[2]]=new[0]
        data[3][self.info[2]]=new[1]
        
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(data,f)
        
        self.log_out()
        
        print("密码更改成功！正在退出登录……")
        
        return True
    
    
    def about_me(self,index=None):
        '''打印账户信息'''
        
        data=self._read_data()
        
        if index==None:
            index=self.info[2]
        
        op=["用户","管理员","超级管理员"]
        
        print(f"用户名：{data[0][index]}")
        print(f"职位：秦始皇({op[data[2][index]]})")
        print(f"UID:{index+100_000_000}")
        
        return True
    
    
    def all_users(self,all_user=False):
        '''打印所有用户名'''
        
        data=self._read_data()
        
        if all_user:
            s=0
        else:
            s=1
        
        print("所有用户名如下：")
        for i in range(s,len(data[0])):
            if all_user==False and data[4][i]==False:
                continue
            print(data[0][i],end=" , ")
        print("")
        
        return True
    
    
    def delete(self,pwd="",index=None,op=False):
        '''删除用户'''
        
        data=self._read_data()
        
        if index==None:
            index=self.info[2]
        
        if not op:
            if not self._check_pwd(index,pwd,data):
                print("密码错误！正在退出删除界面……")
                return False
        
        check=input(f"是否删除账户 {data[0][index]} ？该操作不可逆！(Yes/No)\n（删除账户不会解除用户名的占用）\n")
        if check != "Yes":
            print("正在退出删除界面……")
            return False
        
        data[1][index]=""
        data[3][index]=""
        data[4][index]=False
        
        with open(self.path,"w",encoding="utf-8") as f:
            json.dump(data,f)
        
        if self.info[2]==index:
            self.log_out()
        
        print("删除成功！")
        
        return True
    
    
    def op(self,index,op):
        '''更改用户权限'''
        
        op_list=["用户","管理员","超级管理员"]
        
        data=self._read_data()
        
        check=input(f"是否要将用户 {data[0][index]} 的权限更改为 {op_list[op]} ？(y/n)\n")
        
        if check.lower() == "y":
            data[2][index]=op
            with open(self.path,"w",encoding="utf-8") as f:
                json.dump(data,f)
            print("更改成功！")
            return True
        else:
            print("取消更改中……")
            return False



class GracefulCMD:
    '''使用命令行操作秦始皇系统'''
    
    def __init__(self,path):
        '''初始化资源'''
        
        self.ETS=EmperorTsingSystem(path)
        self.greet()
    
    
    def greet(self):
        print("\033[H\033[J",end="")
        print("欢迎来到秦始皇系统\n")
    
    def inputCMD(self):
        '''输入命令并将命令分割为列表'''
        
        self.cmd=[]
        
        cmd=input("$ ")
        
        self.cmd=cmd.split()
        
        return True
    
    
    def _check_len(self,length):
        if len(self.cmd)<length:
            print("错误：命令参数不足！")
            return True
        elif len(self.cmd)>length:
            print(f"错误：意外的 {self.cmd[length]} 出现在了命令中")
            return True
        else:
            return False
    
    
    def run(self):
        '''判断命令含义'''
        
        if self.cmd==[]:
            return True
        
        debug=-1
        
        if self.ETS.logged:
            if self.cmd[0]=="me":
                if self.ETS.info[1]==0:
                    if len(self.cmd)>1:
                        debug=1
                    else:
                        self.ETS.about_me()
                else:
                    try:
                        if len(self.cmd)==1:
                            self.ETS.about_me()
                        elif len(self.cmd)>2:
                            debug=2
                        elif (self.ETS.info[1]==1 and int(self.cmd[1])==0) or int(self.cmd[1])<0:
                            raise IndexError
                        else:
                            self.ETS.about_me(int(self.cmd[1]))
                    except ValueError:
                        debug=1
                    except IndexError:
                        print(f'错误：未知的用户索引 "{self.cmd[1]}"')
            elif self.cmd[0]=="pwd":
                if self._check_len(4):
                    pass
                else:
                    self.ETS.change_pwd(self.cmd[1],self.cmd[2],self.cmd[3])
            elif self.cmd[0]=="user":
                if self.ETS.info[1]==0:
                    debug=0
                elif self.ETS.info[1]==1:
                    if len(self.cmd)>1:
                        debug=1
                    else:
                        self.ETS.all_users()
                else:
                    if len(self.cmd)>2:
                        debug=2
                    elif len(self.cmd)==1:
                        self.ETS.all_users()
                    elif self.cmd[1]=="all":
                        self.ETS.all_users(True)
                    else:
                        debug=1
            elif self.cmd[0]=="delete":
                if self._check_len(3):
                    pass
                elif self.cmd[1]=="pwd":
                    self.ETS.delete(pwd=self.cmd[2])
                elif self.cmd[1]=="op":
                    if self.ETS.info[1]==2:
                        try:
                            self.ETS.delete(index=int(self.cmd[2]),op=True)
                        except ValueError:
                            debug=2
                    else:
                        debug=1
                else:
                    debug=1
            elif self.cmd[0]=="logout":
                if len(self.cmd)>1:
                    debug=1
                else:
                    self.ETS.log_out()
            elif self.cmd[0]=="op":
                try:
                    if self.ETS.info[1]!=2 and self.ETS.info[2]!=0:
                        debug=0
                    elif self._check_len(3):
                        pass
                    else:
                        if int(self.cmd[2])!=0 and int(self.cmd[2])!=1 and int(self.cmd[1]) !=0:
                            debug=2
                        else:
                            self.ETS.op(int(self.cmd[1]),int(self.cmd[2]))
                except ValueError:
                        print("错误：命令中出现了非数字")
                except IndexError:
                        print(f'错误：未知的用户索引 "{self.cmd[1]}"')
            elif self.cmd[0]=="exit":
                if len(self.cmd)>1:
                    debug=1
                else:
                    return False
            else:
                other=["login","register"]
                if self.cmd[0] in other:
                    print(f"命令 {self.cmd[0]} 不能在已登录状态下使用")
                else:
                    debug=0
        else:
            if self.cmd[0]=="login":
                if self._check_len(3):
                    pass
                else:
                    self.ETS.log_in(self.cmd[1],self.cmd[2])
            elif self.cmd[0]=="register":
                if self._check_len(4):
                    pass
                else:
                    self.ETS.register_in(self.cmd[1],self.cmd[2],self.cmd[3])
            elif self.cmd[0]=="exit":
                if len(self.cmd)>1:
                    debug=1
                else:
                    return False
            else:
                other=["me","pwd","user","delete","logout","op"]
                if self.cmd[0] in other:
                    print(f"命令 {self.cmd[0]} 不能在未登录状态下使用")
                else:
                    debug=0
        if debug>-1:
            print(f"错误：意外的 {self.cmd[debug]} 出现在了命令中")
        
        return True
    
    
    def main(self):
        '''使用命令行操作秦始皇系统的主循环'''
        
        while True:
            self.inputCMD()
            if not self.run():
                break



if __name__=="__main__":
    main=GracefulCMD("/storage/emulated/0/MCandPHI/Code/Python/EmperorTsingSystem_cmdEdition/data.json")
    main.main()
