# import the dependencies
from pprint import pprint
import pymongo
from bson.json_util import dumps

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# create a database
mydb = myclient["meteorite_landings_db_v2"]

# list all the databases
print(myclient.list_database_names())

 #Create a collection called "landings":
landings = mydb["landings"]


# documents = landings.find()
# for doc in documents:
#     landings.update_one(
#         {'_id': doc['_id']},
#         {'$set': {'year': int(doc['year'])}}
#     )
# Import the dependencies.
from flask import Flask, jsonify, Response
from flask_cors import CORS

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

################################################################

# Define what to do when a user hits the index route.
@app.route("/")
def home():
    return (
        f"<h1>Welcome to Meteorite Landings API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<h2>/api/v1.0/meteorite-landings</h2>"
        f"<h2>/api/v1.0/meteorite-landings/first-rec</h2>"
        f"<h2>/api/v1.0/meteorite-landings/year/<int:year></h2>"
        f"<h2>/api/v1.0/meteorite-landings/unique-years</h2>"
        f"<h2>/api/v1.0/meteorite-landings/unique-names</h2>"
        f"<h2>/api/v1.0/merteorite-landings/count-all-years</h2>"
        f"<h2>/api/v1.0/merteorite-landings/max-year-count</h2>"
        f"<h2>/api/v1.0/meteorite-landings/name?</h2>"
        f"<h2>/api/v1.0/meteorite-landings/stats-year/year?<h2>"
        f"<h2>/api/v1.0/meteorite-landings/top-years</h2>"
        f"<h2>/api/v1.0/meteorite-landings/statistics</h2>"
    )

################################################################

# Define what to do when a user hits the /first-rec route
@app.route("/api/v1.0/meteorite-landings/first-rec")
def first_rec():
    #printing  the first element 
    result=landings.find_one()
    print(f"name {list[result]}")
    return dumps(result), 200, {'Content-Type': 'application/json'}

################################################################

# Select all the documents
@app.route("/api/v1.0/meteorite-landings")
def all_rec():
    #print all the documents 
    result=landings.find()
    #print(f"name {list[result]}")
    return dumps(result), 200, {'Content-Type': 'application/json'}

################################################################

# Define when user select particular document based on name
@app.route("/api/v1.0/meteorite-landings/<mert_name>")
def name(mert_name):
    #Find the number of landings with name ; AAchen'
    query = {'name': mert_name}
    results= landings.find(query)
    return dumps(results), 200, {'Content-Type': 'application/json'}

################################################################   

# Define when user select particular document based on year
@app.route("/api/v1.0/meteorite-landings/year/<int:year>")
def search_by_year(year):
    # Query MongoDB for the given year
    query = {'year': year}
    results = landings.find(query)
    # Return the results as JSON
    return Response(
        dumps(results),
        status=200,
        mimetype='application/json'
    ) 

################################################################

@app.route("/api/v1.0/meteorite-landings/unique-years")
def get_unique_years():
    # Use distinct to get unique values of the 'year' field
    unique_years = landings.distinct('year')

    # Return the result as a JSON response
    return jsonify({"unique_years": unique_years}), 200 

################################################################

@app.route("/api/v1.0/meteorite-landings/unique-names")
def get_unique_names():
    # Use distinct to get unique values of the 'year' field
    unique_names = landings.distinct('name')

    # Return the result as a JSON response
    return jsonify({"unique_names": unique_names}), 200 

################################################################

@app.route("/api/v1.0/merteorite-landings/count-all-years")
def count_meteorites_by_year():
    # MongoDB aggregation pipeline
    pipeline = [
        {"$group": {
            "_id": "$year",  # Group by the 'year' field
            "count": {"$sum": 1}  # Count the number of meteorites in each year
        }},
        {"$sort": {"_id": 1}}  # Optional: Sort the years in ascending order
    ]
    
    # Run the aggregation pipeline
    result = list(landings.aggregate(pipeline))

    # Format the response as a dictionary
    response = []
    for doc in result:
        year_count = {
            "year": doc["_id"],
            "meteorite_count": doc["count"]
        }
        response.append(year_count)
    return jsonify(response), 200

################################################################

@app.route("/api/v1.0/merteorite-landings/max-year-count")
def max_meteorites_by_year():
    # MongoDB aggregation pipeline
    pipeline = [
        {"$group": {
            "_id": "$year",  # Group by the 'year' field
            "count": {"$sum": 1}  # Count the number of meteorites in each year
        }},
        {"$sort": {"count": -1}},  # Sort by count in descending order (highest count first)
        {"$limit": 1}  # Get only the first document (the one with the highest count)
    ]
    
    # Run the aggregation pipeline
    result = list(landings.aggregate(pipeline))

    # Check if result is not empty and return the response
    if result:
        max_year_data = result[0]  # Get the document with the maximum count
        response = {
            "year": max_year_data["_id"],
            "meteorite_count": max_year_data["count"]
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "No data found"}), 404
    
################################################################


@app.route("/api/v1.0/meteorite-landings/map/year/<int:year>")
def get_meteorites_by_year(year):
    # Get year from query parameters
    if year is None:
        return jsonify({"error": "Year parameter is required"}), 400

    # Query MongoDB
    query = {"year": year}
    projection = {"_id": 0, "name": 1, "mass": 1, "GeoLocation": 1, "year": 1, "recclass":1 }
    results = list(landings.find(query, projection))

    if not results:
        return jsonify({"message": "No meteorites found for the given year"}), 404

    return jsonify(results), 200


################################################################

@app.route("/api/v1.0/meteorite-landings/stats-year/<int:year>")
def get_meteorite_stats_year(year):
    # Aggregation pipeline
    pipeline = [
        {"$match": {"year": year}},
        {
            "$group": {
                "_id": "$year",
                "count": {"$sum": 1},
                "min_mass": {"$min": "$mass"},
                "max_mass": {"$max": "$mass"}
            }
        }
    ]

    # Execute aggregation query
    result = list(landings.aggregate(pipeline))    

    if result:
        # Prepare response
        response = {
            "year": year,
            "count": result[0]["count"],
            "min_mass": result[0]["min_mass"],
            "max_mass": result[0]["max_mass"]
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": "No data found for the given year"}), 404

################################################################

@app.route("/api/v1.0/meteorite-landings/top-years")
def get_top_years():
    
    # Aggregation pipeline
    pipeline = [
        {
            "$group": {
                "_id": "$year",  # Group by year
                "count": {"$sum": 1}  # Count number of documents per year
            }
        },
        {"$sort": {"count": -1}},  # Sort by count in descending order
        {"$limit": 10}  # Limit to top 10 results
    ]

    # Execute aggregation query
    result = list(landings.aggregate(pipeline))

    # Format the result for the response
    top_years = [{"year": doc["_id"], "count": doc["count"]} for doc in result]

    return jsonify(top_years), 200

################################################################

@app.route("/api/v1.0/meteorite-landings/statistics")
def meteorite_statistics():
    # Aggregation pipeline for statistical analysis
    pipeline = [
        {
            "$group": {
                "_id": None,  # No grouping key, calculate stats for all documents
                "min_mass": {"$min": "$mass"},
                "max_mass": {"$max": "$mass"},
                "average_mass": {"$avg": "$mass"},
                "total_meteorites": {"$sum": 1}
            }
        }
    ]

    # Aggregation pipeline for counting unique years
    unique_years_pipeline = [
        {
            "$group": {
                "_id": "$year"  # Group by year
            }
        },
        {
            "$count": "total_years"  # Count the number of unique years
        }
    ]

    # Execute the aggregation pipelines
    stats_result = list(landings.aggregate(pipeline))
    years_result = list(landings.aggregate(unique_years_pipeline))

    if not stats_result or not years_result:
        return jsonify({"message": "No data found"}), 404

    # Extract results
    stats = stats_result[0]
    total_years = years_result[0]["total_years"]

    response = {
        "min_mass": stats["min_mass"],
        "max_mass": stats["max_mass"],
        "average_mass": stats["average_mass"],
        "total_meteorites": stats["total_meteorites"],
        "total_years": total_years
    }
    return jsonify(response)

################################################################

if __name__ == "__main__":
    app.run(debug=True)