from misc.logging import logging
# json
import json

# подключаем posgr
import psycopg2 as PG
from psycopg2 import sql
from config.config import db_pgdev


# posgree
try:
    logging.info("Connection to DB PGSQL: Start")
    # con = PG.connect(dbname='postgres', user='chat_bot_prod',
    #                  password='HEbCr79ho8M2JcBx2vli', host='lnxcruvpsap0068')
    con = PG.connect(dbname=db_pgdev['dbname'], user=db_pgdev["user"], password=db_pgdev["pwd"], host=db_pgdev["host"])
    logging.info("Connection to DB PGSQL: Done")
except PG.Error as err:
    logging.exception("Connection to DB PGSQL: Error: {}".format(err))


# получение номера Job
def f_get_execution_id():
    logging.info('f_get_execution_id: Start')
    try:
        with con.cursor() as cursor:
            cursor.execute(
                "SELECT nextval('chat_bot_prod.seq_notifier_execution_id')"
            )
            ret = cursor.fetchall()
        cursor.close()
        logging.debug(ret)
        logging.info(f'f_get_execution_id: Done')
    except PG.Error as err:
        logging.exception("f_get_execution_id: Query error: {}".format(err))
    return ret[0][0]


# логирование setup_notifier
def f_logging(p_notifier_id, p_execution_id, p_log_json, p_is_error, log_message):
    logging.info('f_logging: Start')
    try:
        logging.info(log_message)
        with con.cursor() as cursor:
            v_sql = " insert into chat_bot_prod.log_notifier " \
                    " (notifier_id, execution_id, log_json, is_error, load_dt, log_message) " \
                    " values " \
                    " ( " \
                    "  %(notifier_id)s " \
                    ", %(execution_id)s " \
                    ", %(log_json)s " \
                    ", %(is_error)s " \
                    ", clock_timestamp() " \
                    ", %(log_message)s " \
                    " )"
            # logging.info(insert)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id), 'execution_id': str(p_execution_id),
                                   'log_json': json.dumps(p_log_json), 'is_error': p_is_error
                , 'log_message': str(log_message)})
            con.commit()
        cursor.close()
        logging.info('f_logging: Done')
    except PG.Error as err:
        logging.exception("f_logging: query error: {}".format(err))


# старт обновление setup_notifier
def f_start_update_setup_notifier(p_notifier_id, p_execution_id, p_start_dt):
    logging.info('f_start_update_setup_notifier: Start')
    try:
        with con.cursor() as cursor:
            v_sql = ' update chat_bot_prod.setup_notifier' \
                    ' set                                  ' \
                    ' tech_status_id=-1                  ' \
                    ' ,tech_execution_id= %(execution_id)s   ' \
                    ' ,tech_execution_start_last_dt=%(execution_start_last_dt)s' \
                    ' ,tech_execution_finish_last_dt = null' \
                    '    where notifier_id= %(notifier_id)s '
            # logging.info(update)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id), 'execution_id': str(p_execution_id),
                                   'execution_start_last_dt': p_start_dt})
            con.commit()
        cursor.close()
        logging.info('f_start_update_setup_notifier: Done')
    except PG.Error as err:
        logging.exception("f_start_update_setup_notifier: Query error: {}".format(err))


# окончание обновление setup_notifier
def f_finish_update_setup_notifier(p_notifier_id, p_execution_id, p_is_error, p_start_dt, p_finish_dt, p_report_json):
    logging.info('f_finish_update_setup_notifier: Start')
    try:
        with con.cursor() as cursor:
            v_sql = ' update chat_bot_prod.setup_notifier ' \
                    ' set' \
                    ' tech_status_id=2' \
                    ' ,tech_execution_id= %(execution_id)s' \
                    ' ,tech_execution_start_last_dt=%(execution_start_last_dt)s' \
                    ' ,tech_execution_finish_last_dt=%(execution_finish_last_dt)s' \
                    ' ,tech_need_send_allert=coalesce (case when (' \
                    'select tech_is_error_status_last ' \
                    'from chat_bot_prod.setup_notifier where notifier_id= %(notifier_id)s )!=%(is_error_status)s ' \
                    ' then 1 end,tech_need_send_allert)' \
                    ' ,tech_is_error_status_last= %(is_error_status)s' \
                    ' ,tech_report_last= %(last_report_json)s' \
                    '    where notifier_id= %(notifier_id)s '
            # logging.info(update)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id), 'execution_id': str(p_execution_id),
                                   'is_error_status': str(p_is_error)
                , 'execution_start_last_dt': p_start_dt, 'execution_finish_last_dt': p_finish_dt,
                                   'last_report_json': json.dumps(p_report_json)})
            con.commit()
        cursor.close()
        logging.info('f_finish_update_setup_notifier: Done')
    except PG.Error as err:
        logging.exception("f_finish_update_setup_notifier: Query error: {}".format(err))


# вставка данных в лог отчетов
def f_logging_report(p_notifier_id, p_execution_id, p_start_dt, p_finish_dt, p_report_json, p_is_error):
    logging.info('f_finish_update_setup_notifier: Start')
    try:
        with con.cursor() as cursor:
            v_sql = ' insert into chat_bot_prod.log_notifier_report' \
                    ' ( notifier_id, report_json, is_error, execution_id, execution_start_dt, execution_finish_dt) ' \
                    ' values' \
                    ' (' \
                    ' %(notifier_id)s,' \
                    ' %(report_json)s,' \
                    ' %(p_is_error)s,' \
                    ' %(execution_id)s,' \
                    ' %(execution_start_last_dt)s,' \
                    ' %(execution_finish_last_dt)s ' \
                    ')'
            # logging.info(v_sql)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id), 'execution_id': str(p_execution_id),
                                   'p_is_error': str(p_is_error)
                , 'execution_start_last_dt': p_start_dt, 'execution_finish_last_dt': p_finish_dt,
                                   'report_json': json.dumps(p_report_json)})
            con.commit()
        cursor.close()
        logging.info('f_finish_update_setup_notifier: Done')
    except PG.Error as err:
        logging.exception("f_finish_update_setup_notifier: Query error: {}".format(err))


# процедура начала
def f_start(p_notifier_id, p_start_dt):
    logging.info('f_finish_update_setup_notifier: Start')
    execution_id = f_get_execution_id() # получаем номер job
    f_start_update_setup_notifier(p_notifier_id=p_notifier_id, p_execution_id=execution_id, p_start_dt=p_start_dt) # получаем обновляем setup


    f_logging(p_notifier_id=p_notifier_id, p_execution_id=execution_id, p_log_json=None, p_is_error=0,
              log_message='Начало ' + str(p_notifier_id) + '.Подготовка завершена') # пишем в лог
    logging.info('f_finish_update_setup_notifier: Done')
    return execution_id


# процедура начала
def f_finish(p_notifier_id, p_execution_id, p_is_need_send_allert, p_start_dt, p_finish_dt, p_report_json):
    logging.info('f_finish_update_setup_notifier: Start')
    f_finish_update_setup_notifier(p_notifier_id=p_notifier_id, p_execution_id=p_execution_id,
                                   p_is_error=p_is_need_send_allert, p_start_dt=p_start_dt,
                                   p_finish_dt=p_finish_dt, p_report_json=p_report_json)

    # Сохраняем данные в лог
    f_logging(p_notifier_id=p_notifier_id, p_execution_id=p_execution_id, p_log_json=p_report_json,
              p_is_error=0, log_message='Обновл setup завершено. Вставка отчета в log')

    # пишем отчет в лог
    f_logging_report(p_notifier_id=p_notifier_id, p_execution_id=p_execution_id, p_start_dt=p_start_dt,
                     p_finish_dt=p_finish_dt, p_report_json=p_report_json,
                     p_is_error=p_is_need_send_allert)

    # Сохраняем данные в лог
    f_logging(p_notifier_id=p_notifier_id, p_execution_id=p_execution_id, p_log_json=None,
              p_is_error=0,
              log_message='Вставка отчета в log завершено. Завершение программы')
    logging.info('f_finish_update_setup_notifier: Done')
    return 1


# проверка юзеров для отправки
def f_user_check(p_user_id, p_notifier_id):
    logging.info('f_user_check: Start')
    try:
        with con.cursor() as cursor:
            v_sql = "SELECT count(*) FROM chat_bot_prod.setup_notifier_users where user_id = %(user_id)s and notifier_id=%(notifier_id)s"
            # logging.info(v_sql)
            cursor.execute(v_sql, {'user_id': p_user_id, 'notifier_id': p_notifier_id})
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0])
        logging.info('f_user_check: done')
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_user_check: query error: {}".format(err))


# подписка на ноды
def f_user_subscribe(p_user_id, p_notifier_id):
    logging.info(f'f_user_subscribe: Start, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
    try:
        if f_user_check(p_user_id=p_user_id, p_notifier_id=p_notifier_id) == 0:
            with con.cursor() as cursor:
                v_sql = ' INSERT INTO chat_bot_prod.setup_notifier_users' \
                        ' ( user_id, notifier_id) ' \
                        ' values' \
                        ' (' \
                        ' %(user_id)s,' \
                        ' %(notifier_id)s' \
                        ')'
                # logging.info(values)
                cursor.execute(v_sql, {'user_id': p_user_id, 'notifier_id': p_notifier_id})
                con.commit()
            cursor.close()
            logging.info(f'f_user_subscribe: Subscribe done, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
            return 'Подписка оформлена'
        else:
            logging.info(f'f_user_subscribe: Subscribe done before, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
            return 'Подписка была оформлена ранее'
    except PG.Error as err:
        logging.info("f_user_subscribe: Query error: {}".format(err))


# отписка на ноды
def f_user_unsubscribe(p_user_id, p_notifier_id):
    logging.info(f'f_user_unsubscribe: Start, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
    try:
        if f_user_check(p_user_id=p_user_id, p_notifier_id=p_notifier_id) == 0:
            logging.info(f'Subscribe not done before, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
            return 'Подписка не была оформлена ранее'
        else:
            with con.cursor() as cursor:
                v_sql = "delete FROM chat_bot_prod.setup_notifier_users where user_id = %(user_id)s and notifier_id=%(notifier_id)s"
                # logging.info(values)
                cursor.execute(v_sql, {'user_id': p_user_id, 'notifier_id': p_notifier_id})
                con.commit()
            cursor.close()
            logging.info(f'f_user_unsubscribe: Unsubscribe Done, user_id: {p_user_id}, notifier_id: {p_notifier_id}')
            return 'Вы отписались от рассылки'
    except PG.Error as err:
        logging.exception("f_user_unsubscribe: Query error: {}".format(err))


def f_queue():
    logging.info(f'f_queue: Start')
    try:
        with con.cursor() as cursor:
            v_sql = "select queue,notifier_ids from chat_bot_prod.queue_notifier"
            # logging.info(v_sql)
            cursor.execute(v_sql)
            rows = cursor.fetchall()
        cursor.close()
        # logging.info('проверка очереди'+time.ctime())
        # logging.info(rows[0])
        # logging.info(rows[0][0])
        # logging.info(rows[0][1])
        logging.info(f'f_queue: done')
        return rows[0][0], rows[0][1]
    except PG.Error as err:
        logging.exception("f_queue: Query error: {}".format(err))


# обновление статусов по необходимости отправки сообщений
def f_is_error_status_last(p_notifier_id):
    # Статусы потока: "0" - ни разу не запускался, "-1" - работает сейчас, "2" - успешно завершенный, "-2" - ошибка
    logging.info(f'f_is_error_status_last: Start')
    try:
        with con.cursor() as cursor:
            v_sql = ' update chat_bot_prod.setup_notifier ' \
                    ' set' \
                    ' tech_need_send_allert=0' \
                    '    where notifier_id= %(notifier_id)s ' \
                    '   and tech_need_send_allert=1 ' \
                    '   and tech_is_error_status_last=0 '
            # logging.info(v_sql)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id)})
            con.commit()
        cursor.close()
        # logging.info('обновлено')
        logging.info(f'f_is_error_status_last: Done')
        return 1
    except PG.Error as err:
        logging.exception("f_queue: Query error: {}".format(err))


# обновление статусов по отправке данных
def f_out_status(p_notifier_id, p_status):
    # Статус потока: "0" - ни разу не запускался, "-1" - работает сейчас, "2" - успешно завершенный, "-2" - ошибка
    logging.info(f'p_notifier_id: Start, notifier_id: {p_notifier_id}, status: {p_status}')
    try:
        with con.cursor() as cursor:
            v_sql = ' update chat_bot_prod.setup_notifier ' \
                    ' set' \
                    ' tech_out_status_id= %(p_status)s' \
                    ' ,tech_out_execution_mod_last_dt=now()' \
                    '    where notifier_id= %(notifier_id)s '
            # logging.info(update)
            cursor.execute(v_sql, {'notifier_id': str(p_notifier_id), 'p_status': str(p_status)})
            con.commit()
        cursor.close()
        if p_status == 2:
            f_is_error_status_last(p_notifier_id)
        logging.info(f'p_notifier_id: Done, notifier_id: {p_notifier_id}, status: {p_status}')
        return 1
    except PG.Error as err:
        logging.exception("p_notifier_id: Query error: {}".format(err))


# обновление статусов по отправке данных
def f_out_statuses(p_notifier_ids, p_status):
    logging.info(f'f_out_statuses: Start, notifier_ids: {str(p_notifier_ids)}, status: {str(p_status)}')
    # Статус потока: "0" - ни разу не запускался, "-1" - работает сейчас, "2" - успешно завершенный, "-2" - ошибка
    for notifier_id in p_notifier_ids:
        f_out_status(notifier_id, p_status)
    logging.info(f'f_out_statuses: Done, notifier_ids: {str(p_notifier_ids)}, status: {str(p_status)}')


# проверка юзеров для отправки
def f_setup_json(p_notifier_id,p_collumn='IP'):
    logging.info(f'f_setup_json: Start, p_notifier_id: {str(p_notifier_id)}')
    try:
        with con.cursor() as cursor:
            v_sql = "SELECT setup_json FROM chat_bot_prod.setup_notifier where notifier_id=%(notifier_id)s"
            # logging.info(v_sql)
            cursor.execute(v_sql, {'notifier_id': p_notifier_id})
            rows = cursor.fetchall()
        cursor.close()
        # logging.info(rows[0][0][p_collumn])
        logging.info(f'f_setup_json: f_setup_json: Done, p_notifier_id: {str(p_notifier_id)}')
        return rows[0][0][p_collumn]
    except PG.Error as err:
        logging.exception("f_setup_json: Query error: {}".format(err))

# проверка юзеров для отправки
def f_setup_json2(p_notifier_id):
    logging.info(f'f_setup_json: Start, p_notifier_id: {str(p_notifier_id)}')
    try:
        with con.cursor() as cursor:
            v_sql = "SELECT setup_json FROM chat_bot_prod.setup_notifier where notifier_id=%(notifier_id)s"
            # logging.info(v_sql)
            cursor.execute(v_sql, {'notifier_id': p_notifier_id})
            rows = cursor.fetchall()
        cursor.close()
        logging.info(rows[0][0])
        logging.info(f'f_setup_json: f_setup_json: Done, p_notifier_id: {str(p_notifier_id)}')
        return rows[0][0]
    except PG.Error as err:
        logging.exception("f_setup_json: Query error: {}".format(err))

# import F_TELEGRAM_MESSAGE as F_TELEGRAM_MESSAGE
#
# queue,notifier_ids = f_queue()
# logging.info(type(queue))
# logging.info(queue)
# logging.info(type(queue))
# logging.info(notifier_ids)
# #потоки в процессе
# if queue is None:
#     logging.info('type')
# else:
#     #потоки начали выполнение
#     f_out_statuses(p_notifier_ids=notifier_ids,p_status=-1)
#     for rep in queue:
#         logging.info(rep)
#         v_report = F_TELEGRAM_MESSAGE.f_message_header(p_header='Статусы')
#         v_report += F_TELEGRAM_MESSAGE.f_message_format_table(rep['report_json'])
#         logging.info(v_report)
#     #потоки в выполнены
#     f_out_statuses(p_notifier_ids=notifier_ids,p_status=2)
# сброс уведомления для отправки

#
# import F_TELEGRAM_MESSAGE as F_TELEGRAM_MESSAGE
#
# q=f_queue()
# logging.info(type(q))
# report_json=[]
# v_dict={}
# logging.info('0 - '+str(q))
# for i in q:
#     logging.info('1 - '+str(i))
#     logging.info(type(i))
#     #logging.info(i['user_id'])
#     for z in i:
#         logging.info('2 - '+str(z))
#         logging.info(z['user_id'])
#         logging.info(z['report_json'])
#         logging.info(F_TELEGRAM_MESSAGE.f_message_format_table(z['report_json']))
#         #logging.info(z['report_json'])
#         #for x in z['report_json']:
#             #logging.info('3 - '+str(x))
#             #v_dict[x['FLOW']]= str(x['IS_ERROR'])
#             #report_json.append(v_dict)
#             #logging.info(F_TELEGRAM_MESSAGE.f_message_format_table(v_dict))
# #logging.info(v_dict)


# # тест
# def f_test():
#     try:
#         with con.cursor() as cursor:
#             cursor.execute(
#                 "select setup_json ,setup_json->>'SETUP' AS title from chat_bot_prod.setup_notifier"
#             )
#             logging.info(cursor.fetchall())
#         cursor.close()
#     except PG.Error as err:
#         logging.info("Query error: {}".format(err))
#     return

# # #Сохраняем данные в лог
# # try:
# #     f_log(1,'{"146.240.224.143": "running", "146.240.224.144": "running"}', 0, 1)
# # except pgdb.Error as err:
# #     logging.info("Query error: {}".format(err))
#
# seq = f_seq_execution_id()
# logging.info (seq)
#
# #Сохраняем данные в лог
# try:
#     f_test()
# except pg.Error as err:
#     logging.info("Query error: {}".format(err))
#
# f_start_update_setup_notifier(1,seq)
#
# f_finish_update_setup_notifier(1,seq,0)
#
# f_logging_notifier(1, 1,None,1, 'start job')
