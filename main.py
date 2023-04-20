from generate_data import *


def main():
    # 扫描并保存项目名称与路径
    # 结果存入 .\my_data\app_dict.pkl
    print("Scanning C Project...")
    get_project_info()

    # 使用pycparser将代码转化为AST，使用静态分析器分析代码并根据结果打上label
    # 结果存入 .\my_data\ast_label.pkl
    print("Analyzing and Parsing project code...")
    analyze_and_parse_C_code()

    # 划分训练集和测试集
    # 结果分别存入
    # 训练集：.\my_data\train_set.pkl
    # 测试集：.\my_data\test_set.pkl
    print("Split dataset...")
    divide_dataset('5:1:1')


#     todo


if __name__ == "__main__":
    main()
