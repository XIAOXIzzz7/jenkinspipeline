import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
workspace = os.environ["WORKSPACE"]
path = workspace.split("jenkins")[0] + "Wartune/svn"
version_path_svn = path+"/publish_versions/"+os.environ.get("version_path")


# def search():
#     version_list = []
#     for item in os.listdir(version_path_svn):
#         lis = os.listdir(os.path.join(version_path_svn, item))
#         if "version.json" in lis:
#             version_list.append(item)
#     return version_list
#
#
# if __name__ == '__main__':
#     lis = search()
#     logger.info("存在version.json的版本")
#     for i in lis:
#         logger.info(i)
for item in os.listdir(version_path_svn):
    print(item)