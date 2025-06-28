# PythonCiweimaoDownloader

#### 介绍
使用python编写的针对刺猬猫的下载程序，可以轻而易举地登录，自动识别付费章节，自动调用ocr模型识别文字，下载小说并自动压入epub

#### 下载链接
https://wwob.lanzoum.com/b0ko7ra2b
密码:a5f4

#### 使用教程

4. 先下载release中的python压缩包（zip和7z内容一样），并把它解压到一个名为python的文件夹下
3. 再下载此项目的源代码的压缩包，并解压到一个纯英文路径的文件夹（比如D:\cwmDown）
2. 把刚才的python文件夹挪到源代码根目录下（比如下载\python ->  D:\cwmDown\python）
1. 双击运行A1 Run.bat
0. 输入`python main.py`
1.  首次运行，会自动下载chrome浏览器
2.  最好挂上能上谷歌的梯
3.  运行脚本，初次运行时稍作等待后会自动由Chrome打开刺猬猫登录界面，正常登录后不要关闭浏览器窗口，在脚本的命令控制台按下回车。若一切正常，稍后会自动打印出你的login_token和user_id和reader_id
4.  输入你要下载的小说的url，按下回车
5.  等待下载完成..
6.  脚本根目录会出现小说id命名的文件夹，里面有你想要的一切东西

#### 参与贡献

由于本项目使用的轻量级ocr模型识别效果可能不很好，如果出现了识别错误，请把book/xxxxxx/img文件夹中相应章节的 xxx.jpg文件发到reimu1@qq.com邮箱中。
同时，我也在积极地寻找app端用的api
