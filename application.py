from flask import Flask, request, jsonify
import pandas as pd
from collections import OrderedDict
import capsule_calc as cc
import time

app = Flask(__name__)

# Explicitly define the column order
columns_order = [
    'Piston Cap Ball End', 'Sleeve Body',
    'Piston', 'Activation Pin','Ball End Type', 'Extended Ball to Ball Distance', 
    'Compressed Ball to Ball Distance', 'Locked Ball to Ball Distance',
    'Pallet Stop Shelf Gap', 'Retainer Clearance Distance', 'Extended Wedge Annulus Clearance'
]

@app.route('/api/find_combinations', methods=['POST'])
def find_combinations():
    # From App.js
    # const handleSubmit = async (e) => {
    #     e.preventDefault();
    #     try {
    #       const response = await axios.post('/api/find_combinations', {
    #         extendedDistance,
    #         compressedDistance,
    #         lockedDistance,
    #         lockStatus,
    #         wedgeSize,
    #         retainerClearanceDistance,
    #         extendedWedgeAnnulusClearance,
    #       });
    #       setResults(response.data);
    #       setColumnsOrder(response.data.columns_order);
    #     } catch (error) {
    #       console.error('Error fetching results:', error);
    #     }
    #   };
    
    params = request.json
    extended_distance = float(params['extendedDistance']) if params['extendedDistance'] else None
    compressed_distance = float(params['compressedDistance']) if params['compressedDistance'] else None
    locked_distance = float(params['lockedDistance']) if params['lockedDistance'] else None
    lock_status = params['lockStatus']
    wedge_size = params['wedgeSize']
    retainer_clearance_distance = float(params['retainerClearanceDistance']) if params['retainerClearanceDistance'] else None
    extended_wedge_annulus_clearance = float(params['extendedWedgeAnnulusClearance']) if params['extendedWedgeAnnulusClearance'] else None    

    # Select the appropriate dataset based on wedge size
    if wedge_size == '17mm':
        cc.return_combinations('17mm', retainer_clearance_distance, extended_wedge_annulus_clearance)
    elif wedge_size == '12.8mm':
        cc.return_combinations('128mm', retainer_clearance_distance, extended_wedge_annulus_clearance)

    # Wait for 1 second
    time.sleep(1)
    
    data = pd.read_csv('combinations.csv')
    
    ball_end_type = 'Male' if lock_status.lower() == 'locked' else 'Female'
    
    filtered_data = data[data['Ball End Type'] == ball_end_type].copy()
    
    # Calculate the difference for each provided distance
    if extended_distance is not None:
        filtered_data['extended_diff'] = abs(filtered_data['Extended Ball to Ball Distance'] - extended_distance)
    if compressed_distance is not None:
        filtered_data['compressed_diff'] = abs(filtered_data['Compressed Ball to Ball Distance'] - compressed_distance)
    if locked_distance is not None:
        filtered_data['locked_diff'] = abs(filtered_data['Locked Ball to Ball Distance'] - locked_distance)
    
    # Calculate the total difference
    diff_columns = [col for col in ['extended_diff', 'compressed_diff', 'locked_diff'] if col in filtered_data.columns]
    filtered_data['total_diff'] = filtered_data[diff_columns].sum(axis=1)
    
    sorted_data = filtered_data.sort_values('total_diff')
    
    def create_ordered_dict(row):
        return OrderedDict((col, row[col]) for col in columns_order)

    closest = create_ordered_dict(sorted_data.iloc[0])
    larger = [create_ordered_dict(row) for _, row in sorted_data[sorted_data['Extended Ball to Ball Distance'] > closest['Extended Ball to Ball Distance']].head(7).iterrows()]
    smaller = [create_ordered_dict(row) for _, row in sorted_data[sorted_data['Extended Ball to Ball Distance'] < closest['Extended Ball to Ball Distance']].head(7).iterrows()]
    
    return jsonify({
        'closest': closest,
        'larger': larger,
        'smaller': smaller,
        'columns_order': columns_order
    })
    

if __name__ == '__main__':
    app.run(debug=True)