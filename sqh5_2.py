# import os
# import logging
# import shutil
# import time
# import zipfile
# from datetime import datetime
#
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# logger = logging.getLogger(__name__)
# workspace = os.environ["WORKSPACE"]
# path = workspace.split("jenkins")[0] + "Wartune/svn"
# svn_url = os.environ.get("svn_url")
# tools_path = path + "/tools"
# svn_sql_path = path + "/svn_sql"
# svn_sql_resource = svn_url.split("WartuneH5")[1].split("/")
# svn_path = "/opt/homebrew/bin/svn"
# resource_path = path + "/resource/" + svn_sql_resource[1] + "_" + svn_sql_resource[2]
# svn_client_path = path + "/wartune_performance_1.2"
# version_path = os.path.dirname(workspace)+"/version"
# dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# android_path = workspace.split("jenkins")[0] +"Wartune/android/android_wartune"
# ios_path = workspace.split("jenkins")[0] +"Wartune/ios/ios_warturne"
#
#
# def svn_update():
#     logger.info("开始更新tools -- svn update {}".format(tools_path))
#     os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, tools_path))
#     logger.info("开始更新svn_client -- svn update {}".format(svn_client_path))
#     os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_client_path))
#     logger.info("开始更新svn_sql -- svn update {}".format(svn_sql_path))
#     os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path))
#     logger.info(resource_path)
#     if os.path.exists(resource_path):
#         logger.info("开始更新resource -- svn update {}".format(resource_path))
#         os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, resource_path))
#     else:
#         logger.info('目录不存在开始创建--{}'.format(resource_path))
#         os.system("mkdir {}".format(resource_path))
#         cmd = "{} checkout {} {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_url, resource_path)
#         logger.info("开始执行命令 --{}".format(cmd))
#         status = os.system(cmd)
#         logger.info("当前状态-- {}".format(status))
#
#
# def sql_copy():
#     logger.info("复制文件至指定目录")
#     zip_path = workspace + "/sql/server/dts/data"
#     os.makedirs(zip_path)
#     old_file_list = os.listdir(svn_sql_path)
#     for item in old_file_list:
#         if os.path.splitext(item)[-1] == ".sql" or os.path.splitext(item)[-1] == ".txt":
#             shutil.copy(svn_sql_path + "/" + item, zip_path)
#     zip_dir(workspace+"/sql", "./server.zip")
#     shutil.rmtree(workspace+"/sql")
#
#
# def zip_dir(dirpath, outFullName):
#     logger.info("开始压缩文件夹")
#     zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
#     for path, dirnames, filenames in os.walk(dirpath):
#         fpath = path.replace(dirpath, '')
#         for filename in filenames:
#             zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
#     zip.close()
#
#
# def sql2_Utf8():
#     shutil.copy(tools_path+"/sql2json/format.json", workspace)
#     cmd = f"python3 {tools_path}/sql2json/sql2json.py server.zip"
#     logger.info("执行脚本-- {}".format(cmd))
#     os.system(cmd)
#     cmd2 = f"python3 {tools_path}/sql2json/Utf8Change.py config"
#     logger.info("执行脚本-- {}".format(cmd2))
#     os.system(cmd2)
#     file_list = os.listdir(workspace+"/config2")
#     logger.info(file_list)
#     logger.info("移动config2内文件至 {}".format(svn_client_path+"/bin/res/config"))
#     for item in file_list:
#         shutil.copy(workspace+"/config2/"+item, svn_client_path+"/bin/res/config")
#
#
# def clint_build():
#     os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(svn_client_path))
#     os.chdir(svn_client_path)
#     logger.info("当前路径为 -- {}".format(os.getcwd()))
#     cmd = "npm run build"
#     if os.path.exists(svn_client_path +"/resBackup"):
#         shutil.rmtree(svn_client_path +"/resBackup")
#         logger.info("删除 {}".format(svn_client_path +"/resBackup"))
#     logger.info("执行命令 -- {}".format(cmd))
#     os.system(cmd)
#     logger.info("执行命令 -- python3 {} {}".format(tools_path+"/ASTCTools/ASTCTools.py", svn_client_path+"/bin"))
#     os.system("python3 {} {}".format(tools_path+"/ASTCTools/ASTCTools.py", svn_client_path+"/bin"))
#     if not os.path.exists(svn_client_path + "/resBackup"):
#         raise "ASTCTools.py执行失败"
#     cmd2 = "layaair2-cmd publish -c web"
#     logger.info("执行命令 -- {}".format(cmd2))
#     os.system(cmd2)
#     os.chdir(svn_client_path + "/release/web")
#     logger.info("复制一份web_client")
#     web_client()
#     cmd3 = " layadcc ./"
#     logger.info("执行命令 -- {}".format(cmd3))
#     os.system(cmd3)
#     if not os.path.exists(svn_client_path+"/release/web/update"):
#         raise "layadcc执行失败"
#
#
# def server_update():  # 首包出后打开
#     logger.info("当前路径为 -- {}".format(os.getcwd()))
#     cmd = "python3 {} ./version.json {}".format(tools_path+"/VersionDiff/VersionDiff.py", svn_client_path+"/release/web")
#     logger.info("执行命令 -- {}".format(cmd))
#     os.system(cmd)
#     if not os.path.exists("./server.zip"):
#         raise "VersionDiff.py执行失败"
#     vspath = version_path+"/"+dt
#     os.mkdir(vspath)
#     shutil.copy(svn_client_path+"/release/web/version.json", vspath)
#     if len(os.listdir(vspath)) == 0:
#         raise "version拷贝失败"
#
#
# def resource_copy():
#     logger.info("复制资源文件animation")
#     logger.info(os.listdir(svn_client_path+"/bin/res"))
#     shutil.rmtree(svn_client_path+"/bin/res/animation")
#     logger.info(os.listdir(svn_client_path + "/bin/res"))
#     time.sleep(1)
#     shutil.copytree(resource_path+"/animation", svn_client_path+"/bin/res/animation")
#     logger.info(os.listdir(svn_client_path + "/bin/res"))
#     if not os.path.exists(svn_client_path+"/bin/res/animation"):
#         raise "resource_copy执行错误"
#
#
# def layadcc_cache(client_path):
#     # os.chdir(svn_client_path + "/release/web")
#     logger.info("客户端工程更新")
#     os.system(
#         "git -C {} pull http://xingjian.tian:a123456!!!@192.168.1.94/yuanzhan.yu/android_wartune".format(client_path)
#     )
#     logger.info("当前路径为 -- {}".format(os.getcwd()))
#     cmd = "layadcc ./ -cache url https://scicd-hd-cdn.7road.net "
#     logger.info("执行脚本 -- {}".format(cmd))
#     os.system(cmd)
#     if os.path.exists(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"):
#         logger.info("删除{}".format(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"))
#         shutil.rmtree(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
#     os.mkdir(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
#     file_list = os.listdir(svn_client_path+"/release/web/update")
#     for item in file_list:
#         shutil.copy(svn_client_path+"/release/web/update/"+item, client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
#
#
# def android_build():
#     os.chdir(android_path)
#     if os.path.exists(android_path+"/app/build/outputs/apk/release/app-release.apk"):
#         shutil.rmtree(android_path+"/app/build")
#     logger.info("已删除旧apk")
#     logger.info("当前路径 -- {}".format(os.getcwd()))
#     logger.info("执行 gradle clean")
#     os.system("gradle clean")
#     logger.info("执行 gradle init")
#     os.system("gradle init")
#     logger.info("执行 gradle wrapper")
#     os.system("gradle wrapper")
#     logger.info("执行 gradlew assembleRelease")
#     os.system("gradlew assembleRelease")
#
#
# def ios_build():
#     pass
#
#
# def delete():
#     shutil.rmtree(svn_client_path+"/release/web")
#
#
# def ssh_update():
#     autoscp_path = workspace.split("jenkins")[0]+"jenkins/workspace/autoscp.sh"
#     serverzip_path = workspace.split("jenkins")[0]+"jenkins/workspace/server.zip"
#     cmd = "sh {} {}".format(autoscp_path, serverzip_path)
#     logger.info("上传server.zip {}".format(cmd))
#     os.system(cmd)
#
#
# def web_client():
#     web_client_path = svn_client_path+"/release/web_client"
#     shutil.copy(svn_client_path+"/release/web", web_client_path)
#     os.chdir(web_client_path)
#     logger.info("当前路径 {}".format(os.getcwd()))
#
#
# def main():
#
#     # svn_update()
#     # sql_copy()
#     # sql2_Utf8()
#     # resource_copy()
#     # clint_build()
#     # client = os.environ.get("os")
#     # client_path = []
#     # if client == "all":
#     #     client_path.append(android_path)
#     #     client_path.append(ios_path)
#     # elif client == "android":
#     #     client_path.append(android_path)
#     # else:
#     #     client_path.append(ios_path)
#     # for i in client_path:
#     #     layadcc_cache(i)
#     # if client == "all":
#     #     android_build()
#     #     ios_build()
#     # elif client == "android":
#     #     android_build()
#     # else:
#     #     ios_build()
#     # delete()
#
#
#
# if __name__ == '__main__':
#     main()
#


import os
import logging
import shutil
import time
import zipfile
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
workspace = os.environ["WORKSPACE"]
path = workspace.split("jenkins")[0] + "Wartune/svn"
svn_url = os.environ.get("svn_url")
tools_path = path + "/tools"
svn_sql_path = path + "/svn_sql"
svn_sql_resource = svn_url.split("WartuneH5")[1].split("/")
svn_path = "/opt/homebrew/bin/svn"
resource_path = path + "/resource/" + svn_sql_resource[1] + "_" + svn_sql_resource[2]
svn_client_path = path + "/wartune_performance_1.2"
version_path = os.path.dirname(workspace) + "/version"
dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# android_path = workspace.split("jenkins")[0] +"Wartune/android/android_wartune"
android_path = ""
ios_path = workspace.split("jenkins")[0] + "Wartune/ios/ios_warturne"
web_client_path = svn_client_path + "/release/web_client"
git_branch = os.environ.get("gitbranch")


def svn_update():
    logger.info("开始更新tools -- svn update {}".format(tools_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, tools_path))
    logger.info("开始更新svn_client -- svn update {}".format(svn_client_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_client_path))
    logger.info("开始更新svn_sql -- svn update {}".format(svn_sql_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path))
    logger.info(resource_path)
    if os.path.exists(resource_path):
        logger.info("开始更新resource -- svn update {}".format(resource_path))
        os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, resource_path))
    else:
        logger.info('目录不存在开始创建--{}'.format(resource_path))
        os.system("mkdir {}".format(resource_path))
        cmd = "{} checkout {} {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_url, resource_path)
        logger.info("开始执行命令 --{}".format(cmd))
        status = os.system(cmd)
        logger.info("当前状态-- {}".format(status))


def git_update():
    global android_path
    android_path = workspace.split("jenkins")[0] + "Wartune/android/{}/android_wartune".format(git_branch)
    if os.path.exists(workspace.split("jenkins")[0] + "Wartune/android/{}/android_wartune".format(git_branch)):
        os.chdir(android_path)
        cmd = "git pull"
        logger.info("开始更新git工程 {}".format(cmd))
        os.system(cmd)
    else:
        client_path = workspace.split("jenkins")[0] + "Wartune/android/{}".format(git_branch)
        os.mkdir(client_path)
        os.chdir(client_path)
        logger.info('当前目录'.format(os.getcwd()))
        cmd2 = "git clone -b {} http://xingjian.tian:a123456!!!@192.168.1.94/yuanzhan.yu/android_wartune".format(
            git_branch)
        logger.info("开始导入工程 {}".format(cmd2))
        os.system(cmd2)
        logger.info("替换文件- local.properties- build.gradle -MainActivity.java")
        shutil.copy(workspace + "/local.properties", client_path + "/android_wartune/local.properties")
        shutil.copy(workspace + "/build.gradle", client_path + "/android_wartune/app/build.gradle")
        shutil.copy(workspace + "/MainActivity.java",
                    client_path + "/android_wartune/app/src/main/java/demo/MainActivity.java")

    os.chdir(workspace)

    # if git_branch != "master":
    #     if os.path.exists(workspace.split("jenkins")[0] +"Wartune/android/{}/android_wartune".format(git_branch)):
    #         android_path = workspace.split("jenkins")[0] +"Wartune/android/{}/android_wartune".format(git_branch)
    #         os.system("")
    #     os.makedirs(workspace.split("jenkins")[0] +"Wartune/android/{}".format(git_branch))


def sql_copy():
    logger.info("复制文件至指定目录")
    zip_path = workspace + "/sql/server/dts/data"
    os.makedirs(zip_path)
    old_file_list = os.listdir(svn_sql_path)
    for item in old_file_list:
        if os.path.splitext(item)[-1] == ".sql" or os.path.splitext(item)[-1] == ".txt":
            shutil.copy(svn_sql_path + "/" + item, zip_path)
    zip_dir(workspace + "/sql", "./server.zip")
    shutil.rmtree(workspace + "/sql")


def zip_dir(dirpath, outFullName):
    logger.info("开始压缩文件夹")
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def sql2_Utf8():
    shutil.copy(tools_path + "/sql2json/format.json", workspace)
    cmd = f"python3 {tools_path}/sql2json/sql2json.py server.zip"
    logger.info("执行脚本-- {}".format(cmd))
    os.system(cmd)
    cmd2 = f"python3 {tools_path}/sql2json/Utf8Change.py config"
    logger.info("执行脚本-- {}".format(cmd2))
    os.system(cmd2)
    file_list = os.listdir(workspace + "/config2")
    logger.info(file_list)
    logger.info("移动config2内文件至 {}".format(svn_client_path + "/bin/res/config"))
    for item in file_list:
        shutil.copy(workspace + "/config2/" + item, svn_client_path + "/bin/res/config")


def clint_build():
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(svn_client_path))
    os.chdir(svn_client_path)
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "npm run build"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if os.path.exists(svn_client_path + "/resBackup"):
        logger.info("删除 {}".format(svn_client_path + "/resBackup"))
        shutil.rmtree(svn_client_path + "/resBackup")
    logger.info("执行命令 -- python3 {} {}".format(tools_path + "/ASTCTools/ASTCTools.py", svn_client_path + "/bin"))
    os.system("python3 {} {}".format(tools_path + "/ASTCTools/ASTCTools.py", svn_client_path + "/bin"))
    if not os.path.exists(svn_client_path + "/resBackup"):
        raise "ASTCTools.py执行失败"
    cmd2 = "layaair2-cmd publish -c web"
    logger.info("执行命令 -- {}".format(cmd2))
    os.system(cmd2)
    os.chdir(svn_client_path + "/release/web")

    web_server()
    logger.info("复制一份web为web_client")

    shutil.copytree(svn_client_path + "/release/web", web_client_path)
    web_client(web_client_path)


def version_update():  # 首包出后打开
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py", version_path + "/last.json",
                                    svn_client_path + "/release/web")
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists("./server.zip"):
        raise "VersionDiff.py执行失败"
    ssh_update(svn_client_path + "/release/web/server.zip")
    shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/{}.json".format(dt))
    shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/last.json")

    # vspath = version_path+"/"+dt
    # os.mkdir(vspath)
    # shutil.copy(svn_client_path+"/release/web/version.json", vspath)
    # if len(os.listdir(vspath)) == 0:
    #     raise "version拷贝失败"


def resource_copy():
    logger.info("复制资源文件animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    shutil.rmtree(svn_client_path + "/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    time.sleep(1)
    shutil.copytree(resource_path + "/animation", svn_client_path + "/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    if not os.path.exists(svn_client_path + "/bin/res/animation"):
        raise "resource_copy执行错误"


def layadcc_cache_android(client_path):
    os.chdir(web_client_path)
    """
    后续url地址以及url目录地址需要可配置

    """
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "layadcc ./ -cache url https://scicd-hd-cdn.7road.net "
    logger.info("执行脚本 -- {}".format(cmd))
    os.system(cmd)

    if os.path.exists(client_path + "/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"):
        logger.info("删除{}".format(client_path + "/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"))
        shutil.rmtree(client_path + "/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
    os.mkdir(client_path + "/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
    file_list = os.listdir(web_client_path + "/update")
    for item in file_list:
        shutil.copy(web_client_path + "/update/" + item,
                    client_path + "/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")


def layadcc_cache_ios(val):
    pass


def android_build():
    if os.path.exists(android_path + "/gradlew"):
        os.remove(android_path + "/gradlew")
    os.chdir(android_path)
    if os.path.exists(android_path + "/app/build/outputs/apk/release/app-release.apk"):
        shutil.rmtree(android_path + "/app/build")
    logger.info("已删除旧apk")
    logger.info("当前路径 -- {}".format(os.getcwd()))
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle clean")
    os.system("/opt/gradle/gradle-7.2/bin/gradle clean")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle init")
    os.system("/opt/gradle/gradle-7.2/bin/gradle init")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle wrapper")
    os.system("/opt/gradle/gradle-7.2/bin/gradle wrapper")
    logger.info("执行 {} assembleRelease".format(android_path + "/gradlew"))
    os.system("{}assembleRelease".format(android_path + "/gradlew"))


def ios_build():
    pass


def delete():
    shutil.rmtree(svn_client_path + "/release/web")
    shutil.rmtree(web_client_path)


def ssh_update(server_path):
    autoscp_path = workspace.split("jenkins")[0] + "jenkins/workspace/autoscp.sh"
    serverzip_path = server_path
    # serverzip_path = workspace.split("jenkins")[0]+"jenkins/workspace/server1.zip"
    cmd = "sh {} {}".format(autoscp_path, serverzip_path)
    logger.info("上传server.zip {}".format(cmd))
    os.system(cmd)


def web_client(web_client_path):
    os.chdir(web_client_path)
    logger.info("当前路径 {}".format(os.getcwd()))
    # 删除res中指定内容
    cmd = " layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(web_client_path + "/update"):
        raise "layadcc执行失败"


def web_server():
    logger.info("当前路径 {}".format(os.getcwd()))
    # res内可能有需要删除的内容
    cmd = " layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(svn_client_path + "/release/web/update"):
        raise "layadcc执行失败"

    # version_update() #执行 server_update() 差分脚本 出一个server.zip上传 version.json保存


# def build_sdk_package():
#     sdk_parameter = os.environ.get("渠道参数")
#     parameter_list = []
#     for parameter in sdk_parameter.split(";"):
#         if parameter != "":
#             _dict = {
#                 "appId": parameter.split(",")[0],
#                 "packageId": parameter.split(",")[1],
#                 "dataSource": parameter.split(",")[2],
#                 "source": parameter.split(",")[3]
#             }
#             parameter_list.append(_dict)
#     apk_path = android_path+"/app/build/outputs/apk/release/app-release.apk"


def main():
    svn_update()
    git_update()
    sql_copy()
    sql2_Utf8()
    resource_copy()
    clint_build()
    client = os.environ.get("os")
    if client == "all":
        layadcc_cache_android(android_path)
        layadcc_cache_ios(ios_path)
    elif client == "android":
        layadcc_cache_android(android_path)
    else:
        layadcc_cache_ios(ios_path)
    if client == "all":
        android_build()
        ios_build()
    elif client == "android":
        android_build()
    else:
        ios_build()

    # delete()


if __name__ == '__main__':
    main()


