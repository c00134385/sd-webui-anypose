import os
import sys

current_script = os.path.realpath(__file__)
work_basedir = os.path.dirname(current_script)  # 本插件目录
base = os.path.normpath(work_basedir + r"/poses")


def findAllFile(dir):
    for root, ds, fs in os.walk(dir):
        for f in fs:
            yield os.path.join(root, f)

def findAllFiles():
    dic = {}
    for f in os.listdir(base):
        filepath = os.path.join(base, f)
        if os.path.isdir(filepath):
            dic1 = {}
            for ff in os.listdir(filepath):
                # 获取文件扩展名
                file_name, file_ext = os.path.splitext(ff)
                # print(f'{file_name} {file_ext}')
                # 判断文件扩展名是否为json格式
                if file_ext.lower() == '.json':
                    # print(f'file-name: {file_name}')
                    dic1[file_name] = os.path.join(filepath, ff)
            dic[f] = dic1
    return dic


def main():
    print(f'{base} {os.path.exists(base)}')
    dic = findAllFiles()
    print(f'dic: {dic}')
    # for f in os.listdir(base):
    #     filepath = os.path.join(base, f)
    #     if os.path.isdir(filepath):
    #         dic[f] = findAllFiles(filepath)
    # print(f'dic: {dic}')
    # for i in findAllFile(base):
    #     print(f'------------ {i}')
    #     (filepath, tempfilename) = os.path.split(i)
    #     filepathname = os.path.dirname(filepath)
    #     # 获取文件扩展名
    #     # file_base_name = os.path.splitext(tempfilename)[0]
    #     # print(f'dic: {dic[filepath]}')
    #     # if dic[filepath] is None:
    #     #     dic[filepath] = {}
        
    #     # dic[filepath] += {file_base_name: tempfilename}
    #     print(f'{filepathname} {filepath}  {tempfilename}')

    # print(f'dic: {dic}')

if __name__ == '__main__':
    main()