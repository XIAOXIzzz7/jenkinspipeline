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
# svn_client_path = path + "/wartune_performance_1.2"
svn_client_path = path + "/" + os.environ.get("svn_client_path").split("/")[-1]
version_path = os.path.dirname(workspace)+"/version"
dt = datetime.now().strftime("%Y%m%d")
dt2 = datetime.now().strftime("%Y%m%d_%H%M%S")
# dt2 = "1"
# android_path = workspace.split("jenkins")[0] +"Wartune/android/android_wartune"
android_path = ""
ios_path = workspace.split("jenkins")[0] +"Wartune/ios/ios_warturne"
web_client_path = svn_client_path + "/release/web_client"
git_branch = os.environ.get("gitbranch")
type = os.environ.get("Type")
Type = "debug" if type == "Debug" else "release"
cache_url = os.environ.get("cacheurl")
# build_apk = os.environ.get("build_apk")
run_mode = os.environ.get("run_mode")
version_path_svn = path+"/publish_versions/"+os.environ.get("version_path")
web_pkg_upload = os.environ.get("web_pkg_upload")


def svn_update():

    logger.info("开始更新tools -- svn update {}".format(tools_path))
    os.system("{} revert -R {}".format(svn_path, tools_path))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, tools_path))
    logger.info("开始更新publish_versions -- svn update {}".format(version_path_svn))
    os.system("{} revert -R {}".format(svn_path, version_path_svn))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
    if os.path.exists(svn_client_path):
        logger.info("开始更新svn_client -- svn update {}".format(svn_client_path))
        os.system("{} revert -R {}".format(svn_path, svn_client_path))
        os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_client_path))
    else:
        logger.info("svn工程不存在，开始获取时间较长请稍等")
        os.chdir(path)
        logger.info("当前路径-{}".format(os.getcwd()))
        cmd = "{} co {} --username sqh5 --password sqh5sqh5".format(svn_path, os.environ.get("svn_client_path"))
        # logger.info("执行-{}".format(cmd))
        os.system(cmd)
    # logger.info("替换文件- laya.core.js")
    # shutil.copy(workspace + "/laya.core.js", svn_client_path+"/bin/libs/laya.core.js")
    """
    当前资源全部在svn_client中不需要转换与替换
    """
    # logger.info("开始更新svn_sql -- svn update {}".format(svn_sql_path))
    # os.system("{} revert -R {}".format(svn_path, svn_sql_path))
    # os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path))
    # logger.info(resource_path)
    # if os.path.exists(resource_path):
    #     logger.info("开始更新resource -- svn update {}".format(resource_path))
    #     os.system("{} revert -R {}".format(svn_path, resource_path))
    #     os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, resource_path))
    # else:
    #     logger.info('目录不存在开始创建--{}'.format(resource_path))
    #     os.system("mkdir {}".format(resource_path))
    #     cmd = "{} checkout {} {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_url, resource_path)
    #     logger.info("开始执行命令 --{}".format(cmd))
    #     status = os.system(cmd)
    #     logger.info("当前状态-- {}".format(status))


def git_update():
    client_path = workspace.split("jenkins")[0] + "Wartune/android/{}".format(git_branch)
    global android_path
    android_path = workspace.split("jenkins")[0] +"Wartune/android/{}/android_wartune".format(git_branch)
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
    if run_mode == "build_apk":
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


def sql_copy():
    logger.info("复制sql文件")
    zip_path = workspace + "/sql/server/dts/data"
    os.makedirs(zip_path)
    old_file_list = os.listdir(svn_sql_path)
    for item in old_file_list:
        if os.path.splitext(item)[-1] == ".sql" or os.path.splitext(item)[-1] == ".txt":
            shutil.copy(svn_sql_path + "/" + item, zip_path)
    zip_dir(workspace+"/sql", "./server.zip")
    shutil.rmtree(workspace+"/sql")


def zip_dir(dirpath, outFullName):
    logger.info("开始压缩文件夹")
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def sql2_Utf8():
    shutil.copy(tools_path+"/sql2json/format.json", workspace)
    cmd = f"python3 {tools_path}/sql2json/sql2json.py server.zip"
    logger.info("执行脚本-- {}".format(cmd))
    os.system(cmd)
    cmd2 = f"python3 {tools_path}/sql2json/Utf8Change.py config"
    logger.info("执行脚本-- {}".format(cmd2))
    os.system(cmd2)
    file_list = os.listdir(workspace+"/config2")
    logger.info(file_list)
    logger.info("移动config2内文件至 {}".format(svn_client_path+"/bin/res/config"))
    for item in file_list:
        shutil.copy(workspace+"/config2/"+item, svn_client_path+"/bin/res/config")


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
    # logger.info("删除png与jpg")
    # jpg_png_path = os.path.join(svn_client_path, "bin/res")
    # delete_jpg_png(jpg_png_path)
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "/usr/local/bin/npm run build"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    ### client_path = workspace.split("jenkins")[0] + "Wartune/android/{}".format(git_branch)
    ### shutil.copy(workspace + "/publish.js", client_path + "/android_wartune/local.properties")
    cmd2 = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layaair2-cmd publish -c web"

    logger.info("执行命令 -- {}".format(cmd2))
    logger.info("路径{}".format(os.getcwd()))
    os.system(cmd2)
    if not os.path.exists(svn_client_path+"/release/web/index.js"):
        lis = os.listdir(svn_client_path + "/release/web")
        for item in lis:
            if item.startswith('index') and item.endswith('.js'):
                shutil.copy(f'{svn_client_path}/release/web/{item}', f'{svn_client_path}/release/web/index.js')
    if run_mode == "build_apk":
        logger.info("复制一份web为web_client")
        shutil.copytree(svn_client_path + "/release/web", web_client_path)
    if run_mode == "build_all" or run_mode == "build_server.zip":
        web_server()
    if run_mode == "build_apk":
        web_client(web_client_path)


def version_update1():
    logger.info("开始更新svn -- svn update {}".format(version_path_svn))
    os.system("{} revert -R {}".format(svn_path, version_path_svn))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
    if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"))):
        logger.info("当前版本文件夹已存在-{}".format(os.environ.get("versionName")))
    else:
        os.mkdir(version_path_svn + "/" + os.environ.get("versionName"))
        logger.info("创建文件夹并上传-{}".format(os.environ.get("versionName")))
        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"))))
        os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
            "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))
    if run_mode == "build_all":
        logger.info("压缩web为web_all.zip")
        os.makedirs(svn_client_path + "/release/web_server/server/webapp/wartune")
        shutil.copytree(svn_client_path + "/release/web",
                        svn_client_path + "/release/web_server/server/webapp/wartune/7road")
        zip_dir(svn_client_path + "/release/web_server",
                svn_client_path + "/release/web_all.zip")
        ssh_update(svn_client_path + "/release/web_all.zip")
        web_all_path = svn_client_path + "/release/web_all.zip"
        logger.info("web_all_path:{}".format(web_all_path))
        md5 = ""
        if os.path.isfile(web_all_path):
            fp = open(web_all_path, "rb")
            contents = fp.read()
            fp.close()
            md5 = hashlib.md5(contents).hexdigest()
        else:
            logger.info("file not exists")
            raise
        msg = "web_all.zip上传完毕！\n" \
              "md5：{}\n" \
              "完成时间：{}\n".format(md5, dt2)
        send_email(msg)
        version_type = True
        logger.info("整包不需要版本对比与上传,保存version")
        if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json")):
            version_type = False
            logger.info("version.json已存在，重命名version.json")
            shutil.move(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json"),
                        os.path.join(version_path_svn, os.environ.get("versionName"), "version_{}.json".format(dt2)))
            logger.info("add1")
            os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                                "version_{}.json".format(dt2))))
        logger.info("开始复制version.json")
        shutil.copy(svn_client_path + "/release/web/version.json",
                    version_path_svn + "/" + os.environ.get("versionName"))
        if version_type:
            logger.info("add2")
            os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                                "version.json")))
        os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
            "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))

    # elif run_mode == "build_apk":
    #     version_type = True
    #     logger.info("保存version")
    #     if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json")):
    #         version_type = False
    #         logger.info("version.json已存在，重命名version.json")
    #         shutil.move(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json"),
    #                     os.path.join(version_path_svn, os.environ.get("versionName"), "version_{}.json".format(dt2)))
    #         logger.info("add1")
    #         os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
    #                                                             "version_{}.json".format(dt2))))
    #     logger.info("开始复制version.json")
    #     shutil.copy(svn_client_path + "/release/web/version.json",
    #                 version_path_svn + "/" + os.environ.get("versionName"))
    #     if version_type:
    #         logger.info("add2")
    #         os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
    #                                                             "version.json")))
    #     os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
    #         "versionName") + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))
    elif run_mode == "build_server.zip":
        if os.path.exists(version_path_svn+"/"+os.environ.get("选择对比差分版本")+"/version.json") == False:
            logger.info("差分失败,该文件不存在"+version_path_svn+"/"+os.environ.get("选择对比差分版本")+"/version.json")
            return
        else:
            # os.chdir(svn_client_path + "/release/web")
            logger.info("当前路径为 -- {}".format(os.getcwd()))
            logger.info("开始对version.json文件开始进行版本对比")
            cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py",
                                             version_path_svn+"/"+os.environ.get("选择对比差分版本")+"/version.json",
                                            svn_client_path + "/release/web")
            logger.info("执行命令 -- {}".format(cmd))
            logger.info("当前路径为 -- {}".format(os.getcwd()))
            os.system(cmd)
            if not os.path.exists(svn_client_path + "/release/web/patch.zip"):
                raise "VersionDiff.py执行失败"
            logger.info("差分对比完毕，上传patch.zip")
            os.rename(svn_client_path + "/release/web/patch.zip", svn_client_path + "/release/web/web_patch_{}.zip".format(os.environ.get("versionName")))
            ssh_update(svn_client_path + "/release/web/web_patch_{}.zip".format(os.environ.get("versionName")))
            patch_path = svn_client_path + "/release/web/web_patch_{}.zip".format(os.environ.get("versionName"))
            logger.info("patch_path:{}".format(patch_path))
            md5 = ""
            if os.path.isfile(patch_path):
                fp = open(patch_path, "rb")
                contents = fp.read()
                fp.close()
                md5 = hashlib.md5(contents).hexdigest()
            else:
                logger.info("file not exists")
                raise
            msg = "web_patch_{}.zip上传完毕！\n" \
                  "md5：{}\n" \
                  "完成时间：{}\n".format(os.environ.get("versionName"), md5, dt2)
            send_email(msg)
            version_type = True
            if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json")):
                logger.info("version.json已存在，重命名version.json")
                version_type = False
                shutil.move(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json"),
                            os.path.join(version_path_svn, os.environ.get("versionName"), "version_{}.json".format(dt2)))
                logger.info("add1")
                os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                                    "version_{}.json".format(dt2))))
            logger.info("开始复制version.json")
            shutil.copy(svn_client_path + "/release/web/version.json",
                        version_path_svn + "/" + os.environ.get("versionName"))
            if version_type:
                os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                                    "version.json")))
                logger.info("add2")
            os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
                "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))






# def svn_commit():
#     os.chdir(version_path_svn)
#     logger.info("当前路径为 -- {}".format(os.getcwd()))
#     logger.info("当前路径-{}".format(os.getcwd()))
#     logger.info("开始更新svn -- svn update {}".format(version_path_svn))
#     os.system("{} revert -R {}".format(svn_path, version_path_svn))
#     os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
#
#     os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"))))
#     os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾"+os.environ.get("versionName")+dt,
#                                           os.path.join(version_path_svn, os.environ.get("versionName"))))



# def version_update():
#     if run_mode == "build_all":
#         logger.info("整包不需要版本对比与上传,保存version")
#         shutil.copy(svn_client_path + "/release/web/version.json",
#                     version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"),
#                                                               os.environ.get("versionName"), git_branch, type))
#         shutil.copy(svn_client_path + "/release/web/version.json",
#                     version_path + "/last_{}_{}.json".format(git_branch, type))
#         logger.info("压缩web为server.zip")
#         zip_dir(svn_client_path + "/release/web", svn_client_path + "/release/server.zip")
#         ssh_update(svn_client_path + "/release/server.zip")
#     elif run_mode == "build_server.zip":
#         if os.path.exists(version_path + "/last_{}_{}.json".format(git_branch, type)) == False:
#             logger.info("差分失败，未找到last_{}_{}.json，首次执行请先执行build_all".format(git_branch, type))
#         else:
#             logger.info("开始对version.json文件开始进行版本对比")
#             logger.info("当前路径为 -- {}".format(os.getcwd()))
#             logger.info("复制一份到workspace下")
#             shutil.copy(version_path + "/last_{}_{}.json".format(git_branch, type), workspace + "/version.json")
#             logger.info(os.listdir(workspace))
#
#             cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py",
#                                             workspace + "/version.json",
#                                             svn_client_path + "/release/web")
#             logger.info("执行命令 -- {}".format(cmd))
#             os.system(cmd)
#             if not os.path.exists(svn_client_path + "/release/web/server.zip"):
#                 raise "VersionDiff.py执行失败"
#             ssh_update(svn_client_path + "/release/web/server.zip")
#             logger.info("替换last_version")
#             shutil.copy(svn_client_path + "/release/web/version.json",
#                         version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"),
#                                                                   os.environ.get("versionName"), git_branch, type))
#             shutil.copy(svn_client_path + "/release/web/version.json",
#                         version_path + "/last_{}_{}.json".format(git_branch, type))

    # if os.path.exists(version_path+"/last_{}_{}.json".format(git_branch, type)):
    #     logger.info("存在version.json文件开始进行版本对比")
    #     logger.info("当前路径为 -- {}".format(os.getcwd()))
    #     logger.info("复制一份到workspace下")
    #     shutil.copy(version_path + "/last_{}_{}.json".format(git_branch, type), workspace + "/version.json")
    #     logger.info(os.listdir(workspace))
    #
    #     cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py",
    #                                     workspace + "/version.json",
    #                                     svn_client_path + "/release/web")
    #     logger.info("执行命令 -- {}".format(cmd))
    #     os.system(cmd)
    #     if not os.path.exists(svn_client_path + "/release/web/server.zip"):
    #         raise "VersionDiff.py执行失败"
    #     ssh_update(svn_client_path + "/release/web/server.zip")
    #     logger.info("替换last_version")
    #     shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"), os.environ.get("versionName"), git_branch, type))
    #     shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/last_{}_{}.json".format(git_branch, type))
    # elif os.path.exists(version_path+"/last_{}_{}.json".format(git_branch, type)) == False and run_mode == "build_server.zip":
    #     logger.info("差分失败，未找到last_{}_{}.json，首次执行请先执行build_all".format(git_branch, type))
    #     return
    # else:
    #     logger.info("首包不需要版本对比与上传,保存version")
    #     shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/{}_{}_{}_{}.json".format(os.environ.get("versionCode"), os.environ.get("versionName"), git_branch, type))
    #     shutil.copy(svn_client_path + "/release/web/version.json", version_path + "/last_{}_{}.json".format(git_branch, type))


def resource_copy():
    logger.info("复制资源文件animation")
    logger.info(os.listdir(svn_client_path+"/bin/res"))
    shutil.rmtree(svn_client_path+"/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))

    shutil.copytree(resource_path+"/animation", svn_client_path+"/bin/res/animation")
    logger.info(os.listdir(svn_client_path + "/bin/res"))
    if not os.path.exists(svn_client_path+"/bin/res/animation"):
        raise "resource_copy执行错误"


def layadcc_cache_android(client_path):
    os.chdir(web_client_path)
    """
    后续url地址以及url目录地址需要可配置，完成
    
    """
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./ -cache -url {}".format(cache_url)
    logger.info("执行脚本 -- {}".format(cmd))
    os.system(cmd)
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(android_path))
    #
    if os.path.exists(client_path+"/app/src/main/assets/cache"):
        logger.info("删除目录{}".format(client_path+"/app/src/main/assets/cache"))
        logger.info(os.listdir(client_path+"/app/src/main/assets"))
        shutil.rmtree(client_path+"/app/src/main/assets/cache")
        logger.info(os.listdir(client_path + "/app/src/main/assets"))

    logger.info("复制文件至工程目录")
    shutil.copytree(web_client_path+"/layadccout/cache", client_path+"/app/src/main/assets/cache")
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


# def ios_build():
#     pass


def delete():
    if os.path.exists(svn_client_path+"/release"):
        logger.info("删除release")
        shutil.rmtree(svn_client_path+"/release")
        logger.info("创建release")
        os.mkdir(svn_client_path+"/release")
    # if os.path.exists(svn_client_path+"/release/web"):
    #     shutil.rmtree(svn_client_path + "/release/web")
    #     logger.info("删除web")
    # if os.path.exists(svn_client_path + "/release/web_server"):
    #     shutil.rmtree(svn_client_path + "/release/web_server")
    #     logger.info("删除web_server")
    # if os.path.exists(web_client_path):
    #     shutil.rmtree(web_client_path)
    #     logger.info("删除web_client")
    # if os.path.exists(svn_client_path+"/release/server.zip"):
    #     os.remove(svn_client_path+"/release/server.zip")
    #     logger.info("删除server.zip")
    # if os.path.exists(svn_client_path+"/release/web1"):
    #     shutil.rmtree(svn_client_path+"/release/web1")
    #     logger.info("删除web1")
    # if os.path.exists(svn_client_path+"/release/web.zip"):
    #     os.remove(svn_client_path+"/release/web.zip")
    #     logger.info("删除web.zip")


def ssh_update(server_path):
    autoscp_path = workspace.split("jenkins")[0]+"jenkins/workspace/autoscp.sh"
    serverzip_path = server_path
    # serverzip_path = workspace.split("jenkins")[0]+"jenkins/workspace/server1.zip"
    cmd = "sh {} {}".format(autoscp_path, serverzip_path)
    logger.info("上传server.zip {}".format(cmd))
    os.system(cmd)


def web_client(web_client_path):

    os.chdir(web_client_path)
    logger.info("当前路径 {}".format(os.getcwd()))
    # 删除res中指定内容
    logger.info("删除png与jpg")
    jpg_png_path = os.path.join(web_client_path, "bin/res")
    delete_jpg_png(jpg_png_path)
    delete_web()
    time.sleep(5)
    delete_res()
    # time.sleep(5)
    # delete_png_jpg()
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(web_client_path+"/update"):
        raise "layadcc执行失败"


def web_server():
    os.chdir(svn_client_path + "/release/web")
    logger.info("当前路径 {}".format(os.getcwd()))
    #res内可能有需要删除的内容
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    if not os.path.exists(svn_client_path + "/release/web/update"):
        raise "layadcc执行失败"

    version_update1()


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
    text = os.environ.get("copy_res_file").replace('\\', '/').replace('\n', '')
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
    logger.info("删除{}".format(web_client_path+"/res"))
    shutil.rmtree(web_client_path+"/res")
    logger.info("移动/res2/res--/res")
    shutil.move(web_client_path+"/res2/res", web_client_path)
    shutil.rmtree(web_client_path+"/res2")
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


def web_pkg():
    logger.info("开始更新svn -- svn update {}".format(version_path_svn))
    os.system("{} revert -R {}".format(svn_path, version_path_svn))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
    web_type = True
    logger.info("压缩web后续上传svn")
    shutil.copytree(svn_client_path + "/release/web", svn_client_path + "/release/web1/web")
    zip_dir(svn_client_path + "/release/web1", svn_client_path + "/release/web.zip")
    if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"))):
        logger.info("当前版本文件夹已存在-{}".format(os.environ.get("versionName")))
    else:
        os.mkdir(version_path_svn + "/" + os.environ.get("versionName"))
        logger.info("创建文件夹并上传-{}".format(os.environ.get("versionName")))

        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"))))
        os.system(
            "{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
                "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))
    if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"), "web.zip")):
        logger.info("web.zip已存在，重命名web.zip")
        web_type = False
        shutil.move(os.path.join(version_path_svn, os.environ.get("versionName"), "web.zip"),
                    os.path.join(version_path_svn, os.environ.get("versionName"), "web_{}.zip".format(dt2)))
        logger.info("add1")
        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                            "web_{}.zip".format(dt2))))
    logger.info("复制web至svn目录下")
    shutil.copy(svn_client_path + "/release/web.zip", os.path.join(version_path_svn, os.environ.get("versionName")))
    if web_type:
        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                            "web.zip")))
        logger.info("add2")
    os.system(
        "{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
            "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))


def apk_version():
    logger.info("开始更新svn -- svn update {}".format(version_path_svn))
    os.system("{} revert -R {}".format(svn_path, version_path_svn))
    os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, version_path_svn))
    if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"))):
        logger.info("当前版本文件夹已存在-{}".format(os.environ.get("versionName")))
    else:
        os.mkdir(version_path_svn + "/" + os.environ.get("versionName"))
        logger.info("创建文件夹并上传-{}".format(os.environ.get("versionName")))

        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"))))
        os.system(
            "{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
                "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))
    version_type = True
    logger.info("保存version")
    if os.path.exists(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json")):
        version_type = False
        logger.info("version.json已存在，重命名version.json")
        shutil.move(os.path.join(version_path_svn, os.environ.get("versionName"), "version.json"),
                    os.path.join(version_path_svn, os.environ.get("versionName"), "version_{}.json".format(dt2)))
        logger.info("add1")
        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                            "version_{}.json".format(dt2))))
    logger.info("开始复制version.json")
    shutil.copy(svn_client_path + "/release/web/version.json",
                version_path_svn + "/" + os.environ.get("versionName"))
    if version_type:
        logger.info("add2")
        os.system("{} add {}".format(svn_path, os.path.join(version_path_svn, os.environ.get("versionName"),
                                                            "version.json")))
    os.system("{} commit -m {} {} --username sqh5 --password sqh5sqh5".format(svn_path, "上传文件夾" + os.environ.get(
        "versionName") + "_" + dt, os.path.join(version_path_svn, os.environ.get("versionName"))))


def send_email(msg):
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72f7898c-7c59-46c7-9ca3-80634137124b"
    _time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    data = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    _data = json.dumps(data)
    response = requests.post(url, data=_data, headers={"Content-Type": "application/json"})


def main():
    try:
        if run_mode == "build_server.zip" and os.environ.get("选择对比差分版本") == os.environ.get("versionName"):
            raise "对比差分版本不可以和当前版本相同"
        if run_mode == "build_server.zip" and os.environ.get("选择对比差分版本") == None:
            raise "对比差分时未选择对比版本"
        if run_mode == "build_apk":
            try:
                int(os.environ.get("versionCode"))
                int(os.environ.get("gameVersionCode"))
            except:
                raise "versionCode or gameVersionCode is not integer type"
        delete()
        svn_update()
        git_update()
        clint_build()
        if run_mode == "build_apk":
            layadcc_cache_android(android_path)
            android_build()
            build_sdk_package()
            apk_version()
        if web_pkg_upload == "true":
            web_pkg()



        # os.chdir("/Users/jun.nie/Wartune/svn/test/wartune_performance_1.2")
        # os.system("layaair2-cmd publish -c web")


        # delete()
        # os.chdir(svn_client_path + "/release/web")
        # version_update1()
        # if web_pkg_upload == "true":
        #     web_pkg()
    except Exception as e:

        raise e

    # svn_update()
    # git_update()
    """
    测试中手动替换 后续svn提交上去后打开
    """
    ## resource_copy()
    ## sql_copy()
    ## sql2_Utf8()

    # clint_build()
    # if run_mode == "build_apk":
    #     layadcc_cache_android(android_path)
    #     android_build()
    #     build_sdk_package()
    # svn_commit()











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

