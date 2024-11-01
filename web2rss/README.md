# web2rss

## 介绍
`web2rss` 项目用于从指定的网站抓取博客文章，并生成 RSS 订阅源。该项目使用 Selenium 和 BeautifulSoup 来抓取网页内容，并使用 Feedgen 来生成 RSS 订阅源。

## 安装

1. 克隆此仓库到本地：
    ```sh
    git clone <仓库地址>
    ```
2. 进入项目目录：
    ```sh
    cd web2rss
    ```
3. 创建并激活虚拟环境（可选）：
    ```sh
    python -m venv venv
    source venv/bin/activate  # 对于 Windows 系统，使用 `venv\Scripts\activate`
    ```
4. 安装依赖：
    ```sh
    pip install -r requirements.txt
    ```

## 配置

1. 编辑 `config.json` 文件，添加你想要抓取的网站配置：
    ```json
    {
        "sites": [
            {
                "name": "anthropic_news",
                "follow_desc": "feedId:71805759203098624+userId:71370844472670208",
                "url": "https://www.anthropic.com/research",
                "block_css": "a.PostCard_post-card___tQ6w",
                "title_css": "h3",
                "description_css": ".PostCard_post-info__gybiy",
                "link_css": "",
                "use_headless_browser": true
            }
        ]
    }
    ```

## 使用

1. 运行脚本生成 RSS 订阅源：
    ```sh
    python web2rss/gen_rss.py
    ```

2. 生成的 RSS 文件将保存在 `rss` 目录下。

## 致谢

特别感谢 [https://github.com/xxcdd/web2rss](https://github.com/xxcdd/web2rss) 项目提供的灵感和部分代码参考。