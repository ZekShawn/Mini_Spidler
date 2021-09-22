#coding=utf-8
import re
import time
import requests
import pandas as pd
from xpinyin import Pinyin


date_from = '20210729'
cities = ['南京市', '天津市', '上海市']
headers = {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"}


def get_weather(date_from, cities, headers):

    # 数据存储
    data = []

    # 获取城市拼音
    pin = Pinyin()
    city_pinyin = [pin.get_pinyin(city[:-1]).replace("-", "") for city in cities]

    # 转换为时间戳
    date_stamp = time.strptime(date_from, "%Y%m%d")
    date_stamp = time.mktime(date_stamp)

    # 获取直到昨天的历史天气信息
    while (date_stamp + 24*3600) < time.time():

        # 打印日志
        print(f'正在获取「{time.strftime("%Y/%m/%d", time.localtime(date_stamp))}」数据，从「{date_from}」开始：')

        # 获取当天的所有城市天气信息
        for city_pin, city_name in zip(city_pinyin, cities):

            # 获取天气源代码
            temp_date = time.strftime("%Y%m%d", time.localtime(date_stamp))
            url = f"http://www.tianqihoubao.com/lishi/{city_pin}/{temp_date}.html"
            html = requests.get(url, headers=headers).text

            # 天气信息
            weather_info = re.findall(r"alt='.*?' width='48' class='legend' /><br />", html)
            weather_info = [x[5:-36] for x in weather_info]

            # 温度信息
            temperature_info = re.findall(r'<td style="color:.*?><b>.*?</b></td>', html)
            temperature_info = [x[-12:-9] for x in temperature_info]

            # 风力风向
            wind_info = re.findall(r'<td>.*?风.*?级.*?</td>', html)
            wind_info = [x[4:-5] for x in wind_info]

            # 存储数据
            data.append([city_name, time.strftime("%Y/%m/%d", time.localtime(date_stamp)), "白天", weather_info[0], temperature_info[0], wind_info[0]])
            data.append([city_name, time.strftime("%Y/%m/%d", time.localtime(date_stamp)), "夜晚", weather_info[1], temperature_info[1], wind_info[1]])

            # 日志输出
            print(f"{data[-2]}\n{data[-1]}")


        # 时间迭代
        date_stamp += 24 * 3600

    # 返回数据
    return data


def main():
    data = get_weather(date_from, cities, headers)
    data = pd.DataFrame(data, columns=['城市', '日期', '白天/夜晚', '天气', '温度', '风向/风力/等级'])
    data.to_csv(f'Weather_{date_from}.csv', index=False, encoding='utf_8_sig')


if __name__ == "__main__":
    main()