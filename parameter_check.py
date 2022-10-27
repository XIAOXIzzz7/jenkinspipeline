import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

workspace = os.environ.get('WORKSPACE').replace('/sqh5_client_autobuild_parameter_check', '/')
run_mode = os.environ.get('run_mode')
push_server = os.environ.get('push_server')
build_os = os.environ.get('build_os')
diff_version = os.environ.get('diff_version')
svn_client_path = os.environ.get('svn_client_path')
svn_sql_path = os.environ.get('svn_sql_path')
del_png_jpg = os.environ.get('del_png_jpg')
del_ktx = os.environ.get('del_ktx')
web_pkg_upload = os.environ.get('web_pkg_upload')
version_path = os.environ.get('version_path')
versionCode = os.environ.get('versionCode')
versionName = os.environ.get('versionName')
gameVersionCode = os.environ.get('gameVersionCode')
gameVersionName = os.environ.get('gameVersionName')
android_build_type = os.environ.get('android_build_type')
cacheurl = os.environ.get('cacheurl')
android_gitbranch = os.environ.get('android_gitbranch')
ios_gitbranch = os.environ.get('ios_gitbranch')
android_copy_res_file = os.environ.get('android_copy_res_file')
ios_copy_res_file = os.environ.get('ios_copy_res_file')
channels_parameter = os.environ.get('渠道参数')

error_msg = '\n'


def check_parameters():
    global error_msg
    if not svn_client_path:
        error_msg += "错误信息：svn_client_path为必须填项\n"
    if not svn_sql_path:
        error_msg += "错误信息：svn_sql_path为必须填项\n"
    if del_png_jpg == del_ktx == 'true':
        error_msg += "错误信息：不能同时勾选del_png_jpg和del_ktx\n"
    if run_mode != 'pkg':
        if not push_server:
            error_msg += "错误信息：打整包或差分包必须勾选需要推送的服务器\n"
        if not versionName:
            error_msg += "错误信息：打差分包和整包时，versionName为必填项\n"
    if run_mode == 'diff':
        if not diff_version:
            error_msg += "错误信息：打差分包时，diff_version为必填项\n"
    if build_os == 'android':
        if not versionName or not versionCode or not gameVersionName or not gameVersionCode:
            error_msg += "错误信息：Android打包时，versionName，versionCode， gameVersionName， gameVersionCode为必填项\n"
        if versionName and versionCode and gameVersionName and gameVersionCode:
            try:
                int(versionCode)
                int(gameVersionCode)
            except ValueError:
                error_msg += "错误信息：versionCode和gameVersionCode必须为自然数\n"
            try:
                for version in [versionName, gameVersionName]:
                    for n in version.split('.'):
                        int(n)
            except ValueError:
                error_msg += "错误信息：versionName和gameVersionName格式不规范\n"
        if not android_copy_res_file:
            error_msg += "错误信息：Android打包时，android_copy_res_file为必填项\n"
    if build_os != 'not_build':
        if not versionName or not versionCode or not gameVersionName or not gameVersionCode:
            error_msg += "错误信息：Android&iOS打包时，versionName，versionCode， gameVersionName， gameVersionCode为必填项\n"
        if versionName and versionCode and gameVersionName and gameVersionCode:
            try:
                int(versionCode)
                int(gameVersionCode)
            except ValueError:
                error_msg += "错误信息：versionCode和gameVersionCode必须为自然数\n"
            try:
                for version in [versionName, gameVersionName]:
                    for n in version.split('.'):
                        int(n)
            except ValueError:
                error_msg += "错误信息：versionName和gameVersionName格式不规范\n"
        if build_os == 'android':
            if not android_copy_res_file:
                error_msg += "错误信息：Android打包时，android_copy_res_file为必填项\n"
        if build_os == 'ios':
            if not ios_copy_res_file:
                error_msg += "错误信息：iOS打包时，ios_copy_res_file为必填项\n"
        if build_os == 'all':
            if not android_copy_res_file or not ios_copy_res_file:
                error_msg += "错误信息：Android打包时，android_copy_res_file为必填项\n"
                error_msg += "错误信息：iOS打包时，ios_copy_res_file为必填项\n"
    if diff_version == versionName:
        error_msg += "错误信息：diff_version和versionName不可以相同\n"


def save_ip_file():
    servers = push_server.split(';') if push_server else []
    server_types = []
    server_ips = []
    for server in servers:
        server_type, server_name, server_ip = server.split("_")
        if server_type not in server_types:
            server_types.append(server_type)
        server_ips.append(server_ip)
    if len(server_types) > 1:
        raise RuntimeError("不能内外网同时打包推送")
    if run_mode != 'pkg' and not server_ips:
        raise RuntimeError("整包和差分打包时，必须选择推送的服务器")
    if server_ips:
        ip_text = open(f'{workspace}/ip.txt', 'w')
        for s in server_ips:
            ip_text.write(f"{s}\n")
        ip_text.close()


if __name__ == "__main__":
    check_parameters()
    if error_msg == '\n':
        save_ip_file()
    else:
        logger.info(error_msg)
        raise RuntimeError

