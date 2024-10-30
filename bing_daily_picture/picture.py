import requests
import datetime
import re
from selenium import webdriver
from zhipuai import ZhipuAI
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def extract_json_from_string(out):
    pattern = re.compile(r"```[\s\S]*```")
    s = pattern.findall(out)
    if s:    
        s1 = s[0].replace("```","")
        s1 = s1.replace("json","")
        return s1
    else:
        return out

def get_formatted_title(pic_title, api_key):
    prompt = '''
    请将输入改写为可以作为windows文件名的形式。
    要求中文即可，并且按输出格式输出，不要做额外输出。

    ***注意***
    一定要注意，输出要为中文。
    一定要注意输出格式为json格式，否则无法通过测试。
    请注意参考的输出格式案例。

    ***输入***
    ''' + pic_title + '''

    ***输出格式***
    输出格式：{"reasoning":{解释一步一步解决问题的过程},"result":最后的提取的文件名}

    ***例子***
    input:每日一图: 奇迹湖附近池塘里的北美海狸，德纳里国家公园，阿拉斯加州，美国

    输出：{"reasoning":"推理过程","result":"每日一图_奇迹湖附近池塘里的北美海狸_德纳里国家公园_阿拉斯加州_美国"}
    '''

    client = ZhipuAI(api_key=api_key)
    context = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型名称
        messages=context,
        temperature=0.01,
    )
    res = extract_json_from_string(response.choices[0].message.content)
    try:
        return json.loads(res)["result"]
    except json.JSONDecodeError:
        print(json.JSONDecodeError) 
        with open("log.txt", "a") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d"))
            f.write(res)
            f.write("---------------------------------------------------/n")
            f.close()
        exit(0)

def fetch_image():
    # 创建一个浏览器实例
    driver = webdriver.Chrome()
    print("浏览器实例已经创建")
    # 打开网页
    driver.get('https://cn.bing.com/?mkt=zh-CN#')
    print("网页已经打开")

    element1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.hpapp > div > div:nth-child(1) > div.hp_media_container > div.img_cont > div.img_uhd"))
    )
    element2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#headline"))
    )
    actions = ActionChains(driver)
    actions.move_to_element(element2)
    actions.perform()
    elememt3 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#vs_cont > div.mc_caro > div.musCard.focusin > div.musCardCont > h3 > a"))
    )
    print("元素已经加载")

    # 提取元素的 style 属性
    style_attribute = element1.get_attribute('style')
    title_attribute = elememt3.get_attribute('aria-label')
    driver.quit()

    pattern = re.compile(r'url\("([^"]+\.jpg)')
    pic_href = pattern.findall(style_attribute)
    return pic_href[0], title_attribute

def main(path, api_key):
    pic_href, pic_title = fetch_image()
    formatted_title = get_formatted_title(pic_title, api_key)
    curr_time = datetime.datetime.now()
    pic = requests.get(pic_href)

    file_path = path + curr_time.strftime("%Y-%m-%d") + "_" + formatted_title + ".jpg"
    with open(file_path, "wb") as f:
        f.write(pic.content)

if __name__ == "__main__":
    path = "" ### 请填写你图片保存的文件路径
    api_key = "" ### 请填写你的智谱AI的API_KEY
    main()
