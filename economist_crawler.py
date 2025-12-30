import requests
from lxml import etree
from datetime import datetime
import os

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}

def download_economist():
    # 使用found标志代替flag
    found = False
    pdf_path = None
    
    for i in range(1, 5):
        if found:
            break
            
        url = f"https://freemagazinespdf.com/category/economics-business-politics-finances/page/{i}/"
        
        try:
            re = requests.get(url, headers=header, timeout=30)
            re.raise_for_status()
        except Exception as e:
            print(f"请求列表页失败: {e}")
            continue

        html = etree.HTML(re.text)
        namelist = html.xpath('//h2[@class = "entry-title"]/a/text()')
        url_list = html.xpath('//h2[@class = "entry-title"]/a/@href')

        dic1 = dict(zip(namelist, url_list))
        
        for name, url in dic1.items():
            if "The Economist" in name:
                found = True
                print(f"找到目标: {name}")
                
                try:
                    re_2 = requests.get(url, headers=header, timeout=30)
                    re_2.raise_for_status()
                    html_2 = etree.HTML(re_2.text)
                    
                    try:
                        url_2 = html_2.xpath('//a[contains(text(), "Download PDF")]/@href')[0]
                        
                        re_3 = requests.get(url_2, headers=header, timeout=30)
                        re_3.raise_for_status()
                        
                        # 保存HTML文件用于调试（可选）
                        html_3 = etree.HTML(re_3.text)
                        url_3 = html_3.xpath('//link[@rel="preload"]/@href')[0]
                        print(f"PDF链接: {url_3}")

                        # 生成带日期的文件名
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        filename = f"The_Economist_{date_str}.pdf"
                        pdf_path = filename

                        re_download = requests.get(url = url_3, headers=header, timeout=120, stream=True)
                        re_download.raise_for_status()

                        with open(filename, "wb") as f:
                            for chunk in re_download.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                            
                        print(f"下载完成: {filename}")
                        print(f"文件大小: {os.path.getsize(filename) / 1024 / 1024:.2f} MB")
                        
                    except IndexError as e:
                        print(f"解析出错: {e}")
                        return None
                    
                except Exception as e:
                    print(f"下载过程出错: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
                
                # 找到第一个就结束
                break
    
    if not found:
        print("未找到 The Economist")
        return None
    
    return pdf_path

if __name__ == "__main__":
    print("开始爬取 The Economist...")
    print("-" * 50)
    
    pdf_file = download_economist()
    
    print("-" * 50)
    if pdf_file:
        print(f"成功下载: {pdf_file}")
    else:
        print("下载失败")
        # 退出状态码非0，让GitHub Actions知道失败了
        exit(1)