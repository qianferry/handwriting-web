[English](README_en.md) | [中文](README.md)

# 手写文字生成网站

欢迎来到我的手写文字生成网站！这个平台允许你使用现有的字体来创建模拟手写文字的图片。

网址：https://handwrite.paperai.life
![Alt text](image.png)

## 功能

### 自定义字体

你可以上传自己的字体来生成符合你需求的独特手写风格。

### 背景图片

上传你想要的背景图片，为你的手写文字添加个人风格。如果你没有背景图片，别担心！只需指定图片的宽度和高度，我的网站将自动为你生成带有横线的背景图片。

### 可调参数

你可以完全控制各种参数，如边距（上、下、左、右），字符间的随机扰动，笔画的旋转偏移，墨水的深度变化，涂改痕迹。这使你可以微调你的手写文字的外观。

### 从各种文件类型中提取文本

我的网站可以从各种文件类型中提取文本内容（如 pdf，docs），使你能够方便地上传文本。

### 预览功能

我在网站的右侧添加了预览功能。这使你可以在最终确定之前方便地查看你的手写文字图片的效果。

### 完整图片生成

一旦你对预览满意，你可以生成一整套图片。这些图片将被方便地打包成一个 zip 文件，以便于下载。

### pdf 导出功能

一键生成 pdf，不用再手动粘贴图片

## 自己搭建的方法

克隆项目，在项目目录中使用`docker-compose up -d`，默认端口为 2345

若要添加字体，字体文件放在项目根目录下的 ttf_files 中

## 系统环境
虚拟机初始化
```
sudo yum install -y openssh-server
vi /etc/ssh/sshd_config
Port 22：定义 SSH 监听的端口号，默认为 22。
ListenAddress 0.0.0.0
PermitRootLogin yes：设置是否允许 root 登录，默认允许。
PasswordAuthentication yes：设置是否使用口令认证方式，若要使用公钥认证方式，可将其设置为 no。

sudo systemctl start sshd
sudo systemctl enable sshd
sudo systemctl status sshd
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

ip a

重启

```

更换YUM源为国内源
```
备份原有的YUM源配置：
bash
cd /etc/yum.repos.d/
mkdir backup && mv *repo backup/

下载阿里云的YUM源配置：
bash
wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-8.repo

清除YUM缓存并生成新的缓存：
bash
yum clean all
yum makecache

验证当前配置的YUM源：
bash
yum repolist all
```

Python 3.9.19
```shell


su -

sudo dnf update

下载 Python 3.9.19 源码包
bash
wget https://www.python.org/ftp/python/3.9.19/Python-3.9.19.tgz

3. 解压源码包
bash
tar -xzf Python-3.9.19.tgz

4. 创建安装目录
bash
mkdir /usr/local/python3

5. 编译安装 Python 3.9.19
bash
cd Python-3.9.19
./configure --prefix=/usr/local/python3 --enable-optimizations
make && make altinstall

--prefix指定安装路径，--enable-optimizations可以提高 10-20% 的性能。
使用 make altinstall 而不是 make install，可以避免覆盖系统自带的 Python 2.x。
6. 创建软链接
bash
ln -s /usr/local/python3/bin/python3.9 /usr/bin/python39
ln -s /usr/local/python3/bin/pip3.9 /usr/bin/pip39

7. 验证安装
bash
python39 --version
pip39 --version

出现版本号说明安装成功。
8. 配置 pip 国内源
bash
mkdir ~/.pip
vim ~/.pip/pip.conf

添加以下内容:
text
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com

保存后即可使用国内源安装 Python 包。
```
系统：CentOS 8.0.1905 x86_64
- https://archive.kernel.org/centos-vault/8.0.1905/isos/x86_64/
- 选择 CentOS-8-x86_64-1905-dvd1.iso

node
```
安装Node.js v18.20.4
```
python
```
1.更换国内源
2.根据错误提示安装前置工具
```

端口占用
```
sudo lsof -i :8080
kill -9 <PID>
```

## 本地运行
1. 克隆项目到本地
2. 进入backend文件夹，运行后端程序
```shell
cd backend
pip install -r requirements.txt
python app.py
```
3. 进入frontend文件夹，运行前端程序
```shell
cd frontend
npm install
npm run serve
```
4. 打开浏览器，输入http://localhost:8080，即可访问网站

## 结语

我希望你喜欢使用我的手写文字生成网站来创建你的个性化手写文字图片！

## 随笔
2024.6.13 由于昨天需要完成政治论文的手写，于是亲自体验了我的程序，发现效果确实不错，但是几个月来一直没有解决处理大量文字的时候程序没响应的问题，经过我添加日志发现，其实后端一直在生成图片，但是由于nginx的超时限制导致请求失败（这个在docker的日志中可以看到），于是我修改了外部和镜像内部的nginx的超时配置，但是问题仍然存在，这时我发现前端控制台中不再是504错误而是524错误，经过查询发现这是因为cf的超时限制是100秒，超过cf的限制而报错，解决方法是关闭小黄云不享受cf的保护，还有一种解决方法就是让后端不断给前端传输数据保持连接活跃。
