import pickle
import struct

import pandas
import pandas as pd
import pycparser
import random
import xml.etree.ElementTree as ET
import os

app_path = r'E:\GraduationDesign\apps'
project_info_pickle_path = r'.\my_data\app_dict.pkl'
analyzer_dict = {
    0: 'TscanCode',
    1: 'FlawFinder',
    2: 'CPPCheck',
    3: 'VisualCodeGrepper'
}


def get_project_info():
    # app_dict {'项目名称':'项目路径'}
    if os.path.exists(project_info_pickle_path):
        print("Exist project info pickle already")
    else:
        app_dict = {}
        for root, dirs, files in os.walk(app_path):
            if root != app_path:
                break
            for project_dir_name in dirs:
                project_dir_path = os.path.join(root, project_dir_name)
                app_dict[project_dir_name] = project_dir_path
        print('Found ' + str(len(app_dict)) + ' projects')
        df = pd.DataFrame.from_dict(app_dict, orient='index').reset_index()
        df.columns = ['project_name', 'project_dir_path']
        pd.set_option('expand_frame_repr', False)
        print(df)
        df.to_pickle(project_info_pickle_path)
        print("Saved projects' name and path as pickle")


def analyze_and_parse_C_code():
    print("Reading project info pickle...")
    project_dict_df = pd.read_pickle(project_info_pickle_path)
    project_dict = dict(zip(project_dict_df['project_name'], project_dict_df['project_dir_path']))

    # key:项目名称 value:项目路径
    for key, value in project_dict.items():
        print("Analyzing and parsing C code files of project:" + str(key))
        c_file_path_list = search_c_file(value)

        for c_file_path in c_file_path_list:
            # 转化为AST
            ast = get_AST(c_file_path)

            # 使用静态分析器分析并判断效果
            result = analyze_and_compare(c_file_path)
    print()


def search_c_file(dir_name) -> list:
    c_file_path_list = []
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            if file.endswith(".c"):
                c_file_path = os.path.join(root, file)
                # print(c_file_path)
                c_file_path_list.append(c_file_path)
    return c_file_path_list


def get_AST(file_path):
    ast = pycparser.parse_file(file_path, use_cpp=True)
    # ast.show()
    return ast


def analyze_and_compare(file_path) -> int:
    result_error_num_list = []
    for key, value in analyzer_dict:
        error_num = invoke_analyzer_by_name(value, file_path)
        result_error_num_list.append(error_num)

    def get_all_max_element_index(src_list) -> list:
        result = []
        for i in range(len(src_list)):
            if src_list[i] == max(result_error_num_list):
                result.append(i)
        return result

    best_analyzer_index_list = get_all_max_element_index(result_error_num_list)
    # 当有相同的错误检测数量时，随机选择一个
    if len(best_analyzer_index_list) > 1:
        return random.choice(best_analyzer_index_list)
    elif len(best_analyzer_index_list) == 1:
        return best_analyzer_index_list[0]
    else:
        return -1


def invoke_analyzer_by_name(name, file_path) -> int:
    """
    Args:
        name: 分析器名称
        file_path: 要分析的C文件路径
    Returns:
        找到的缺陷个数
    """
    full_func_name = str(name) + '_analyze'
    # 根据函数名调用对应的分析函数
    return eval(full_func_name)(file_path)


def exec_cmd(cmd):
    """
    Args:
        cmd: 要执行的命令
    Returns:
        控制台的输出
    """
    r = os.popen(cmd, 'r')
    text = r.read()
    r.close()
    return text


def get_file_name_with_suffix_from_path(file_path) -> str:
    split_list = str.split(file_path, '\\')
    depth = len(split_list)
    return split_list[depth - 1]


def get_file_name_from_path(file_path) -> str:
    full_name = get_file_name_with_suffix_from_path(file_path)
    return str.split(full_name, '.')[0]


def TscanCode_analyze(file_path):
    full_file_name = get_file_name_with_suffix_from_path(file_path)
    file_name = get_file_name_from_path(file_path)
    inst_pre = "tscancode --xml "
    inst_mid = " 2>./TscanCodeResult/"
    inst_post = "_TscanCode.xml"
    # full instruction will be like:
    # tscancode --xml E:\GraduationDesign\apps\clamav\clamav-milter\allow_list.c 2>./TscanCodeResult/allow_list.c_TscanCode.xml
    full_inst = inst_pre + str(file_path) + inst_mid + full_file_name + inst_post
    result = exec_cmd(r'cd E:\GraduationDesign\Analyzer\TscanCodeWin && ' + full_inst)

    try:
        xml_tree = ET.parse("./TscanCodeResult/" + file_name + inst_post)
        root = xml_tree.getroot()
        errors = root.findall('error')
        if errors is None:
            return 0
        else:
            count = 0
            for error in errors:
                # 只计算Critical和Serious，不计算Warning,Style等
                if str(error.get('severity')) in ['Critical', 'Serious']:
                    count = count + 1
            return count
    except:
        print("Error occurred when TscanCode analyzing " + str(file_path))
        return -1


def FlawFinder_analyze(file_path):
    # cd E:\Anaconda\Anaconda\envs\python36\Scripts &&
    #  .\flawfinder.exe --csv > E:\GraduationDesign\Analyzer\flawfinder-2.0.19\FlawFinderResult\FlawFinder_allow_list.csv E:\GraduationDesign\apps\clamav\clamav-milter\allow_list.c
    file_name = get_file_name_from_path(file_path)
    inst_pre = r".\flawfinder.exe --csv > "
    result_file_path = r"E:\GraduationDesign\Analyzer\flawfinder-2.0.19\FlawFinderResult\FlawFinder_" + file_name + ".csv"
    full_inst = r"cd E:\Anaconda\Anaconda\envs\python36\Scripts && " + inst_pre + result_file_path + " " + file_path
    result = exec_cmd(full_inst)

    try:
        result_file = open(result_file_path, 'rb+')
        line_num = len(result_file.readlines())
        if line_num < 3:
            return -1
        elif line_num == 3:
            line = open(result_file_path, 'rb+').readlines()[1]
            if line == b'\x00\r\x00\n':
                return 0
        else:
            count = 0
            df = pandas.read_csv(result_file_path)
            for index, data in df.iterrows():
                # 只计算严重等级为4和5的错误
                if int(data["Level"]) > 3:
                    count = count + 1
            return count
    except:
        print("Error occurred when FlawFinder analyzing " + str(file_path))
        return -1


def CPPCheck_analyze(file_path):
    # todo
    # cppcheck E:\GraduationDesign\apps\clamav\clamav-milter\allow_list.c --enable=all --output-file=E:\GraduationDesign\Analyzer\cppcheck\qwq.xml --xml
    return 1


def VisualCodeGrepper_analyze(file_path):
    # todo
    return 1


def divide_dataset(ratio):
    # todo：分割数据集
    ratios = [int(r) for r in ratio.split(':')]
    print("111")