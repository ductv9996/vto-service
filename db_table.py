import psycopg2

TABLE_NAME = 'avatar_ai_side'
DB_NAME = 'avatar_status_db'
DB_USER = 'testuser'
DB_PASS = 'testpassword'
DB_HOST = 'localhost'
DB_PORT = 5432

def delete_table():
    dbname = DB_NAME
    user = DB_USER
    password = DB_PASS  # replace with your postgres password
    host = DB_HOST
    port = DB_PORT
    
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(dbname=dbname, 
                                      user=user, 
                                      password=password, 
                                      host=host, port=port)
        cursor = connection.cursor()
        
        # Delete the table
        drop_table_query = f'''
        DROP TABLE IF EXISTS {TABLE_NAME};
        '''
        
        cursor.execute(drop_table_query)
        connection.commit()
        print(f"Table {TABLE_NAME} deleted successfully")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def create_table():
    # Database connection parameters
    dbname = DB_NAME
    user = DB_USER
    password = DB_PASS  # replace with your postgres password
    host = DB_HOST
    port = DB_PORT
    
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()
        # item_id / user_id / face_status / face_model_path / body_status / body_model_path / avatar_status
        # Create a table
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                            id SERIAL PRIMARY KEY,
                                            userId VARCHAR(100) UNIQUE,
                                            faceStatus VARCHAR(100),
                                            faceModelPath VARCHAR(100),
                                            bodyStatus VARCHAR(100),
                                            bodyModelPath VARCHAR(100),
                                            avatarStatus VARCHAR(100),
                                            avatarPath VARCHAR(100)
                                        );
        '''
        
        cursor.execute(create_table_query)
        connection.commit()
        print(f"Table {TABLE_NAME} created successfully")

        set_trigger_query = '''
                            CREATE TRIGGER my_avatar_changes
                            AFTER INSERT OR UPDATE OR DELETE ON avatar_ai_side
                            FOR EACH ROW
                            EXECUTE FUNCTION notify_change();
                            '''
        cursor.execute(set_trigger_query)
        connection.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

class AvatarStatusHandler():
    def __init__(self) -> None:
        self.dbname = DB_NAME
        self.user = DB_USER
        self.password = DB_PASS  # replace with your postgres password
        self.host = DB_HOST
        self.port = DB_PORT

        self.components = ['faceStatus', 'faceModelPath', 'bodyStatus', 
                           'bodyModelPath', 'avatarStatus', 'avatarPath']

        try:
            # Connect to the PostgreSQL database
            self.__connection = psycopg2.connect(dbname=self.dbname, 
                                          user=self.user, password=self.password, 
                                          host=self.host, port=self.port)
            self.__cursor = self.__connection.cursor()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")

    def insert_data(self, data):
        userId = data['userId']
        faceStatus = data['faceStatus']
        faceModelPath = data['faceModelPath']
        bodyStatus = data['bodyStatus']
        bodyModelPath = data['bodyModelPath']
        avatarStatus = data['avatarStatus']
        avatarPath = data['avatarPath']

        insert_data_query = f'''
        INSERT INTO {TABLE_NAME} (userId, faceStatus, faceModelPath, bodyStatus, bodyModelPath, avatarStatus, avatarPath)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        insert_data = (userId, faceStatus, faceModelPath, bodyStatus, bodyModelPath, avatarStatus, avatarPath)
        self.__cursor.execute(insert_data_query, insert_data)
        self.__connection.commit()
    
    def update_component(self, data):
        userId = data['userId']
        key = data['key']
        if key not in self.components:
            return
        update_query = f'''
                        UPDATE {TABLE_NAME}
                        SET {key} = %s
                        WHERE userId = %s;
                        '''
        new_values = (data['value'], userId)

        self.__cursor.execute(update_query, new_values)
        self.__connection.commit()

    def update_data(self, data):
        userId = data['userId']
        faceStatus = data['faceStatus']
        faceModelPath = data['faceModelPath']
        bodyStatus = data['bodyStatus']
        bodyModelPath = data['bodyModelPath']
        avatarStatus = data['avatarStatus']
        avatarPath = data['avatarPath']
        # Update data in the table
        update_query = f'''
        UPDATE {TABLE_NAME}
        SET faceStatus = %s, faceModelPath = %s, bodyStatus = %s, bodyModelPath=%s, avatarStatus = %s, avatarPath=%s
        WHERE userId = %s;
        '''
        
        # Define new values and the userId to update
        new_values = (faceStatus, faceModelPath, bodyStatus, bodyModelPath, avatarStatus, avatarPath, userId)
        
        self.__cursor.execute(update_query, new_values)
        self.__connection.commit()
    
    def show_table(self, table_name):
        # Select all data from the table
        select_query = f'SELECT * FROM {table_name};'
        self.__cursor.execute(select_query)
        
        # Fetch all rows from the executed query
        rows = self.__cursor.fetchall()
        id_keys = []
        # Print each row
        for row in rows:
            # print(row)
            # userId, faceStatus, faceModelPath, bodyStatus, 
            # bodyModelPath, avatarStatus, avatarPath
            id_keys.append(row[0])
        return id_keys
    
    def close_conn(self):
        if self.__connection:
            self.__cursor.close()
            self.__connection.close()
            print("PostgreSQL connection is closed")

    def upsert(self, data):
        userId = data['userId']
        faceStatus = data['faceStatus']
        faceModelPath = data['faceModelPath']
        bodyStatus = data['bodyStatus']
        bodyModelPath = data['bodyModelPath']

        avatarStatus = data['avatarStatus']
        avatarPath = data['avatarPath']
        upsert_query = f'''
                    INSERT INTO {TABLE_NAME} (userId, faceStatus, faceModelPath, bodyStatus, bodyModelPath, avatarStatus, avatarPath)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (userId)
                    DO UPDATE SET 
                        faceStatus = EXCLUDED.faceStatus,
                        faceModelPath = EXCLUDED.faceModelPath,
                        bodyStatus = EXCLUDED.bodyStatus,
                        bodyModelPath = EXCLUDED.bodyModelPath,
                        avatarStatus = EXCLUDED.avatarStatus,
                        avatarPath = EXCLUDED.avatarPath
                    WHERE 
                        testtable.faceStatus IS DISTINCT FROM EXCLUDED.faceStatus OR
                        testtable.faceModelPath IS DISTINCT FROM EXCLUDED.faceModelPath OR
                        testtable.bodyStatus IS DISTINCT FROM EXCLUDED.bodyStatus OR
                        testtable.bodyModelPath IS DISTINCT FROM EXCLUDED.bodyModelPath OR
                        testtable.avatarStatus IS DISTINCT FROM EXCLUDED.avatarStatus OR
                        testtable.avatarPath IS DISTINCT FROM EXCLUDED.avatarPath;
                    '''

        # Execute the upsert query
        self.__cursor.execute(upsert_query, (userId, faceStatus, faceModelPath, bodyStatus, bodyModelPath, avatarStatus, avatarPath))
        self.__connection.commit()

if __name__ == '__main__':
    # delete_table()
    create_table()
    controller = AvatarStatusHandler()
    data = dict(userId = '999',
                faceStatus = 'yes',
                faceModelPath = 'faceModelPath/dsd/as/d//ds',
                bodyStatus = 'no',
                bodyModelPath = 'bodyModelPath',
                avatarStatus = 'xxx',
                avatarPath = 'avatarPath')
    
    # data = dict(userId = '999',
    #             key = 'faceStatus',
    #             value = 'nmj')
    
    # controller.update_component(data)
    controller.show_table(TABLE_NAME)