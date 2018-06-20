from bs4 import BeautifulSoup
import requests
import json

head_Html='https://ticket.travel4u.com.tw/Travel4u_BFM/Flights'
className = ['flybox','fldata','fllogo','fllcheck']
fly_Air_Ticket_ClassName = ['order_price','order_airline','order_timeg','order_timeb']
fly_Data_ClassName = ['fob']
fly_Logo_ClassName = ['h6']
fly_Check_ClassName = ['fly_price']
plane_Info_title = ['DepartTime','DepartAirport','ArrivalTime','ArrivalAirport','TakeTime','DepartTime_return','DepartAirport_return','ArrivalTime_return','ArrivalAirport_return','TakeTime_return']
airplane_Price_ClassName = 'fly_price'
airline_idname = "req_retairport"
detal_info_idName = 'collapsef'
airplane_datetime_title = ['DepartAirport_Time', 'ArrivalAirport_Time', 'DepartDay', 'ArrivalDay', 'DepartAirport_Time_return', 'ArrivalAirport_Time_return', 'DepartDay_return', 'ArrivalDay_return']
def get_html(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return " ERROR "

def post_html(url,payload):
    try:
        rs = requests.session()
        r = rs.post(url,data=payload,timeout=30)
        print(r.url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return " ERROR "
def parse_partial_html(soup,className):
    airplane_info = {}
    fly_info = soup.find_all(class_ = className[0])
    plane_info_dict = {}
    airplane_name_dict = {}
    count = 0
    price_info_dict = {}
    airplane_datetime = {}
    for item in fly_info:
        plane_info = parse_detal_hteml(item,className[1])
        if '轉機' not in ' '.join(plane_info):
            plane_info_dict[count] = list(plane_info)
            fllogo_info = item.find_all(class_ = className[2])
            airplane_name_dict[count] = get_airplane_name(fllogo_info,'h6')
            price_info_dict[count] = get_airplane_price(item,className[3])
            airplane_datetime[count]=get_airplane_datetime(item)
            count+=1
    print(count)
    return plane_info_dict,airplane_name_dict,price_info_dict,airplane_datetime
def parse_detal_hteml(soup,className):
    flydata_info = soup.find_all(class_ = className)
    plane_info = []
    for item_i in flydata_info:
            flydata_detal_info = item_i.find_all(text = find_text_content)
            for text_tmp in flydata_detal_info:
                info_text = text_tmp.replace("\n","").replace("\r","").replace(" ","")
                if(info_text != '+1'):
                    plane_info.append(info_text)
    return plane_info

def get_airplane_name(soup,className='h6'):
    airplane_name = []
    for item in soup:
        fllogo_info = item.find_all(className)
        for item_i in fllogo_info:
            airplane_name.append(item_i.text.replace(" ","").replace("\n",""))
    return airplane_name
def find_text_content(cssname):
    if cssname != None:
        for css_index in cssname:
            if(css_index != '\n'):
                return cssname
def get_airplane_price(soup,className):
    flycheck_info = soup.find_all(class_ = className)
    price_info = []
    for item in flycheck_info:
        price_soup = item.find_all(class_ = airplane_Price_ClassName)
        for item_i in price_soup:
            price_info.append(item_i.text)
    return price_info
def get_air_detal_info(cssname):
    if(cssname != None):
        if(detal_info_idName in cssname):
            return cssname
def get_airplane_datetime(soup):
    airplane_datetime = []
    fly_detal_info = soup.find_all(id = get_air_detal_info)
    for item in fly_detal_info:
        fly_detal_info_second =  item.find_all(class_="flyg")
        for item_i in fly_detal_info_second:
            airplane_datetime.append(item_i.text)
    return airplane_datetime
def processing_airplane_info(plane_info_dict,airplane_name_dict,price_info_dict,airplane_datetime):
    airplane_all_detal_info_dict = {}
    for keys in plane_info_dict:
        i = 0
        j = 0
        airplane_all_detal_info = {}
        for plane_info_tmp in plane_info_dict[keys]:
            airplane_all_detal_info[plane_Info_title[i]] = plane_info_tmp
            i +=1
        for airplane_name in airplane_name_dict[keys]:
            airplane_all_detal_info['company'] = airplane_name
        for price_info_tmp in price_info_dict[keys]:
            airplane_all_detal_info['price'] = price_info_tmp
        for airplane_datetime_tmp in airplane_datetime[keys]:
            if( j< len(airplane_datetime_title)):
                airplane_all_detal_info[airplane_datetime_title[j]] = airplane_datetime_tmp
            j+=1
        airplane_all_detal_info_dict[keys] = dict(airplane_all_detal_info)
    return airplane_all_detal_info_dict
def load_json_file(filename):
    with open(filename) as outfile:
        data = json.load(outfile)
    return  data
def main_search_airticket_info(var_depairport,var_retairport,var_depdate,var_retdate,var_direct = 'Y',var_rbd ='5'):
    payload = {
        'triptype': 'Return',
        'depairport': var_depairport,
        'retairport': var_retairport,
        'depdate': var_depdate,
        'retdate': var_retdate,
        'direct': 'Y',
        'addthree': 'N',
        'airline': '',
        'rbd': '5',
        'adult': ' 1',
        'child': ' 0',
        'inft': ' 0',
        'openjaw': '',
    }
    res = post_html(head_Html, payload)
    soup = BeautifulSoup(res, 'lxml')
    plane_info_dict, airplane_name_dict, price_info_dict, airplane_datetime = parse_partial_html(soup, className)
    airplane_all_detal_info_dict = processing_airplane_info(plane_info_dict, airplane_name_dict, price_info_dict,
                                                            airplane_datetime)
    return airplane_all_detal_info_dict
def get_airticket_title_Info():
    plane_Info_title_dict = {'DepartDay': '啟程日期','DepartTime':'啟程時間', 'DepartAirport':'啟程機場', 'ArrivalDay': '抵達日期','ArrivalTime':'抵達時間', 'ArrivalAirport':'抵達機場', 'TakeTime':'飛行時數','DepartDay_return': '回程日期', 'DepartTime_return':'回程時間',
                        'DepartAirport_return':'回程機場','ArrivalDay_return': '抵達日期', 'ArrivalTime_return':'抵達時間', 'ArrivalAirport_return':'抵達機場名稱', 'TakeTime_return':'飛行時數'}
    airplane_datetime_title_dict = {'DepartAirport_Time':'啟程機場與時間', 'ArrivalAirport_Time':'抵達機場與時間', 'DepartDay':'啟程日期', 'ArrivalDay':'抵達日期',
                               'DepartAirport_Time_return':'回程機場與時間', 'ArrivalAirport_Time_return':'抵達機場與時間', 'DepartDay_return':'回程日期',
                               'ArrivalDay_return':'抵達日期'}
    airplane_datetime_title_dict_02 = {
                                    'DepartDay': '啟程日期', 'ArrivalDay': '抵達日期',
                                    'DepartDay_return': '回程日期',
                                    'ArrivalDay_return': '抵達日期'}
    companyName = {'company':'航空公司'}
    price_dict = {'price':'含稅價格'}
    return plane_Info_title_dict,companyName,price_dict