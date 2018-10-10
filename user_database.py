import pymysql
#import pandas 
import os 
import gc
import config

""" Helper method which returns the connection and cursor """
def connect():
	conn = pymysql.connect(host='localhost',user=config.databaseUsername,password=config.databasePassword,db='AMP',charset="utf8")
	c = conn.cursor()
	
	return conn, c


# Get user csv file
def get_file():
    file_name = "user_spread_sheet.csv"
    cwd = os.getcwd()
    os.chdir("../../Downloads")
    df = pandas.read_csv(file_name)
    
    return df
        

# one-time-only function 
def insert_user(conn, c, df):
    try:
        insert_query = 'INSERT INTO user (firstName, lastName, loginEmail, notificationEmail) VALUES (%s, %s, %s, %s)'

        for i in df.index:
            c.execute(insert_query, (df['First Name'][i],df['Last Name'][i], df['Login Email'][i], df['Notification Email'][i]))
            conn.commit()

        gc.collect()
    finally:
        print('Internal User data injected')



def update_user(conn, c, df):

    # Check if row exists
    try:
        print('Updating Internal User Database...')
        update_count = 0
        insert_count = 0
        update_query = "UPDATE user SET {} = '{}' WHERE lastName = '{}'"
        insert_query = 'INSERT INTO user (firstName, lastName, loginEmail, notificationEmail) VALUES (%s, %s, %s, %s)'
        select_query = 'SELECT * FROM user WHERE (firstName=%s) and (lastName=%s)'
        # if yes, see if any there is any change, if so, change the repsected column
        for i in df.index:
            c.execute(select_query, (str(df['First Name'][i]),str(df['Last Name'][i])))
            result = c.fetchone()
            if (result):
                if ( df['Login Email'][i] != result[2] ):
                    update_query = update_query.format('loginEmail',(df['Login Email'][i]),(df['Last Name'][i]))
                    print('Updated {} of {} to {}'.format('first name',result[0],str(df['First Name'][i])))
                    c.execute(update_query)
                    update_count += 1 
                if ( df['Notification Email'][i] != result[3] ):
                    update_query = update_query.format('notificationEmail',(df['Notification Email'][i]),(df['Last Name'][i]))
                    print('Updated {} of {} to {}'.format('first name',result[0],str(df['First Name'][i])))
                    c.execute(update_query)
                    update_count += 1
                conn.commit()

        # if not, insert new user data into db
            else:
                if (df['First Name'][i] != 'a0603-test-jeff' and df['First Name'][i] != 'A0603-jeff'):
                    c.execute(insert_query, (df['First Name'][i],df['Last Name'][i], df['Login Email'][i], df['Notification Email'][i]))
                    print('Added {}, {}'.format(str(df['First Name'][i]),str(df['Last Name'][i])))
                    insert_count += 1   
                    conn.commit()
        print('Number of update : {}'.format(update_count))
        print('Number of new insert : {}'.format(insert_count))
        gc.collect()
    # except Exception as e:
    #     pass
    #     # print('Error : {}'.format(str(e)))
    finally:
        conn.close()
        print('Connection to user table closed')

def update_user_database():
    conn, c = connect()
    df = get_file()
    update_user(conn,c,df)
