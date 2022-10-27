import hashlib
import os
import logging
import shutil
import time
import zipfile
from datetime import datetime
from collections import OrderedDict
import json
import requests
from config import web_list

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
type = os.environ.get("Type")
Type = "debug" if type == "Debug" else "release"
cache_url = os.environ.get("cacheurl")
# build_apk = os.environ.get("build_apk")
run_mode = os.environ.get("run_mode")
version_path_svn = path + "/publish_versions/" + os.environ.get("version_path")


def svn_update():
    logger.info("开始更新tools -- svn update {}".format(tools_path))
    os.system("{} revert -R {}".format(svn_path, tools_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, tools_path))
    logger.info("开始更新svn_client -- svn update {}".format(svn_client_path))
    os.system("{} revert -R {}".format(svn_path, svn_client_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_client_path))
    logger.info("开始更新svn_sql -- svn update {}".format(svn_sql_path))
    os.system("{} revert -R {}".format(svn_path, svn_sql_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path))
    logger.info("开始更新publish_versions -- svn update {}".format(version_path_svn))
    os.system("{} revert -R {}".format(svn_path, version_path_svn))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
    logger.info(resource_path)
    if os.path.exists(resource_path):
        logger.info("开始更新resource -- svn update {}".format(resource_path))
        os.system("{} revert -R {}".format(svn_path, resource_path))
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
        logger.info("当前路径{}".format(os.getcwd()))
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
        logger.info("替换文件- local.properties - build.gradle - MainActivity.java")
        shutil.copy(workspace + "/local.properties", client_path + "/android_wartune/local.properties")
        shutil.copy(workspace + "/build.gradle", client_path + "/android_wartune/app/build.gradle")
        shutil.copy(workspace + "/MainActivity.java",
                    client_path + "/android_wartune/app/src/main/java/demo/MainActivity.java")

    os.chdir(workspace)


def sql_copy():
    logger.info("复制sql文件")
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


def delete_jpg_png(path):
    if os.path.isfile(path):
        if os.path.splitext(path)[-1] == ".jpg" or os.path.splitext(path)[-1] == ".png":
            try:
                os.remove(path)
                logger.info("删除{}".format(path))
            except Exception as e:
                print(e)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            delete_jpg_png(itempath)
    # logger.info("png与jpg删除完毕")


def clint_build():
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(svn_client_path))
    os.chdir(svn_client_path)
    logger.info("删除png与jpg")
    jpg_png_path = os.path.join(svn_client_path, "bin/res")
    delete_jpg_png(jpg_png_path)
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "/usr/local/bin/npm run build"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)

    cmd2 = "layaair2-cmd publish -c web"
    logger.info("执行命令 -- {}".format(cmd2))
    os.system(cmd2)
    # if build_apk == "true":
    logger.info("复制一份web为web_client")
    shutil.copytree(svn_client_path + "/release/web", web_client_path)
    if run_mode == "build_all" or run_mode == "build_server.zip":
        web_server()
    # if build_apk == "true":
    if run_mode == "build_all" or run_mode == "build_apk":
        web_client(web_client_path)


def version_update():
    if os.path.exists(version_path + "/last_{}_{}.json".format(git_branch, type)):
        logger.info("存在version.json文件开始进行版本对比")
        logger.info("当前路径为 -- {}".format(os.getcwd()))
        logger.info("复制一份到workspace下")
        shutil.copy(version_path + "/last_{}_{}.json".format(git_branch, type), workspace + "/version.json")
        logger.info(os.listdir(workspace))

        cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py",
                                        workspace + "/version.json",
                                        svn_client_path + "/release/web")
        logger.info("执行命令 -- {}".format(cmd))
        os.system(cmd)
        if not os.path.exists(svn_client_path + "/release/web/server.zip"):
            raise "VersionDiff.py执行失败"
        ssh_update(svn_client_path + "/release/web/server.zip")
        logger.info("替换last_version")
        shutil.copy(svn_client_path + "/release/web/version.json",
                    version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"),
                                                              os.environ.get("versionName"), git_branch, type))
        shutil.copy(svn_client_path + "/release/web/version.json",
                    version_path + "/last_{}_{}.json".format(git_branch, type))
    elif os.path.exists(
            version_path + "/last_{}_{}.json".format(git_branch, type)) == False and run_mode == "build_server.zip":
        logger.info("差分失败，未找到last_{}_{}.json，首次执行请先执行build_all".format(git_branch, type))
        return
    else:
        logger.info("首包不需要版本对比与上传,保存version")
        shutil.copy(svn_client_path + "/release/web/version.json",
                    version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"),
                                                              os.environ.get("versionName"), git_branch, type))
        shutil.copy(svn_client_path + "/release/web/version.json",
                    version_path + "/last_{}_{}.json".format(git_branch, type))


def resource_copy():
    logger.info("复制资源文件animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    shutil.rmtree(svn_client_path + "/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))

    shutil.copytree(resource_path + "/animation", svn_client_path + "/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    if not os.path.exists(svn_client_path + "/bin/res/animation"):
        raise "resource_copy执行错误"


def layadcc_cache_android(client_path):
    os.chdir(web_client_path)
    """
    后续url地址以及url目录地址需要可配置，完成

    """
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "layadcc ./ -cache -url {}".format(cache_url)
    logger.info("执行脚本 -- {}".format(cmd))
    os.system(cmd)
    #
    if os.path.exists(client_path + "/app/src/main/assets/cache"):
        logger.info("删除目录{}".format(client_path + "/app/src/main/assets/cache"))
        logger.info(os.listdir(client_path + "/app/src/main/assets"))
        shutil.rmtree(client_path + "/app/src/main/assets/cache")
        logger.info(os.listdir(client_path + "/app/src/main/assets"))

    logger.info("复制文件至工程目录")
    shutil.copytree(web_client_path + "/layadccout/cache", client_path + "/app/src/main/assets/cache")
    logger.info(os.listdir(client_path + "/app/src/main/assets"))
    # if os.path.exists(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"):
    #     logger.info("删除并创建{}".format(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"))
    #     shutil.rmtree(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
    # os.mkdir(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")
    # logger.info("复制文件至{}".format(client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net"))
    # if os.path.exists(web_client_path+"/layadccout/cache/https._"):
    #     raise "生成layadccout失败"
    # file_list = os.listdir(web_client_path+"/layadccout/cache/https._")
    # for item in file_list:
    #     shutil.copy(web_client_path+"/layadccout/cache/https._/"+item, client_path+"/app/src/main/assets/cache/https.__scicd-hd-cdn.7road.net")


# def layadcc_cache_ios(val):
#     pass


def android_build():
    os.chdir(android_path)
    if os.path.exists(android_path + "/gradle"):
        shutil.rmtree(android_path + "/gradle")
        logger.info("已删除旧gradle文件夹")
    if os.path.exists(android_path + "/gradlew"):
        os.remove(android_path + "/gradlew")
        logger.info("已删除旧gradlew")
    if os.path.exists(android_path + "/app/build/outputs/apk/{}".format(Type)):
        shutil.rmtree(android_path + "/app/build/outputs/apk/{}".format(Type))
        logger.info("已删除旧{}文件夹".format(Type))
    logger.info("当前路径 -- {}".format(os.getcwd()))
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle clean")
    os.system("/opt/gradle/gradle-7.2/bin/gradle clean")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle init")
    os.system("/opt/gradle/gradle-7.2/bin/gradle init")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle wrapper")
    os.system("/opt/gradle/gradle-7.2/bin/gradle wrapper")
    logger.info("执行 {} assemble{}".format("./gradlew", type))
    os.system("{} assemble{}".format("./gradlew", type))


# def ios_build():
#     pass


def delete():
    shutil.rmtree(svn_client_path + "/release/web")
    if os.path.exists(web_client_path):
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
    delete_web()
    time.sleep(5)
    delete_res()
    # time.sleep(5)
    # delete_png_jpg()
    cmd = "layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(web_client_path + "/update"):
        raise "layadcc执行失败"


def web_server():
    os.chdir(svn_client_path + "/release/web")
    logger.info("当前路径 {}".format(os.getcwd()))
    # res内可能有需要删除的内容
    cmd = "layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(svn_client_path + "/release/web/update"):
        raise "layadcc执行失败"

    version_update()  # 执行 server_update() 差分脚本 出一个server.zip上传 version.json保存


def build_sdk_package():
    if os.environ.get("渠道参数") != None:
        # sdk_parameter = os.environ.get("渠道参数")
        channels = os.environ['渠道参数'].split(';')
        parameter_list = []
        for channel_info in channels:
            channel_parameters = channel_info.split('：')[1].strip()
            if channel_parameters != "":
                _dict = {
                    "appId": channel_parameters.split("_")[0],
                    "packageId": channel_parameters.split("_")[1],
                    "dataSource": channel_parameters.split("_")[2],
                    "source": channel_parameters.split("_")[3]
                }
                parameter_list.append(_dict)
        # parameter_list = []
        # for parameter in sdk_parameter.split(";"):
        #     if parameter != "":
        #         _dict = {
        #             "appId": parameter.split(",")[0],
        #             "packageId": parameter.split(",")[1],
        #             "dataSource": parameter.split(",")[2],
        #             "source": parameter.split(",")[3]
        #         }
        #         parameter_list.append(_dict)
        apk_path = android_path + "/app/build/outputs/apk/{}/app-{}.apk".format(Type, Type)
        logger.info("apk_path:{}".format(apk_path))
        md5 = ""
        if os.path.isfile(apk_path):
            fp = open(apk_path, "rb")
            contents = fp.read()
            fp.close()
            md5 = hashlib.md5(contents).hexdigest()
        else:
            logger.info("file not exists")
            raise
        url = "http://10.10.1.72:916/file/pack/packByApi"
        apk_name = "app-{}.apk".format(Type)
        for parameter_dict in parameter_list:
            if parameter_list.index(parameter_dict) == 0:
                params = OrderedDict([
                    ("isCheck", (None, 0)),
                    ("appId", (None, int(parameter_dict["appId"]))),
                    ("dataSource", (None, parameter_dict["dataSource"])),
                    ("packageId", (None, int(parameter_dict["packageId"]))),
                    ("source", (None, int(parameter_dict["source"]))),
                    ("versionCode", (None, os.environ["versionCode"])),
                    ("versionName", (None, os.environ["versionName"])),
                    ("gameVersionCode", (None, os.environ["gameVersionCode"])),
                    ("gameVersionName", (None, os.environ["gameVersionName"])),
                    ("userName", (None, "yuanzhan.yu")),
                    ("notifyType", (None, 1)),
                    ("notifyUsers", (None, "72f7898c-7c59-46c7-9ca3-80634137124b")),
                    ("fileMd5Code", (None, md5)),
                    ("file", (apk_name, open(apk_path, 'rb'), 'application/zip'))
                ])
            else:
                params = OrderedDict([
                    ("isCheck", (None, 0)),
                    ("appId", (None, int(parameter_dict["appId"]))),
                    ("dataSource", (None, parameter_dict["dataSource"])),
                    ("packageId", (None, int(parameter_dict["packageId"]))),
                    ("source", (None, int(parameter_dict["source"]))),
                    ("versionCode", (None, os.environ["versionCode"])),
                    ("versionName", (None, os.environ["versionName"])),
                    ("gameVersionCode", (None, os.environ["gameVersionCode"])),
                    ("gameVersionName", (None, os.environ["gameVersionName"])),
                    ("userName", (None, "yuanzhan.yu")),
                    ("notifyType", (None, 1)),
                    ("notifyUsers", (None, "72f7898c-7c59-46c7-9ca3-80634137124b")),
                    ("fileMd5Code", (None, md5))
                ])
            logger.info("打包请求参数:{}".format(params))
            response = requests.post(url, files=params)
            result = json.loads(response.text)
            try:
                if result["code"] == 0:
                    logger.info("开始打包，请在企业微信查看打包结果")
                else:
                    logger.info("打包失败:{}".format(result.get("message", "未知结果")))
            except Exception:
                logger.info(response.text)
            try_count = 0
            while result["code"] == 110 and result[
                "message"] == "Packaging is already in progress, please operate in 5 minutes" and try_count < 5:
                time.sleep(240)
                try_count += 1
                logger.info("打包请求参数:{}".format(params))
                response = requests.post(url, files=params)
                result = json.loads(response.text)
                try:
                    if result["code"] == 0:
                        logger.info("开始打包，请在企业微信查看打包结果")
                    else:
                        logger.info("打包失败:{}".format(result.get("message", "未知结果")))
                except Exception:
                    logger.info(response.text)
    else:
        logger.info("未选渠道参数")


def delete_web():
    lis = os.listdir()
    path = os.getcwd()
    for item in lis:
        if item not in web_list:
            if os.path.isdir(path + "/" + item):
                logger.info("删除目录 - {}".format(path + "/" + item))
                shutil.rmtree(path + "/" + item)
            elif os.path.isfile(path + "/" + item):
                logger.info("删除文件 - {}".format(path + "/" + item))
                os.remove(path + "/" + item)
            else:
                logger.info("{}不是文件也不是目录".format(path + "/" + item))
    logger.info("删除完毕")


def delete_res():
    lis = []
    for line in open(workspace + "/delete_res_config.txt"):
        logger.info(f"res_path:{line}")
        lis.append(line.split("web")[1].replace('\\', '/').replace('\n', ''))
    path = os.getcwd()
    tar_dir = path + "/res2"
    os.mkdir(tar_dir)
    for item in lis:
        if os.path.isdir(path + item):
            if os.path.exists(tar_dir + "/".join(item.split("/")[:-1])):
                logger.info("目录已存在，复制目录{} 至 {}".format(path + item, tar_dir + item))
                shutil.copytree(path + item, tar_dir + item)
            else:
                logger.info("创建目录 {}".format(tar_dir + "/".join(item.split("/")[:-1])))
                os.makedirs(tar_dir + "/".join(item.split("/")[:-1]))
                logger.info("复制目录{} 至 {}".format(path + item, tar_dir + item))
                shutil.copytree(path + item, tar_dir + item)
        elif os.path.isfile(path + item):
            if os.path.exists(tar_dir + "/".join(item.split("/")[:-1])):
                logger.info("目录已存在，复制文件{} 至 {}".format(path + item, tar_dir + item))
                shutil.copy(path + item, tar_dir + item)
            else:
                logger.info("创建文件目录 {}".format(tar_dir + "/".join(item.split("/")[:-1])))
                os.makedirs(tar_dir + "/".join(item.split("/")[:-1]))
                logger.info("复制文件{} 至 {}".format(path + item, tar_dir + item))
                shutil.copy(path + item, tar_dir + item)
        else:
            logger.info("不存在该目录或文件-{}".format(path + item))
    logger.info("删除{}".format(web_client_path + "/res"))
    shutil.rmtree(web_client_path + "/res")
    logger.info("移动/res2/res--/res")
    shutil.move(web_client_path + "/res2/res", web_client_path)
    shutil.rmtree(web_client_path + "/res2")
    logger.info("res内容复制完毕")


# def delete_png_jpg():
#     logger.info("删除png jpg")
#     lis = []
#     for line in open(workspace + "/delete_res_config.txt"):
#         logger.info(f"res_path:{line}")
#         lis.append(line.split("web")[1].replace('\\', '/').replace('\n', ''))
#     for item in lis:
#         path = web_client_path+item
#         lis2 = os.listdir(path)
#         for i in lis2:
#             if os.path.isdir(path+"/"+i):
#                 lis3 = os.listdir("{}/{}".format(path, i))
#                 for j in lis3:
#                     if os.path.splitext(j)[-1] == ".png" or os.path.splitext(j)[-1] == ".jpg":
#                         os.remove("{}/{}/{}".format(path, i, j))
#             elif os.path.isfile(path+"/"+i):
#                 if os.path.splitext(i)[-1] == ".png" or os.path.splitext(i)[-1] == ".jpg":
#                     os.remove("{}/{}".format(path, i))
def main():
    svn_update()
    git_update()
    """
    测试中手动替换 后续svn提交上去后打开
    """
    ## resource_copy()
    ## sql_copy()
    ## sql2_Utf8()

    clint_build()
    if run_mode == "build_all" or run_mode == "build_apk":
        layadcc_cache_android(android_path)
        android_build()
        build_sdk_package()
    # delete()
    # client = os.environ.get("os")
    # if client == "all":
    #     layadcc_cache_android(android_path)
    #     layadcc_cache_ios(ios_path)
    # elif client == "android":
    #     layadcc_cache_android(android_path)
    # else:
    #     layadcc_cache_ios(ios_path)
    # if client == "all":
    #     android_build()
    #     build_sdk_package()
    #     ios_build()
    #
    # elif client == "android":
    #     android_build()
    #     build_sdk_package()
    #
    # else:
    #     ios_build()

    # delete_jpg_png("/Users/jun.nie/Wartune/svn/test/wartune_performance_1.2/bin/res")
    # os.chdir(svn_client_path)
    # os.system("layaair2-cmd publish -c web")
    # global android_path
    # android_path = "/Users/jun.nie/Wartune/android/master/android_wartune"
    # build_sdk_package()

    # delete()
    # if run_mode == "build_all" or run_mode == "build_apk":
    #     client = os.environ.get("os")
    #     if client == "all":
    #         layadcc_cache_android(android_path)
    #         layadcc_cache_ios(ios_path)
    #     elif client == "android":
    #         layadcc_cache_android(android_path)
    #     else:
    #         layadcc_cache_ios(ios_path)
    #     if client == "all":
    #         android_build()
    #         build_sdk_package()
    #         ios_build()
    #
    #     elif client == "android":
    #         android_build()
    #         build_sdk_package()
    #
    #     else:
    #         ios_build()


if __name__ == '__main__':
    main()

