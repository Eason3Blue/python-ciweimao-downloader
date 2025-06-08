# PythonCiweimaoDownloader

#### 介绍
使用python编写的针对刺猬猫的下载程序，采用了简单易懂的模块化设计，用main.py将一切粘连起来，可以简单地登陆，下载小说并自动压入epub，要求安装了chrome浏览器

2.登录:获得login_token，reader_id，user_id，ci_session
3.等待用户输入book_id
4.获得书籍信息:AccessKey, Keys, Content
5.下载并解码每一章的内容
6.每章各生成一个html文件
7.合并所有html文件


#### 安装教程

1.  安装Chrome浏览器
2.  最好挂上能上谷歌的梯(因为本项目使用 ChromeDriverManager 自动下载 ChromeDriver )
3.  下载
4.  运行脚本，初次运行时稍作等待后会自动由Chrome打开刺猬猫登录界面，正常登录后不要关闭浏览器窗口，在脚本的命令控制台按下回车。若一切正常，稍后会自动打印出你的login_token和user_id和reader_id
5.  输入你要下载的book_id，完成后按下回车
6.  等待下载完成..
7.  脚本根目录会出现小说名字命名的文件夹，里面有封面图片(cover.jpg)和以小说名字命名的html文件
8.  最后，脚本会自动打包章节进入一个epub文件

#### 使用说明

1.  安装Chrome
2.  下载本项目的Release中的可执行文件
3.  按步骤做

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
