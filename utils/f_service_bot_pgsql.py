from misc.logging import logging
import psycopg2 as PG
from psycopg2 import sql
from config.config import db_pgdev

# json
import jsonpickle

#########################CONNECT TO PG########################################
def PG_connect():
    try:
        logging.info("Connection to DB PGSQL: Start")
        con_pg = PG.connect(dbname=db_pgdev['dbname'], user=db_pgdev["user"], password=db_pgdev["pwd"], host=db_pgdev["host"])
        logging.info("Connection to DB PGSQL: Done")
    except PG.Error as err:
        logging.exception("Connection to DB PGSQL: Query error: {}".format(err))
    return con_pg

# логирование
def f_logging(message_id, chat_id, content_type, from_user_id, date_id, text_, message):
    logging.info("f_logging: Start")
    try:
        with PG_connect().cursor() as cursor:
            values = [
                (message_id, chat_id, content_type, from_user_id, date_id, text_, jsonpickle.encode(f"{message.location} {message_id}"))
            ]
            logging.info(values)
            insert = sql.SQL(
                'INSERT INTO chat_bot_prod.log_bot (message_id,chat_id, content_type, from_user_id, date_dt,text_,message) VALUES {}').format(
                sql.SQL(',').join(map(sql.Literal, values))
            )
            cursor.execute("rollback")
            cursor.execute(insert)
            PG_connect().commit()
        logging.info("f_logging: Done")
    except PG.Error as err:
        logging.exception("f_user_check_phone: Query error: {}".format(err))
        with PG_connect().cursor() as cursor:
            cursor.execute("rollback")

# проверка юзера по номеру телефона
def f_user_check_phone(phone_number):
    logging.info(f"f_user_check_phone: Start, {phone_number}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "SELECT count(*) FROM chat_bot_prod.tbot_valid_user where phone_number = %(phone_number)s and enabled = True"
            # logging.info(v_sql)
            # cursor.execute("rollback")
            cursor.execute(v_sql, {'phone_number': phone_number})
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_user_check_phone: Done. Count:{rows[0][0]}")
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_user_check_phone: Query error: {}".format(err))

# проверка юзера по номеру юзера и доступа Enabled
def f_user_check_id(user_id):
    logging.info(f"f_user_check_id: Start, {user_id}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "SELECT count(*) FROM chat_bot_prod.tbot_valid_user where user_id = %(user_id)s and enabled = True"
            # logging.info(v_sql)
            cursor.execute("rollback")
            cursor.execute(v_sql, {'user_id': user_id})
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_user_check_id: Done, {user_id}")
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_user_check_phone: Query error: {}".format(err))

# проверка id юзера в списке для доступа к сервису
def f_user_ids():
    logging.info(f"f_user_ids: Start")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "SELECT array_agg(user_id::bigint) FROM chat_bot_prod.tbot_valid_user where user_id>0 and enabled = True"
            # logging.info(v_sql)
            cursor.execute("rollback")
            cursor.execute(v_sql)
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_check_ids: Done")
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_check_ids: Query error: {}".format(err))

# регистрация
def f_user_registration(phone_number, user_id, name):
    logging.info(f"f_user_registration: Start, {phone_number}, {user_id}, {name}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "update chat_bot_prod.tbot_valid_user set user_id=%(user_id)s ,name=%(name)s where phone_number = %(phone)s"#почему phone?
            # logging.info(v_sql)
            cursor.execute(v_sql, {'phone': phone_number, 'user_id': user_id, 'name': name})
            PG_connect().commit()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_user_registration: Done, {phone_number}, {user_id}, {name}")
        return 1
    except PG.Error as err:
        logging.exception("f_user_registration: Query error: {}".format(err))

#новая регистрация
'''def f_user_registration(phone_number, user_id, first_name):
    logging.info(f"f_user_registration: Start, {phone_number}, {user_id}, {first_name}")
    try:
        with con.cursor() as cursor:
            v_sql = "update chat_bot_prod.tbot_valid_user set user_id=%(user_id)s ,first_name=%(first_name)s where phone_number = %(phone)s"
            # logging.info(v_sql)
            cursor.execute(v_sql, {'phone': phone_number, 'user_id': user_id, 'first_name': first_name})
            con.commit()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_user_registration: Done, {phone_number}, {user_id}, {first_name}")
        return 1
    except PG.Error as err:
        logging.exception("f_user_registration: Query error: {}".format(err))'''

# поиск уведомлений: уведомление,юзеры, текст для отправки
def f_start():
    logging.info(f"f_start: Start")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "select report_json from chat_bot_prod.v_bot_messege_start"
            # logging.info(v_sql)
            cursor.execute(v_sql)
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info(f"f_start: Done")
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_start: Query error: {}".format(err))


def save_prompts(user_id: str, report_id: str,  prompts):
    logging.info(f"Save prompts. user_id:{user_id}, report_id:{report_id}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "INSERT INTO chat_bot_prod.setup_report_prompts (user_id, report_id, prompts) " \
                    f"VALUES (%(user_id)s, %(report_id)s, %(prompts)s) " \
                    "ON CONFLICT ON CONSTRAINT setup_report_prompts_pk " \
                    "DO UPDATE SET " \
                    "user_id = EXCLUDED.user_id, " \
                    "report_id = EXCLUDED.report_id, " \
                    "prompts = EXCLUDED.prompts "
            logging.debug(v_sql)
            logging.debug(prompts)
            cursor.execute(v_sql, {'user_id': user_id, 'report_id': report_id, 'prompts': prompts})
            PG_connect().commit()
        cursor.close()
        logging.info(f"Done. user_id:{user_id}, report_id:{report_id}")
        return 1
    except PG.Error as err:
        logging.exception(f"user_id:{user_id}, report_id:{report_id}, prompts: {prompts}")
        logging.exception("Query error: {}".format(err))


def delete_prompts(user_id: str, report_id: str, promts):
    logging.info(f"Delete prompts. user_id:{user_id}, report_id:{report_id}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "DELETE FROM chat_bot_prod.setup_report_prompts " \
                    f"WHERE user_id=%(user_id)s " \
                    f"AND report_id=%(report_id)s "
            cursor.execute(v_sql, {'user_id': user_id, 'report_id': report_id})
            PG_connect().commit()
        cursor.close()
        logging.info(f"Done. user_id:{user_id}, report_id:{report_id}")
        return 1
    except PG.Error as err:
        logging.exception(f"user_id:{user_id}, report_id:{report_id}")
        logging.exception("Query error: {}".format(err))


def get_prompts(user_id: str, report_id: str):
    logging.info(f"Save prompts. user_id:{user_id}, report_id:{report_id}")
    try:
        with PG_connect().cursor() as cursor:
            v_sql = "SELECT prompts FROM chat_bot_prod.setup_report_prompts " \
                    f"WHERE user_id=%(user_id)s " \
                    f"AND report_id=%(report_id)s "
            logging.info(v_sql)
            cursor.execute(v_sql, {'user_id': user_id, 'report_id': report_id})
            rows = cursor.fetchall()
        cursor.close()
        logging.info(f"Done. user_id:{user_id}, report_id:{report_id},'{rows}'")
        if rows:
            return rows[0][0]
    except PG.Error as err:
        logging.exception(f"user_id:{user_id}, report_id:{report_id}")
        logging.exception("Query error: {}".format(err))
