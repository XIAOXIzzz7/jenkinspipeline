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
svn_path = "/opt/homebrew/bin/svn"
svn_client_path = path + "/" + os.environ.get("svn_client_path").split("/")[-1]
tools_path = path + "/tools"
version_path_svn = path+"/publish_versions/"+os.environ.get("version_path")
dt = datetime.now().strftime("%Y%m%d")
dt2 = datetime.now().strftime("%Y%m%d_%H%M%S")
webapk_client_path = svn_client_path + "/release/webapk_client"
cache_url = os.environ.get("cacheurl")
git_branch = os.environ.get("android_gitbranch")
type = os.environ.get("android_build_type")
Type = "debug" if type == "Debug" else "release"
android_path = workspace.split("jenkins")[0] +"Wartune/android/{}/android_wartune".format(git_branch)


def git_update():
    client_path = workspace.split("jenkins")[0] + "Wartune/android/{}".format(git_branch)
    if os.path.exists(workspace.split("jenkins")[0] +"Wartune/android/{}/android_wartune".format(git_branch)):
        os.chdir(android_path)
        logger.info("当前路径{}".format(os.getcwd()))
        cmd = "git pull"
        logger.info("开始更新git工程 {}".format(cmd))
        os.system(cmd)
    else:
        os.mkdir(client_path)
        os.chdir(client_path)
        logger.info('当前目录'.format(os.getcwd()))
        cmd2 = "git clone -b {} http://xingjian.tian:a123456!!!@192.168.1.94/yuanzhan.yu/android_wartune".format(git_branch)
        logger.info("开始导入工程 {}".format(cmd2))
        os.system(cmd2)

    logger.info("替换文件- local.properties - build.gradle - MainActivity.java")
    shutil.copy(workspace + "/local.properties", client_path + "/android_wartune/local.properties")
    shutil.copy(workspace + "/build.gradle", client_path + "/android_wartune/app/build.gradle")
    cache_name = cache_url.replace(":", "").replace("//", "").replace("/", "")
    logger.info(workspace + "/MainActivity_{}.java".format(cache_name))
    if not os.path.exists(workspace + "/MainActivity_{}.java".format(cache_name)):
        logger.info("未找到{}".format(workspace + "/MainActivity_{}.java".format(cache_name)))
        raise
    shutil.copy(workspace + "/MainActivity_{}.java".format(cache_name), client_path + "/android_wartune/app/src/main/java/demo/MainActivity.java")

    os.chdir(workspace)


def web_client():

    os.chdir(webapk_client_path)
    logger.info("当前路径 {}".format(os.getcwd()))
    # 删除res中指定内容
    delete_web()
    time.sleep(5)
    delete_res()
    # time.sleep(5)
    # delete_png_jpg()
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(webapk_client_path+"/update"):
        raise "layadcc执行失败"


def delete_web():
    lis = os.listdir()
    path = os.getcwd()
    for item in lis:
        if item not in web_list:
            if os.path.isdir(path+"/"+item):
                logger.info("删除目录 - {}".format(path+"/"+item))
                shutil.rmtree(path+"/"+item)
            elif os.path.isfile(path+"/"+item):
                logger.info("删除文件 - {}".format(path + "/" + item))
                os.remove(path+"/"+item)
            else:
                logger.info("{}不是文件也不是目录".format(path + "/" + item))
    logger.info("删除完毕")


def delete_res():
    text = os.environ.get("android_copy_res_file").replace('\\', '/').replace('\n', '')
    target_list = text.split(",") if "," in text else text.split("，")
    for i in range(len(target_list)):
        if target_list[i] == "":
            del target_list[i]
    lis = [i.split("web")[1] for i in target_list]
    # lis = []
    # for line in open(workspace+"/delete_res_config.txt"):
    #     logger.info(f"res_path:{line}")
    #     lis.append(line.split("web")[1].replace('\\', '/').replace('\n', ''))
    path = os.getcwd()
    tar_dir = path+"/res2"
    os.mkdir(tar_dir)
    for item in lis:
        if os.path.isdir(path + item):
            if os.path.exists(tar_dir + "/".join(item.split("/")[:-1])):
                logger.info("目录已存在，复制目录{} 至 {}".format(path+item, tar_dir+item))
                shutil.copytree(path + item, tar_dir+item)
            else:
                logger.info("创建目录 {}".format(tar_dir + "/".join(item.split("/")[:-1])))
                os.makedirs(tar_dir + "/".join(item.split("/")[:-1]))
                logger.info("复制目录{} 至 {}".format(path + item, tar_dir + item))
                shutil.copytree(path + item, tar_dir + item)
        elif os.path.isfile(path + item):
            if os.path.exists(tar_dir + "/".join(item.split("/")[:-1])):
                logger.info("目录已存在，复制文件{} 至 {}".format(path+item, tar_dir+item))
                shutil.copy(path + item, tar_dir+item)
            else:
                logger.info("创建文件目录 {}".format(tar_dir + "/".join(item.split("/")[:-1])))
                os.makedirs(tar_dir + "/".join(item.split("/")[:-1]))
                logger.info("复制文件{} 至 {}".format(path + item, tar_dir + item))
                shutil.copy(path + item, tar_dir + item)
        else:
            logger.info("不存在该目录或文件-{}".format(path + item))
    logger.info("删除{}".format(webapk_client_path+"/res"))
    shutil.rmtree(webapk_client_path+"/res")
    logger.info("移动/res2/res--/res")
    shutil.move(webapk_client_path+"/res2/res", webapk_client_path)
    shutil.rmtree(webapk_client_path+"/res2")
    logger.info("res内容复制完毕")


def layadcc_cache_android(client_path):
    os.chdir(webapk_client_path)
    """
    后续url地址以及url目录地址需要可配置，完成

    """
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./ -cache -url {}".format(cache_url)
    logger.info("执行脚本 -- {}".format(cmd))
    os.system(cmd)
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(android_path))
    #
    if os.path.exists(client_path + "/app/src/main/assets/cache"):
        logger.info("删除目录{}".format(client_path + "/app/src/main/assets/cache"))
        logger.info(os.listdir(client_path + "/app/src/main/assets"))
        shutil.rmtree(client_path + "/app/src/main/assets/cache")
        logger.info(os.listdir(client_path + "/app/src/main/assets"))

    logger.info("复制文件至工程目录")
    shutil.copytree(webapk_client_path + "/layadccout/cache", client_path + "/app/src/main/assets/cache")
    logger.info(os.listdir(client_path + "/app/src/main/assets"))


def android_build():
    os.chdir(android_path)
    if os.path.exists(android_path + "/gradle"):
        shutil.rmtree(android_path + "/gradle")
        logger.info("已删除旧gradle文件夹")
    if os.path.exists(android_path + "/gradlew"):
        os.remove(android_path + "/gradlew")
        logger.info("已删除旧gradlew")
    if os.path.exists(android_path+"/app/build/outputs/apk/{}".format(Type)):
        shutil.rmtree(android_path+"/app/build/outputs/apk/{}".format(Type))
        logger.info("已删除旧{}文件夹".format(Type))
    logger.info("当前路径 -- {}".format(os.getcwd()))
    if type == "Debug":
        logger.info("替换文件- config_debug.ini")
        shutil.copy(workspace + "/config_debug.ini", android_path + "/app/src/main/assets/config.ini")
    elif type == "Release":
        logger.info("替换文件- config_release.ini")
        shutil.copy(workspace + "/config_release.ini", android_path + "/app/src/main/assets/config.ini")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle clean")
    os.system("/opt/gradle/gradle-7.2/bin/gradle clean")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle init")
    os.system("/opt/gradle/gradle-7.2/bin/gradle init")
    logger.info("执行 /opt/gradle/gradle-7.2/bin/gradle wrapper")
    os.system("/opt/gradle/gradle-7.2/bin/gradle wrapper")
    logger.info("执行 {} assemble{}".format("./gradlew", type))
    os.system("{} assemble{}".format("./gradlew", type))


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


def main():
    try:
        git_update()
        web_client()
        layadcc_cache_android(android_path)
        android_build()
        build_sdk_package()
    except Exception as e:
        raise e


if __name__ == '__main__':
    main()


