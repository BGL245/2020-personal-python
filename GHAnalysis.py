import json
import os
import argparse


class Data:
    # 初始化Data类
    def __init__(self, dict_address: int = None, reload: int = 0):
        if reload == 1:
            self.__init(dict_address)
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists(
                '2.json') and not os.path.exists('3.json'):  # 判断文件是否存在
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()
        self.__4Events4PerP = json.loads(x)  # 将已编码的 JSON 字符串解码为 Python 对象
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    # 解析json文件
    def __init(self, dict_address: str):
        json_list = []  # 定义一个列表
        # os.walk()遍历一个目录内各子目录和子文件
        # root 所指的是当前正在遍历的这个文件夹的本身的地址
        # dirs 是一个 list ，内容是该文件夹中所有的目录的名字(不包括子目录)
        # files 同样是 list , 内容是该文件夹中所有的文件(不包括子目录)
        for root, dic, files in os.walk(dict_address):  # topdown默认为true，walk会遍历每个文件夹与文件夹中子目录
            for f in files:
                if f[-5:] == '.json':  # 文件后缀为.json
                    json_path = f  # 将.json路径记录下来
                    x = open(dict_address + '\\' + json_path,
                             'r', encoding='utf-8').read()  # 打开.json文件 只读 readline返回一行 read读整个文件会爆？ readline每次读一行
                    str_list = [_x for _x in x.split('\n') if len(_x) > 0]
                    for i, _str in enumerate(str_list):  # enumerate函数将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
                        try:
                            # 在列表末尾添加新的对象
                            json_list.append(json.loads(_str))  # json.load()将json格式的字符串转换成python的数据类型，返回的是str不是dict
                        except:
                            pass  # 防止出错
        records = self.__listOfNestedDict2ListOfDict(json_list)  # 转换为字典
        self.__4Events4PerP = {}  # 个人的四个事件dict字典
        self.__4Events4PerR = {}  # 项目的四个事件dict字典
        self.__4Events4PerPPerR = {}  # 每个人每个项目的四个事件dict字典
        for i in records:
            if not self.__4Events4PerP.get(i['actor__login'], 0):  # 判断字典中是否有键actor_login
                self.__4Events4PerP.update({i['actor__login']: {}})  # 没有就加入
                self.__4Events4PerPPerR.update({i['actor__login']: {}})
            self.__4Events4PerP[i['actor__login']][i['type']
            ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0) + 1  # 获取到相应type的值+1，type没有为0
            if not self.__4Events4PerR.get(i['repo__name'], 0):
                self.__4Events4PerR.update({i['repo__name']: {}})
            self.__4Events4PerR[i['repo__name']][i['type']
            ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0) + 1
            if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'],
                                                                  0):
                self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})
            self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
            ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0) + 1
        with open('1.json', 'w', encoding='utf-8') as f:  # 文件不存在就生成
            json.dump(self.__4Events4PerP, f)  # 将内容序列化，并写入打开的文件中 存个人事件
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR, f)  # 项目事件
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR, f)  # 每个人每个项目的事件

    # 将列表转为字典
    def __parseDict(self, d: dict, prefix: str):
        _d = {}  # 定义dict字典数据类型
        for k in d.keys():
            if str(type(d[k]))[-6:-2] == 'dict':
                _d.update(self.__parseDict(d[k], k))
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k
                _d[_k] = d[k]
        return _d

    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []  # 定义一个列表
        for d in a:
            _d = self.__parseDict(d, '')
            records.append(_d)
        return records

    def getEventsUsers(self, username: str, event: str) -> int: #返回int型
        if not self.__4Events4PerP.get(username, 0):
            return 0
        else:
            return self.__4Events4PerP[username].get(event, 0)

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame, 0):
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event, 0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username, 0):
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame, 0):
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event, 0)


class Run:
    def __init__(self):  # 初始化
        # 创建解析器ArgumentParser()对象 保存把命令行解析成Python数据类型所需要的所有信息
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')  # 添加参数 告诉ArgumentParser如何接收命令行上的字符串并将它们转换成对象 --init可选参数 不指定为NULL
        self.parser.add_argument('-u', '--user')  # -u参数简写
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        # 解析添加的参数 将之前add_argument()定义的参数进行赋值，并返回相关的namespace
        if self.parser.parse_args().init:  # init没有指定参数为null执行else
            self.data = Data(self.parser.parse_args().init, 1)  # 对data进行初始化
            return 0
        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo,
                            self.parser.parse_args().event)
                    else:
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    a = Run()
