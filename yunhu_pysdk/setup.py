from setuptools import setup, find_packages

setup(
    name="yunhu_pysdk",
    version="0.1.0",
    author="ShanFish",
    author_email="zcsfish@qq.com",
    description="基于Flask的开源云湖社交机器人SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),  # 排除测试目录
    install_requires=[
        "requests>=2.25.1",
        "loguru>=0.6.0",
        "flask>=2.3.2"
    ],
    extras_require={
        "dev": ["pytest", "mypy"],
    },
    python_requires=">=3.8",
    package_data={
        "yunhu_pysdk": ["config/*.json"],
    },
    entry_points={
        "console_scripts": ["yunhu-cli=yunhu_pysdk.cli:main"],
    },
)