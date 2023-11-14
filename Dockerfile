# 使用 aarch64 架构的 Python 镜像
FROM arm64v8/python:3.9-alpine

# 安装 gcc 和其他编译依赖
RUN apk add --no-cache build-base libffi-dev

# 复制文件到容器内
COPY ./utils /srv/utils/
COPY ./requirements.txt /tmp
COPY ./miuitask.py /srv/

# 定义数据卷（这里定义数据卷在 Dockerfile 中不会生效，它需要在 docker run 命令中指定）
VOLUME ["/srv/data"]

# 安装依赖项和 PyInstaller
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install pyinstaller && \
    rm -rf /tmp/*

# 使用 PyInstaller 编译 Python 脚本
RUN pyinstaller -F /srv/miuitask.py

# 设置工作目录
WORKDIR /srv

# 定义运行时的命令（这里用 crond 作为示例，但实际上你可能想要运行编译后的二进制文件）
CMD ["/usr/sbin/crond", "-f"]
