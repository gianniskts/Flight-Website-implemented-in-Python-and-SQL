# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import lib.pymysql as db

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def getAircraftsOfAirline(cursor, airline_id):
    ret = ()
    query = '''
    			SELECT count( distinct aha.airplanes_id )
				FROM airlines_has_airplanes aha
				WHERE aha.airlines_id = %d;
    		''' % (airline_id)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        ret = result
        return (result)
    except:
        print("Error retrieving aircraft number from airline id")
        return ret

def findAirlinebyAge(x,y):
    
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cursor=con.cursor()
	
	
    x = int(x)
    y = int(y)
    ###   	retrieve the airline id, and count of passengers for airlines
    ###		who apply to the given rules

    query1 = ''' 
    			SELECT 
                    aha.airlines_id , count(distinct passengers.id) as passengers_count
				FROM 
                    flights, flights_has_passengers fhp, airlines_has_airplanes aha, passengers
				WHERE 	
                    flights.id = fhp.flights_id 
				    AND aha.airplanes_id = flights.airplanes_id
				    AND fhp.passengers_id = passengers.id 
                    AND ( 
				    	(2022 - passengers.year_of_birth) < %d
				        AND	
						(2022 - passengers.year_of_birth) > %d )
				GROUP BY aha.airlines_id;
            ''' % (y,x)

    ret = ()
    try:
        cursor.execute(query1)
        results = cursor.fetchall()
         
        # num tuple = (id | number of passengers)
        # set the num tuple as the very first item, in order to find the maximum on the list of tuples
        num = (results[0][0], results[0][1])
		
        # find the tuple which has the maximum number of passengers, and set it as the num_tuple
        for row in results:
            if row[1] > num[1]:
                num = row
        		
        id = num[0]
        query2 = '''
           			SELECT airlines.name
					FROM airlines
					WHERE airlines.id = %d;
        		 ''' % (id)
        try:
            cursor.execute(query2)
            results = cursor.fetchall()

            # name of the airline now stored at the first position of the first tuple
            name = results[0][0]
            num_of_aircrafts = getAircraftsOfAirline(cursor, id)

            if num_of_aircrafts:
                num_of_aircrafts = num_of_aircrafts[0][0]
                ret = (name, num[1], num_of_aircrafts)
            else:
                pass
                
        except:
            print("Error in retrieving name")
        
    except:
        print ("Error: unable to fetch data")
	
    ret_list = []
    row_one = ("airline_name","num_of_passengers", "num_of_aircrafts")
    ret_list.append(row_one)

    if not ret:    # if ret tuple is empty, an error occured so return just one row
    	return ret_list 
    else:
        ret_list.append(ret)
        return ret_list


def findAirportVisitors(x,a,b):
    
    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    res = []

    get_id_of_airline_x = """
    	SELECT airlines.id
		FROM airlines
		WHERE airlines.name = '%s';
    """ % (x)

    try:
        cur.execute(get_id_of_airline_x)
        id_of_airline = cur.fetchall()[0][0]

        get_routes_served_by_airline = """
        	SELECT 
                routes.id, source.name as "FROM" , dest.name as "TO"
			FROM 
                routes, airports source, airports dest
			WHERE 
                routes.airlines_id = %d
			    AND routes.source_id = source.id
			    AND routes.destination_id = dest.id;
        """ % (id_of_airline)

        try:
            cur.execute(get_routes_served_by_airline)
            all_routes_served = cur.fetchall()

            for routes in all_routes_served:
                name_of_airport = routes[2]
                route_id = routes[0]

                get_passengers = """
                	SELECT 
                        COUNT(fhp.passengers_id)
					FROM 
                        flights, flights_has_passengers fhp
					WHERE 
                        flights.routes_id = %d
					    AND flights.id = fhp.flights_id
					    AND flights.date >= '%s'
					    AND flights.date <= '%s';
                """ % (route_id, a, b)

                cur.execute(get_passengers)
                count_of_airport = cur.fetchall()[0][0]
                tup = (name_of_airport, count_of_airport)
                res.append(tup)
        except:
            print("Error finding routes of airline")
    except:
        print("Could not find airline id")
    
    # sort by descending, on the number of visitors which is second
    res.sort(key = lambda tup:tup[1], reverse=True)

    return [("airport_name", "number_of_visitors"),] + res

def getAirportIdFromCity(cur, city):
	
    query = '''
    			SELECT airports.id
				FROM airports
				WHERE airports.city = '%s';
    		''' % (city)
    try:
        cur.execute(query)
        res = cur.fetchall()
        return res
    except:
        print("Error returing airport id from city")

def getAliasOfAirlineId(cur, id):
    query = '''
    			SELECT distinct airlines.alias
                FROM airlines
                WHERE airlines.id = %d
    		''' % (id)
    try:
        cur.execute(query)
        res = cur.fetchall()
        if not res:
            alt_name = ""
        else:
            alt_name = res[0][0]
        return alt_name
    except:
        print("Could not get alias")

def getCityFromAirportId(cur, id):
    query = '''
    			SELECT distinct airports.city
                FROM airports
                WHERE airports.id = %d
    		''' % (id)
    try:
        cur.execute(query)
        res = cur.fetchall()
        if not res:
            alt_name = ""
        else:
            alt_name = res[0][0]
        return alt_name
    except:
        print("Could not get city name")

def getModelFromAirplaneId(cur, id):
    query = '''
    			SELECT airplanes.model
				FROM airplanes
				WHERE airplanes.id = %d;
    		''' % (id)
    try:
        cur.execute(query)
        res = cur.fetchall()
        if not res:
            alt_name = ""
        else:
            alt_name = res[0][0]
        return alt_name
    except:
        print("Could not get model")

def findFlights(x,a,b):

    con=connection()
    cur=con.cursor()
    
    ids_a = getAirportIdFromCity(cur, a)

    ids_b = getAirportIdFromCity(cur, b)

    ret_list = []
    row_one = ("flight_id", "alt_name", "dest_name", "aircraft_model")
    ret_list.append(row_one)

    for source_id in ids_a:
        for dest_id in ids_b:
            s_id = source_id[0]
            d_id = dest_id[0]
            
            query = '''
                    	SELECT 
                            flights.id, airlines.id, aha.airplanes_id
						FROM 
                            routes, flights, airlines, airlines_has_airplanes aha
						WHERE 
                            routes.source_id = '%d'
						    AND routes.destination_id = '%d'
						    AND flights.date = '%s'
						    AND flights.routes_id = routes.id
						    AND routes.airlines_id = airlines.id
						    AND airlines.active = 'Y'
						    AND aha.airlines_id = airlines.id
						    AND aha.airplanes_id = flights.airplanes_id;
                    ''' % (s_id, d_id, x)
            try:
                cur.execute(query)
                res = cur.fetchall()
                if not res:
                    # if result set is empty we pass, that means that there are no flights 
                    # that satisfy our search
                    pass
                else:
                    for flight in res:
                        flight_id = flight[0]
                        alt_name = getAliasOfAirlineId(cur, flight[1])
                        dest_name = getCityFromAirportId(cur, d_id)
                        aircraft_model = getModelFromAirplaneId(cur, flight[2])
                        tup = (flight_id, alt_name, dest_name, aircraft_model)
                        ret_list.append(tup)
            except:
                print("Error in finding flights")
 
    
    return ret_list
    

def findLargestAirlines(N):
    con=connection()
    cur=con.cursor()
    N = int(N)

    ret_list = []
    row_one = ("name", "id", "num_of_aircrafts", "num_of_flights")
    ret_list.append(row_one)

    query = '''
    			SELECT
                    airlines.name, airlines.code , airlines.id, count(distinct flights.id)
				FROM
                    flights, routes, airlines
				WHERE 
                    flights.routes_id = routes.id
				    AND	airlines.id = routes.airlines_id
				GROUP BY airlines.id
				ORDER BY COUNT(distinct flights.id) DESC;
    		'''
    try:
        cur.execute(query)
        results = cur.fetchall()
        for i in range(0,N):
            res_tuple = results[i]
            name = res_tuple[0]
            code = res_tuple[1]
            id = res_tuple[2]

            num_of_aircrafts = getAircraftsOfAirline(cur, id)

            if num_of_aircrafts:
                num_of_aircrafts = num_of_aircrafts[0][0]
            else:
                print("Error: Could not get aircrafts of airline")
            num_of_flights = res_tuple[3]
			
            tup = (name, code, num_of_aircrafts, num_of_flights)
            ret_list.append(tup)
			
            # if we are the last iteration and there are other left with equal number of flights, we continue to search and output
            if i == N - 1: 
                j = N
                res_tuple = results[j]
                while ( res_tuple[3] == num_of_flights ):
                    name = res_tuple[0]
                    code = res_tuple[1]
                    id = res_tuple[2]
        
                    num_of_aircrafts = getAircraftsOfAirline(cur, id)
        
                    if num_of_aircrafts:
                        num_of_aircrafts = num_of_aircrafts[0][0]
                    else:
                        print("Error: Could not get aircrafts of airline")
                    
                    num_of_flights = res_tuple[3]

                    tup = (name, code, num_of_aircrafts, num_of_flights)
                    ret_list.append(tup)

                    j = j + 1
                    res_tuple = results[j]
                        
    except:
        print("Error")

    return ret_list

def insertNewRoute(x,y):
    # Create a new connection\
    con=connection()

    # x -> alias of the airline
    # y -> source

    # Create a cursor on the connection
    cur=con.cursor()

    qry1 = """  SELECT id, name
                FROM airlines
                WHERE alias = '%s';
    """ % (x)

    qry2 = """  SELECT id
                FROM airports
                WHERE name = '%s';
    
    """ % (y)

    try:
        # get airlines id
        cur.execute(qry1)
        res1 = cur.fetchall()
        airline_id = res1[0][0]
        print("Airline_id =", airline_id)

        # get source airport id 
        cur.execute(qry2)
        res2 = cur.fetchall()
        source_id = res2[0][0]
        print("Source_id=", source_id)

        # get all airline sources
        get_all_airline_sources = """
            SELECT DISTINCT
                r.source_id
            FROM 
                airlines a, routes r
            WHERE
                a.id = %d;
        """ % (airline_id)

        cur.execute(get_all_airline_sources)
        all_airline_sources = cur.fetchall()

        # convert tuple to list for searching purposes
        list_of_all_airline_sources = []
        for sources in all_airline_sources:
            list_of_all_airline_sources.append(sources[0])

        # check if given source is valid
        valid = False
        if source_id in list_of_all_airline_sources:
            valid = True
        # if given source does not already exist in airlines'
        # routes then it's treated as error
        if (valid == False):
            print("Airline has no routes from given source", y)
            return [(), ]


        # get all possible destinations
        get_all_destinations = """
            SELECT *
            FROM airports;
        """
        cur.execute(get_all_destinations)
        all_destinations = cur.fetchall()      

        # convert tuple to list for searching purposes
        list_of_all_destinations = []
        for destination in all_destinations:
            list_of_all_destinations.append(destination)

        # get all airline destinations
        get_all_airline_destinations = """
            SELECT DISTINCT
                airports.city
            FROM 
                airlines, routes, airports
            WHERE
                routes.airlines_id = airlines.id
                AND airlines.id = %d
                AND routes.destination_id = airports.id;
        """ % (airline_id)
        cur.execute(get_all_airline_destinations)
        all_airline_destinations = cur.fetchall()
        
        # convert tuple to list for searching purposes
        list_of_all_airline_destinations = []
        for destination in all_airline_destinations:
            list_of_all_airline_destinations.append(destination[0])

        print(list_of_all_airline_destinations)


        # finding an airport which is not part
        # of airlines' destinations
        for airports in list_of_all_destinations:
            # if current airport derived from list_of_all_destinations is not contained 
            # to list_of_all_airline_destinations then:
            if list_of_all_airline_destinations.count(airports[2]) == 0:
                # found a new destination
                new_destination_id = airports[0] 
                print(airports[2])
                print( "(id_of_x = %d, id_of_new_destination = %d, id_of_source = %d)" % (airline_id, new_destination_id, source_id))
                
                try:
                     # get id of route to insert into, 
                     # this however should have been taken care of by the database with autoincrement !!!
                    find_available_route_id = """ 
                                                SELECT MAX(routes.id)
	    										FROM routes;
                                              """
                    
                    cur.execute(find_available_route_id)
                    new_id = cur.fetchall()[0][0] + 1
                    print(new_id)

                    insert_query = """
                                    INSERT INTO routes(id, airlines_id, source_id, destination_id)
                                    VALUES (%d, %d, %d, %d);
                                   """ % (new_id, airline_id, source_id, new_destination_id)

                    print("ready to insert new route conducted by: (%d,%d,%d,%d)" % (new_id, airline_id, source_id, new_destination_id))
                    
                    cur.execute(insert_query)
                    con.commit()

                    return [(), ("ok", )]
                    break
                except:
                    print("Error getting the id of the destination airport")
                    break
            # else current airport is already in airlines' destinations
            else:
                print("Airport with id: %d, at city %s was found inside the destinations." % (airports[0], airports[2]))
        
        print("airline capacity full")
        return [(), ("airline capacity full", )]
    except:
        print("Error occured while retreiving airlines' name")
    return[(),]


# example to insert::: (uncomment)
# insertNewRoute("Air Asia", "Kalibo")