# -*- coding: utf-8-*-
from bs4 import BeautifulSoup
import requests,re,os,json
import pandas as pd
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process
import threading,os

headers = {'Content-Type': 'application/json;charset=UTF-8',
           'Cookie': '_ga=GA1.3.1392185054.1591847338; _gid=GA1.3.762883749.1591847338; __BWfp=c1591847338332xec3680f27; _gcl_au=1.1.1587304046.1591847338; _fbp=fb.2.1591847338370.673347900; Token=VfaU+LJXyYZp7Nr3mFhCQtBfZ/rL2AQmOjkOW4W1uZVumEKn0wIHcD/RsdkmgB8di2Y9HFgUS/7HFxHm4m9eACLvfBCTdBEGoGqcd6RDUeZNSwlOrVeFarS9bEalGyz6; clientID=1392185054.1591847338; Tagtoo_pta=pta_03+_&gpa+_&gpb+_&gpc+_&vip+_; _TUCI_T=sessionNumber+18426&pageView+18426&Search+18426; _TUCS=1; _gat_UA-11424410-1=1; _gat_UA-34980571-16=1; _TUCI=sessionNumber+12523&ECId+387&hostname+www.hotcar.com.tw&pageView+92454&Search+6000',
           'Referer': 'https://www.hotcar.com.tw/SSAPI45/proxyPage/proxyPage.html'}

url = 'https://www.hotcar.com.tw/SSAPI45/API/SPRetB?Token=VfaU%2BLJXyYZp7Nr3mFhCQtBfZ%2FrL2AQmOjkOW4W1uZVumEKn0wIHcD%2FRsdkmgB8di2Y9HFgUS%2F7HFxHm4m9eACLvfBCTdBEGoGqcd6RDUeZNSwlOrVeFarS9bEalGyz6'
data = {
    'PARMS': ["https://www.hotcar.com.tw", "https://www.hotcar.com.tw/image/nophoto.png", "", "", 0, 0, "", "", 0, 0, "", "", "", "", "", "", "", "", "", "", "", ""],
    'SPNM': "CWA050Q1_2018",
    'SVRNM': ["HOTCARAPP"]
}


total_EQUIP_column=["id","brand","type","link","year","price","seller","kind","sys",'color','locate','miles',"cc","power","car_gas","safe_bag","abs","air_con","back_radar","back_screen","gps",
                    "window","auto_windows","auto_side","l_chair","alert","auto_chair","cd","media","ss","alu",
                    "hid","tpms","fog_lights","ldws","blind_spot","electric_tailgate","silde_door","whole_window","key_less","isofix",
                    "lcd","shift_paddles","es"]

class Crawler(object):
	def __init__(self): #initial
		self.car_id = self.all_car_list()

	def all_car_list(self): #crawl all the car's id
		global data,url,headers
		res = requests.post(url, json=data, headers=headers)
		car = res.text
		data = json.loads(car)
		car_id = []
		for i in data['DATA']['Table1']:
			car_id.append(i[u'TSEQNO'])
		return car_id

	def by_car_crawler(self): #carwl the info by car
		result=[]
		for i in range(len(self.car_id)):
			data2 = {
				'PARMS': [self.car_id[i], "https://www.hotcar.com.tw", "https://www.hotcar.com.tw/image/nophoto.png", "", ""],
				'SPNM': "CWA060Q_2018",
				'SVRNM': ["HOTCARAPP"]
				}
			res2 = requests.post(url, json=data2, headers=headers)
			by_cars = res2.text
			data = json.loads(by_cars)
			reObj = re.compile('EQUIP') #Regular Expression to find the match item
			print(i)
			print(self.car_id[i]) #for counting
			car_brand= data['DATA']['Table1'][0][u'BRANDNM'].lower() #translate to lower case
			car_type= data['DATA']['Table1'][0][u'CARTYPENM'].lower()
			EQUIP_append=[]
			x = data['DATA']['Table1'][0]['WDTYPENM']
			y = lambda x:"2" if x=='二輪傳動' else( "4" if  x=='四輪傳動' else "null")
			for j in data['DATA']['Table1'][0].keys():
				if(reObj.match(j)):
					x2 = data['DATA']['Table1'][0][j]
					y2 = lambda x2:"1" if x2=="Y" else( "0" if x2=="" or x2 == "N" else "0")
					EQUIP_append.append(y2(x2))
			z =  [EQUIP_append[i] for i in range(len(EQUIP_append)) if i!=13 and i!=18 and i!=19 and i!=20 and i!=21]#catch the item equip which we need
			by_car_list=[self.car_id[i],car_brand.strip(),car_type.strip(),'https://www.hotcar.com.tw/CWA/CWA060.html?TSEQNO='+str(self.car_id[i]),data['DATA']['Table1'][0][u'CARYY'],
				data['DATA']['Table1'][0][u'SALAMT1'].strip('萬'),data['DATA']['Table1'][0][u'NAME'],data['DATA']['Table1'][0][u'BODYTYPENM'],data['DATA']['Table1'][0][u'GEARTYPENM'],
				data['DATA']['Table1'][0][u'CCORLORNM'],data['DATA']['Table1'][0][u"MCITYNM"],data['DATA']['Table1'][0][u'KM1'],round(int(data['DATA']['Table1'][0]['CCNUM_R1'].replace(',',"")),-2),
				y(x),data['DATA']['Table1'][0]["GASTYPENM"]]
			by_car_list = by_car_list +z
			result.append(by_car_list)
			print(by_car_list)
		car_total_df=pd.DataFrame(result,columns = total_EQUIP_column,index=None) #convert to the dataframe form
		car_total_dict = car_total_df.T.to_dict() #for svaing to json file needed to get dict form first
		with open('All_HOT_car.json', 'w',encoding='utf-8-sig') as fp:
			json.dump(car_total_dict, fp,ensure_ascii=False)


	def image_crawler(self): #crawl all the photos by car
			for i in range(len(self.car_id)):
				try:
					photo_temp=[]
					data2 = {
					'PARMS': [self.car_id[i], "https://www.hotcar.com.tw", "https://www.hotcar.com.tw/image/nophoto.png", "", ""],
					'SPNM': "CWA060Q_2018",
					'SVRNM': ["HOTCARAPP"]
					}
					res2 = requests.post(url, json=data2, headers=headers)
					by_cars = res2.text
					data = json.loads(by_cars)
					reObj = re.compile('^PHOTOPATH')
					print(i)
					print(self.car_id[i])
					self.car_brand_lower = data['DATA']['Table1'][0]['BRANDNM'].lower() #<class 'str'>
					print(self.car_brand_lower)
					self.car_type_lower = data['DATA']['Table1'][0]['CARTYPENM'].lower().strip() #<class 'str'>
					self.car_year = data['DATA']['Table1'][0]['CARYY']

					if not os.path.exists('./HOT_image/{}'.format(self.car_brand_lower)):#if the folder not exist and needed to create a new folder
						os.mkdir('./HOT_image/{}'.format(self.car_brand_lower))

					j = 1
					for item in data['DATA']['Table1'][0].keys():#if the item photo match the re
						if reObj.match(item) and data['DATA']['Table1'][0][item][-3:]=='jpg':
							photo_temp.append(data['DATA']['Table1'][0][item])
							if len(photo_temp)<10:
								img_name = self.car_brand_lower + '_' + self.car_type_lower + '_' + self.car_year + '_' + str(self.car_id[i]) + '_' + '0' + str(j) + '_' +  'l' + '.jpg'
							if len(photo_temp)>=10:
								img_name = self.car_brand_lower + '_' + self.car_type_lower + '_' + self.car_year + '_' + str(self.car_id[i]) + '_' + str(j) + '_' + 'l' + '.jpg'
							get_img = requests.get(data['DATA']['Table1'][0][item])#by get method to get the photo
							get_img.raise_for_status()
							if not os.path.exists('./HOT_image/{}/{}'.format(self.car_brand_lower,self.car_type_lower)):
								os.mkdir('./HOT_image/{}/{}'.format(self.car_brand_lower,self.car_type_lower))
							if not os.path.exists('./HOT_image/{}/{}/{}'.format(self.car_brand_lower,self.car_type_lower,self.car_year)):
								os.mkdir('./HOT_image/{}/{}/{}'.format(self.car_brand_lower,self.car_type_lower,self.car_year))
							if not os.path.exists('./HOT_image/{}/{}/{}/{}'.format(self.car_brand_lower,self.car_type_lower,self.car_year,str(self.car_id[i]))):
								os.mkdir('./HOT_image/{}/{}/{}/{}'.format(self.car_brand_lower,self.car_type_lower,self.car_year,str(self.car_id[i])))
							j+=1
							#save to the file
							with open('./HOT_image/{}/{}/{}/{}/{}'.format(self.car_brand_lower,self.car_type_lower,self.car_year,str(self.car_id[i]),img_name), 'wb') as img_in:
								for diskStorage in get_img.iter_content(10240):
										img_in.write(diskStorage)
				except:
					print(str(self.car_id[i])+'getting wrong!')
					continue

if __name__ == '__main__':
	car = Crawler()
	p1 = threading.Thread(target= car.by_car_crawler)
	p2 = threading.Thread(target=car.image_crawler)
	p1.start()
	p2.start()
	p1.join()
	p2.join()


