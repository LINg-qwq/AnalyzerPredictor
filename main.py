from generate_data import *


def main():
    # ɨ�貢������Ŀ������·��
    # ������� .\my_data\app_dict.pkl
    print("Scanning C Project...")
    get_project_info()

    # ʹ��pycparser������ת��ΪAST��ʹ�þ�̬�������������벢���ݽ������label
    # ������� .\my_data\ast_label.pkl
    print("Analyzing and Parsing project code...")
    analyze_and_parse_C_code()

    # ����ѵ�����Ͳ��Լ�
    # ����ֱ����
    # ѵ������.\my_data\train_set.pkl
    # ���Լ���.\my_data\test_set.pkl
    print("Split dataset...")
    divide_dataset('5:1:1')


#     todo


if __name__ == "__main__":
    main()
