from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)
ma = Marshmallow(app) 

class MemberSchema(ma.Schema): # Schema for members 
    name = fields.String(required=True)
    age = fields.String(required=True)  
    
    class Meta:
        fields = ("name", "age", "id") 
        
member_schema = MemberSchema()  # can have one single member 
members_schema = MemberSchema(many=True)  # can have multiple members 

class WorkoutSchema(ma.Schema):  # schema for workout sessions
    pass


def get_db_connection():
    """ Connect to MySQL database and return the connection object """ 
    # Database connection parameters 
    db_name = "db_name"
    user = "user_name"
    password = "password" 
    host = "host_name"
    
    try:
        # attempting to establish connection
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        
        # check if connection is successful
        print("Connected to MySQL database successfully.")
        return conn 
    except Error as e:
        # Handling any connection errors
        print(f"Error: {e}")
 
       
@app.route('/')  # Main home page route, first thing that opens before other routes are entered 
def home():
    return 'Welcome To My Fitness Center Management System!' 

@app.route("/members", methods=["GET"]) # GET route to retrieve all members 
def get_members():
    try:
        conn = get_db_connection()  # connect to db 
        if conn is None: # return error if no connection
            return jsonify({"Error": "Database connection failed."}), 500 
        cursor = conn.cursor(dictionary=True) # else if connection, create cursor 
        
        query = "SELECT * FROM members" 
        
        cursor.execute(query)   
        
        members = cursor.fetchall() 
        
        return members_schema.jsonify(members) 
    
    except Error as e:
        print(f"Error: {e}") 
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


@app.route("/members/<int:id>", methods=["GET"]) # GET route for specific member 
def get_member(id):
    try:
        conn = get_db_connection()  # connect to db 
        if conn is None: # return error if no connection
            return jsonify({"Error": "Database connection failed."}), 500 
        cursor = conn.cursor(dictionary=True) # else if connection, create cursor 
        
        find_member = (id,)
        query = "SELECT * FROM members WHERE id LIKE %s" 
        
        cursor.execute(query, find_member)   
        
        member = cursor.fetchone() 
        
        return member_schema.jsonify(member) 
    
    except Error as e:
        print(f"Error: {e}") 
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 
    
    
@app.route("/members", methods=["POST"])  # POST route to add new member
def add_member():
    try:
        member_data = member_schema.load(request.json) # receive post request, deserialize from json, fall within 'customer' schema
    
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400 
    
    try: 
        conn = get_db_connection() # connect to db
        if conn is None:
            return jsonify({"Error": "Database connection failed."}), 500 
        cursor = conn.cursor()
        
        new_member = (member_data['name'], member_data['age']) 
        
        query = "INSERT INTO members(name, age) VALUES(%s, %s)"
        
        cursor.execute(query, new_member)
        conn.commit()
        
        return jsonify({"message" : "New member added successfully"}), 201 
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error" : "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


@app.route("/members/<int:id>", methods=["PUT"]) # PUT method to update members
def update_member(id):
    try:
        member_data = member_schema.load(request.json) # receive put request, deserialize from json, fall within 'customer' schema
    
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400 
    
    try: 
        conn = get_db_connection() 
        if conn is None:
            return jsonify({"Error": "Database connection failed."}), 500 
        cursor = conn.cursor()
        
        updated_member = (member_data['name'], member_data['age'], id)
        
        query = "UPDATE members SET name = %s, age = %s WHERE id = %s"
    
        cursor.execute(query, updated_member)
        conn.commit()
        
        return jsonify({"message" : "Member Updated successfully"}), 201 
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error" : "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 
    

@app.route("/members/<int:id>", methods=["DELETE"]) # DELETE method to remove members 
def remove_member(id):
    try:
        conn = get_db_connection() # connect to db 
        if conn is None:
            return jsonify({"Error": "Database connection failed."}), 500 
        cursor = conn.cursor()
        
        member_to_remove = (id,)  # tuple, member id for validation, data retrieval 
        
        cursor.execute("SELECT * FROM members WHERE id = %s", member_to_remove)  # validate id given is in members
        member = cursor.fetchone()
        if not member:
            return jsonify({"Error" : "Member not found"}), 404
        
        cursor.execute("SELECT * FROM workoutsessions WHERE member_id = %s", member_to_remove) # validate member has a workout session 
        member_session = cursor.fetchone() 
        if not member_session: # if not in workoutsessions table 
            query = "DELETE FROM members WHERE id = %s" 
            cursor.execute(query, member_to_remove)
            conn.commit()
        
            return jsonify({"message" : "Member removed successfully"}), 200
        
        else:
            return jsonify({"message" : "Error, member workout session must be removed."}), 400  
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error" : "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 


if __name__ == '__main__':
    app.run(debug=True) 