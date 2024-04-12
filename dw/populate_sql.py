import mysql.connector
from mysql.connector import Error

def populate_odb():
    # Connect to MySQL database
    conn = None
    query_country = "INSERT INTO country(countryID,country_txt) " \
            "VALUES(%s,%s)"
    tuples_country = [(1,'Norway'),(2,'USA')]   

    query_region = "INSERT INTO region(regionID,region_txt, countryID) " \
            "VALUES(%s,%s,%s)"
    tuples_region = [(1,'Oslo Fylke', 1),(2,'Eastern US', 2)]    

    query_provstate = "INSERT INTO provstate(provstateID,provstate_txt, regionID) " \
            "VALUES(%s,%s,%s)"
    tuples_provstate = [(1,'Oslo Kommune', 1),(2,'New York', 2)]

    query_city = "INSERT INTO city(cityID,city_txt, provstateID) " \
            "VALUES(%s,%s,%s)"
    tuples_city = [(1,'Oslo', 1),(2,'New York City', 2)]

    try:  
        conn = mysql.connector.connect(host='localhost',
                                  port=13306, 
                                  database = 'odb',
                                  user='dbuser',
                                  password='secret')
        if conn.is_connected():
                print('Connected to MySQL database')
        
        cursor = conn.cursor()
        
        for tuple in tuples_country:
            cursor.execute(query_country,tuple)
        
        for tuple in tuples_region:
            cursor.execute(query_region,tuple)
        
        for tuple in tuples_provstate:
            cursor.execute(query_provstate,tuple)
        
        for tuple in tuples_city:
            cursor.execute(query_city,tuple)
        
            
        conn.commit()
        
        cursor.execute("SELECT count(*) FROM country")
        res = cursor.fetchone()
    
        print('ODB is populated: {} new tuples are inserted'.format(len(tuples_country)+len(tuples_region)+len(tuples_provstate)+len(tuples_city)))
        print('                  {} total tuples are inserted'.format(res[0]))    
        
            
    except Error as e:
        print(e)
        
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

def load_dw():
    # Connect to MySQL database
    odb_conn = None
    dw_conn = None
    adb_load_query = "INSERT INTO fact(factid, eventID, iyear, imonth, iday, crit1, crit2, crit3, success, suicide, gname, individual, nkill, nwound, property, countryID, regionID, provstateID, cityID) " \
                     "VALUES(%s,%s,%s)"
    odb_aggregate_query = "SELECT location, product, sum(sale) "\
                          " FROM transaction "\
                          " GROUP BY location, product"    
                                     
    try:  
        odb_conn = mysql.connector.connect(host='localhost', 
                                  port=13306, 
                                  database = 'odb',
                                  user='dbuser',
                                  password='secret')
        
        dw_conn = mysql.connector.connect(host='localhost',
                                  port=23306, 
                                  database = 'dw',
                                  user='dbuser',
                                  password='secret')
        
        if odb_conn.is_connected():
                print('Connected to source ODB MySQL database')
                
        if dw_conn.is_connected():
                print('Connected to destination DW MySQL database')
        
        odb_cursor = odb_conn.cursor()
        dw_cursor = dw_conn.cursor()
        
        odb_cursor.execute(odb_aggregate_query)
        aggr_tuples = odb_cursor.fetchall()
    
        dw_cursor.executemany(adb_load_query,aggr_tuples)
        
        dw_conn.commit()
        
        dw_cursor.execute("SELECT count(*) FROM fact")
        res = dw_cursor.fetchone()
    
        print('DW is loaded: {} new tuples are inserted'.format(len(aggr_tuples)))
        print('               {} total tuples are inserted'.format(res[0]))    
        
            
    except Error as e:
        print(e)
        
    finally:
        if odb_conn is not None and odb_conn.is_connected():
            odb_cursor.close()
            odb_conn.close()
        if dw_conn is not None and dw_conn.is_connected():
            dw_cursor.close()
            dw_conn.close()    

if __name__ == '__main__':
    populate_odb()
    #load_dw()
    