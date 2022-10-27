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
run_mode = os.environ.get("run_mode")
dt = datetime.now().strftime("%Y%m%d")
dt2 = datetime.now().strftime("%Y%m%d_%H%M%S")
webapk_client_path = svn_client_path + "/release/webapk_client"
webipa_client_path = svn_client_path + "/release/webipa_client"
web_pkg_upload = os.environ.get("web_pkg_upload")
build_os = os.environ.get("build_os")
svn_sql_path = os.environ.get("svn_sql_path")
svn_sql_path_local = path + "/svn_sql"
"""
http://test2.svn.7road-inc.com/svn/slg/WartuneH5/数据表管理/svn_sql/inland/V2.4.6-1.2.0.9
"""

def delete():
    if os.path.exists(svn_client_path+"/release"):
        logger.info("删除release")
        shutil.rmtree(svn_client_path+"/release")
        logger.info("创建release")
        os.mkdir(svn_client_path+"/release")


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
        os.system(cmd)
    if os.path.exists(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]):
        if os.path.exists(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2]):
            logger.info("开始更新svn_sql -- svn update {}".format(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2]))
            os.system("{} revert -R {}".format(svn_path, svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2]))
            os.system("{} update {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2]))
        else:
            logger.info("暂未拉过该版本，开始拉取")
            os.chdir(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1])
            logger.info("当前路径-{}".format(os.getcwd()))
            cmd = "{} co {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path)
            os.system(cmd)
    else:
        logger.info("暂未拉过该分支与该版本，开始拉取")
        os.mkdir(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1])
        os.chdir(svn_sql_path_local + "/" + svn_sql_path.split("svn_sql")[1].split("/")[1])
        logger.info("当前路径-{}".format(os.getcwd()))
        cmd = "{} co {} --username sqh5 --password sqh5sqh5".format(svn_path, svn_sql_path)
        os.system(cmd)
    os.chdir(workspace)


def clint_build():
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(svn_client_path))
    os.chdir(svn_client_path)
    logger.info("当前路径-{}".format(os.getcwd()))
    if os.environ.get("del_png_jpg") == "true":
        logger.info("删除png与jpg")
        jpg_png_path = os.path.join(svn_client_path, "bin/res")
        delete_jpg_png(jpg_png_path)
    else:
        logger.info("保留png与jpg")
    if os.environ.get("del_ktx") == "true":
        logger.info("删除ktx")
        ktx_path = os.path.join(svn_client_path, "bin/res")
        delete_ktx(ktx_path)
    else:
        logger.info("保留ktx")
    cmd = "/usr/local/bin/npm run build"
    logger.info("执行命令 -- {}".format(cmd))
    os.system(cmd)
    cmd2 = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layaair2-cmd publish -c web"

    logger.info("执行命令 -- {}".format(cmd2))
    logger.info("路径{}".format(os.getcwd()))
    os.system(cmd2)
    if not os.path.exists(svn_client_path+"/release/web/index.js"):
        lis = os.listdir(svn_client_path + "/release/web")
        for item in lis:
            if item.startswith('index') and item.endswith('.js'):
                shutil.copy(f'{svn_client_path}/release/web/{item}', f'{svn_client_path}/release/web/index.js')

    if build_os == "all":
        logger.info("复制webapk_client与webipa_client")
        shutil.copytree(svn_client_path + "/release/web", webapk_client_path)
        shutil.copytree(svn_client_path + "/release/web", webipa_client_path)
    elif build_os == "android":
        logger.info("复制webapk_client")
        shutil.copytree(svn_client_path + "/release/web", webapk_client_path)
    elif build_os == "ios":
        logger.info("复制webipa_client")
        shutil.copytree(svn_client_path + "/release/web", webipa_client_path)
    # if run_mode == "full" or run_mode == "diff":
    web_server()


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


def delete_ktx(path):
    if os.path.isfile(path):
        if os.path.splitext(path)[-1] == ".ktx":
            try:
                os.remove(path)
                logger.info("删除{}".format(path))
            except Exception as e:
                print(e)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            delete_ktx(itempath)


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
    if run_mode == "full":
        logger.info("压缩web为web_all.zip")
        os.makedirs(svn_client_path + "/release/web_server/server/webapp/wartune")
        shutil.copytree(svn_client_path + "/release/web",
                        svn_client_path + "/release/web_server/server/webapp/wartune/7road")
        zip_dir(svn_client_path + "/release/web_server",
                svn_client_path + "/release/web_all.zip")
        # if build_os == "not_build":
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
              "推送服务器地址：\n{}\n" \
              "完成时间：{}\n".format(md5, os.environ.get("push_server").replace(";", "\n"), dt2)
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
    elif run_mode == "diff":
        if os.path.exists(version_path_svn+"/"+os.environ.get("diff_version")+"/version.json") == False:
            logger.info("差分失败,该文件不存在"+version_path_svn+"/"+os.environ.get("diff_version")+"/version.json")
            return
        else:
            # os.chdir(svn_client_path + "/release/web")
            logger.info("当前路径为 -- {}".format(os.getcwd()))
            logger.info("开始对version.json文件开始进行版本对比")
            cmd = "python3 {} {} {}".format(tools_path + "/VersionDiff/VersionDiff.py",
                                             version_path_svn+"/"+os.environ.get("diff_version")+"/version.json",
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
                  "推送服务器地址：\n{}\n" \
                  "完成时间：{}\n".format(os.environ.get("versionName"), md5, os.environ.get("push_server").replace(";", "\n"), dt2)
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
    elif run_mode == "pkg":
        apk_version()


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


def zip_dir(dirpath, outFullName):
    logger.info("开始压缩文件夹")
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def send_email(msg):
    # url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=91a105b7-cf31-43e7-b893-feb11b62e848"
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


def ssh_update(server_path):
    autoscp_path = workspace.split("jenkins")[0]+"jenkins/workspace/autoscp.sh"
    serverzip_path = server_path
    # serverzip_path = workspace.split("jenkins")[0]+"jenkins/workspace/server1.zip"
    cmd = "sh {} {}".format(autoscp_path, serverzip_path)
    logger.info("上传server.zip {}".format(cmd))
    os.system(cmd)


def sql_copy():
    logger.info("复制文件至指定目录")
    zip_path = workspace + "/sql/server/dts/data"
    os.makedirs(zip_path)
    old_file_list = os.listdir(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2])
    for item in old_file_list:
        if os.path.splitext(item)[-1] == ".sql" or os.path.splitext(item)[-1] == ".txt":
            shutil.copy(svn_sql_path_local+"/"+svn_sql_path.split("svn_sql")[1].split("/")[1]+"/"+svn_sql_path.split("svn_sql")[1].split("/")[2] + "/" + item, zip_path)
    zip_dir(workspace + "/sql", "./server.zip")
    shutil.rmtree(workspace + "/sql")


def sql2_Utf8():
    logger.info("当前路径-{}".format(os.getcwd()))
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


def main():
    try:
        if run_mode == "diff":
            if os.path.exists(version_path_svn + "/" + os.environ.get("diff_version") + "/version.json") == False:
                logger.info("差分失败,该文件不存在" + version_path_svn + "/" + os.environ.get("diff_version") + "/version.json")
                return
        delete()
        svn_update()
        sql_copy()
        sql2_Utf8()
        clint_build()
        if web_pkg_upload == "true":
            web_pkg()
    except Exception as e:
        raise e


if __name__ == '__main__':
    main()
