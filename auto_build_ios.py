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
from config1 import web_list
from plistlib import readPlist, writePlist


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
workspace = os.environ["WORKSPACE"]
path = workspace.split("jenkins")[0] + "Wartune/svn"
svn_path = "/opt/homebrew/bin/svn"
svn_client_path = path + "/" + os.environ.get("svn_client_path").split("/")[-1]
tools_path = path + "/tools"
dt = datetime.now().strftime("%Y%m%d")
dt2 = datetime.now().strftime("%Y%m%d_%H%M%S")
# dt2 = "20221024_120345"
webipa_client_path = svn_client_path + "/release/webipa_client"
git_branch = os.environ.get("ios_gitbranch")
ios_path = workspace.split("jenkins")[0] + "Wartune/ios/{}/ios_wartune".format(git_branch)
cacheurl = "stand.alone.version"
build_path = workspace.split("jenkins")[0] + "Wartune/ios/build/{}".format(dt2)
build_type = os.environ.get("ios_build_type")
plist_build_path = workspace.split("jenkins")[0] + "/jenkins/workspace/plist/export_adhoc.plist" if build_type == "测试版" \
    else workspace.split("jenkins")[0] + "/jenkins/workspace/plist/export_appstore.plist"
ipa_name = "Wartune_{}_{}.ipa".format("adhoc", dt2) if build_type == "测试版" \
    else "Wartune_{}_{}.ipa".format("appstore", dt2)
plist_path = workspace.split("jenkins")[0] + "/jenkins/workspace/plist/example_1.plist"
up_path = workspace.split("jenkins")[0] + "/jenkins/workspace/sqh5_pkg_upload.py"



def git_update():
    client_path = workspace.split("jenkins")[0] + "Wartune/ios/{}".format(git_branch)
    if os.path.exists(workspace.split("jenkins")[0] +"Wartune/ios/{}/ios_wartune".format(git_branch)):
        os.chdir(ios_path)
        logger.info("当前路径{}".format(os.getcwd()))
        cmd = "git pull"
        logger.info("开始更新git工程 {}".format(cmd))
        os.system(cmd)
    else:
        os.mkdir(client_path)
        os.chdir(client_path)
        logger.info('当前目录'.format(os.getcwd()))
        cmd2 = "git clone -b {} http://xingjian.tian:a123456!!!@192.168.1.94/yuanzhan.yu/ios_wartune".format(git_branch)
        logger.info("开始导入工程 {}".format(cmd2))
        os.system(cmd2)
    os.chdir(workspace)


def web_client():

    os.chdir(webipa_client_path)
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
    if not os.path.exists(webipa_client_path+"/update"):
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
    text = os.environ.get("ios_copy_res_file").replace('\\', '/').replace('\n', '')
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
    logger.info("删除{}".format(webipa_client_path+"/res"))
    shutil.rmtree(webipa_client_path+"/res")
    logger.info("移动/res2/res--/res")
    shutil.move(webipa_client_path+"/res2/res", webipa_client_path)
    shutil.rmtree(webipa_client_path+"/res2")
    logger.info("res内容复制完毕")


def layadcc_cache_ios(client_path):
    os.chdir(webipa_client_path)
    """
    后续url地址以及url目录地址需要可配置，完成

    """
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    cmd = "/Users/jun.nie/.nvm/versions/node/v8.17.0/bin/layadcc ./ -cache -url {}".format(cacheurl)
    logger.info("执行脚本 -- {}".format(cmd))
    os.system(cmd)
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(ios_path))
    #
    if os.path.exists(client_path + "/Wartune/resource/cache"):
        logger.info("删除目录{}".format(client_path + "/Wartune/resource/cache"))
        logger.info(os.listdir(client_path + "/Wartune/resource"))
        shutil.rmtree(client_path + "/Wartune/resource/cache")
        logger.info(os.listdir(client_path + "/Wartune/resource"))

    logger.info("复制文件至工程目录")
    shutil.copytree(webipa_client_path + "/layadccout/cache", client_path + "/Wartune/resource/cache")
    logger.info(os.listdir(client_path + "/Wartune/resource"))


def ios_build():
    os.system("echo \"123456\" | sudo -S chmod -R 777 {}".format(workspace.split("jenkins")[0] + "Wartune/ios"))
    if os.path.exists(workspace.split("jenkins")[0] + "Wartune/ios/build"):
        logger.info("删除build文件夹")
        shutil.rmtree(workspace.split("jenkins")[0] + "Wartune/ios/build")
    os.makedirs(build_path)
    ios_client = ios_path + "/Wartune"
    os.chdir(ios_client)
    logger.info("当前路径为 -- {}".format(os.getcwd()))
    os.system("echo \"123456\" | sudo -S security unlock-keychain -p \"123456\" ~/Library/Keychains/login.keychain")
    logger.info("开始构建xcarchive")
    cmd1 = "echo \"123456\" | sudo -S xcodebuild clean"
    logger.info(cmd1)
    os.system(cmd1)
    cmd2 = "echo \"123456\" |sudo -S xcodebuild archive -project {} -configuration Release -archivePath {} -scheme Wartune".format(ios_client+"/Wartune.xcodeproj", build_path+"/Wartune.xcarchive")
    logger.info(cmd2)
    os.system(cmd2)
    if "Wartune.xcarchive" in os.listdir(build_path):
        logger.info(".xcarchive生成成功")
    else:
        raise ".xcarchive生成失败"
    cmd3 = "echo \"123456\" |sudo -S xcodebuild -exportArchive -archivePath {} -exportPath {} -exportOptionsPlist {}".format(build_path+"/Wartune.xcarchive", build_path, plist_build_path)
    logger.info(cmd3)
    os.system(cmd3)
    flag = 1
    ipa_path = ""
    for item in os.listdir(build_path):
        if os.path.splitext(item)[-1] == ".ipa":
            logger.info("ipa生成成功")
            ipa_path = build_path+"/"+item
            flag = 0
    if flag == 1:
        raise "ipa生成失败"
    logger.info(build_type)
    logger.info(plist_build_path)
    os.rename(ipa_path, build_path+"/"+"{}".format(ipa_name))


def plist():
    os.chdir(build_path)
    logger.info(os.listdir())
    example_name = ipa_name.replace(".ipa", ".plist")
    ipa_cmd = "echo \"123456\" |sudo -S python3 {} {} {}".format(up_path, "sqh5_cn_ios", ipa_name)
    example_cmd = "echo \"123456\" |sudo -S python3 {} {} {}".format(up_path, "sqh5_cn_ios", example_name)
    example_plist = readPlist(plist_path)
    example_plist["items"][0]["assets"][0]["url"] = "https://sqh5-apk-1301056917.cos.ap-guangzhou.myqcloud.com/{}/{}".format("sqh5_cn_ios", ipa_name)
    # example_plist["items"][0]["thinned-assets"][0]["url"] = "https://sqh5-pkg-cdn.wan.com/{}/{}".format("sqh5_cn_ios", ipa_name)
    writePlist(example_plist, "{}/{}".format(build_path, example_name))
    logger.info("开始上传ipa")
    os.system(ipa_cmd)
    logger.info("开始上传plist")
    os.system(example_cmd)
    download_path = "itms-services://?action=download-manifest&url=https://sqh5-apk-1301056917.cos.ap-guangzhou.myqcloud.com/{}/{}".format("sqh5_cn_ios", example_name)
    msg = "在线安装成功\n" \
          "在Safari中输入下载地址\n" \
          "下载地址：{}\n" \
          "完成时间：{}\n".format(download_path, dt2)
    send_email(msg)


def send_email(msg):
    # url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=91a105b7-cf31-43e7-b893-feb11b62e848"
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=72f7898c-7c59-46c7-9ca3-80634137124b"
    # url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d783d968-0416-48ca-92f1-462ec57c5d1c"
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
        git_update()
        web_client()
        layadcc_cache_ios(ios_path)
        ios_build()
        plist()

    except Exception as e:
        raise e


if __name__ == '__main__':
    main()