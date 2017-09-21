import json
import pytz
import uuid

from collections import defaultdict, OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import abort, make_response

from app import app, session
from utils import CustomEncoder

@app.route('/')
def index():
    return make_response(open('app/templates/index.html').read())

########## Networks API ############
@app.route('/api/networks', methods=['GET'])
@app.route('/api/networks/<int:bucket>', methods=['GET'])
def get_networks(bucket=0):
    query = "SELECT * FROM networks WHERE bucket=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (bucket,)).result()
    data = [row for row in rows]

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/network/<string:network_id>', methods=['GET'])
def get_network(network_id):
    query = "SELECT * FROM network_info_by_network WHERE id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (network_id,)).result()
    try:
        data = rows[0]
    except IndexError:    
        abort(404)
    
    return json.dumps(data, cls=CustomEncoder) 
    
@app.route('/api/stations_by_network/<string:network_id>', methods=['GET'])
def get_stations_by_network(network_id):
    query = "SELECT * FROM stations_by_network WHERE network_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (network_id,)).result()
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)


########## Stations API ############

@app.route('/api/stations', methods=['GET'])
@app.route('/api/stations/<int:bucket>', methods=['GET'])
def get_stations(bucket=0):
    query = "SELECT * FROM stations WHERE bucket=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (bucket,)).result()
    data = [row for row in rows]

    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/station/<string:station_id>', methods=['GET'])
def get_station(station_id):
    query = "SELECT * FROM station_info_by_station WHERE id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    try:
        data = rows[0]
    except IndexError:    
        abort(404)
    
    return json.dumps(data, cls=CustomEncoder)    
    
@app.route('/api/webcam_live_urls_by_station/<string:station_id>', methods=['GET'])
def get_webcam_live_urls_by_station(station_id):
    query = "SELECT * FROM webcam_live_urls_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/video_urls_by_station/<string:station_id>/<int:on_date>', methods=['GET'])
def get_video_urls_by_station(station_id, on_date):
    query = "SELECT * FROM video_urls_by_station WHERE station_id=? AND date=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    on_dt = datetime.fromtimestamp(on_date/1000)
    rows = session.execute_async(prepared, (station_id, on_dt,)).result()   
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/webcam_photos_by_station/<string:station_id>/<int:on_date>', methods=['GET'])
def get_webcam_photos_by_station_on_date(station_id, on_date):
    query = "SELECT * FROM webcam_photos_by_station WHERE station_id=? AND date=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    on_dt = datetime.fromtimestamp(on_date/1000)
    rows = session.execute_async(prepared, (station_id, on_dt,)).result()   
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/webcam_photos_by_station/<string:station_id>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_webcam_photos_by_station(station_id, from_timestamp, to_timestamp):
    query = "SELECT * FROM webcam_photos_by_station WHERE station_id=? AND date=? AND timestamp >=? AND timestamp <=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_date = datetime(from_dt.year, from_dt.month, from_dt.day)

    while (current_date <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, current_date, from_timestamp, to_timestamp,)))
        current_date += relativedelta(days=1)
    
    data = []
    
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/webcam_photos_by_station_by_limit/<string:station_id>/<int:date>', methods=['GET'])
@app.route('/api/webcam_photos_by_station_by_limit/<string:station_id>/<int:date>/<int:limit>', methods=['GET'])
def get_webcam_photos_by_station_by_limit(station_id, date, limit=None):
    query = "SELECT * FROM webcam_photos_by_station WHERE station_id=? AND date=?"
    date_partition = datetime.fromtimestamp(date/1000.0)
    if limit:
        query += " LIMIT ?"
    prepared = session.prepare(query)
    if limit: 
        rows = session.execute_async(prepared, (station_id, date_partition, limit,)).result()
    else:
        rows = session.execute_async(prepared, (station_id, date_partition, )).result()
    data =  [row for row in rows]

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/parameters_by_location/<string:location_id>', methods=['GET'])
def get_parameters_by_location(location_id):
    query = "SELECT * FROM parameters_by_location WHERE location_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (location_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/parameter_groups_by_location/<string:location_id>', methods=['GET'])
def get_parameter_groups_by_location(location_id):
    query = "SELECT * FROM parameter_groups_by_location WHERE location_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (location_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/sensors_by_station/<string:station_id>', methods=['GET'])
def get_sensors_by_station(station_id):
    query = "SELECT * FROM sensors_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/parameters_all_measurement_types_by_station/<string:station_id>', methods=['GET'])
def get_parameters_all_measurement_types_by_station(station_id):
    query = "SELECT * FROM parameters_all_measurement_types_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/parameters_by_station/<string:station_id>', methods=['GET'])
def get_parameters_by_station(station_id):
    query = "SELECT * FROM parameters_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/profile_parameters_by_station/<string:station_id>', methods=['GET'])
def get_profile_parameters_by_station(station_id):
    query = "SELECT * FROM profile_parameters_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/groups_by_station/<string:station_id>', methods=['GET'])
def get_groups_by_station(station_id):
    query = "SELECT * FROM parameter_groups_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/parameter_groups_by_station/<string:station_id>', methods=['GET'])
def get_parameter_groups_by_station(station_id):
    query = "SELECT * FROM parameter_groups_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/measurement_frequencies_by_station/<string:station_id>', methods=['GET'])
def get_measurement_frequencies_by_station(station_id):
    query = "SELECT * FROM measurement_frequencies_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id,)).result()
    try:
        row = rows[0]
    except IndexError:
        data = {}
    else:
        data = row
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/group_measurements_by_station/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    
    frequencies_query = "SELECT * FROM group_measurement_frequencies_by_station WHERE station_id=? AND group_id=?"
    prepared_frequencies_query = session.prepare(frequencies_query)
    frequencies_rows = session.execute_async(prepared_frequencies_query, (station_id, group_id,)).result()
    frequencies = []
    
    try:
        frequencies_row = frequencies_rows[0]
    except IndexError as e:
        print(e)
    else:
        frequencies = frequencies_row.get('measurement_frequencies', [])
        
    if not frequencies:
        return json.dumps([], cls=CustomEncoder)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    delta = to_dt - from_dt

    if delta.days > 465:
        if 'Daily' in frequencies:
            return get_daily_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif 'Hourly' in frequencies:
            return get_hourly_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif '5 Min' in frequencies:
            return get_five_min_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    else:   # days <= 465
        if delta.days <= 30:
            if delta.days <= 1:
                if '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            else: # 1 < days <= 30
                if 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        else:   # 30 < days <= 465 
            if 'Daily' in frequencies:
                return get_daily_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif 'Hourly' in frequencies:
                return get_hourly_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif '5 Min' in frequencies:
                return get_five_min_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    
    
    return json.dumps([], cls=CustomEncoder)
    
@app.route('/api/group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    
    frequencies_query = "SELECT * FROM group_measurement_frequencies_by_station WHERE station_id=? AND group_id=?"
    prepared_frequencies_query = session.prepare(frequencies_query)
    frequencies_rows = session.execute_async(prepared_frequencies_query, (station_id, group_id,)).result()
    frequencies = []
    
    try:
        frequencies_row = frequencies_rows[0]
    except IndexError as e:
        print(e)
    else:
        frequencies = frequencies_row.get('measurement_frequencies', [])
        
    if not frequencies:
        return json.dumps([], cls=CustomEncoder)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    delta = to_dt - from_dt

    if delta.days > 465:
        if 'Daily' in frequencies:
            return get_daily_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif 'Hourly' in frequencies:
            return get_hourly_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif '5 Min' in frequencies:
            return get_five_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    else:   # days <= 465
        if delta.days <= 30:
            if delta.days <= 1:
                if '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            else: # 1 < days <= 30
                if 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        else:   # 30 < days <= 465 
            if 'Daily' in frequencies:
                return get_daily_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif 'Hourly' in frequencies:
                return get_hourly_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif '5 Min' in frequencies:
                return get_five_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    
    
    return json.dumps([], cls=CustomEncoder)

@app.route('/api/group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    
    frequencies_query = "SELECT * FROM group_measurement_frequencies_by_station WHERE station_id=? AND group_id=?"
    prepared_frequencies_query = session.prepare(frequencies_query)
    frequencies_rows = session.execute_async(prepared_frequencies_query, (station_id, group_id,)).result()
    frequencies = []
    
    try:
        frequencies_row = frequencies_rows[0]
    except IndexError as e:
        print(e)
    else:
        frequencies = frequencies_row.get('measurement_frequencies', [])
        
    if not frequencies:
        return json.dumps({}, cls=CustomEncoder)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    delta = to_dt - from_dt

    if delta.days > 465:
        if 'Daily' in frequencies:
            return get_daily_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif 'Hourly' in frequencies:
            return get_hourly_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        elif '5 Min' in frequencies:
            return get_five_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    else:   # days <= 465
        if delta.days <= 30:
            if delta.days <= 1:
                if '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            else: # 1 < days <= 30
                if 'Hourly' in frequencies:
                    return get_hourly_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
                elif '5 Min' in frequencies:
                    return get_five_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
        else:   # 30 < days <= 465 
            if 'Daily' in frequencies:
                return get_daily_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif 'Hourly' in frequencies:
                return get_hourly_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
            elif '5 Min' in frequencies:
                return get_five_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp)
    
    
    return json.dumps({}, cls=CustomEncoder)
    
@app.route('/api/daily_single_parameter_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date>/<int:to_date>', methods=['GET'])
def get_daily_stations_average_parameter_measurements_by_station(station_id, parameter_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date>=? AND date<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date, to_date, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/daily_single_parameter_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date>/<int:to_date>', methods=['GET'])
def get_daily_single_parameter_measurements_by_station_chart(station_id, parameter_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date>=? AND date<=? ORDER BY date ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date, to_date, )))
    
    sensors = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': sensor_id, 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('date'), row.get('avg_value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]
    
    return json.dumps(series, cls=CustomEncoder)    

@app.route('/api/hourly_single_parameter_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_single_parameter_measurements_by_station(station_id, parameter_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/hourly_single_parameter_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_single_parameter_measurements_by_station_chart(station_id, parameter_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=? ORDER BY date_hour ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    sensors = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': "{}-series".format(sensor_id), 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('date_hour'), row.get('avg_value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]
    
    return json.dumps(series, cls=CustomEncoder)

@app.route('/api/single_parameter_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_single_parameter_measurements_by_station(station_id, parameter_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/single_parameter_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_single_parameter_measurements_by_station_chart(station_id, parameter_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM single_parameter_measurements_by_station WHERE station_id=? AND parameter_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    sensors = OrderedDict()
    
    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': "{}-series".format(sensor_id), 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('timestamp'), row.get('value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]
    
    return json.dumps(series, cls=CustomEncoder)

@app.route('/api/daily_profile_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date>/<int:to_date>')
def get_daily_profile_measurements_by_station(station_id, parameter_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date>=? AND date<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date, to_date, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/daily_profile_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date>/<int:to_date>/')
def get_daily_profile_measurements_by_station_chart(station_id, parameter_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date>=? AND date<=? ORDER BY date ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date, to_date, )))
    
    sensors = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': "{}-series".format(sensor_id), 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('date'), row.get('depth'), row.get('avg_value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]

    return json.dumps(series, cls=CustomEncoder)

@app.route('/api/hourly_profile_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_profile_measurements_by_station(station_id, parameter_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/hourly_profile_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_profile_measurements_by_station_chart(station_id, parameter_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=? ORDER BY date_hour ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    sensors = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': "{}-series".format(sensor_id), 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('date_hour'), row.get('depth'), row.get('avg_value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]

    return json.dumps(series, cls=CustomEncoder)

@app.route('/api/profile_measurements_by_station/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_profile_measurements_by_station(station_id, parameter_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    
    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/profile_measurements_by_station_chart/<string:station_id>/<string:parameter_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_profile_measurements_by_station_chart(station_id, parameter_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM profile_measurements_by_station_time WHERE station_id=? AND parameter_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    
    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, parameter_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    sensors = OrderedDict()
    
    for future in futures:
        rows = future.result()
        for row in rows:
            sensor_id = row.get('sensor_id')
            
            if sensor_id not in sensors:
                sensors[sensor_id] = {'id': "{}-series".format(sensor_id), 'name': row.get('sensor_name'), 'data': []}
                
            sensors[sensor_id]['data'].append([row.get('timestamp'), row.get('depth'), row.get('value')])

    series = [sensor_name_data for sensor_id, sensor_name_data in sensors.items()]

    return json.dumps(series, cls=CustomEncoder)

@app.route('/api/group_measurement_frequencies_by_station/<string:station_id>', methods=['GET'])
def get_group_measurement_frequencies_by_station(station_id):
    query = "SELECT * FROM group_measurement_frequencies_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id, )).result()
    data = [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/group_parameters_by_station/<string:station_id>', methods=['GET'])
def get_group_parameters_by_station(station_id):
    query = "SELECT * FROM group_parameters_by_station WHERE station_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id, )).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/group_parameters_by_station_group/<string:station_id>/<string:group_id>', methods=['GET'])
def get_group_parameters_by_station_group(station_id, group_id):
    query = "SELECT * FROM parameters_by_station_group WHERE station_id=? AND group_id=?"
    prepared = session.prepare(query)
    rows = session.execute_async(prepared, (station_id, group_id, )).result()
    data =  [row for row in rows]
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/daily_group_measurements_by_station/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date>/<int:to_date>', methods=['GET'])
def get_daily_group_measurements_by_station(station_id, group_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date>=? AND date<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date, to_date, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/daily_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date>/<int:to_date>', methods=['GET'])
def get_daily_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date>=? AND date<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date, to_date, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/daily_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date>/<int:to_date>', methods=['GET'])
def get_daily_group_measurements_by_station_chart(station_id, group_id, qc_level, from_date, to_date):
    query = "SELECT * FROM daily_parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date>=? AND date<=? ORDER BY date ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date/1000.0)
    to_dt = datetime.fromtimestamp(to_date/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date, to_date, )))
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('date'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('date'), row.get('min_value'), row.get('max_value')])

    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)

@app.route('/api/hourly_group_measurements_by_station/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_group_measurements_by_station(station_id, group_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)

    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)

    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/thirty_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_thirty_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM thirty_min_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/twenty_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_twenty_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM twenty_min_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/fifteen_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_fifteen_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM fifteen_min_group_meas_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/ten_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_ten_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM ten_min_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/hourly_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>', methods=['GET'])
def get_hourly_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/thirty_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_thirty_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM thirty_min_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])
    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)
    
@app.route('/api/twenty_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_twenty_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM twenty_min_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])
    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)
    
@app.route('/api/fifteen_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_fifteen_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM fifteen_min_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_timestamp, to_timestamp, )))
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])
    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)
    
@app.route('/api/ten_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_ten_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM ten_min_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])

    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)
    
@app.route('/api/one_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_one_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM one_min_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND week_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    year, week_number, weekday = from_dt.isocalendar()
    current_first_day_of_week = datetime.strptime('{} {} 1'.format(year, week_number), '%Y %W %w')
    while (current_first_day_of_week <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_week, from_timestamp, to_timestamp, )))
        current_first_day_of_week += relativedelta(weeks=1)
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])

    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)

@app.route('/api/hourly_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_date_hour>/<int:to_date_hour>/')
def get_hourly_group_measurements_by_station_chart(station_id, group_id, qc_level, from_date_hour, to_date_hour):
    query = "SELECT * FROM hourly_parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND year=? AND date_hour>=? AND date_hour<=? ORDER BY date_hour ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_date_hour/1000.0)
    to_dt = datetime.fromtimestamp(to_date_hour/1000.0)
    
    futures = []
    for year in range(from_dt.year, to_dt.year + 1):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, year, from_date_hour, to_date_hour, )))
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('date_hour'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('date_hour'), row.get('min_value'), row.get('max_value')])
    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)

@app.route('/api/parameter_group_measurements_by_station/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_parameter_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)

    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/five_min_group_measurements_by_station/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_five_min_group_measurements_by_station(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)

    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/five_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_five_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM five_min_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=?"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    
    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)

    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)
    
@app.route('/api/one_min_group_measurements_by_station_time_grouped/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>', methods=['GET'])
def get_one_min_group_measurements_by_station_time_grouped(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    
    query = "SELECT * FROM one_min_group_measurements_by_station_grouped WHERE station_id=? AND group_id=? AND qc_level=? AND week_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []
    year, week_number, weekday = from_dt.isocalendar()
    current_first_day_of_week = datetime.strptime('{} {} 1'.format(year, week_number), '%Y %W %w')
    while (current_first_day_of_week <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_week, from_timestamp, to_timestamp, )))
        current_first_day_of_week += relativedelta(weeks=1)

    data = []
    for future in futures:
        rows = future.result()
        for row in rows:
            data.append(row)
    
    return json.dumps(data, cls=CustomEncoder)

@app.route('/api/five_min_group_measurements_by_station_chart/<string:station_id>/<string:group_id>/<int:qc_level>/<int:from_timestamp>/<int:to_timestamp>/')
def get_five_min_group_measurements_by_station_chart(station_id, group_id, qc_level, from_timestamp, to_timestamp):
    query = "SELECT * FROM five_min_parameter_group_measurements_by_station WHERE station_id=? AND group_id=? AND qc_level=? AND month_first_day=? AND timestamp>=? AND timestamp<=? ORDER BY timestamp ASC"
    prepared = session.prepare(query)
    
    from_dt = datetime.fromtimestamp(from_timestamp/1000.0)
    to_dt = datetime.fromtimestamp(to_timestamp/1000.0)
    
    futures = []

    current_first_day_of_month = datetime(from_dt.year, from_dt.month, 1)
    while (current_first_day_of_month <= to_dt):
        futures.append(session.execute_async(prepared, (station_id, group_id, qc_level, current_first_day_of_month, from_timestamp, to_timestamp, )))
        current_first_day_of_month += relativedelta(months=1)
    
    parameters = OrderedDict()

    for future in futures:
        rows = future.result()
        for row in rows:
            parameter_id = row.get('parameter_id')
            parameter_name = row.get('parameter_name')
            parameter_unit = row.get('unit')
            if parameter_id not in parameters:
                parameters[parameter_id] = {
                    'id': parameter_id, 
                    'name': parameter_name, 
                    'unit': parameter_unit,
                    'averages': [],
                    'ranges': []
                }

            parameters[parameter_id]['averages'].append([row.get('timestamp'), row.get('avg_value')])
            parameters[parameter_id]['ranges'].append([row.get('timestamp'), row.get('min_value'), row.get('max_value')])

    #series = [parameters_data for parameter_id, parameters_data in parameters.items()]

    return json.dumps(parameters, cls=CustomEncoder)
