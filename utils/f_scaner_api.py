from asyncio.windows_events import NULL
import code
from pyzbar import pyzbar
import numpy as np
import pandas.io.sql as sqlio
import oracledb
import psycopg2 as PG
from misc.logging import logging
from config.config import db_smart, db_pgdev

#########################CONNECT TO ORACLE########################################
def SMART_connect():
    try:
        logging.info("Connection to DB EXA: Start")
        cp = oracledb.ConnectParams(user=db_smart['user'],password=db_smart['pwd'],host=db_smart['host'],port=db_smart['port'],service_name=db_smart['name'])
        con_exa = oracledb.connect(params=cp)
        logging.info("Connection to DB EXA: Done")
    except oracledb.Error as err:
        logging.exception("Connection to DB EXA: Query error: {}".format(err))
    return con_exa

def PG_connect():
    try:
        logging.info("Connection to DB PGSQL: Start")
        con_pg = PG.connect(dbname=db_pgdev['dbname'], user=db_pgdev["user"], password=db_pgdev["pwd"], host=db_pgdev["host"])
        logging.info("Connection to DB PGSQL: Done")
    except PG.Error as err:
        logging.exception("Connection to DB PGSQL: Query error: {}".format(err))
    return con_pg


#logging
def scan_logging(user_id, shop, dcode='', art=''):
	con = PG_connect()
	try:
		with con.cursor() as cursor:
			logging.info(f"Logging: {user_id} , {dcode} ,{shop}")
			v_sql = f"""insert into chat_bot_prod.scbot_logs (DT,USER_ID,BCODE,SHOP)
						select CURRENT_TIMESTAMP as DT,
						'{user_id}' as USER_ID,
						'{dcode}' as BCODE,
						'{art}'
						{shop} as SHOP"""
			cursor.execute(v_sql)
			con.commit()
	except Exception as ex:
		logging.info(f"Исключение {ex}")


class SendData():
	#определение EAN по фото
	def f_get_prc(img,loc):
		image = img
		image_data = {}
		barcode = pyzbar.decode(np.asarray(image))
		if len(barcode) == 0:
			bcode = '0'
		else:
			if barcode[0].type =='QRCODE':
				barcode = barcode[1].data
				image_data["barcode"] = int(barcode.decode("utf-8"))
				bcode = image_data["barcode"]
			else:
				barcode = barcode[0].data
				image_data["barcode"] = int(barcode.decode("utf-8"))
				bcode = image_data["barcode"]

		sql_Check = f"""select
						ART as "Артикул",
						EAN as "Штрихкод",
						STOCK as "Сток",
						PRICE as "Цена",
						OBJECT_BK as "Магазин",
						SLS_QTY as "Продажи_7_дней",
						PRODUCT_UNITY as "Юнит",
						trim(STATUS) as "Статус",
						MINSTOCK as "Мин_сток",
						in_way as "В_пути"
						from BOT_SERVICE.BOT_PRC_ST_SLS
						where (EAN = {bcode} or EAN =rpad(substr({bcode},-13,7),13,0))
						and OBJECT_BK = '{loc}' """
		return FetchData.f_get_info_AEM(df_check=FetchData.sql_to_df(sql_Check)),bcode
	#поиск инфы по EAN в SMART
	def f_get_prc_bc(bcode,loc):
		sql_Check = f"""select
						ART as "Артикул",
						EAN as "Штрихкод",
						STOCK as "Сток",
						PRICE as "Цена",
						OBJECT_BK as "Магазин",
						SLS_QTY as "Продажи_7_дней",
						PRODUCT_UNITY as "Юнит",
						trim(STATUS) as "Статус",
						MINSTOCK as "Мин_сток",
						in_way as "В_пути"
						from BOT_SERVICE.BOT_PRC_ST_SLS
						where (EAN = {bcode} or EAN =rpad(substr({bcode},-13,7),13,0))
						and OBJECT_BK = '{loc}'	"""
		return FetchData.f_get_info_AEM(FetchData.sql_to_df(sql_Check))
	#поиск инфы по артикула в SMART
	def f_get_prc_ar(bcode):
		sql_Check = f"""SELECT
						k.shop AS "Магазин",
						k.art AS "Артикул",
						k.artname AS "Наименование",
						k.MART AS "Отдел",
						k.SEGMENT AS "Сегмент",
						k.CATEGORY AS "Категория",
						k.family AS "Семья",
						k."Код марки",
						k."Тип товара",
						k."Дата создания",
						k."Дата изменения",
						k."Модуль",
						k."Код НДС",
						k."Код статуса",
						k."Единица продажи",
						k."Ед. измерения",
						k."Вес штучный (в кг)",
						k."Высота (м)",
						k."Длина (м)",
						k."Ширина (м)",
						k."Объём (в м3)",
						k."Этикетка R1",
						k."Этикетка R5",
						k."Класс хранения",
						k.load_dt AS "Время обновления данных"
						FROM bot_service.dm_mdata_meti k
						WHERE ART = {bcode} """
		return FetchData.f_get_info_art(FetchData.sql_to_df(sql_Check))

class FetchData():
#Fetch dataframe from SMART
	def sql_to_df(sql):
			conn = SMART_connect()
			ocursor = conn.cursor()
			ocursor.execute("alter session set nls_territory = russia")
			df = sqlio.read_sql_query(sql, conn)
			ocursor.close()
			conn.close()
			return (df)
	#EAN Data
	def f_get_info_AEM(df_check):
		if df_check.empty is True:
			itog = "Штрихкод не найден!\nПроверь, правильно ввел ШК? \nЖду 8ми или 13ти значный код. "
		else:
			df_check.fillna('', inplace=True) #replace None values to 'space' in the dataframe
			art = df_check.iloc [0]['Артикул']
			shk = df_check.iloc [0]['Штрихкод']
			stock = df_check.iloc [0]['Сток']
			prc = df_check.iloc [0]['Цена']
			shop = df_check.iloc [0]['Магазин']
			sls = df_check.iloc [0]['Продажи_7_дней']
			unt = df_check.iloc [0]['Юнит']
			sts = df_check.iloc [0]['Статус']
			mins = df_check.iloc [0]['Мин_сток']
			inway = df_check.iloc [0]['В_пути']
			itog ="<b>Артикул</b>:" + f" <code>{art}</code>\n"\
					"<b>Штрихкод</b>:" + f" <code>{shk}</code>\n"\
					"<b>Статус</b>:" + f" {sts}\n"\
					"<b>Сток</b>:" + f" {stock}\n"\
					"<b>Мин.Запас</b>:" + f" {mins}\n"\
					"<b>В пути (на утро)</b>:" + f" {inway}\n"\
					"<b>Продажи за посл. 7 дней</b>:" + f" {sls}\n"\
					"<b>Юнит</b>:" + f" {unt}\n"\
					"<b>Цена</b>:" + f" {prc}\n"\
					"<b>Магазин</b>:" + f" {shop}"
		return itog, art
	#Article Data
	def f_get_info_art(df_check):
		if df_check.empty is True:
			itog = "Артикул не найден!\nПроверьте, правильность введенного значения\Необходим код состоящий не более чем из 6 знаков."
		else:
			df_check.fillna('', inplace=True) #replace None values to 'space' in the dataframe
			shop = df_check.iloc[0]['Магазин']
			art = df_check.iloc [0]['Артикул']
			artnm = df_check.iloc[0]['Наименование'].strip().lower()
			mart = df_check.iloc[0]['Отдел'].strip().lower()
			seg = df_check.iloc[0]['Сегмент'].strip().lower()
			cat = df_check.iloc[0]['Категория'].strip().lower()
			fam = df_check.iloc[0]['Семья'].strip().lower()
			mark = df_check.iloc[0]['Код марки'].strip()
			type = df_check.iloc[0]['Тип товара'].strip()
			cre_date = df_check.iloc[0]['Дата создания'].date()
			cre_ch =df_check.iloc[0]['Дата изменения'].date()
			mod = df_check.iloc[0]['Модуль']
			VAT = df_check.iloc[0]['Код НДС']
			status = df_check.iloc[0]['Код статуса'].strip()
			unit_sl = df_check.iloc[0]['Единица продажи']
			unit = df_check.iloc[0]['Ед. измерения']
			unit_weight = df_check.iloc[0]['Вес штучный (в кг)']
			height = df_check.iloc[0]['Высота (м)']
			width = df_check.iloc[0]['Ширина (м)']
			length = df_check.iloc[0]['Длина (м)']
			volume = df_check.iloc[0]['Объём (в м3)']
			r1 = df_check.iloc[0]['Этикетка R1'].strip().lower()
			r5 = df_check.iloc[0]['Этикетка R5'].strip().lower()
			keep_cl = df_check.iloc[0]['Класс хранения'].strip()
			update = df_check.iloc[0]['Время обновления данных']
			itog =  "<b>Market</b>:" + f" {shop}\n"\
					"<b>Артикул</b>:" + f" <code>{art}</code>\n"\
					"<b>Наименование</b>:" + f"{artnm}\n"\
					"<b>Отдел</b>:" + f" {mart}\n"\
					"<b>Сегмент</b>:" + f" {seg}\n"\
					"<b>Категория</b>:" + f" {cat}\n"\
					"<b>Семья</b>:" + f" {fam}\n"\
					"<b>Код марки</b>:" + f" {mark}\n"\
					"<b>Тип товара</b>:" + f" {type}\n"\
					"<b>Дата создания</b>:" + f" {cre_date}\n"\
					"<b>Дата изменения</b>:" + f" {cre_ch}\n"\
					"<b>Модуль</b>:" + f" {mod}\n"\
					"<b>Код НДС</b>:" + f" {VAT}\n"\
					"<b>Код статуса</b>:" + f" {status}\n"\
					"<b>Единица продажи</b>:" + f" {unit_sl}\n"\
					"<b>Единица измерения</b>:" + f" {unit}\n"\
					"<b>Вес штучный (в кг)</b>:" + f" {unit_weight}\n"\
					"<b>Высота (м)</b>:" + f" {height}\n"\
					"<b>Длина (м)</b>:" + f" {length}\n"\
					"<b>Ширина (м)</b>:" + f" {width}\n"\
					"<b>Объём (в м3)</b>" + f" {volume}\n"\
					"<b>R1</b>:" + f" {r1}\n"\
					"<b>R5</b>:" + f" {r5}\n"\
					"<b>Класс хранения</b>:" + f" {keep_cl}\n"\
					"<b>Дата обновления данных</b>:" +f" {update}"
		return itog

class Locations():
	#take a loc from user_id
	def f_get_loc(user_id):
		con = PG_connect()
		# logging.info("Select location data from user_id")
		try:
			with con.cursor() as cursor:
				v_sql = f"""select LOCATION from chat_bot_prod.setup_scbot_users
							where USER_ID={user_id}"""
				cursor.execute(v_sql)
				ret = cursor.fetchall()
		except Exception as ex:
			logging.exception(f"Возникло исключение {ex}")
		return ret[0][0]
	#change loc for user_id after fetch location'
	def f_upd_loc(user_id,latitude,longitude):
		logging.info(f"Get {latitude} and {longitude} from {user_id}")
		con = PG_connect()
		try:
			with con.cursor() as cursor:
				v_sql = f"""update chat_bot_prod.setup_scbot_users
								set LOCATION =(select COALESCE((
													select OBJECT_BK
													from chat_bot_prod.lu_obj_object_cut
													where cast(LATITUDE as text) like ''||substring(cast({latitude} as text),1,5)||'%'
													and cast(LONGITUDE as text) like ''||substring(cast({longitude} as text),1,5)||'%'
													and IS_ACTIVE=1)
													,(select location from chat_bot_prod.setup_scbot_users where user_id = {user_id}),'001'))
								where USER_ID={user_id}"""
							#Old Oracle DML
    						# f"""update BOT_SERVICE.setup_bot_users
							# set LOCATION =(select nvl((
							# 			select OBJECT_BK from dm.lu_obj_object
							# 			where LATITUDE like ''||substr({latitude},1,4)||'%'
							# 			and LONGITUDE like ''||substr({longitude},1,4)||'%'
							# 			and IS_ACTIVE=1),'001') from dual)
							# where USER_ID={user_id}"""
				cursor.execute(v_sql)
				con.commit()
			logging.info(f"update for {user_id} - complete")
		except Exception as ex:
			logging.exception(f"Возникло исключение {ex}")
