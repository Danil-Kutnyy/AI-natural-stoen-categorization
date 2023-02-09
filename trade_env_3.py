import csv
import random
import os
from datetime import datetime
from datetime import timedelta
from datetime import date
import math
import numpy as np
import calendar
from calendar import monthrange
from dateutil.relativedelta import relativedelta

'''
env.reset
env.step(action)
env.create_env(name,represemtation,render)
env.obser_sapce
env.action_space
env.close
'''


stock_path = '/Users/danilkutny/Desktop/VKR traiding bot/Market_Dataset_full/Stocks'
indicators_path ='/Users/danilkutny/Desktop/VKR traiding bot/Market_Dataset_full/Indicators'
news_path = '/Users/danilkutny/Desktop/VKR traiding bot/Market_Dataset_full/News'
totals_days_per_run = 14 # do not make smaller than in the sotck, hwihc have the less amount of days history 


#test boundaries
lower_date = datetime.strptime('2019-12-31', '%Y-%m-%d')
upper_date_test = datetime.strptime('2020-12-31', '%Y-%m-%d')

#real boundary
upper_date_real = datetime.strptime('2020-12-31', '%Y-%m-%d')
date_min = int(str(lower_date)[:4])

#lower boundary for history
lower_date_dataset = datetime.strptime('1992-01-01', '%Y-%m-%d')
date_min_total = int(str(lower_date_dataset)[:4])
all_dates_new_total = [lower_date_dataset+timedelta(days=number) for number in range((upper_date_real-lower_date_dataset).days+1)]


#create list of total days from 1997-01-02 to 2021-04-07
all_dates_new = [lower_date+timedelta(days=number) for number in range((upper_date_real-lower_date).days+1)]

#transaction_cost = 0.003
eps = np.finfo(np.float32).eps.item()
transaction_cost = eps
back_days = 400
#transaction_cost_min = 1.23

#This function will return a random datetime between two datetime objects.
def random_date(start, end):
    delta = end - start
    int_delta = delta.days
    random_days = random.randrange(int_delta)
    return start + timedelta(days=random_days)


def encoded_date(date_datetime):
	d_1 = (np.sin(date_datetime.weekday() * 2 * np.pi / 7)+1)/2 
	d_2 = (np.cos(date_datetime.weekday() * 2 * np.pi / 7)+1)/2  
	m_1 = (np.sin(date_datetime.day * 2 * np.pi / calendar.monthrange(date_datetime.year, date_datetime.month)[1])+1)/2 
	m_2 = (np.cos(date_datetime.day * 2 * np.pi / calendar.monthrange(date_datetime.year, date_datetime.month)[1])+1)/2 
	y_1 = (np.sin(date_datetime.timetuple().tm_yday * 2 * np.pi / 366)+1)/2
	y_2 = (np.cos(date_datetime.timetuple().tm_yday * 2 * np.pi / 366)+1)/2
	return np.array([y_1, y_2, m_1, m_2, d_1, d_2])

def stock_encoding(number):
	one_hot = np.zeros(100)
	one_hot[number] = 1
	return one_hot


def get_no_value_new(dates_to_date, market_to_date, indicators_to_date, news=[], norm_value=0):
	
	np_dates_to_date = []


	for date_i in dates_to_date:
		np_dates_to_date.append(encoded_date(date_i))
	np_dates_to_date = np.array(np_dates_to_date[-40:])


	np_market_to_date = []
	prices_to_date = []
	max_vol = 0
	max_price = 0


	for date_i in market_to_date:
		np_market_to_date.append([])
		prices_to_date.append([])
		prices_to_date[-1].append(float(market_to_date[date_i][0]))
		prices_to_date[-1].append(float(market_to_date[date_i][3]))
		if max_price < float(market_to_date[date_i][1]):
			max_price =  float(market_to_date[date_i][1])

		if max_price < float(market_to_date[date_i][3]):
			max_price = market_to_date[date_i][1]


		if float(market_to_date[date_i][4]) > max_vol:
			max_vol = float(market_to_date[date_i][4])

		for element in market_to_date[date_i]:
			np_market_to_date[-1].append(float(element))


	for price_i_list in prices_to_date:
		for price_i in price_i_list:
			if price_i != float(0):
				last_price = price_i
				break
	
	if norm_value == 0:
		norm_value = last_price


	np_market_to_date_norm = []
	
	for list_i in np_market_to_date[-40:]:
		np_market_to_date_norm.append([])
	
		np_market_to_date_norm[-1].append(list_i[0]/(norm_value+eps))
		np_market_to_date_norm[-1].append(list_i[1]/norm_value+eps)
		np_market_to_date_norm[-1].append(list_i[2]/norm_value+eps)
		np_market_to_date_norm[-1].append(list_i[3]/norm_value+eps)
		np_market_to_date_norm[-1].append(list_i[4]/(max_vol+eps))


	prices_years = []


	if len(prices_to_date) > 400:
		for i in range(5400):
			if i % 30 == 0:
				try:
					if prices_years.append(prices_to_date[-i]) == float(0):
						if prices_years.append(prices_to_date[-i-1]) == float(0):
							prices_years.append(prices_to_date[-i-2])
						else:
							prices_years.append(prices_to_date[-i-1])
					
					else:
						prices_years.append(prices_to_date[-i])

				except IndexError:
					prices_years.append([0.0,0.0])
	else:
		prices_years =  prices_to_date

	if len(prices_years) <= 180:
		for i in range(180):
			try:
				prices_years[i]
			except IndexError:
				prices_years.inser(0,[0,0])
	else:
		prices_years = prices_years[:180]


	prices_to_date = prices_to_date[-400:]


	#last_price = 0
	

	#price up to days -400
	prices_to_date = np.array(prices_to_date)/(max_price+eps)
	#monthly prices for last 15 years
	prices_years = np.array(prices_years)/(max_price+eps)
	#all informatio about market for the past 40 days:
	np_market_to_date = np.array(np_market_to_date_norm)
	#past 400 days encoded
	np_dates_to_date = np.array(np_dates_to_date)












	d = np.array(np_market_to_date[-back_days:])

	target = np.array([np_market_to_date[-1][0],np_market_to_date[-1][3]])

	np_indicators_to_date = []
	maximum_values_price = []


	for indic_i in indicators_to_date:
		np_indicators_to_date.append([])
		max_val_temp_price = 0
		for date_i in indicators_to_date[indic_i]:
			
			np_indicators_to_date[-1].append([float(i) for i in indicators_to_date[indic_i][date_i]])
			
			if float(indicators_to_date[indic_i][date_i][1]) > max_val_temp_price:
				max_val_temp_price = float(indicators_to_date[indic_i][date_i][1])
		
		maximum_values_price.append(max_val_temp_price)

	
	for ind, val in enumerate(np_indicators_to_date):
		np_indicators_to_date[ind] = val[-back_days:]
		for ind_2, val_2 in enumerate(np_indicators_to_date[ind]):
			temp = [i/(maximum_values_price[ind]+eps) for i in val_2]
			np_indicators_to_date[ind][ind_2] = temp
	np_indicators_to_date = np.array(np_indicators_to_date)

	'''
	if news!=[]:
		for i in range(384):
			try:
				a = news[i]
				for i_2 in range(70):
					try:
						a = news[i][i_2]
					except IndexError:
						news[i]+=' '
			except IndexError:
				news.append(' ')
				for i_2 in range(69):
					news[i]+=' '
	else:
		for i in range(384):
			news.append(' ')
			for i_2 in range(69):
				news[i]+=' '
	news = np.array(news)
	'''

	'''
	if news!=[]:
		for i in range(384):
			try:
				a = news[i]
				for i_2 in range(70):
					try:
						a = news[i][i_2]
					except IndexError:
						news[i]+=' '
			except IndexError:
				news.append(' ')
				for i_2 in range(69):
					news[i]+=' '
	else:
		for i in range(384):
			news.append(' ')
			for i_2 in range(69):
				news[i]+=' '
	news = np.array(news)
	'''


	return 	prices_to_date, prices_years, np_dates_to_date, np_market_to_date, np_indicators_to_date, last_price





def get_np_values(dates_to_date, market_to_date, indicators_to_date, news=[], back_days=back_days):
	np_dates_to_date = []

	dates_str = []

	for date in dates_to_date:
		np_dates_to_date.append(int(str(date)[:4]+str(date)[5:7]+str(date)[8:10]))
		dates_str.append(str(date)[:10])
	np_dates_to_date = np.array(np_dates_to_date[-back_days:])
	
	np_market_to_date = []
	for date_i in market_to_date:
		np_market_to_date.append([])
		for element in market_to_date[date_i]:
			np_market_to_date[-1].append(float(element))
	np_market_to_date = np.array(np_market_to_date[-back_days:])

	target = np.array([np_market_to_date[-1][0],np_market_to_date[-1][3]])

	np_indicators_to_date = []

	for indic_i in indicators_to_date:
		np_indicators_to_date.append([])
		for date_i in indicators_to_date[indic_i]:
			np_indicators_to_date[-1].append(indicators_to_date[indic_i][date_i])
	
	for ind, val in enumerate(np_indicators_to_date):
		np_indicators_to_date[ind] = val[-back_days:]
	np_indicators_to_date = np.array(np_indicators_to_date)

	if news!=[]:
		for i in range(384):
			try:
				a = news[i]
				for i_2 in range(70):
					try:
						a = news[i][i_2]
					except IndexError:
						news[i]+=' '
			except IndexError:
				news.append(' ')
				for i_2 in range(69):
					news[i]+=' '
	else:
		for i in range(384):
			news.append(' ')
			for i_2 in range(69):
				news[i]+=' '
	news = np.array(news)

	return np_dates_to_date, np_market_to_date, np_indicators_to_date, news, target
















class market_environment():
	
	def __init__(self,name):
		#open stock files and make a list of 
		stock_listing = os.listdir(r'{}'.format(stock_path))
		stocks_list = []
		for name in stock_listing:
			if name != '.DS_Store':
				stocks_list.append(name)
		self.total_stocks_quantity = len(stocks_list)

		#create a list of indexes
		listing = os.listdir(r'{}'.format(indicators_path))
		indexes = {}
		for name in listing:
			if name != '.DS_Store':
				indexes[name[:-4]] = {}



		#create a dciitonary, wich contain all information about the market indexes pror to each date
		for index in indexes:
			with open('{}/{}'.format(indicators_path, index+'.csv', 'r')) as csv_file:
				index_csv = csv.DictReader(csv_file)
				for line in iter(index_csv):
					if int(line['Date'][0:4]) < date_min_total:
						pass
					else:
						indexes[index][line['Date']] = []
						try:
							float(line['Open'])
							indexes[index][line['Date']].append(line['Open'])
							indexes[index][line['Date']].append(line['High'])
							indexes[index][line['Date']].append(line['Low'])
							indexes[index][line['Date']].append(line['Close'])
						except ValueError:
							indexes[index][line['Date']].append('0')
							indexes[index][line['Date']].append('0')
							indexes[index][line['Date']].append('0')
							indexes[index][line['Date']].append('0')
		
		self.news_full = {}

		#maximum news per day:  384
		#maximum senteces simbols:  70
		with open('{}/{}'.format(news_path, 'abcnews-date-text'+'.csv', 'r')) as csv_file:
			news_csv = csv.DictReader(csv_file)	
			for date in all_dates_new:
				self.news_full[str(date)[0:4]+'-'+str(date)[5:7]+'-'+str(date)[8:10]] = [] 
			for line in news_csv:
				#print(line['publish_date'],': ',line['headline_text'])
				if int(line['publish_date'][0:4]) < date_min:
					pass
				else:
					try:
						self.news_full[str(line['publish_date'])[0:4]+'-'+str(line['publish_date'])[4:6]+'-'+str(line['publish_date'])[6:8]].append(line['headline_text'])
					except KeyError:
						pass





		self.stocks_list = stocks_list
		self.env_name = name
		self.stock_number = None
		self.stock_name = None
		self.date = None
		self.stock_market_full = None
		self.indicators_full = indexes
		self.day_start = False
		self.done = False #indicators if all dates and all stocks periods have been used
		self.cash = 10000.0
		self.qunaty_stocks = 0
		self.investment = 0.0
		self.reward = 0.0
	
	def training_loop_create(self, portfolio=False):
		if portfolio == True:
			self.portfolio = True
			self.batch_data = []
		#this piese of code create a dictionary with all stocks as keys, and values are lists, containing dates. Each date is used to create new run
		all_stocks_end_start = {}
		stock_date_used = {}
		for stock_name_i in self.stocks_list:
			all_stocks_end_start[stock_name_i[:-4]] = []
			stock_date_used[stock_name_i[:-4]] = []
			last_date = 0
			with open('{}/{}'.format(stock_path, stock_name_i, 'r')) as csv_file:
				stocks_csv = csv.DictReader(csv_file)
				for line in stocks_csv:
					'''
					if int(line['Date'][0:4]) < date_min:
						last_date = int(line['Date'][0:4])
						pass
					if last_date == 0:
						last_date = int(line['Date'][0:4])
					if last_date < int(line['Date'][0:4]):
					'''
					if  datetime.strptime(line['Date'][0:10], '%Y-%m-%d') > lower_date:
						#date_temp_var = line['Date'][0:4]+'-'+'01'+'-'+'01'
						#date_temp_var = datetime.strptime(date_temp_var, '%Y-%m-%d')
						date_temp_var = datetime.strptime(line['Date'][0:10], '%Y-%m-%d')
						for i in range(7):
							if date_temp_var.weekday() == 2:
								all_stocks_end_start[stock_name_i[:-4]].append(date_temp_var)
								all_stocks_end_start[stock_name_i[:-4]].append(upper_date_test)
								break
							else:
								date_temp_var = date_temp_var + relativedelta(days=1)

		#print(all_stocks_end_start)
		all_stocks_periods = {}
		for key in all_stocks_end_start:
			periods_in_each_stock = math.floor(float((all_stocks_end_start[key][1]-all_stocks_end_start[key][0]).days/(totals_days_per_run+eps)))
			all_stocks_periods[key] = []
			all_stocks_periods[key].append(all_stocks_end_start[key][0])
			while True:
				value = (all_stocks_periods[key][-1]+relativedelta(weeks=1))
				if value >= upper_date_test:
					break
				#print(all_stocks_periods[key][-1].weekday())
				all_stocks_periods[key].append(all_stocks_periods[key][-1]+relativedelta(weeks=1))
		
		self.all_stocks_periods = all_stocks_periods

		#not used?
		self.stock_date_used = stock_date_used

		#create a list self.all_limit_dates, which contain all dates of each stocks, used by self.day_start
		#also create self.all_limi_dates_used 
		all_limit_dates = []
		for key in self.all_stocks_periods:
			for value in self.all_stocks_periods[key]:
				all_limit_dates.append(value)
		
		self.all_limit_dates = sorted(all_limit_dates)[:-1]
		return len(self.all_limit_dates)
	def new_date_and_stock(self):
		if self.done == False:
			if len(self.all_limit_dates) != 1:
				for stock_i in self.all_stocks_periods:
					for stock_date_i in self.all_stocks_periods[stock_i]:
						if self.all_limit_dates[0] == stock_date_i:
							#print(self.all_limit_dates[0])
							temp_var = self.all_limit_dates[0]
							self.all_limit_dates = self.all_limit_dates[1:]
							self.all_stocks_periods[stock_i] = self.all_stocks_periods[stock_i][1:]
							return stock_i, temp_var, False
						else:
							pass
			else:
				for stock_i in self.all_stocks_periods:
					for stock_date_i in self.all_stocks_periods[stock_i]:
						if self.all_limit_dates[0] == stock_date_i:
							temp_var = self.all_limit_dates[0]
							self.all_limit_dates = []
							self.done = True
							temp_stock = stock_i
							self.all_stocks_periods[stock_i] = self.all_stocks_periods[stock_i][1:]
							return stock_i, temp_var, True
		else:
			return None, None, True

	def next_batch(self,np=False):
		
		self.day_start = True
		self.b_h_qunat = 0
		self.b_h_cash = 10000.0
		self.b_h_inv = 0.0
		self.b_h = self.b_h_inv+self.b_h_cash
		self.b_h_check = False
		#choose random random stock
		self.cash = 10000.0
		self.qunaty_stocks = 0
		self.investment = 0.0
		self.reward = 0.0
		if self.portfolio == True:
			self.batch_data.append([])

		
		if self.done == False:
			stock_random, date_to_start, done = self.new_date_and_stock()
			self.stock_name = stock_random
			self.stock_number = self.stocks_list.index('{}.csv'.format(self.stock_name))
			


			#create dicitonary of a stock which contain all information about it
			stock = {}
			with open('{}/{}.csv'.format(stock_path, self.stock_name, 'r')) as csv_file:
				stocks_csv = csv.DictReader(csv_file)
				counter = 0
				for line in stocks_csv:
					if int(line['Date'][0:4]) < date_min_total:
						pass
					else:
						try:
							float(line['Open'])
							stock[line['Date']]=[]
							stock[line['Date']].append(line['Open'])
							stock[line['Date']].append(line['High'])
							stock[line['Date']].append(line['Low'])
							stock[line['Date']].append(line['Close'])
							stock[line['Date']].append(line['Volume'])
						except ValueError:
							stock[line['Date']]=[]
							stock[line['Date']].append(0)
							stock[line['Date']].append(0)
							stock[line['Date']].append(0)
							stock[line['Date']].append(0)
							stock[line['Date']].append(0)

						counter += 1
			self.stock_market_full = stock

			#self.date = date_to_start
			self.date = date_to_start

			#creating market envoronemts, up to date
			self.dates_to_date = []
			self.market_to_date = {}
			self.indicators_to_date = {}

			#craet a dcitonry of market indicators.
			counter_inixes_names = 0
			for indicator_name in self.indicators_full:
				self.indicators_to_date[indicator_name] = {}
				counter_inixes_names += 1

			#create up to date dictioanrey of incicators and stock, adn list of up to date dates
			for date_i in all_dates_new_total:
				if date_i == date_to_start+timedelta(days=1):
					break
				else:
					self.dates_to_date.append(date_i)
					try:
						self.market_to_date[str(date_i)[:10]] = self.stock_market_full[str(date_i)[:10]]
					except KeyError:
						self.market_to_date[str(date_i)[:10]] = [0,0,0,0,0]
					for each_index in self.indicators_to_date:
						try:
							self.indicators_to_date[each_index][str(date_i)[:10]] = self.indicators_full[each_index][str(date_i)[:10]]
						except KeyError:
							self.indicators_to_date[each_index][str(date_i)[:10]] = [0,0,0,0]
			
			#porfolio managment
	
			

			try:
				if self.portfolio == False:
					pass
				else:
					self.batch_data[-1].append(self.market_to_date[str(date_i)[:10]][3])

			except KeyError:
				self.batch_data[-1].append(0.0)





			if np == False:
				return self.dates_to_date, stock_random, date_to_start, self.market_to_date, self.indicators_to_date, done
			
			if np==True:


				prices_to_date, prices_years, np_dates_to_date, np_market_to_date,np_indicators_to_date, last_price = get_no_value_new(self.dates_to_date, self.market_to_date, self.indicators_to_date)
				self.norm_value = last_price
				






				









				#np_dates_to_date, np_market_to_date, np_indicators_to_date, news_dummy, target = get_np_values(
				#self.dates_to_date, self.market_to_date, self.indicators_to_date, news=[], back_days=back_days)
				
				return stock_encoding(self.stock_number), stock_random, date_to_start, prices_to_date, prices_years, np_dates_to_date, np_market_to_date, np_indicators_to_date, last_price, 7, done
				
				#return np_dates_to_date, stock_random, date_to_start, np_market_to_date, np_indicators_to_date, done

		else:
			return None, None, None, None, None, True

	def step(self, action, np=False):






		if float(self.market_to_date[str(self.date)[:10]][3]) != float(0) or float(self.market_to_date[str(self.date)[:10]][0]) != float(0):
			if self.b_h_check == False:
				self.b_h_check = True
				if float(self.market_to_date[str(self.date)[:10]][0]) != float(0):
					self.b_h_qunat = math.floor(self.cash/(float(self.market_to_date[str(self.date)[:10]][0])+eps))
					self.b_h_inv = self.b_h_qunat * float(self.market_to_date[str(self.date)[:10]][0])
					self.b_h_cash = self.b_h_cash - self.b_h_inv
				else:
					self.b_h_qunat = math.floor(self.cash/(float(self.market_to_date[str(self.date)[:10]][3])+eps))
					self.b_h_inv = self.b_h_qunat * float(self.market_to_date[str(self.date)[:10]][3])
					self.b_h_cash = self.b_h_cash - self.b_h_inv
				















		old_total = float(self.cash) + float(self.investment)
		if self.day_start == False: #what was yesterday?
			#account rule
			self.news_today = []
			if float(self.market_to_date[str(self.date)[:10]][3]) == float(0):
				pass
			else:
				






				old_quantity = self.qunaty_stocks
				if action == 0:
					if self.investment == 0.0:
						this_transaction_cost = 0.0
					else:
						this_transaction_cost = self.investment * transaction_cost
					self.cash = self.cash+self.qunaty_stocks*float(self.market_to_date[str(self.date)[:10]][3]) - this_transaction_cost
					self.qunaty_stocks = 0
					self.investment = 0.0
					self.reward = self.cash - old_total
				
				if action == 1:
					old_quantity = self.qunaty_stocks
					if math.floor(self.cash/(float(self.market_to_date[str(self.date)[:10]][3])+eps)) == 0.0:
						this_transaction_cost = 0.0
					else:
						this_transaction_cost = float(self.market_to_date[str(self.date)[:10]][3]) * self.qunaty_stocks * transaction_cost
					self.qunaty_stocks = self.qunaty_stocks+math.floor((self.cash-this_transaction_cost)/(float(self.market_to_date[str(self.date)[:10]][3])+eps))
					if old_quantity != self.qunaty_stocks:
						self.cash = self.cash - (self.qunaty_stocks-old_quantity)*float(self.market_to_date[str(self.date)[:10]][3]) - this_transaction_cost
					else:
						pass
					'''
					try:
						if self.stock_market_full[str(self.date + timedelta(days=1))[:10]][0] != 0:
							print("INVESTED!!!")
							self.investment = self.qunaty_stocks * float(self.stock_market_full[str(self.date + timedelta(days=1))[:10]][0])
						else:
							pass
					except KeyError:
						pass
					'''
					self.reward = self.cash + self.investment - old_total
					
			#new market rule
			self.day_start = True
			self.date = self.date + timedelta(days=1)
			self.dates_to_date.append(self.date)
			try:
				self.market_to_date[str(self.date)[:10]] = [float(self.stock_market_full[str(self.date)[:10]][0]),0,0,0,0]
			except KeyError:
				self.market_to_date[str(self.date)[:10]] = [0,0,0,0,0]
			except ValueError:
				self.market_to_date[str(self.date)[:10]] = [0,0,0,0,0]
			for each_index in self.indicators_full:
				try:
					self.indicators_to_date[each_index][str(self.date)[:10]] = [float(self.indicators_full[each_index][str(self.date)[:10]][0]),0,0,0]
				except KeyError:
					self.indicators_to_date[each_index][str(self.date)[:10]] = [0,0,0,0]



		else:
			#account rule
			try:
				self.news_today = self.news_full[str(self.date)[:10]]
			except KeyError:
				self.news_today = []
			if float(self.market_to_date[str(self.date)[:10]][0]) == float(0):
				pass
			else:
				







				old_quantity = self.qunaty_stocks
				if action == 0:
					if self.investment == 0.0:
						this_transaction_cost = 0.0
					else:
						this_transaction_cost = self.investment * transaction_cost
					
					self.cash = self.cash+self.qunaty_stocks*float(self.market_to_date[str(self.date)[:10]][0]) - this_transaction_cost
					self.qunaty_stocks = 0
					self.investment = 0.0
					self.reward = self.cash - old_total

				if action == 1:
					#print('[str(self.date)[:10]')
					#print(str(self.date)[:10])
					#print('self.market_to_date:')
					#print(self.market_to_date)
					#print('float(self.market_to_date[str(self.date)[:10]])')
					#print(float(self.market_to_date[str(self.date)[:10]][0]))
					additional_qunaty_stocks = math.floor((self.cash/(float(self.market_to_date[str(self.date)[:10]][0])+eps))-(self.cash/(float(self.market_to_date[str(self.date)[:10]][0]))+eps)*transaction_cost)
					if math.floor((self.cash+self.cash*transaction_cost)/(float(self.market_to_date[str(self.date)[:10]][0])+eps)) == 0.0:
						this_transaction_cost = 0.0
					else:
						this_transaction_cost = float(self.market_to_date[str(self.date)[:10]][0]) * additional_qunaty_stocks * transaction_cost

					self.qunaty_stocks = self.qunaty_stocks+math.floor((self.cash-this_transaction_cost)/(float(self.market_to_date[str(self.date)[:10]][0])+eps))
					if old_quantity != self.qunaty_stocks:
						'''
						print('old_quantity: ',old_quantity)
						print('self.qunaty_stocks: ',self.qunaty_stocks)
						print('self.market_to_date[str(self.date)[:10]: ',self.market_to_date[str(self.date)[:10]])
						print('(self.qunaty_stocks-old_quantity):',(self.qunaty_stocks-old_quantity))
						print('inv cost:',(self.qunaty_stocks-old_quantity)*float(self.market_to_date[str(self.date)[:10]][0]))
						print('this_transaction_cost: ',this_transaction_cost)
						print('self.cash:',self.cash)
						'''
						self.cash = self.cash - (self.qunaty_stocks-old_quantity)*float(self.market_to_date[str(self.date)[:10]][0]) - this_transaction_cost
						#print('self.cash after:',self.cash)
					else:
						pass
					'''
					print('try to get to secodn rewadr!')

					try:
						if self.stock_market_full[str(self.date + timedelta(days=1))[:10]][3] != 0:
							self.investment = self.qunaty_stocks * float(self.stock_market_full[str(self.date + timedelta(days=1))[:10]][3])
							print('Inside second reward, old quantity is: ', old_quantity)
							self.reward = self.cash + self.investment - old_quantity * float(self.market_to_date[str(self.date)[:10]][0])
						else:
							pass
					except KeyError:
						pass
					'''
			#new market rule	
			self.day_start = False
			try:
				self.market_to_date[str(self.date)[:10]] = list(map(lambda x: float(x), self.stock_market_full[str(self.date)[:10]]))
			except KeyError:
				self.market_to_date[str(self.date)[:10]] = [0,0,0,0,0]
			except ValueError:
				self.market_to_date[str(self.date)[:10]] = [0,0,0,0,0]
			for each_index in self.indicators_full:
				try:
					self.indicators_to_date[each_index][str(self.date)[:10]] = self.indicators_full[each_index][str(self.date)[:10]]
				except KeyError:
					self.indicators_to_date[each_index][str(self.date)[:10]] = [0,0,0,0]
				except ValueError:
					self.indicators_to_date[each_index][str(self.date)[:10]] = [0,0,0,0]
		
		try:
			if float(self.stock_market_full[str(self.date)[:10]][0]) != 0.0:
				if self.day_start == False:
					self.investment = self.qunaty_stocks * float(self.stock_market_full[str(self.date)[:10]][3])
				else:
					self.investment = self.qunaty_stocks * float(self.stock_market_full[str(self.date)[:10]][0])
			else:
				pass
		except KeyError:
			pass






		if float(self.market_to_date[str(self.date)[:10]][0]) != float(0):
			if float(self.market_to_date[str(self.date)[:10]][3]) != float(0):
				self.b_h_inv = self.b_h_qunat * float(self.market_to_date[str(self.date)[:10]][3])
				self.b_h = self.b_h_inv + self.b_h_cash
			else:
				self.b_h_inv = self.b_h_qunat * float(self.market_to_date[str(self.date)[:10]][0])
				self.b_h = self.b_h_inv + self.b_h_cash




		#It is very hard to find the bug, bug i knew which problem it coused,
		#so i has made this patch, which made verything great now!
		if self.investment == 0 and self.qunaty_stocks!= 0:
			self.investment = self.qunaty_stocks * float(self.market_to_date[str(self.date-timedelta(days=1))[:10]][3])


		self.reward = (self.investment + self.cash - old_total)
		'''
		print('self.cash: ', self.cash, ' | ','self.investment: ', self.investment, ' | ','self.qunaty_stocks: ', self.qunaty_stocks)
		print('self.reward: ', self.reward, ' | ','self.action: ', action)
		print('new: ', str(self.date)[:10])
		print('new: ', self.market_to_date[str(self.date)[:10]])
		print('--------------------------')
		'''




		try:
			if self.portfolio == False:
				pass
			else:
				if self.market_to_date[str(self.date)[:10]][3] != float(0):
					self.batch_data[-1].append(float(self.market_to_date[str(self.date)[:10]][3]))
				else:
					self.batch_data[-1].append(float(self.market_to_date[str(self.date)[:10]][0]))
		except KeyError:
			self.batch_data[-1].append(0.0)





		if np==False:
			return self.dates_to_date, self.market_to_date, self.indicators_to_date, self.news_today, self.cash, self.investment, self.reward, self.b_h, self.done
		
		if np==True:

			#np_dates_to_date, np_market_to_date, np_indicators_to_date, np_news, target = get_np_values(self.dates_to_date, self.market_to_date, self.indicators_to_date, self.news_today, back_days=back_days)

			prices_to_date, prices_years, np_dates_to_date, np_market_to_date, np_indicators_to_date, last_price = get_no_value_new(self.dates_to_date, self.market_to_date, self.indicators_to_date, norm_value=self.norm_value)

			#print(np_market_to_date)

			return np_dates_to_date, np_market_to_date, prices_to_date, prices_years, np_indicators_to_date, self.news_today, self.cash, self.investment, self.reward, self.b_h, self.done
			#return np_dates_to_date, np_market_to_date, np_indicators_to_date, np_news, self.cash, self.investment, self.reward, self.b_h, self.done



	def batch_step(self, actions=None, start=False, end=False):

		self.batch_reward = [0.0 for i in range(self.total_stocks_quantity)]
		
		if start == True:
			self.bacth_step = 0
			self.batch_cash = 1000000.0
			self.batch_quant = [0 for i in range(self.total_stocks_quantity)]
			self.batch_data = np.stack(np.array(self.batch_data), axis=1)

		else:
			self.bacth_step += 1
			self.batch_quant_old = self.batch_quant[:]
		#print('prices inside:',self.batch_data[self.bacth_step])
		#print('actions:',actions[:10])
		#print('data:',self.batch_data[self.bacth_step][:10])


		#sell ane -reward for cost transaction
		buy_counter = 0
		if start == False:
			for act_indx, action_i in enumerate(actions[:len(self.batch_data[0])]):
				if action_i == 0:
					if self.batch_quant[act_indx] != 0:
						if self.batch_data[self.bacth_step-1][act_indx] != float(0):
							sell_price = self.batch_quant[act_indx]*self.batch_data[self.bacth_step-1][act_indx]
							self.batch_cash += sell_price - sell_price*transaction_cost
							self.batch_quant[act_indx] = 0
							self.batch_reward[act_indx] = self.batch_reward[act_indx]-sell_price*transaction_cost
							#print('R_sell#{}:'.format(act_indx), sell_price*transaction_cost)
							#self.batch_reward[act_indx] = 0.0
						else:
							pass

					else:
						pass
				if action_i == 1:
					#print('self.bacth_step:',self.bacth_step)
					#print('act_indx: ',act_indx)
					if self.batch_data[self.bacth_step-1][act_indx] != float(0):
						buy_counter+=1
				if action_i == 2:
					pass


		if buy_counter>0:
			buy_flag = True
			money_to_buy = (self.batch_cash/(buy_counter+eps))#-(self.batch_cash/buy_counter)*transaction_cost
		else:
			buy_flag = False

		#buy and -reward for transaction

		if start == False:
			if buy_flag == False:
				pass
			else:
				for act_indx, action_i in enumerate(actions[:len(self.batch_data[0])]):
					if action_i == 1:
						if self.batch_data[self.bacth_step-1][act_indx] != float(0):
							#print('inside buying setting')
							#print('iself.bacth_step: ',self.bacth_step)
							#print('price: ',self.batch_data[self.bacth_step][act_indx])
							#print('money_to_buy:',money_to_buy)
							#print('bouhgt',math.floor( ((money_to_buy-money_to_buy*transaction_cost)/self.batch_data[self.bacth_step][act_indx]) ))
							#print('trnsaction cost:',(money_to_buy/self.batch_data[self.bacth_step][act_indx])*transaction_cost)
							#print('money_to_buy:',money_to_buy)
							this_qunt = math.floor( money_to_buy/(self.batch_data[self.bacth_step-1][act_indx]*(1+transaction_cost)+eps) )#           - math.ceil(money_to_buy*transaction_cost/self.batch_data[self.bacth_step][act_indx]) )
							#print('this_qunt:',this_qunt)
							#print('before bought!',self.batch_quant[act_indx])
							self.batch_quant[act_indx] = self.batch_quant[act_indx]+this_qunt
							#print('after bought!',self.batch_quant[act_indx])
							self.batch_cash = self.batch_cash - (this_qunt*self.batch_data[self.bacth_step-1][act_indx]*(transaction_cost+1))
							self.batch_reward[act_indx] = self.batch_reward[act_indx]-this_qunt*self.batch_data[self.bacth_step-1][act_indx]*transaction_cost 
							#print('R_buy#{}:'.format(act_indx), this_qunt*self.batch_data[self.bacth_step-1][act_indx]*transaction_cost )


			#calculating reward, new qunatoty and selling
		if start == False:
			#print('pased start=false')
			for qunat_indx, qunt_i in enumerate(self.batch_quant):
				if qunt_i == 0:
					pass
				else:
					#print('qunat != 0')
					if self.batch_data[self.bacth_step][qunat_indx] != float(0):
						#print('price not 0')
						if self.batch_data[self.bacth_step-1][qunat_indx] != float(0):
							#print('last price != 0, chnagin reward')
							#print('reward before:',self.batch_reward[qunat_indx])
							#print('R_delta#{}:'.format(qunat_indx), (self.batch_data[self.bacth_step][qunat_indx]-self.batch_data[self.bacth_step-1][qunat_indx] )*self.batch_quant_old[qunat_indx])
							self.batch_reward[qunat_indx] = self.batch_reward[qunat_indx]+(self.batch_data[self.bacth_step][qunat_indx]-self.batch_data[self.bacth_step-1][qunat_indx] )*self.batch_quant[qunat_indx]
							#print('reward after:',self.batch_reward[qunat_indx])
						else:
							#print('last price == 0, lookin for last prices')
							last_price = 0.0
							for p_list in np.flipud(self.batch_data[:self.bacth_step]):
								#print(p_list[qunat_indx])
								if last_price < p_list[qunat_indx]:
									last_price = p_list[qunat_indx]
									#print('found last price')
									break
							if last_price != 0.0:
								#print('chnagin reward inside las price == 0')
								#print('last price:',last_price)
								#print()
								#print('R_delta#{}:'.format(qunat_indx), ( self.batch_data[self.bacth_step][qunat_indx]-last_price )*self.batch_quant_old[qunat_indx])
								self.batch_reward[qunat_indx] = self.batch_reward[qunat_indx]+( self.batch_data[self.bacth_step][qunat_indx]-last_price )*self.batch_quant[qunat_indx]
							else:
								#print('last price == 0')
								pass




		if end==True:
			self.batch_data = []

		return self.batch_reward, self.batch_data, self.batch_quant, self.batch_cash, self.bacth_step

	def batch_steps_end(self):
		self.batch_data = []




#python3 /Users/danilkutny/Desktop/VKR\ traiding\ bot/trade_env.py
'''
env = market_environment('some')
len_of_bacthes = env.training_loop_create()
stock_name, start_date, market_to_date, indicators_to_date, done = env.next_batch()
today_date, market_to_date, indicators_to_date, news_today, cash, investment, reward, done = env.step(1)
'''


#buy and hold strategy:
'''
env = market_environment('some')
len_of_bacthes = env.training_loop_create()
bah_startegy = 0
average = []
for batch in range(len_of_bacthes):
	bah_startegy = 0
	stock_name, start_date, market_to_date, indicators_to_date, done = env.next_batch()
	counter = 0
	counter_inv = 0
	average = []
	for step in range(totals_days_per_run*2):
		today_date, market_to_date, indicators_to_date, news_today, cash, investment, reward, done = env.step(1)
		bah_startegy_end = cash+investment
		if counter == 0:
			start_day = today_date
		if investment!= 0:
			counter_inv+=1
		if counter_inv==1:
			bah_startegy_start = cash + investment
		if investment!= 0:
			counter_inv+=1
		counter+=1
		print(str(today_date)[:10], str(market_to_date)[-130:])
		print('cash: ', cash,'| investment: ',investment,'| quantity: ' ,env.qunaty_stocks ,'| reward: ',  reward)
	with open('{}/{}.csv'.format(stock_path, env.stock_name, 'r')) as csv_file:
		stocks_csv = csv.DictReader(csv_file)
		counter = 0
		for line in stocks_csv:
			#print(line)
			if line['Date'] == str(start_day)[:10]:
				start_fin = line['Open']
				#print(line['Date'], start_fin)
			if line['Date'] == str(today_date)[:10]:
				final = line['Close']
				#print(line['Date'], final)
	#print(bah_startegy_end-bah_startegy_start - (float(final)-float(start_fin))*env.qunaty_stocks)
	if bah_startegy_end-bah_startegy_start - (float(final)-float(start_fin))*env.qunaty_stocks > 15:
		print(stock_name, str(start_day)[:10], ' - ', str(today_date)[:10])
		print('Start: ',bah_startegy_start)
		print('End: ',bah_startegy_end)
		print('Total reward: ', bah_startegy_end-bah_startegy_start)
		print('test reward: ', (float(final)-float(start_fin))*env.qunaty_stocks)
	if bah_startegy_end-bah_startegy_start - (float(final)-float(start_fin))*env.qunaty_stocks < -15:
		print(stock_name, str(start_day)[:10], ' - ', str(today_date)[:10])
		print('Start: ',bah_startegy_start)
		print('End: ',bah_startegy_end)
		print('Total reward: ', bah_startegy_end-bah_startegy_start)
		print('test reward: ', (float(final)-float(start_fin))*env.qunaty_stocks)
'''