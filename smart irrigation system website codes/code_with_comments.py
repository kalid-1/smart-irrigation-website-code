# Import the matplotlib library for plotting
import matplotlib

# Use the Agg backend for rendering plots as image files instead of trying to display them on screen.
# This is necessary in environments without a GUI (e.g., servers), and avoids thread errors.
matplotlib.use('Agg')


# Import the MySQL connector to interact with MySQL databases using Python
import mysql.connector

# Import pyplot module from matplotlib for creating plots
import matplotlib.pyplot as plt

# Import base64 for encoding binary image data to base64 string (used in HTML embedding)
import base64

# Import io module to work with in-memory byte streams (used to store image data temporarily)
import io

# Import Flask modules:
from flask import Flask, render_template, request, url_for, redirect

# Create an instance of the Flask application
app = Flask(__name__)

# === GLOBAL DICTIONARIES ===

# Dictionary to temporarily store sensor readings like temperature, moisture, etc. (with initial value for each)
data = {    
    "Temp_reading": 10,
    "LDR1_reading": 10,
    "LDR2_reading": 10,
    "PIR_reading": 10,
    "Moisture_reading": 10
    }

# Dictionary to temporarily hold credentials entered by a user during login
user_details = {}

# Dictionary to store values entered into the "add user" form
add_user_details = {}

# Dictionary to store values entered into the "delete user" form
delete_user_details = {}

# Function to check if SENSOR_DATABASE exists in MySQL, and create it if it doesn't
def CHECK_FOR_SENSOR_DATABASE():
    # Connect to MySQL server without selecting a database yet
    mydb = mysql.connector.connect(
        host="localhost",        # Server address (localhost = same machine)
        user="root",             # MySQL username
        passwd="2@@623ko"        # MySQL password (ensure this is correct)
    )

    # Create a cursor object to execute SQL queries
    myCursor = mydb.cursor()

    # SQL query to check if SENSOR_DATABASE exists in the schema list
    myCursor.execute(
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'SENSOR_DATABASE'"
    )

    # If nothing is returned (database doesn't exist), create it
    if myCursor.fetchone() is None:
        # Create SENSOR_DATABASE if it doesn't exist
        myCursor.execute("CREATE DATABASE SENSOR_DATABASE")

# Function to check for the existence of a USERS table in SENSOR_DATABASE, and create it if not found
def CHECK_FOR_USERS_TABLE():
    # Connect to SENSOR_DATABASE directly
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"  # Select the correct database
    )

    # Create cursor to execute SQL queries
    myCursor = mydb.cursor()

    # SQL command to check for existence of USERS table
    myCursor.execute("show tables where Tables_in_sensor_database like 'USERS'")

    # If USERS table is not found in the results
    if myCursor.fetchone() is None:
        # Create USERS table with three columns:
        # USERNAME: stores user's login name
        # PASSWORDS: stores the user's password
        # SENSOR_TYPE: stores what sensor data this user can access (e.g., temp, motion)
        myCursor.execute(
            "CREATE TABLE `USERS` ("
            "`USERNAME` varchar(50) NOT NULL,"
            "`PASSWORDS` varchar(20) NOT NULL,"
            "`SENSOR_TYPE` varchar(20) NOT NULL)"
        )
        # Function to check for the SENSOR_DATA table, and create it if it doesn't exist
def CHECK_FOR_SENSOR_DATA_TABLE():
    # Connect to SENSOR_DATABASE
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )

    # Create cursor to execute SQL queries
    myCursor = mydb.cursor()

    # SQL to check if SENSOR_DATA table exists
    myCursor.execute("show tables where Tables_in_sensor_database like 'SENSOR_DATA'")

    # If table does not exist
    if myCursor.fetchone() is None:
        # Create SENSOR_DATA table with fields to store timestamp and all types of sensor readings
        myCursor.execute(
            "CREATE TABLE `SENSOR_DATA` ("
            "`TIME` datetime DEFAULT NULL,"           # Timestamp of the reading
            "`TEMPERATURES` int DEFAULT NULL,"        # Temperature value
            "`LDR_1` int DEFAULT NULL,"               # Light sensor 1 value
            "`LDR_2` int DEFAULT NULL,"               # Light sensor 2 value
            "`MOTION` varchar(50) DEFAULT NULL,"      # Motion state (e.g., "Motion Detected!")
            "`SOIL_MOISTURE` int DEFAULT NULL)"       # Soil moisture percentage
        )

    # Return 0 to indicate the function finished (not used but safe to include)
    return 0

# Function to insert sensor readings into the SENSOR_DATA table
def Send_Data_to_Database():
    # Connect to SENSOR_DATABASE
    mydb = mysql.connector.connect( 
        host="localhost",          # Server address
        user="root",               # MySQL username
        passwd="2@@623ko",         # MySQL password
        database="SENSOR_DATABASE" # Target database
    )

    # Create a cursor object to execute SQL commands
    myCursor = mydb.cursor()

    # SQL insert statement for adding a new sensor data record with current timestamp (NOW())
    SEND_DATA = "INSERT INTO SENSOR_DATA (TIME,TEMPERATURES,LDR_1,LDR_2, MOTION, SOIL_MOISTURE) VALUES(NOW(),%s,%s,%s,%s,%s)" 

    # Get the latest sensor values from the global `data` dictionary
    SEND_TEMP = data['Temp_reading']
    SEND_LDR1 = data['LDR1_reading']
    SEND_LDR2 = data['LDR2_reading']
    SEND_MOTION = data['PIR_reading']
    SEND_MOISTURE = data['Moisture_reading']

    # Bundle the values into a tuple to pass into the SQL insert
    SEND_DATA_LIST = (SEND_TEMP, SEND_LDR1, SEND_LDR2, SEND_MOTION, SEND_MOISTURE)

    # Execute the SQL insert with values
    myCursor.execute(SEND_DATA, SEND_DATA_LIST)

    # Commit the transaction to save changes to the database
    mydb.commit()

    # Return 0 to indicate success (return value is not used)
    return 0

# Function to retrieve and plot temperature data from the database
def RETRIEVE_TEMPETATURES_FROM_DATABASE():
    # Connect to SENSOR_DATABASE
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )

    # Initialize empty lists to hold time and temperature values
    RETRIEVED_TEMPERATURES_TUPLE = []
    RETRIEVED_TIMES_TUPLE = []

    # Create a cursor to execute SQL queries
    myCursor = mydb.cursor()

    # SQL query to get all timestamps from SENSOR_DATA
    RETRIEVE_TIMES = "SELECT TIME FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_TIMES)
    TIMES = myCursor.fetchall()  # Fetch all rows (each row is a tuple)

    # Extract the timestamp values into a list
    for TIME in TIMES:
        RETRIEVED_TIMES_TUPLE.append(TIME[0])

    # SQL query to get all temperature readings
    RETRIEVE_TEMPERATURE = "SELECT TEMPERATURES FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_TEMPERATURE)
    TEMPERATURES = myCursor.fetchall()

    # Extract temperature values into a list
    for TEMPERATURE in TEMPERATURES:
        RETRIEVED_TEMPERATURES_TUPLE.append(TEMPERATURE[0])

    # === Plotting the temperature data ===

    # Label the x and y axes of the graph
    plt.xlabel("Date and time of reading")
    plt.ylabel("Temperature reading")

    # Set figure size (width x height in inches)
    plt.figure(figsize=(12, 10))

    # Rotate x-axis labels so they don't overlap
    plt.xticks(rotation=90)

    # Add grid lines for clarity
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Plot temperature vs. time using solid lines
    plt.plot_date(RETRIEVED_TIMES_TUPLE, RETRIEVED_TEMPERATURES_TUPLE, linestyle="solid")

    # === Save the graph to an in-memory buffer ===

    buffer = io.BytesIO()              # Create an empty byte buffer
    plt.savefig(buffer, format='png')  # Save the plot as a PNG image in memory
    buffer.seek(0)                     # Reset buffer position to the beginning
    IMAGE_BYTES = buffer.read()        # Read the image data from the buffer

    # === Encode the image as base64 so it can be embedded in an HTML <img> tag ===
    BASE64_ENCODED_IMAGE = base64.b64encode(IMAGE_BYTES)     # Encode binary to base64
    BASE64_ENCODED_IMAGE_STRING = BASE64_ENCODED_IMAGE.decode("utf-8")  # Convert to string

    buffer.close()  # Close the memory buffer
    plt.close()     # Close the matplotlib figure to free memory

    # Return the base64 string to be used in the HTML template
    return BASE64_ENCODED_IMAGE_STRING

def RETRIEVE_LIGNT_INTENSITY_1_FROM_DATABASE():
    # Establish connection to MySQL database with specified credentials
    mydb=mysql.connector.connect(
        host="localhost",  # Database server address
        user="root",      # Database username with admin privileges
        passwd="2@@623ko", # Database password (note: hardcoded passwords are security risk)
        database="SENSOR_DATABASE"  # Target database containing sensor data
    )
    # Initialize empty lists to store time and sensor data
    RETRIEVED_LIGHT_INTENSITY_1_TUPLE=[]  # Will hold all LDR1 sensor readings
    RETRIEVED_TIMES_TUPLE=[]              # Will hold corresponding timestamps
    
    # Create database cursor to execute SQL commands
    myCursor=mydb.cursor()
    
    # SQL query to select all timestamps from sensor data table
    RETRIEVE_TIMES="SELECT TIME FROM SENSOR_DATA"
    
    # Execute the timestamp retrieval query
    myCursor.execute(RETRIEVE_TIMES)
    
    # Fetch all results from the executed query
    TIMES=myCursor.fetchall()
    
    # Process each timestamp record from query results
    for TIME in TIMES:
        # Append each timestamp (first column of result) to our list
        RETRIEVED_TIMES_TUPLE.append(TIME[0])
    
    # SQL query to select all LDR1 sensor readings
    RETRIEVE_LIGHT_INTENSITY_1="SELECT LDR_1 FROM SENSOR_DATA"
    
    # Execute the LDR1 data retrieval query
    myCursor.execute(RETRIEVE_LIGHT_INTENSITY_1)
    
    # Fetch all LDR1 readings from query results
    LIGHT_INTENSITES_1=myCursor.fetchall()
    
    # Process each LDR1 reading from query results
    for LIGHT_INTENSITY_1 in LIGHT_INTENSITES_1:
        # Append each reading (first column of result) to our list
        RETRIEVED_LIGHT_INTENSITY_1_TUPLE.append(LIGHT_INTENSITY_1[0])
    
    # Configure graph labels and appearance
    plt.xlabel("Date and time of reading")  # Set x-axis label
    plt.ylabel("Light intensity reading")   # Set y-axis label

    # Create new figure with specified dimensions (12x10 inches)
    plt.figure(figsize=(12,10)) 
    
    # Rotate x-axis labels 90 degrees for better readability
    plt.xticks(rotation=90)
    
    # Configure grid lines (both major and minor, dashed style)
    plt.grid(True,which="both",linestyle="--", linewidth=0.5)
    
    # Create the actual plot with timestamps vs LDR1 values
    # plot_date is used for better datetime handling on x-axis
    LIGHT_INTENSITY_1_GRAPH=plt.plot_date(RETRIEVED_TIMES_TUPLE, RETRIEVED_LIGHT_INTENSITY_1_TUPLE, linestyle="solid")
    
    # Create in-memory buffer to store the generated graph image
    buffer=io.BytesIO() 
    
    # Save the matplotlib figure as PNG into the buffer
    plt.savefig(buffer, format='png')
    
    # Reset buffer position to start for reading
    buffer.seek(0)
    
    # Read the binary image data from buffer
    IMAGE_BYTES=buffer.read()
    
    # Encode binary image data to base64 for HTML embedding
    BASE64_ENCODED_IMAGE=base64.b64encode(IMAGE_BYTES)
    
    # Convert base64 bytes to UTF-8 string for HTML compatibility
    BASE64_ENCODED_IMAGE_STRING=BASE64_ENCODED_IMAGE.decode("utf-8")
    
    # Close the buffer to release memory
    buffer.close()
    
    # Close the matplotlib figure to release memory
    plt.close()
    
    # Return the encoded image string for web display
    return BASE64_ENCODED_IMAGE_STRING

def RETRIEVE_LIGNT_INTENSITY_2_FROM_DATABASE():
    # Connect to MySQL database with same credentials as previous function
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    # Initialize empty lists for LDR2 data and timestamps
    RETRIEVED_LIGHT_INTENSITY_2_TUPLE=[]
    RETRIEVED_TIMES_TUPLE=[]
    
    # Create database cursor
    myCursor=mydb.cursor()
    
    # SQL query to get all timestamps
    RETRIEVE_TIMES="SELECT TIME FROM SENSOR_DATA"
    
    # Execute timestamp query
    myCursor.execute(RETRIEVE_TIMES)
    
    # Fetch all timestamp results
    TIMES=myCursor.fetchall()
    
    # Process each timestamp record
    for TIME in TIMES:
        RETRIEVED_TIMES_TUPLE.append(TIME[0])
    
    # SQL query to get all LDR2 sensor readings
    RETRIEVE_LIGHT_INTENSITY_2="SELECT LDR_2 FROM SENSOR_DATA"
    
    # Execute LDR2 query
    myCursor.execute(RETRIEVE_LIGHT_INTENSITY_2)
    
    # Fetch all LDR2 results
    LIGHT_INTENSITES_2=myCursor.fetchall()
    
    # Process each LDR2 reading
    for LIGHT_INTENSITY_2 in LIGHT_INTENSITES_2:
        RETRIEVED_LIGHT_INTENSITY_2_TUPLE.append(LIGHT_INTENSITY_2[0])
    
    # Configure graph labels
    plt.xlabel("Date and time of reading")
    plt.ylabel("Light intensity reading")
    
    # Set figure size
    plt.figure(figsize=(12,10)) 
    
    # Rotate x-axis labels
    plt.xticks(rotation=90)
    
    # Configure grid
    plt.grid(True,which="both",linestyle="--", linewidth=0.5)
    
    # Create plot for LDR2 data
    LIGHT_INTENSITY_2_GRAPH=plt.plot_date(RETRIEVED_TIMES_TUPLE, RETRIEVED_LIGHT_INTENSITY_2_TUPLE, linestyle="solid")
    
    # Create image buffer
    buffer=io.BytesIO()
    
    # Save figure to buffer
    plt.savefig(buffer, format='png')
    
    # Reset buffer position
    buffer.seek(0)
    
    # Read image data
    IMAGE_BYTES=buffer.read()
    
    # Encode to base64
    BASE64_ENCODED_IMAGE=base64.b64encode(IMAGE_BYTES)
    
    # Convert to string
    BASE64_ENCODED_IMAGE_STRING=BASE64_ENCODED_IMAGE.decode("utf-8")
    
    # Clean up
    buffer.close()
    plt.close()
    
    return BASE64_ENCODED_IMAGE_STRING

def RETRIEVE_SOIL_MOISTURE_FROM_DATABASE():
    # Database connection
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    # Lists for moisture data and timestamps
    RETRIEVED_SOIL_MOISTURE_TUPLE=[]
    RETRIEVED_TIMES_TUPLE=[]
    
    # Create cursor
    myCursor=mydb.cursor()
    
    # Get timestamps
    RETRIEVE_TIMES="SELECT TIME FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_TIMES)
    TIMES=myCursor.fetchall()
    
    # Process timestamps
    for TIME in TIMES:
        RETRIEVED_TIMES_TUPLE.append(TIME[0])
    
    # Get moisture readings
    RETRIEVE_SOIL_MOISTURE="SELECT SOIL_MOISTURE FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_SOIL_MOISTURE)
    _SOIL_MOISTURES=myCursor.fetchall()
    
    # Process moisture data
    for _SOIL_MOISTURE in _SOIL_MOISTURES:
        RETRIEVED_SOIL_MOISTURE_TUPLE.append(_SOIL_MOISTURE[0])
    
    # Configure graph
    plt.xlabel("Date and time of reading")
    plt.ylabel("Soil moisture reading")
    plt.figure(figsize=(12,10)) 
    plt.xticks(rotation=90)
    plt.grid(True,which="both",linestyle="--", linewidth=0.5)
    
    # Create plot
    SOIL_MOISTURE_GRAPH=plt.plot_date(RETRIEVED_TIMES_TUPLE, RETRIEVED_SOIL_MOISTURE_TUPLE, linestyle="solid")
    
    # Generate image
    buffer=io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    IMAGE_BYTES=buffer.read()
    BASE64_ENCODED_IMAGE=base64.b64encode(IMAGE_BYTES)
    BASE64_ENCODED_IMAGE_STRING=BASE64_ENCODED_IMAGE.decode("utf-8")
    buffer.close()
    plt.close()
    
    return BASE64_ENCODED_IMAGE_STRING

def RETRIEVE_MOTION_FROM_DATABASE():
    # Database connection
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    # Lists for motion data and timestamps
    RETRIEVED_MOTION_TUPLE=[]
    RETRIEVED_TIMES_TUPLE=[]
    
    # Create cursor
    myCursor=mydb.cursor()
    
    # Get timestamps
    RETRIEVE_TIMES="SELECT TIME FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_TIMES)
    TIMES=myCursor.fetchall()
    
    # Process timestamps
    for TIME in TIMES:
        RETRIEVED_TIMES_TUPLE.append(TIME[0])
    
    # Get motion detection values
    RETRIEVE_MOTION="SELECT MOTION FROM SENSOR_DATA"
    myCursor.execute(RETRIEVE_MOTION)
    MOTIONS=myCursor.fetchall()
    
    # Process motion data
    for MOTION in MOTIONS:
        RETRIEVED_MOTION_TUPLE.append(MOTION[0])
        
    # Create mapping from text to numerical values for plotting
    MOTION_MAP={'No Motion Detected!':1,'Motion Detected!':2}
    
    # Convert motion text to numerical y-values using the mapping
    y_values=[MOTION_MAP[RETRIEVED_MOTION] for RETRIEVED_MOTION in RETRIEVED_MOTION_TUPLE]
    
    # Configure graph
    plt.xlabel("Date and time of reading")
    plt.ylabel("Motion detector reading")
    plt.figure(figsize=(12,10)) 
    plt.xticks(rotation=90)
    plt.yticks([0,1,2,3])  # Set y-axis tick positions
    plt.minorticks_off()    # Disable minor ticks
    plt.ylim(0,3)          # Set y-axis limits
    plt.yscale             # Note: This line appears incomplete
    
    # Configure grid
    plt.grid(True,which="both",linestyle="--", linewidth=0.5)
    
    # Create plot (note: no linestyle for discrete data)
    MOTION_GRAPH=plt.plot_date(RETRIEVED_TIMES_TUPLE, y_values)
    
    # Generate image
    buffer=io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    IMAGE_BYTES=buffer.read()
    BASE64_ENCODED_IMAGE=base64.b64encode(IMAGE_BYTES)
    BASE64_ENCODED_IMAGE_STRING=BASE64_ENCODED_IMAGE.decode("utf-8")
    buffer.close()
    plt.close()
    
    return BASE64_ENCODED_IMAGE_STRING

def CHECK_IF_USER_EXISTS():
    # Connect to database
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    myCursor=mydb.cursor()
    
    # Get username from temporary storage
    check_username=add_user_details['add_username']
    
    # SQL query to check for username
    check_database="SELECT * FROM USERS WHERE USERNAME LIKE %s"
    
    # Parameter tuple for query (note comma makes it a tuple)
    check_username_list=(check_username,)
    
    # Execute query with parameter
    myCursor.execute(check_database,check_username_list)
    
    # Get first matching record
    check_result=myCursor.fetchone()
    
    # Return True if user exists, False otherwise
    if check_result:
        return True
    else:
        return False
    
def CREATE_USER():
    # Connect to database
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    myCursor=mydb.cursor()
    
    # Get user details from temporary storage
    new_username=add_user_details['add_username']
    new_password=add_user_details['add_password']
    new_user_sensor=add_user_details['add_sensor_type']
    
    # Create parameter tuple
    new_user_list=(new_username, new_password,new_user_sensor)
    
    # SQL insert statement
    add_user_to_database="INSERT INTO USERS (USERNAME, PASSWORDS, SENSOR_TYPE) VALUES (%s, %s, %s)"
    
    # Execute insert with parameters
    myCursor.execute(add_user_to_database,new_user_list)
    
    # Commit transaction
    mydb.commit()
    return 0

def RETRIEVE_USER_DATA():
    # Connect to database
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    myCursor=mydb.cursor()
    
    # Get credentials from temporary storage
    user_name=user_details["username"]
    user_password=user_details["password"]
    
    # SQL query to find user
    RETRIEVE_USER_DETAILS_FROM_DATABASE="SELECT * FROM USERS WHERE USERNAME LIKE %s"
    
    # Parameter tuple
    user_name_list=(user_name,)
    
    # Execute query
    myCursor.execute(RETRIEVE_USER_DETAILS_FROM_DATABASE,user_name_list)
    
    # Get first matching record
    retrieved_details=myCursor.fetchone()
    
    # Return record if found, 0 otherwise
    if retrieved_details:
       return retrieved_details
    else:
       return 0
   
def DELETE_USER():
    # Connect to database
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="2@@623ko",
        database="SENSOR_DATABASE"
    )
    myCursor=mydb.cursor()
    
    # Get credentials from temporary storage
    username_to_delete=delete_user_details['delete_username']
    password_to_delete=delete_user_details['delete_password']
    
    # Parameter tuple
    delete_user_list=(username_to_delete,)
    
    # SQL delete statement
    delete_user_from_database="DELETE FROM USERS WHERE USERNAME LIKE %s"
    
    # Execute delete
    myCursor.execute(delete_user_from_database,delete_user_list)
    
    # Commit transaction
    mydb.commit()
    
    # Check if any rows were affected
    if myCursor.rowcount<=0:
        return False  # No user deleted
    else:
        return True  # User deleted


@app.route('/', methods=("POST","GET"))
def page_1():
    
        if request.method == "POST":
            CHECK_FOR_SENSOR_DATABASE()
            CHECK_FOR_SENSOR_DATA_TABLE()
            CHECK_FOR_USERS_TABLE()
            readings = request.data.decode('utf-8')  #store sensor data from arduino into variable
            sensor_values=readings.split("&")  # seperate the data using "&" as the delimiter
            for sensor_value in sensor_values:
                sensor_type,value=sensor_value.split("=") # seperate the data using "=" as the delimiter
                # save the sensor values into the "data" dictionary
                if sensor_type=="temperature":
                    data['Temp_reading']=value
                elif sensor_type=="ldr1":
                    data['LDR1_reading']=value
                elif sensor_type=="ldr2":
                    data['LDR2_reading']=value
                elif sensor_type=="pir":
                    data['PIR_reading']=value
                elif sensor_type=="moisture":
                    data['Moisture_reading']=value
                else:
                    print("Invalid return from sensor")
                    
            Send_Data_to_Database()
            
            return "data recieved by server"  # send response to the microcontroller
        else:
             # if there is no sensor information from the microcontroller render the "wait" html page
                return render_template("wait.html")
    
# base html route
@app.route('/base')
def base():
    return render_template("base.html")


# temperature sensor login route
@app.route('/login_temp', methods=("POST","GET"))
def login_temp(): 
    # if data is recieved from the login page
    if request.method=="POST":
        #save data from login page to user_details dictionary
        username=request.form['username']
        password=request.form['password']
        user_details['username']=username
        user_details['password']=password
        retrieved_user_data=RETRIEVE_USER_DATA()
        if retrieved_user_data: # if user details is found in the database
            retrieved_username=retrieved_user_data[0]
            retrieved_password=retrieved_user_data[1]
            retrieved_sensor_type=retrieved_user_data[2]
            
            # if the login details are correct
            if retrieved_username==username and retrieved_password==password:
              
                if retrieved_sensor_type=="temperature":   # go to the webpage of the sensor
                    return redirect(url_for('temp'))
                else: #inform user that he/she is on the wrong sensor login page
                    return render_template("login_temp.html",error="User belongs to a differient sensor")
            else: # inform user that the login details are incorrect
                return render_template("login_temp.html",error="Incorrect password")
        
        else: # if user details is not found in the database
            return render_template("login_temp.html",error="User does not exist")
        
           

    else:  # if no  data is recieved from the login page
        return render_template("login_temp.html")
    
@app.route('/login_moisture', methods=("POST","GET"))
def login_moisture():
    # if data is recieved from the login page
    if request.method=="POST":
        #save data from login page to user_details dictionary
        username=request.form['username']
        password=request.form['password']
        user_details['username']=username
        user_details['password']=password

        retrieved_user_data=RETRIEVE_USER_DATA()
        # if user details is found in the database
        if retrieved_user_data: 
            retrieved_username=retrieved_user_data[0]
            retrieved_password=retrieved_user_data[1]
            retrieved_sensor_type=retrieved_user_data[2]
            # if the login details are correct
            if retrieved_username==username and retrieved_password==password:
                
                if retrieved_sensor_type=="moisture": # go to the webpage of the sensor
                    return redirect(url_for('humidity'))
                else: #inform user that he/she is on the wrong sensor login page
                    return render_template("login_moisture.html",error="User belongs to a differient sensor")
                
            else: # inform user that the login details are incorrect
                return render_template("login_moisture.html",error="Incorrect password")
        
        else: # if user details is not found in the database
            return render_template("login_moisture.html",error="User does not exist")
        
    else: # if no  data is recieved from the login page
        return render_template("login_moisture.html")
    
@app.route('/login_ldr1', methods=("POST","GET"))
def login_ldr1():
    # if data is recieved from the login page
    if request.method=="POST":
        #save data from login page to user_details dictionary
        username=request.form['username']
        password=request.form['password']
        user_details['username']=username
        user_details['password']=password

       
        retrieved_user_data=RETRIEVE_USER_DATA()
        
        # if user details is found in the database
        if retrieved_user_data:
            retrieved_username=retrieved_user_data[0]
            retrieved_password=retrieved_user_data[1]
            retrieved_sensor_type=retrieved_user_data[2]
            
            # if the login details are correct
            if retrieved_username==username and retrieved_password==password:
                if retrieved_sensor_type=="ldr1":  # go to the webpage of the sensor
                    return redirect(url_for('LDR1'))
                
                else: #inform user that he/she is on the wrong sensor login page
                    return render_template("login_ldr1.html",error="User belongs to a differient sensor")
                
            else: # inform user that the login details are incorrect
                return render_template("login_ldr1.html",error="Incorrect password")
        
        else: # if user details is not found in the database# if user details is not found in the database
            return render_template("login_ldr1.html",error="User does not exist")
        
        

    else: # if no  data is recieved from the login page
        return render_template("login_ldr1.html")
    
@app.route('/login_ldr2', methods=("POST","GET"))
def login_ldr2():
    # if data is recieved from the login page
    if request.method=="POST":
        #save data from login page to user_details dictionary
        username=request.form['username']
        password=request.form['password']
        user_details['username']=username
        user_details['password']=password

        retrieved_user_data=RETRIEVE_USER_DATA()
        # if user details is found in the database
        if retrieved_user_data:
            retrieved_username=retrieved_user_data[0]
            retrieved_password=retrieved_user_data[1]
            retrieved_sensor_type=retrieved_user_data[2]
            
            # if the login details are correct
            if retrieved_username==username and retrieved_password==password:
                if retrieved_sensor_type=="ldr2":  # go to the webpage of the sensor
                    return redirect(url_for('LDR2'))
                
                else: #inform user that he/she is on the wrong sensor login page
                    return render_template("login_ldr2.html",error="User belongs to a differient sensor")
                
            else:# inform user that the login details are incorrect
                return render_template("login_ldr2.html",error="Incorrect password")
        
        else: # if user details is not found in the database
            return render_template("login_ldr2.html",error="User does not exist")
          

    else:  # if no  data is recieved from the login page
        return render_template("login_ldr2.html")
    
@app.route('/login_motion', methods=("POST","GET"))
def login_motion():
    # if data is recieved from the login page
    if request.method=="POST":
        #save data from login page to user_details dictionary
        username=request.form['username']
        password=request.form['password']
        user_details['username']=username
        user_details['password']=password

       
        retrieved_user_data=RETRIEVE_USER_DATA()
        # if user details is found in the database
        if retrieved_user_data:
            retrieved_username=retrieved_user_data[0]
            retrieved_password=retrieved_user_data[1]
            retrieved_sensor_type=retrieved_user_data[2]
            
            # if the login details are correct
            if retrieved_username==username and retrieved_password==password:
                if retrieved_sensor_type=="motion":  # go to the webpage of the sensor
                    return redirect(url_for('PIR'))
                
                else: #inform user that he/she is on the wrong sensor login page
                    return render_template("login_motion.html",error="User belongs to a differient sensor")
            else:
                # inform user that the login details are incorrect
                return render_template("login_motion.html",error="Incorrect password")
        
        else: # if user details is not found in the database
            return render_template("login_motion.html",error="User does not exist")
        
    else: # if no  data is recieved from the login page
        return render_template("login_motion.html")
    
@app.route('/add_user', methods=("POST","GET"))
def add_user():
    
    # if data is recieved from the add user page
    if request.method=="POST":
        
        add_username=request.form['username']
        add_password=request.form['password']
        add_sensor_type=request.form['sensor_type']
        #save data from add user page to add_user_details dictionary
        add_user_details["add_username"]=add_username
        add_user_details["add_password"]=add_password
        add_user_details["add_sensor_type"]=add_sensor_type
        user_exists=CHECK_IF_USER_EXISTS()
        
        if  user_exists:
            
            error="User exists"
            return render_template("add_user.html",error=error) # show error message 
        else:
            CREATE_USER()
            error="user created"
            
            #inform user that the user was created successfully
            return render_template("add_user.html",error=error) 
        
    else:
        return render_template("add_user.html")
    
    
@app.route('/delete_user', methods=("POST","GET"))
def delete_user():
    # if data is recieved from the delete user page
    if request.method=="POST":
        delete_username=request.form['username']
        delete_password=request.form['password']
        
        #save data from add user page to add_user_details dictionary
        delete_user_details["delete_username"]=delete_username
        delete_user_details["delete_password"]=delete_password
        admin_password="12345"
        
        # if the user inputed the correct admin password
        if delete_password==admin_password :
            
            user_deleted=DELETE_USER() 
            
            
            if user_deleted==True:
                
                #if user deleted  display deletion message
                error="User deleted successfully"
                return render_template("delete_user.html",error=error)
            
            else:   # if user details not found in database display error message that the user does not exist 
                
                error="User not found"
                return render_template("delete_user.html",error=error)
           
        else:  # if the password entered is incorrect display error message that the password is incorrect
            
            error="Incorrect password"
            return render_template("delete_user.html",error=error)
    
    # if no data is recieved from the delete user page 
    else:
        return render_template("delete_user.html")
    

    
    
# Temperature readings route
@app.route('/Temperature')
def temp():
    Temp_reading=data['Temp_reading'] # variable to save current sensor reading 
    GRAPH_DATA=RETRIEVE_TEMPETATURES_FROM_DATABASE()# save plot of the sensor data to graph data
    return render_template("temperature.html",Temp_reading=Temp_reading,GRAPH_IMAGE_STRING=GRAPH_DATA)
 
# Soil moisture readings route   
@app.route('/Humidity')
def humidity():
    Moisture_reading=data['Moisture_reading'] # variable to save current sensor reading 
    GRAPH_DATA=RETRIEVE_SOIL_MOISTURE_FROM_DATABASE()# save plot of the sensor data to graph data
    return render_template("humidity.html",Moisture_reading=Moisture_reading,GRAPH_IMAGE_STRING=GRAPH_DATA)

# LDR1 readings route
@app.route('/LDR1')
def LDR1():
   LDR1_reading=data['LDR1_reading'] # variable to save current sensor reading 
   GRAPH_DATA=RETRIEVE_LIGNT_INTENSITY_1_FROM_DATABASE()# save plot of the sensor data to graph data
   return render_template("LDR1.html",LDR1_reading=LDR1_reading,GRAPH_IMAGE_STRING=GRAPH_DATA)

# LDR2 readings route
@app.route('/LDR2')
def LDR2():
    LDR2_reading=data['LDR2_reading'] # variable to save current sensor reading 
    GRAPH_DATA=RETRIEVE_LIGNT_INTENSITY_2_FROM_DATABASE()# save plot of the sensor data to graph data
    return render_template("LDR2.html",LDR2_reading=LDR2_reading,GRAPH_IMAGE_STRING=GRAPH_DATA)

# motion detector readings route
@app.route('/PIR')
def PIR():
    PIR_reading=data['PIR_reading'] # variable to save current sensor reading 
    GRAPH_DATA=RETRIEVE_MOTION_FROM_DATABASE() # save plot of the sensor data to graph data
    return render_template("PIR.html",PIR_reading=PIR_reading,GRAPH_IMAGE_STRING=GRAPH_DATA)

# Route for admin login page
@app.route('/admin', methods=("POST", "GET"))
def admin():
    if request.method == "POST":
        # Get form input
        username = request.form['username']
        password = request.form['password']

        # Check credentials
        if username == "admin" and password == '12345':
            return redirect(url_for('admin_data'))  # Redirect on success
        else:
            return render_template("admin.html", error="Incorrect username or password")  # Show error
    else:
        return render_template("admin.html")  # Initial page load


# Route for admin dashboard
@app.route('/admin_data')
def admin_data():
    # Get current sensor readings
    Temp_reading = data['Temp_reading']
    Moisture_reading = data['Moisture_reading']
    LDR1_reading = data['LDR1_reading']
    LDR2_reading = data['LDR2_reading']
    PIR_reading = data['PIR_reading']

    # Retrieve historical data for graphs
    
    TEMP_GRAPH_DATA = RETRIEVE_TEMPETATURES_FROM_DATABASE()
    MOISTURE_GRAPH_DATA = RETRIEVE_SOIL_MOISTURE_FROM_DATABASE()
    LDR_1_GRAPH_DATA = RETRIEVE_LIGNT_INTENSITY_1_FROM_DATABASE()
    LDR_2_GRAPH_DATA = RETRIEVE_LIGNT_INTENSITY_2_FROM_DATABASE()
    PIR_GRAPH_DATA = RETRIEVE_MOTION_FROM_DATABASE()

    # Render dashboard with data
    return render_template(
        'admin_data.html',
        Temp_reading=Temp_reading,
        Moisture_reading=Moisture_reading,
        LDR1_reading=LDR1_reading,
        LDR2_reading=LDR2_reading,
        PIR_reading=PIR_reading,
        TGD=TEMP_GRAPH_DATA,
        MGD=MOISTURE_GRAPH_DATA,
        LGD1=LDR_1_GRAPH_DATA,
        LGD2=LDR_2_GRAPH_DATA,
        PGD=PIR_GRAPH_DATA
    )

if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)