#
# import os
#
# # workspace = "/Users/jun.nie/jenkins/workspace/sqh5_client_autobuild"
# # a = workspace.split("jenkins")[0]
# # print(a)
#
# import os
# import shutil
# import zipfile
#
#
#
# import os
# import zipfile
#
#
#
# # def file2zip(zip_file_name: str, file_names: list):
# #
# #     with zipfile.ZipFile(zip_file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
# #         for fn in file_names:
# #             parent_path, name = os.path.split(fn)
# #             print(parent_path,name)
# #             zf.write(fn, arcname=name)
# #
# #
# # if __name__ == "__main__":
# #     zip_name = './test.zip'
# #     files = []
# #     file_names = os.listdir("H:/tt")
# #     for i in file_names:
# #         files.append("H:/tt"+"/"+i)
# #     file2zip(zip_name, files)
# #
#
# def zipDir(dirpath, outFullName):
#
#     zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
#     for path, dirnames, filenames in os.walk(dirpath):
#         fpath = path.replace(dirpath, '')
#
#         for filename in filenames:
#             zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
#     zip.close()
#
#
# if __name__ == "__main__":
#     input_path = "D:/tt2"
#     output_path = "D:/tt2/2.zip"
#     zipDir(input_path, output_path)
# #
# #     zipDir(input_path, output_path)
# # a = 1
# # b = 2
# # c = 3
# #
# # print(os.listdir("D:/tt"))
# # #
# # # shutil.copy("D:/tt/1.txt", "D:/tt/333")
#
# import sys
#
#
# #
# # print(os.getcwd())
# # import json
# # with open("./count.json", 'r', encoding='utf-8') as load_f:
# #     load_dict = json.load(load_f)
# # print(load_dict["count"])
# # load_dict["count"] += 1
# # with open("./count.json", "w") as f:
# #     json.dump(load_dict, f, ensure_ascii=False)
#
# # ktx   publich dcc diff cacsh
# import shutil
#
# # cd /Users/jun.nie/Wartune/android/android_wartune
# # JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.0.16.1.jdk/Contents/Home
# # PATH=$JAVA_HOME/bin:$PATH:.
# # CLASSPATH=$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:.
# # export JAVA_HOME
# # export PATH
# # export CLASSPATH
# # /opt/gradle/gradle-7.2/bin/gradle clean
# # print(os.listdir("./"))
#
#
# # if os.path.exists("D:/tt2/1.txt"):
# #     os.remove("D:/tt2/1.txt")
#
#
# # from datetime import datetime
# # dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# # shutil.copy("D:/tt2/1.txt", "D:/tt2/last.txt")
# # shutil.copy("D:/tt2/1.txt", "D:/tt2/time.txt")
# # shutil.move("D:/tt2/last.txt", "D:/tt2/tt/last.txt")
# # shutil.move("D:/tt2/time.txt", "D:/tt2/tt/{}.txt".format(dt))
# # 家中有事
#
# #
# # shutil.copytree("D:/tt2","D:/tt2/tt2")
# # JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.0.16.1.jdk/Contents/Home
# # PATH=$JAVA_HOME/bin:$PATH:.
# # CLASSPATH=$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:.
# # export JAVA_HOME
# # export PATH
# # export CLASSPATH
# # if "master" != 'master':
# #     print(1)
# #
# #
# # a = {
# #     'isCheck': int,  # 需要
# #     'appId': int,
# #     'dataSource': str,
# #     'packageId': int,
# #     'source': int,
# #     'versionCode': str,
# #     'versionName': str,
# #     'gameVersionCode': str,
# #     'gameVersionName': str,
# #     'userName': str,
# #     'notifyType': int,
# #     'notifyUsers': str,
# #     'fileMd5Code': str,
# #     'file': ''
# # }
# # import logging
# #
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# # logger = logging.getLogger(__name__)
# # logger.info(shutil.copy("D:/tt2/1.txt", "D:/tt2/tt/1.txt"))
#
#
# # from datetime import datetime
# #
# # dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# # shutil.copy("D:/tt2/1.txt", "D:/tt2/tt/{}.txt".format(dt))
# # shutil.copy("D:/tt2/1.txt", "D:/tt2/tt/last.txt")
# # # shutil.move("D:/tt2/{}.txt".format(dt), "D:/tt2/tt/{}.txt".format(dt))
# # # shutil.move("D:/tt2/last.txt", "D:/tt2/tt/last.txt")
# import json
#
# jsonStr = '{"name":"aspiring", "age": 17, "hobby": ["money","power", "read"],"parames":{"a":1,"b":2}}'
#
# # 将json格式的字符串转为python数据类型的对象
# # jsonData = json.loads(jsonStr)
# # print(jsonData)
# # print(type(jso))
# # print(jsonData['hobby'])
#
# # # 加载json文件
# # path1 = r'E:\***\ddd.json'
# #
# # with open(path1, 'rb') as f:
# #     data = json.load(f)
# #     print(data)
# #     # 字典类型
# #     print(type(data))
#
#
# web_list = ["js", "layadccout", "libs", "res", ]
#
#
# # lis = ["1","2"]
# # if "1" in lis:
# #     print(1)
#
# # path = "D:/tt2/2.zip"
# # if os.path.isdir(path):
# #     print(1)
# # elif os.path.isfile(path):
# #     print(2)
# # else:
# #     print(3)
#
# # os.chdir('D:/')
# # print(os.getcwd())
# # print(os.listdir())
# # from config import web_list
# # print(web_list)
# # import os
# # f = open("config.txt")  # 返回一个文件对象
# # line = f.readline()  # 调用文件的 readline()方法
# # lis = []
# # while line:
# #     res = line.split("web")[1]
# #     tar = res.replace("\\", "/")
# #     lis.append(tar.split("\n")[0])
# #     line = f.readline()
# # f.close()
#
# # shutil.copytree("D:/tt", "D:/tt2/t22t2")

# import os
# os.chdir("D:/tt")
# def delete():
#     lis = os.listdir()
#     for i in lis:
#         lis2 = os.listdir("D:/tt/{}".format(i))
#         for j in lis2:
#             if os.path.splitext(j)[-1] == ".png" or os.path.splitext(j)[-1] == ".jpg":
#                 os.remove("D:/tt/{}/{}".format(i, j))
#
#
# delete()
# import os
# path = "D:/tt"
# def delete(path):
#     if os.path.isfile(path):
#         if os.path.splitext(path)[-1] == ".jpg" or os.path.splitext(path)[-1] == ".png":
#             try:
#                 os.remove(path)
#             except Exception as e:
#                 print(e)
#     elif os.path.isdir(path):
#         for item in os.listdir(path):
#             itempath = os.path.join(path, item)
#             delete(itempath)
#
# print(delete(path))
# a = 3
# import os
# print(os.path.exists("D:/111111"))
# if os.path.exists("D:/e1"):
#     print(1)
# elif os.path.exists("D:/e1") == False and a == 3:
#     print(2)
# else:
#     print(3)
# import os
# version_path = "D:/tt"
# git_branch = "1"
# type = "1"
#
# if os.path.exists(version_path + "/last_{}_{}.json".format(git_branch, type)) == False:
#     print(2)
# import shutil
# import os
# shutil.copy("D:/tt3/1.txt", os.path.join("D:/tt3", "1"))
# os.mkdir("D:/tt3"+"/"+"2")
# import os
# print("{}".format("1"+os.environ.get("os")))

# from datetime import datetime
# dt = datetime.now().strftime("%Y%m%d_%H_%M_%S")
# print(dt)
import os
# if os.path.exists("D:/tt3/22"):
#     print(1)
# print(len(os.listdir("D:/tst3")))

# a = "index-58a98677dd.js"
# if a.startswith('index') and a.endswith('.js'):
#     print("222")

# import requests
# from datetime import datetime
# import time
# import json
# dt2 = datetime.now().strftime("%Y%m%d_%H_%M_%S")
#
#
# url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=91a105b7-cf31-43e7-b893-feb11b62e848"
# _time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
# msg = "appId：60031\n" \
#       "packageId：311\n" \
#       "打包状态：打包成功！\n" \
#       "打包进度：打包结束！\n" \
#       "完成时间：{}\n" .format(time)
# data = {
#     "msgtype": "text",
#     "text": {
#             "content": msg
#         }
# }
# _data = json.dumps(data)
# response = requests.post(url, data=_data, headers={"Content-Type": "application/json"}
# import shutil
# shutil.copytree("D:/tt/1", "D:/tt/2/3")
# a = "https://scicd-hd-cdn.7road.net/index.html"
# a = a.replace(":", "").replace("//", "").replace("/", "")
# print(a)
import os
# import subprocess
# cmd = subprocess.Popen("dir",stdout=subprocess.PIPE, shell=True)
# print(cmd)
# x = cmd.stdout.read().decode()
# print(x)
# cmd = os.popen("dir","r",1)
# print(cmd.read())
# cmd = os.system("dir")
# print(cmd)
# a = os.system("adb devices")
# print(a)
#
# lis = []
# for line in open("delete_res_config.txt"):
#     lis.append(line.split("web")[1].replace('\\', '/').replace('\n', ''))
# print(lis)
import shutil
#
# shutil.copytree("D:/tt/1", "D:/tt3/1/1/1")

# a = "http://test2.svn.7road-inc.com/svn/slg/WartuneH5/数据表管理/svn_sql/inland/V2.4.6-1.2.0.9"
# print(a.split("svn_sql")[1].split("/")[1])
# print(a.split("svn_sql")[1].split("/")[2])
import shutil
shutil.rmtree("D:/ckeditor/ckeditor5-build-classic")
