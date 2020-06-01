import os
import requests
from bs4 import BeautifulSoup
import json


# 从url中获取html
def getHTMLTest(url):
    # 藏下身份把
    kv = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "爬取失败"


# 从html中提取id,并存储在一个id[]列表中
def getGoodsId(html, id):
    # 使用soup解析
    soup = BeautifulSoup(html, 'html.parser')
    # name = li,attrs: data-sku : "100008610496"....
    # <li data-sku="100008610496" data-spu="100008610496" ware-type="10" class="gl-item">
    # 首先寻找li标签
    li = soup.find_all('li')
    for i in li:
        try:
            # 查找i中的'data-sku'属性，返回值至列表
            nameId = i.attrs['data-sku']
            # 将nameId存储到id列表
            id.append(nameId)
        except:
            # 使用异常继续查找规避异常
            continue


def getDetail(url, id, name, price, path):
    # 增加一个计数器
    count = 0
    for i in id:
        count += 1
        newUrl = url + i + '.html'
        html = getHTMLTest(newUrl)
        # 使用soup库构造类型
        soup = BeautifulSoup(html, 'html.parser')
        # <div class="sku-name"> <img src="//img13.360buyimg.com/devfe/jfs/t10852/94/3121149093/1595/4d1f4721/5ce3b828Ne1fdf8f6.png" alt="京品电脑">   “惠普（HP）战99-25 15.6英寸 工作站 设计本 笔记本i7-9750H/16GB/256GB PCIe+2TB/W10 Home/4G独显</div>
        divIteminfo = soup.find_all(name='div', attrs={'class': "itemInfo-wrap"})
        # 二次筛选
        for n in divIteminfo:
            # 搜索名字
            # 使用一个笨的式子，提取名字,之后测试返回类型不是string
            # .split('>')[-2].split('<')[-2]
            divName = soup.find(name='div', attrs={'class': "sku-name"})
            # 除去前后括号,并存储
            n1 = divName.get_text().strip()
            name.append(n1)
            saveFile(string="商品名称：" + n1 + '\n', path=path)
            # 检索价格，由于价格是动态生成的，这里我们通过分析其生成的url请求，
            # 通过network查询，我们可以看到
            # Request URL: https://p.3.cn/prices/mgets?callback=jQuery5820455&type=1&area=6_303_36784_36794&pdtk=&pduid=158998460077444674093&pdpin=jd_4395429aa8763&pin=jd_4395429aa8763&pdbp=0&skuIds=J_100004578219%2CJ_100004247816%2CJ_100009238742%2CJ_100002609755%2CJ_100004156957%2CJ_100013068430%2CJ_100007124066%2CJ_100007124481%2CJ_100009691768%2CJ_100011674276%2CJ_100005626917%2CJ_100004790399%2CJ_100009691776%2CJ_100009898546%2CJ_100005442503&ext=11100000&source=item-pc
            # 但是这个太长了，不分析了，使用搜索得来了一个api就是一个url
            # http://p.3.cn/prices/mgets?skuIds=J_2510388
            #
            # divPrice = soup.find(name='span', attrs={'class': "price J-p-" + i})
            divPrice = requests.request('GET', 'http://p.3.cn/prices/mgets?skuIds=J_' + i)
            # 这里请求回来得是一个response对象，使用json得方法解析，然后从列表中提取一个字典，最后得到最
            # {'cbf': '0', 'id': 'J_100013263242', 'm': '9999.00', 'op': '7999.00', 'p': '7999.00'}
            dictPrice = (json.loads(divPrice.text))[0]
            # 添加到price列表
            p1 = dictPrice['p']
            price.append(p1)
            saveFile(string="商品价格：" + p1 + '\n', path=path)
        # 搜索详细信息,在每个网页中我们尝试只找一次，
        divDetailInfo = soup.find(name='div', attrs={'class': "detail"})
        # 继续遍历详细信息
        detailList = divDetailInfo.find(name='ul', attrs={'class': "parameter2 p-parameter-list"})
        # 向下遍历所有子节点
        for child in detailList.children:
            saveFile(string=child.string, path=path)
        print('\r当前进度:{:.2f}%'.format(count / len(id) * 100), end="")


def saveFile(string, path):
    string = str(string)
    try:
        # 判断路径
        if not os.path.exists(path[:-6]):
            os.mkdir(path)
        with open(path, 'a+', encoding='utf-8') as f:
            f.write(string)

    except:
        print("爬取失败")
    finally:
        f.close()

# 这里本来想打印，名称和价格的，但是 格式一直有问题，拉倒吧
def printUnivList(name):
    tplt = "{0:{1}^120}"
    # 使用中文字符填充空白部分
    print(tplt.format("名称", chr(12288)))
    for i in range(len(name)):
        n = name[i]
        p = price[i]
        print(tplt.format(n, chr(12288)))


if __name__ == '__main__':
    # 搜索url,这里经过分析统一使用后面得滑动url
    # url1 = 'https://search.jd.com/Search?keyword=%E7%94%B5%E8%84%91&enc=utf-8&suggest=1.his.0.0&wq=&pvid=75b0f6a2d96a44aca4353a9cc9122164'
    # 滑动url
    url3 = 'https://search.jd.com/s_new.php?keyword={0}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page={1}&s={2}&scrolling=y'
    # 爬取纵深
    depth = 2
    # 单个商品url
    url2 = 'https://item.jd.com/'
    # 将id存储在一个列表中
    id = []
    # 名称列表
    name = []
    # 价格列表
    price = []
    # 详细信息
    detail = []
    # 字符存储的地方,这里我们写死好了,
    path = "D:/Py2020/com/lc/电脑.txt"
    # 将返回的html返回至变量
    for i in range(1, depth):
        url = url3.format("电脑", str(i), str(i * 50))
        html = getHTMLTest(url)
        # 从html中提取id
        getGoodsId(html, id)
        # 测试
        # print(id)
        getDetail(url2, id, name, price, path)
    printUnivList(name)
