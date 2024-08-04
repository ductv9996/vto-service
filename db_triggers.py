import psycopg2
import select
import logging
from db_table import AvatarStatusHandler
from worker_multiple.tasks import avatar_merge_task

controller = AvatarStatusHandler()
# Set up logging
logging.basicConfig(filename='db_changes.log', level=logging.INFO, format='%(asctime)s - %(message)s')
TABLE_NAME = 'avatar_ai_side'
DB_NAME = 'avatar_status_db'
DB_USER = 'testuser'
DB_PASS = 'testpassword'
DB_HOST = 'localhost'
DB_PORT = 5432

def listen_to_db():
    dbname = DB_NAME
    user = DB_USER
    password = DB_PASS  # replace with your postgres password
    host = DB_HOST
    port = DB_PORT
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,  # replace with your postgres password
        host=host,
        port=port
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    curs.execute('LISTEN my_event;')

    logging.info('Listening for changes in the database...')

    try:
        while True:
            if select.select([conn], [], [], 30) == ([], [], []):
                logging.info('Timeout or no events')
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    data = notify.payload
                    fields = data.split(',')
                    data_dict = {}
                    for field in fields:
                        key, value = field.split('=')
                        data_dict[key] = value
                    logging.info(f"Received notification: {data_dict}")
                    #'userId': '999', 
                    # 'faceStatus': 'nmj', 'faceModelPath': 'faceModelPath/dsd/as/d//ds', 
                    # 'bodyStatus': 'no', 'bodyModelPath': 'bodyModelPath', 
                    # 'avatarStatus': 'xxx', 'avatarPath': 'avatarPath'
                    if data_dict['faceStatus'] == 'yes' \
                            and data_dict['bodyStatus'] == 'yes' \
                            and data_dict['avatarStatus'] == 'no':
                        avatar_merge_task.delay(data_dict)
    except KeyboardInterrupt:
        logging.info('Stopping listener...')
    finally:
        curs.close()
        conn.close()

if __name__ == '__main__':
    listen_to_db()
