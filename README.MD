## 一、说点东西

老早就想搞个基金监控机器人了，方便自己查看自己关注基金的各种指数涨跌情况，及时进行止损或者止盈，从今天开始，我们先建楼基，手把手带大家实现一个基金查询机器人，目前主要可以查询基金指定日期段数据和查看基金净值走势图，后面慢慢新增功能。


![](https://files.mdnice.com/user/2046/052c957e-e575-45f6-b882-b6b9798cb13d.png)


## 二、开始动手动脑

### 2.1 环境准备

- Linux、Mac、Windows 都可以
- python 3.7及以上
- 相关第三方包：pandas（数据处理）、requests（爬取数据）、re（文本内容解析）、akshare（获取基金股票数据）、matplotlib（数据可视化）、dataframe-image（dataframe表格转成图片）


### 2.2 获取指定日期段基金数据

基金数据可以从一些金融相关的网站获取到，比如天天基金网、新浪基金网等，可以自己写爬虫程序获取网站数据，也可以使用现成的工具包获取数据，比如：[一行代码获取股票、基金数据，并绘制K线图](https://mp.weixin.qq.com/s?__biz=MzUyOTAwMzI4NA==&mid=2247516713&idx=2&sn=48be07fa8337885b33e9a7a4d69a2050&chksm=fa656452cd12ed441d29d51e90a2ae0a6fdbbc63171be3168a879692805d2c221d037770e166&scene=21#wechat_redirect)里用到的`akshare`。

这里我们同时介绍下两种方法：

#### 2.2.1 回顾下akshare获取基金数据

目前akshare不支持获取指定日期范围内的基金净值数据，但是可以一次获取到基金历史净值数据，调用函数`fund_em_open_fund_info`获取基金历史数据，然后自己根据日期选取时间断进行分析。

![](https://files.mdnice.com/user/2046/2b8027d9-54f1-41b7-8842-f41fb56c59bf.png)


```python
import akshare as ak
fund_data = ak.fund_em_open_fund_info(fund='005827', indicator='单位净值走势')

print(fund_data)
```

![](https://files.mdnice.com/user/2046/44c8fe2a-5643-47bd-a254-7f4cbac5945f.png)



#### 自己调用现成数据接口

本质上akshare也是从一些金融相关的网站获取到数据，我们也可以自己写代码进行获取，通过浏览器我们很快能搜索到基金数据接口，来自东方财富的天天基金网。
```python
f'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={code}&page={page}&sdate={start_date}&edate={end_date}&per={per}'

code - 基金代码
page - 基金数据页码
start_date - 数据开始日期
end_date - 数据结束日期
per - 每页展现数据量，最多40
```

![](https://files.mdnice.com/user/2046/7235806a-7550-4edd-9c36-c989c1c61548.png)

根据指定参数，浏览器会返回指定参数，一段js赋值代码，包括了 基金数据（content）、总记录条数（records）、总页数（pages）、当前页数（curpage）。

格式非常规整，我们可以直接通过正则提取数据，
```python
'''
获取单页面 基金数据
'''
def get_html(code, start_date, end_date, page=1, per=40):
    url = f'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={code}&page={page}&sdate={start_date}&edate={end_date}&per={per}'
    # print(url)
    rsp = requests.get(url)
    html = rsp.text
    
    return html
```


![](https://files.mdnice.com/user/2046/58b3468c-3906-4e63-a061-066ea8c89e0e.png)

通过返回的数据可以发现，基金数据部分是一个由table标签包裹的html代码，那我们可以直接使用pandas的read_html来解析数据。

```python
# 从html中解析出数据表部分 并解析成df
def parses_table(html):
    # 获取基金数据表
    pattern = 'content:"<table(.*)</table>",'
    table = re.search(pattern, html).group(1)
    table = '<table' + table + '</table>'
    fund_data = pd.read_html(table)[0]
    return fund_data
```

前面有提到，基金数据接口返回数据每页最多展示40条，所以要想获取所有数据，我们可能需要遍历每一页，那么我们还需要通过正则将总页数`pages`获取到，然后遍历调用`get_html`和`parses_table`函数解析出所有数据。

```python
# 从html中解析出数据表部分 并解析成df
def parses_table(html):
    # 获取基金数据表
    pattern = 'content:"<table(.*)</table>",'
    table = re.search(pattern, html).group(1)
    table = '<table' + table + '</table>'
    fund_data = pd.read_html(table)[0]
    return fund_data

# 获取指定日期内 累计净值 等数据
def get_fund_data(code, start_date, end_date):
    first_page = get_html(code, start_date, end_date)
    # 获取总页数
    pattern = 'pages:(.*),'
    pages = re.search(pattern, first_page).group(1)
    # 转成int数据
    try:
        pages = int(pages)
    except Exception as e:
        r = f'【错误信息】{e}'
        # print(r)
        return r 
    
    # 存放每页获取到的基金数据 dataframe格式 便于后面合并
    fund_df_list = []
    
    # 循环便利所有页面
    for i in range(pages): 
        if i == 0:
            fund_data = parses_table(first_page)
        else:
            page_html = get_html(code, start_date, end_date, page=i+1)
            fund_data = parses_table(page_html)
        fund_df_list.append(fund_data)
    
    # 将每页的数据合并到一起
    fund_df = pd.concat(fund_df_list)
    
    return fund_df
```

![](https://files.mdnice.com/user/2046/24fb93bb-4eda-499a-a97f-7d4836179bac.png)

上面两种方法都可以获取到基金净值数据，最后我选择了`akshare`方式获取，设置一个定时任务，每天三点更新自己关注的基金所有数据，存储到本地，后面要查询的时候直接读取本地文件查询即可。

- 定时任务：每天早上3点获取所有关注的基金历史数据，存储到本地

```python
# 定时任务：每天早上3点获取所有关注的基金历史数据，存储到本地
def get_all():
    try:
        # 从文件读取 自己关注的基金代码列表
        with open('./FD/funds.txt') as f:
            funds = [i.strip() for i in f.readlines()]
        # 遍历 一个个更新数据
        for fund in funds:
            fund_df = ak.fund_em_open_fund_info(fund, indicator='单位净值走势')
            fund_df = fund_df.sort_values(by=['净值日期'], ascending=False)
            fund_df.to_csv(f"./FD/DATA/F{fund}_data.csv", index=False)
            # print(f"./FD/DATA/F{fund}_data.csv")
            time.sleep(random.randint(1,5))
        return '基金数据更新完成'
    except Exception as e:
        r = f"【错误信息】{e}"
        return r
```

- 获取指定基金 指定日期段 净值数据
```python
# 获取指定基金 指定日期段 净值数据
def get_fund_data(fund, start_d, end_d):
    fund_df = pd.read_csv(f'./FD/DATA/{fund}_data.csv')
    result_df = fund_df.query(f"'{start_d}'<=净值日期<='{end_d}'")
    return result_df
```

### 2.3 返回数据呈现方式

目前先简单点，设置规则如下：
- 1）如果数据量小于等于30条，就返回原始数据图

`原始数据图`就是直接将获取到的数据转成图片的方式发送给用户，这里我们使用`dataframe-image`这个第三方包，使用非常简单，pip安装后，直接调用`export`函数即可快速将datafrmae数据转成图片。

```python
# 将dtaframe表格转变成图片
def df_to_img(fund_df, fund, start_d, end_d):
    if fund_df.shape[0] <=1:
        dfi.export(fund_df, f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')
        return 
    
    # 格式化表格 凸显最大最小值
    fund_df = fund_df.style.highlight_max(subset=['单位净值'], color='red')\
             .highlight_min(subset=['单位净值'], color='green')\
             .format({'日增长率': '{:}%'})
    
    dfi.export(fund_df, f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')
```

为了图片数据更好看，我们还使用了`df.style`设置数据表格样式（单位净值最大值、最小值高亮和日增长率添加百分号）。

![](https://files.mdnice.com/user/2046/6d58ccac-a0f2-4b15-b7d5-4f871bac37a0.png)


- 2）如果数据量大于30条，就返回原始数据趋势图

`原始数据趋势图`就是将数据可视化下，然后返回给用户，这里我们选择绘制数据的走（趋）势图，使用`matplotlib`进行绘制。

```python
# 绘制基金单位净值走势图
def draw_fund_line(fund_df, fund, start_d, end_d):
    plt.rcParams['figure.figsize'] = (8.0, 4.0) # 设置figure_size尺寸
    plt.rcParams['savefig.dpi'] = 300 #保存图片分辨率

    # 不显示右、上边框
    ax=plt.gca() 
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # 设置坐标网格
    plt.grid(axis="y", color='gray')  

    # 计算最大值 最小值坐标 并标注到图中
    fund_max = fund_df.loc[fund_df['单位净值'].idxmax()]
    fund_min = fund_df.loc[fund_df['单位净值'].idxmin()]

    ax.annotate(f'({fund_max[0]},{fund_max[1]})', xy=(fund_max[0], fund_max[1]), color='red')
    ax.annotate(f'({fund_min[0]},{fund_min[1]})', xy=(fund_min[0], fund_min[1]), color='green')

    # 画图
    plt.plot(fund_df['净值日期'],fund_df['单位净值'], color="c")
    plt.title('基金单位净值走势图')
    plt.xticks(rotation=30)
    plt.xlabel('净值日期')
    plt.ylabel('单位净值')
    plt.savefig(f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')
```

这里使用的是折线图，有一些对图片样式的设置，比如：大小、边框、最大/小值标注，但依然不是很美观，后面继续优化。

![](https://files.mdnice.com/user/2046/812ff9e4-3ed5-46c4-b18d-ebb736f76196.png)

- 完整调用

```python
# 返回数据
def response_data(fund, start_d, end_d):
    # 本地查看 查询结果是否已存在
    imgs = os.listdir('./FD/IMG/')
    if f'{fund}_{start_d}_{end_d}_data.png' in imgs:
        return f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png'
    
    # 获取数据
    fund_df = get_fund_data(fund, start_d, end_d)
    
    # 如果数据量小于等于30条，就返回原始数据图
    if fund_df.shape[0]<= 30:
        df_to_img(fund_df, fund, start_d, end_d)
    else:
        # 否则返回数据趋势图
        fund_df = fund_df.sort_values(by=['净值日期'])
        draw_fund_line(fund_df, fund, start_d, end_d)

    return f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png'
```

### 2.4 对接钉钉机器人设置守护程序

目前项目中使用到了之前介绍过的两种机器人：钉钉群机器人、企业机器人，相关配置方法和代码可以查看之前的文章：[如何用Python发送告警通知到钉钉？](https://mp.weixin.qq.com/s?__biz=MzUyOTAwMzI4NA==&mid=2247522498&idx=1&sn=02fc691a18fb4d4b9231a126aa5d1da2&chksm=fa657eb9cd12f7af7adc29ff39567f3c9f7e2fae4c3b59bfdd06c4c0cb8c1d03f74823cfe798&scene=21#wechat_redirect) 和 [如何打造一个能自动回复的钉钉机器人](https://mp.weixin.qq.com/s?__biz=MzUyOTAwMzI4NA==&amp;mid=2247524687&amp;idx=1&amp;sn=ce3079579493bad88635992140db0615&amp;chksm=fa658734cd120e22e5fc14640daabdd9239796b11cc4de18d7f1094a7eeabf100f8d9a6f2f63&token=920949564&lang=zh_CN#rd)，非常详细。

钉钉群机器人主要用来汇报每天自动汇报基金数据更新情况，后面还可以加基金涨跌检测情况等。

企业机器人主要用来做基金数据查询自动回复功能，也可以拓展主动发消息给用户，后面研究研究。



### 2.5 遇到问题及解决方法

#### 2.5.1 Linux上datafrmae-image转图片出错

最开始是提示没有`chrom`，然后按网上教程安装了google chrom。

参考：https://segmentfault.com/a/1190000022425145

![](https://files.mdnice.com/user/2046/129d9bf3-8456-41f3-b906-494d2bab0e7a.png)

安装后，运行代码提示`SyntaxError: not a PNG file`。

![](https://files.mdnice.com/user/2046/555bd9d1-6e21-4c87-ab3e-46d2f2e8c61b.png)

看错误提示以为是Pillow和matplotlib的问题，修改到了和本地一样的版本也不行。

最后看了源码，发现可以转换方法除了使用`chrom`，还可以用`matplotlib`，修改后，确实可以正常生成图片了，但是没有格式！！！

![](https://files.mdnice.com/user/2046/f12b0670-47b4-4035-b27a-b9bb2651c494.png)

最后改回默认`table_conversion`，仔细看，发现有提示以下内容，大概意思linux下不能直接使用root用户权限允许谷歌chrome，最简单的方法就是创建一个普通用户。

```bash
[0209/162730.350381:ERROR:zygote_host_impl_linux.cc(90)] Running as root without --no-sandbox is not supported. See https://crbug.com/638180
```

在root权限下，新建一个用户`od`，并将`/root`目录权限授予给它，然后输入su指令切换到新用户下。
```bash
useradd od
chown -R od /root
su od
```

再次运行确实能解决图片生成和数据格式问题，但是有新问题：表头中文无法显示。。。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1edf02fafff94aed93927a0fa1634f4c~tplv-k3u1fbpfcp-zoom-1.image)

百般搜索，看源码调试、看项目仓库问题都没解决，最后，最后我突然想到，我本地可以，两个包的版本又是一样，应该不是代码问题，会不会是因为linux里没有安装中文字体，所以无法显示中文？

root用户权限下，先创建一个目录，存放中文字体，创建好后，可以直接利用宝塔将本地的`SimHei`字体上传到对应目录即可。
```bash
mkdir -p /usr/share/fonts/my_fonts
```

可以通过下面指令查看中文字体是否安装成功，

```bash
fc-list :lang=zh
```

![](https://files.mdnice.com/user/2046/5375b520-3eb2-4ef5-a3ab-647b1edec906.png)

再次运行代码，生成的图片就正常啦～开心！

![](https://files.mdnice.com/user/2046/8fa55857-9207-425c-97ff-19d27dac5cd2.png)



#### 2.5.2 matplotlib图片中文显示问题
![](https://files.mdnice.com/user/2046/b14fcfd2-7bdf-427e-8407-53a262135ec1.png)

之前有写过详细解决方法，可以直接查看之前文章：[永久解决matplotlib中文乱码](https://mp.weixin.qq.com/s?__biz=MzUyOTAwMzI4NA==&mid=2247517356&idx=3&sn=5700dc51ba92f56c66d667623060ae12&chksm=fa6562d7cd12ebc1658d599767a82c56701675ddd38551324440e61966e99128bc353d8ea18d&token=920949564&lang=zh_CN#rd)

#### 2.5.3 钉钉机器人无法直接传输图片

钉钉机器人目前只支持传输：普通文本、markdown文本、连接、actionCard消息和feedCard消息类型。

如果我想要将生成的基金数据图发送给用户，最好的方法是和之前一样，先将图片转成链接，然后通过markdown形式传输。

如果系统仅个人使用，数据量不大，我们不必选择网络上现有的图床工具（这样我们还要写接口对接代码），可以直接开放个http端口去共享我们的图片，本身企业机器人就使用到了flask，所以我们可以更简单的实现这个功能。

```python
app = Flask(__name__, static_folder='xxx/FD/IMG', static_url_path='/static')
```
在初始化flask app时，指定静态文件所在目录和静态文件路由后缀即可，这样，我们就可以通过：http://服务器IP地址:端口号/static/图片文件名，访问到对应图片了。

![](https://files.mdnice.com/user/2046/3fd2103f-32d1-4a6d-a3ce-1297f4d7ec26.png)

然后将图片链接嵌入到markdown中，即可正常返回给用户了。

![](https://files.mdnice.com/user/2046/61e0d96c-6878-4aca-9760-6397e403449e.png)

### 2.6 最终效果图

- 指定查询
> 查看某基金某个时间段内的基金净值数据。（30条以内数据，表格展示；大于30条，趋势图展示）<br>
<br>**查询格式：** F基金代码 起始日期 结束日期，如：F005827 2021-12-03 2022-02-10

![效果图](https://files.mdnice.com/user/2046/84c551f0-599e-408f-9b43-ed43bf18fbe3.png)

- 普通查询
> 查看某基金近10天内净值和日增长率数据+趋势图
<br>
<br>**查询格式：** F基金代码，如：F005827

![最近10天内，只有两个交易日](https://files.mdnice.com/user/2046/294d19f4-72f8-4cf0-ad31-1f65eddef776.png)

## 三、后言后语

这项目说大不大，说小也不小，百行代码，本机测试还是很顺畅的，主要是迁移到Linux上后出现一些问题，从最开始的python版本问题（安装了一个3.7.9），到datafrmae-image问题，延展出来的Linux安装谷歌、设置新用户、分配权限，以及源码测试学习。

遇到问题、解决问题的过程确实花费了我很长时间，一度还让我很苦恼，但是，这个过程也让我觉得很有益，是一个不断积累、不断练习、不断巩固的过程，解决问题后更会为自己欢呼。

目前基金监测机器人还比较简陋，甚至都没有监测功能（目前只支持数据查询和更新），但是这个楼基很稳、很深，后面添加其他功能会简单、便捷许多，欢迎大家评论区留言，说说你想为这个机器人添加的功能。

坚持 and 努力 ： 终有所获。

本项目源码地址：[https://github.com/XksA-me/EnterpriseBot](https://github.com/XksA-me/EnterpriseBot)

**如何找到我：**

[![img](https://camo.githubusercontent.com/3173ad049f9e13f352bb149610c9eb2e237a59dd7ea9d213a5c1b09857507d41/68747470733a2f2f696d672d626c6f672e6373646e696d672e636e2f62313637313536313336653834306132613033373037396537333533643330372e706e673f782d6f73732d70726f636573733d696d6167652f77617465726d61726b2c747970655f5a484a766157527a5957357a5a6d467362474a685932732c736861646f775f35302c746578745f51314e455469424135363641364b2d3055486c30614739752c73697a655f32302c636f6c6f725f4646464646462c745f37302c675f73652c785f3136237069635f63656e746572)](https://camo.githubusercontent.com/3173ad049f9e13f352bb149610c9eb2e237a59dd7ea9d213a5c1b09857507d41/68747470733a2f2f696d672d626c6f672e6373646e696d672e636e2f62313637313536313336653834306132613033373037396537333533643330372e706e673f782d6f73732d70726f636573733d696d6167652f77617465726d61726b2c747970655f5a484a766157527a5957357a5a6d467362474a685932732c736861646f775f35302c746578745f51314e455469424135363641364b2d3055486c30614739752c73697a655f32302c636f6c6f725f4646464646462c745f37302c675f73652c785f3136237069635f63656e746572)
