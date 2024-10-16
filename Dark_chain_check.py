import html
import re
import os
import threading
import sys
import argparse
import requests
import urllib3
import csv
from datetime import datetime

# 禁用不安全请求的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 请求头设置
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible;Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)'
}

proxies = {
    #'http':'http://127.0.0.1:8080',
    #'https':'http://127.0.0.1:8080',
}
# 从文件中读取正则规则
with open('./config/DarkChainRules.txt', 'r', encoding='utf-8') as s:
    re_rules_list = [rule.strip() for rule in s.read().splitlines() if rule.strip()]

# 存储结果的列表
results = []

def clear_files():
    """ 清空结果文件 """
    for filename in ["darkresult.txt", "dark_role_ruleresult.txt"]:
        if os.path.exists(filename):
            os.remove(filename)

def banner():
    """ 显示帮助信息 """
    print('+------------------------暗链检测工具----------------------------------------------------+')
    print('python Dark_chain_check.py -u/--url -f/--filename')
    print('+---------------------------------------------------------------------------------------+')

def normalize_url(url):
    """ 规范化URL，确保其包含协议 """
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # 默认使用http
    return url

def probe_url(domain):
    """ 尝试获取可用的URL """
    if "http" not in domain:
        for scheme in ['https', 'http']:
            try:
                response = requests.get(f'{scheme}://{domain}', timeout=15, verify=False, headers=headers, proxies=proxies)
                if response.status_code in [200, 403, 404]:
                    return f'{scheme}://{domain}'
            except requests.RequestException as e:
                print(f'尝试访问 {scheme}://{domain} 时出错: {str(e)}')
    else:
        try:
            response = requests.get(f'{domain}', timeout=15, verify=False, headers=headers, proxies=proxies)
            if response.status_code in [200, 403, 404]:
                return f'{domain}'
        except requests.RequestException as e:
            print(f'尝试访问 {domain} 时出错: {str(e)}')
    return None

def find_darkchain(url):
    """ 检查单个URL中的暗链 """
    try:
        print(f"正在检测URL: {url}")  # 输出当前检测的URL
        
        # 尝试探测URL
        final_url = probe_url(url)
        if not final_url:
            print(f'{url} 请求出错：无法连接到该网址或无效的URL')
            return

        # 获取页面内容
        res = requests.get(final_url, headers=headers, timeout=15, verify=False, proxies=proxies).text
        respose = html.unescape(res)

        matched_rules = []  # 存储匹配到的规则
        for re_rule in re_rules_list:
            if re.search(re_rule, respose, re.S | re.I):
                matched_rules.append(re_rule)

        if matched_rules:
            print(f'{final_url} 存在暗链，命中规则---> {matched_rules}')
            results.append([final_url, matched_rules])  # 将结果添加到 results
        else:
            print(f'{final_url} 未检测出暗链，未命中规则')

    except Exception as e:
        print(f'{url} 请求出错，错误信息: {str(e)}')

def save_results_to_files():
    """ 保存结果到文件 """
    # 生成 dark_role_ruleresult.txt 文件
    with open("dark_role_ruleresult.txt", "w", encoding='utf-8') as file2:
        for result in results:
            file2.write(f"URL：{result[0]}\n")
            file2.write(f"匹配规则：{', '.join(result[1])}\n\n")
    print("dark_role_ruleresult.txt 文件已生成。")
    
    # 生成 darkresult.txt 文件
    with open("darkresult.txt", "w", encoding='utf-8') as file2:
        for result in results:
            file2.write(f"{result[0]}\n")
    print("darkresult.txt 文件已生成。")

    # 生成 CSV 文件，使用时间戳 + 后缀名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{timestamp}_darkchain_results.csv"

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["序号", "URL", "匹配到的规则"])  # 写入表头
        for i, result in enumerate(results, start=1):
            csv_writer.writerow([i, result[0], ', '.join(result[1])])  # 写入每一行
    print(f"结果已保存到文件: {csv_filename}")

def open_darkurl_check(filename):
    """ 从文件中读取URL并启动检查 """
    clear_files()  # 清空结果文件
    print('清空旧结果文件完成。')  # 确保打印信息

    with open(filename, 'r', encoding='utf-8') as f:
        urls_list = f.read().splitlines()

    print('检测暗链主线程开始')
    
    # 使用线程池处理多个URL
    thread_list = []
    for url in urls_list:
        normalized_url = normalize_url(url.strip())  # 规范化URL
        t = threading.Thread(target=find_darkchain, args=(normalized_url,))
        t.start()
        thread_list.append(t)

    # 等待所有线程完成
    for t in thread_list:
        t.join()

    print('检测暗链主线程结束')

    # 保存结果到文件
    save_results_to_files()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Help')
    parser.add_argument('-f', '--filename', help='Please Input a file, the option is urls.txt or other', default='')
    parser.add_argument('-u', '--url', help='Please Input a url', default='')
    args = parser.parse_args()
    filename = args.filename
    url = args.url

    if filename == "" and url == "":
        banner()
        sys.exit()
    elif filename == "" and url != "":
        try:
            clear_files()
            normalized_url = normalize_url(url)  # 规范化URL
            final_url = probe_url(normalized_url)  # 先探测URL
            if not final_url:
                print(f'{normalized_url} 请求出错：无法连接到该网址或无效的URL')
                sys.exit()

            # 检查页面内容
            find_darkchain(normalized_url)  # 直接调用函数处理单个URL
            save_results_to_files()
        except Exception as e:
            print(f'{normalized_url} 请求出错，错误信息: {str(e)}')
    elif filename != "" and url == "":
        print(f"正在检测 {filename} 中的站点")
        open_darkurl_check(filename)
    else:
        banner()
        sys.exit()
