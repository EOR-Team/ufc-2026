# 后端开发配置教程

本文档在 `ubuntu 24.04` &amp; `Python 3.12.0 with pyenv` 环境下通过测试。

## 1. 安装依赖

首先，确保系统包是最新的：

```bash
$ sudo apt update && sudo apt upgrade -y
```

然后，安装以下系统依赖：

```bash
$ sudo apt install -y build-essential cmake
```

接下来，创建 Python 虚拟环境并激活它：

```bash
$ cd backend
$ python -m venv ./venv
$ source ./venv/bin/activate
```

然后，安装 Python 依赖：

如果你打算使用 __*CPU*__ 进行本地推理 **(推荐)** ，请用下面的指令指定 *OpenBLAS* 版本后安装：

```bash
$ CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    pip install -r requirements.txt --timeout 300
```

如果你打算使用 __*GPU*__ 进行本地推理 **(不推荐)**，请遵循以下步骤进行安装：

1. 安装 *NVIDIA* 驱动， *cuDNN* 和 *CUDA* 工具包。

2. 安装 并 配置 *llama.cpp* - [Official Docs Here](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

3. 使用以下命令安装 Python 依赖：

```bash
$ CMAKE_ARGS="-DGGML_CUDA=on" \
    pip install -r requirements.txt --timeout 300
```