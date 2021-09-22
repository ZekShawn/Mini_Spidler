import re               # 正则表达式
import requests         # 读取网页源码
import pandas as pd     # 数据保存


# ## url
# ### 综艺栏腾讯自制筛选：
# - https://v.qq.com/channel/variety?listpage=1&channel=variety&source=1&exclusive=1
# ### 电影栏院线大片筛选：
# - https://v.qq.com/channel/movie?channel=movie&itype=100062&listpage=1&sort=18
# ### 电视剧筛选
# - https://v.qq.com/channel/tv?listpage=1&channel=tv&sort=18&_all=1

# ## pattern
# ### 综艺栏腾讯自制筛选：
# - https://v.qq.com/x/cover/mzc.*html
# ### 电影栏院线大片筛选：
# - https://v.qq.com/x/cover/.*?html
# ### 电视剧筛选
# - https://v.qq.com/x/cover/.*?html

## 分类
catagory_list = ['variety', 'movie', 'tv']

# 初始链接
vanilla_url_list = ['https://v.qq.com/channel/variety?listpage=1&channel=variety&source=1&exclusive=1',
                    'https://v.qq.com/channel/movie?channel=movie&itype=100062&listpage=1&sort=18', 
                    'https://v.qq.com/channel/tv?listpage=1&channel=tv&sort=18&_all=1']

# 视频分类 正则表达式
pattern_list = ['https://v.qq.com/x/cover/mzc.*html', 
                'https://v.qq.com/x/cover/.*?html', 
                'https://v.qq.com/x/cover/.*?html']

# 视频标题，主演，视频 ID，匹配正则表达式
pattern_vedio_pages = ['<title>.*?</title>', 
                       'class="name" title="[\u4e00-\u9fa5].*?"',
                       '"comment_id":"[0-9].*?"']

# 当前页ID，下一页评论页面ID, 昵称，评论，点赞，评论
pattern_comment = ['"first":"[0-9].*?"', 
                    '"last":"[0-9].*?"',
                    'nick":".*?"',
                    '"content":"[\u4e00-\u9fa5].*?"',
                    '"up":"[0-9].*?"',
                    '"pokenum":"[0-9].*?"']

# 获取每个分类的视频链接，并返回一个list
def get_url(pattern, string):
    str_temp = string
    url_list = []
    i = 1
    while re.search(pattern, str_temp) != None:
        temp_match_obj = re.search(pattern, str_temp)
        temp_match_str = temp_match_obj.group()
        url_list.append(temp_match_str)
        print(f'{i}. Find the url: {temp_match_str}')
        str_temp = str_temp.replace(temp_match_str, '')
        i += 1
    return url_list

# 获取每个链接的 源码 信息，并转换为 字符串
def get_html_str(url):
    temp_url = url
    # str_html = request.urlopen(temp_url).read().decode("utf-8","ignore")
    str_html = requests.get(temp_url, verify=False)
    str_html.encoding = "utf-8"
    str_html = str_html.text
    return str_html

# 获取字符串中符合正则表达式的字符串
def get_str_re(pattern, string):
    temp_obj = re.search(pattern, string)
    return None if temp_obj == None else temp_obj.group()

# 拼接 评论 json 文件
def get_json_str(vedio_id, cusor_id):
    url = f'https://video.coral.qq.com/varticle/{vedio_id}/comment/v2?callback=_varticle{vedio_id}commentv2&orinum=10&oriorder=o&pageflag=1&cursor={cusor_id}&scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=132&_='
    return get_html_str(url)

# 记录的获取 每条视频的评论控制
item = 0 
items_each_vedio = 20
data = []

# 评论的获取
# https://video.coral.qq.com/varticle/
# 6217620376
# /comment/v2?callback=_varticle
# 6217620376
# commentv2&orinum=10&oriorder=o&pageflag=1&cursor=
# 6738564045058799374
# &scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=132&_=


# 开始循环
for i in range( len(vanilla_url_list) ):

    # 获取每个视频分类的 HTML 源码
    temp_prime_string = get_html_str( vanilla_url_list[i] )

    # 获取每个视频分类的 视频链接 List
    temp_list = get_url(pattern_list[i], temp_prime_string)
    print(f"---正在获取{i+1}个分类的视频信息---")
    
    for vedio_url in temp_list:

        # 获取视频 HTML 源码
        temp_html = get_html_str(vedio_url)
        print(f"***视频链接：{vedio_url}***")

        # 获取视频 标题
        title_name = get_str_re(pattern_vedio_pages[0],temp_html)
        if title_name == None:
            title_name = '<title>无法正常获取标题</title>'
        title_name = title_name[7:-8]               # <title>.*?</title>
        print(title_name)

        # 获取视频 主演 信息
        temp_actor_list = []
        print(get_str_re(pattern_vedio_pages[1],temp_html))
        while get_str_re(pattern_vedio_pages[1],temp_html) != None:

            string = get_str_re(pattern_vedio_pages[1], temp_html)
            temp_html = temp_html.replace(string, '')
            string = string[20:-1]                  # class="name" title="[\u4e00-\u9fa5].*?"

            temp_actor_list.append(string)

        actor_name = ','.join(temp_actor_list)

        # 获取视频 ID
        vedio_id = get_str_re(pattern_vedio_pages[2], temp_html)
        vedio_id = vedio_id[14:-1]                  # "comment_id":"[0-9].*?"

        # 获取第一个评论页 源码
        page_string = get_json_str(vedio_id, '')

        # 获取当前页 ID：
        current_page_id = get_str_re(pattern_comment[0], page_string)
        current_page_id = current_page_id[9:-1]     # "first":"[0-9].*?"

        # 下一页 ID：
        next_page_id = get_str_re(pattern_comment[1], page_string)
        next_page_id = next_page_id[8:-1]           # "last":"[0-9].*?"

        while current_page_id != next_page_id:
            
            temp_list = []

            while get_str_re(pattern_comment[2], page_string) != None:
                
                # 清空 List
                temp_list = []
                
                # 昵称
                nick_name = get_str_re(pattern_comment[2], page_string)
                if nick_name == None:
                    continue
                page_string = page_string.replace(nick_name, '')
                nick_name = nick_name[7:-1]         # nick":".*?"
                
                # 评论信息
                comment_content = get_str_re(pattern_comment[3], page_string)
                if comment_content == None:
                    continue
                page_string = page_string.replace(comment_content, '', 1)
                comment_content = comment_content[11:-1] # "content":"[\u4e00-\u9fa5].*?"

                # 点赞数
                up_num = get_str_re(pattern_comment[4], page_string)
                if up_num == None:
                    continue
                page_string = page_string.replace(up_num, '', 1)
                up_num = up_num[6:-1]                   # "up":"[0-9].*?"

                # 回复数
                poke_num = get_str_re(pattern_comment[5], page_string)
                if poke_num == None:
                    continue
                page_string = page_string.replace(poke_num, '', 1)
                poke_num = poke_num[11:-1]                  # "pokenum":"[0-9].*?"


                # 添加数据到 List 里面
                temp_list.append(catagory_list[i])
                temp_list.append(vanilla_url_list[i])
                temp_list.append(title_name)
                temp_list.append(vedio_url)
                temp_list.append(actor_name)
                
                temp_list.append(nick_name)
                temp_list.append(comment_content)
                temp_list.append(up_num)
                temp_list.append(poke_num)

                data.append(temp_list)
                # print(f"---We already add {len(data)} items to data list!---")
                item += 1
                if item >= items_each_vedio:
                    break
                print(temp_list)

            # 评论页面 加载
            page_string = get_json_str(vedio_id, next_page_id)

            # 获取当前页 ID：
            if current_page_id == None:
                break
            current_page_id = get_str_re(pattern_comment[0], page_string)
            if current_page_id == None:
                break
            current_page_id = current_page_id[9:-1]     # "first":"[0-9].*?"

            # 下一页 ID：
            if next_page_id == None:
                break
            next_page_id = get_str_re(pattern_comment[1], page_string)
            if next_page_id == None:
                break
            next_page_id = next_page_id[8:-1]           # "last":"[0-9].*?"

            if item >= items_each_vedio:
                item = 0
                break;
        
        temp_data = pd.DataFrame(data)
        temp_data.to_csv("Comment_data_of_tencent_videos.csv",encoding="utf_8_sig", header = None, index = False)

data = pd.DataFrame(data)
data.to_csv("Comment_data_of_tencent_videos.csv",encoding="utf_8_sig",header = None, index = False)