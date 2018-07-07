from chalice import Chalice, Response
from decimal import Decimal
import boto3
import json

app = Chalice(app_name='whereami-api')
app.debug = True

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/save', methods=['POST'])
def save_post():
    locations = app.current_request.json_body
    
    # Replace empty values with null
    r = json.dumps(locations).replace('""', 'null')
    locations = json.loads(r)

    print("Invoking Save Locations endpoint")
    print("Data received: {}".format(locations))

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('locations')

    for loc in locations['locations']:
        timestamp = loc['properties']['timestamp']
        loc['timestamp'] = timestamp

        loc['properties']['battery_level'] = str(Decimal(str(loc['properties']['battery_level'])))
        
        # Change Coordinates to string to avoid float errors
        if 'geometry' in loc:
            i = 0
            for coord in loc['geometry']['coordinates']:
                loc['geometry']['coordinates'][i] = str(Decimal(str(coord)))
                i = i + 1
                
        print(json.dumps(loc, indent=3))
        table.put_item(
            Item=loc
        )

    result = {"result": "ok"}
    return Response(body=result,
                    status_code=200,
                    headers={'Content-Type': 'application/json'})
