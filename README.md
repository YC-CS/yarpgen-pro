## OOP-YARPGen

基于随机程序生成器 YARPGen进行扩展，提供以下特性

- 结构体
- 面向对象
- 指针、动态内存分配
- 赋值关键词 (const, static等)



### 一、安装与部署

在项目根目录执行如下指令：

创建 `build` 文件夹

```
mkdir build
cd build
```

编译

```
cmake ..
make
```

执行成功后，产生名为 `yarpgen` 的文件，即可执行文件

```
./yarpgen
```

 生成的 `test.cpp` 即测试程序



### 二、测试脚本

测试脚本位于 `/runner` 路径下

#### 1、默认测试

通过执行如下命令，进行默认测试

```
python3 __main__.py
```

脚本会生成大量测试用例，并进行编译和运行。

在项目根目录的 `/Testing` 路径下，会产生一个名为测试时间的文件夹，其中：

- `/backup` 存放着可能存在bug的测试用例
- `/cases` 存放所有测试用例
- `/log` 存放所有测试日志信息



#### 2、自定义测试

通过 `/runner/default.yaml` 可以自定义测试规模

- language：一般无需改动
- generator_path：指 OOP-YARPGen 的可执行文件路径
- testing_path：测试文件夹路径，用于存放测试用例和日志
- timeout：编译的超时时间（以秒为单位）
- run_count：每次脚本生产的测试用例数量
- compiler：用户指定的编译器列表
- optimization：用户指定的优化选项列表
- extra_option：用户指定的额外编译选项列表
- march：用户指定的架构列表

