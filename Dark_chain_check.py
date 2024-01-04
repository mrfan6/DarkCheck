import html,re,os,threading,sys,argparse,requests,urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Referer':'https://www.baidu.com/'
}
with open(f'./config/DarkChainRules.txt', 'r',encoding='utf-8') as s:
    re_rules_list = s.read().split('\n')
def clear_darkresult():#每次执行darkresult.txt"文件都会清空，不想清空可以把该函数注释
    if os.path.exists("darkresult.txt"):
        os.remove("darkresult.txt")
def banner():
    print('+------------------------暗链检测工具----------------------------------------------------+')
    print('python Dark_chain_check.py -u/--url -f/--filename')
    print('+---------------------------------------------------------------------------------------+')

def probe_url(domain):
    try:
        # 尝试使用https协议
        response = requests.get(f'https://{domain}', timeout=5, verify=False)
        if response.status_code == 200 or response.status_code == 403:
            return f'https://{domain}'
    except requests.RequestException:
        try:
            # 尝试使用http协议
            response = requests.get(f'http://{domain}', timeout=5, verify=False)
            if response.status_code == 200 or response.status_code == 403:
                return f'http://{domain}'
        except requests.RequestException:
            print("HTTP错误")
            return domain
    return domain

def FindDarkchain(urls):
    for url in urls:
        try:
            if "http" not in url:
                # url = "http://" + url
                url = probe_url(url)
            if "http" not in url:
                print('{} 请求出错'.format(url))
            else:
                res=requests.get(url,headers=headers,timeout=10,verify=False).text
                respose=html.unescape(res)
                rules = []#匹配到的标签
                host=True
                for re_rules in re_rules_list:
                    chashuibiao=re.findall(r'{}'.format(re_rules),respose,re.S|re.I)
                    if chashuibiao !=[]:
                        rules.append(re_rules)
                        host=False
                        print('{}:{} 存在暗链，命中规则--->{}'.format(threading.current_thread().name,url,chashuibiao))
                if host ==False:
                    with open("darkresult.txt", "a+") as file1:
                        file1.write('{}\n'.format(url))
                else:
                    print('{}:{} 未检测出暗链，未命中规则'.format(threading.current_thread().name,url))
        except:
            print('{}:{}请求出错'.format(threading.current_thread().name,url))

def openDarkurlcheck(filename):
    xc = 4 # 设置线程数
    with open(filename, 'r',encoding='utf-8') as f:
        urls_list = f.read().split('\n')
    urls = []
    twoList = [[] for i in range(xc)]
    for i, e in enumerate(urls_list):
        twoList[i % xc].append(e)
    for i in twoList:
        urls.append(i)
    print('检测暗链主线程开始')
    thread_list = [threading.Thread(target=FindDarkchain, args=(urls[i],)) for i in range(len(urls))]
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    print('检测暗链主线程结束')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Help')
    parser.add_argument('-f', '--filename', help='Please Input a file,the option is urls.txt or other)', default='')
    parser.add_argument('-u', '--url', help='Please Input a url', default='')
    args = parser.parse_args()
    filename = args.filename
    url =  args.url
    if filename=="" and url== "":
        banner()
        sys.exit()
    elif filename=="" and url!= "":
        try:
            clear_darkresult()
            if "http" not in url:
                # url = "http://" + url
                url = probe_url(url)
            if "http" not in url:
                print('{} 请求出错'.format(url))
            else:
                res=requests.get(url,headers=headers,timeout=10,verify=False).text
                respose=html.unescape(res)
                rules = []#匹配到的标签
                host=True
                for re_rules in re_rules_list:
                    chashuibiao=re.findall(r'{}'.format(re_rules),respose,re.S|re.I)
                    if chashuibiao !=[]:
                        rules.append(re_rules)
                        host=False
                        print('{} 存在暗链，命中规则--->{}'.format(url,chashuibiao))
                if host ==False:
                    with open("darkresult.txt", "a+") as file1:
                        file1.write('{}\n'.format(url))
                    print("存在暗链的url放置在darkresult.txt文件中")
                else:
                    print('{} 未检测出暗链，未命中规则'.format(url))
        except:
            print('{} 请求出错'.format(url))
    elif filename!="" and url== "":
        print(f"正在检测{filename}中的站点")
        clear_darkresult()
        # 检测暗链是否存在
        openDarkurlcheck(filename)
        print("存在暗链的url放置在darkresult.txt文件中")
    else:
        banner()
        sys.exit()
