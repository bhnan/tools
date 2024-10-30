# 介绍
该项目用来爬取 Bing 的每日一图，并且记录爬取时间和地点的信息。

# 安装

1. 克隆此仓库到本地：
    ```sh
    git clone <仓库地址>
    ```
2. 进入项目目录：
    ```sh
    cd bing_daily_picture
    ```
3. 安装依赖：
    ```sh
    pip install -r requirements.txt
    ```
4. 安装对应版本的ChromeDriver到python环境更目录下
   下载地址链接为https://googlechromelabs.github.io/chrome-for-testing/#canary


# 使用

1. 在 `bing_daily_picture/picture.py` 文件中填写图片保存路径和智谱AI的 API_KEY：
    ```python
    if __name__ == "__main__":
        path = "你的图片保存路径"  # 请填写你图片保存的文件路径
        api_key = "你的智谱AI的API_KEY"  # 请填写你的智谱AI的API_KEY
        main(path, api_key)
    ```

2. 也可以使用 `run.bat` 文件来运行脚本：
    ```bat
    chcp 65001
    cd C:\Users\Users\Desktop\每日一图   # 请根据实际情况修改路径
    python picture.py
    pause
    ```

