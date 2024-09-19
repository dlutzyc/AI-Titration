# Copyright (c) 慕乐网络科技(大连)有限公司(MoolsNet Inc.) and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup, find_packages

setup(
    name='Automatic_Titration_Control',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,  # 确保您有MANIFEST.in文件来指定要包含的文件
    install_requires=[
        'tensorflow',
        'numpy',
        'torch',
        'Pillow',
        'scikit-learn',
        'opencv-python',
        'pyautogui',
        'pyserial'
    ],
    # 其他有用的元数据选项
    description='A package for reporting similar items',  # 简短的描述
    long_description=open('README.md').read(),  # 如果存在README.md文件，可以读取其内容作为长描述
    long_description_content_type='text/markdown',  # 如果README.md是Markdown格式，请指定内容类型
    author='慕乐网络科技(大连)有限公司(MoolsNet Inc.)',  # 作者或组织名
    author_email='moolsnet@126.com',  # 作者的电子邮件地址
    classifiers=[  # 分类信息，帮助用户了解包
        'Development Status :: 3 - Alpha',  # 这表示项目目前处于开发阶段，并且是Alpha版本。Alpha版本通常意味着软件的功能尚未完整，可能包含严重的错误，不适合生产环境使用。
        'Intended Audience :: Developers',  # 这表示项目主要面向开发者。这意味着包可能包含一些高级功能或API，主要用于构建其他软件，而不是直接面向最终用户
        'Topic :: Software Development :: Build Tools', # 这表示项目是关于软件开发，特别是构建工具的。这告诉用户包可能用于自动化构建过程、管理依赖关系或其他与软件构建相关的任务。
        'License :: OSI Approved :: MIT License',   # 这表示项目使用MIT许可证。MIT许可证是一种非常宽松的开源许可证，允许用户自由地使用、修改和分发代码，但通常要求他们保留原始版权和许可信息。
        'Programming Language :: Python :: 3.10',   #这表示项目是用Python编写的，并且支持Python 3.10版本。这告诉用户他们需要有Python 3.10环境来运行代码。
        # 其他分类...
    ],
)
