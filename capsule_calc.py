import os
import pandas as pd
from flask import redirect
from dtale.app import build_app
from dtale.views import startup

# capsuleChoice = input("12.8mm (1) or 17mm? (2)")

# if capsuleChoice == "1":
#     file_path = "output_measurements_128mm.xlsx.xlsx"
#     output_path = "combinations_128mm.csv"
# if capsuleChoice == "2":
#     file_path = "output_measurements_17mm.xlsx"
#     output_path = "combinations_17mm.csv"
# else:
#     print("Invalid input")
#     exit()

# # Read the data into dataframes
# piston_cap_ball_end_df = pd.read_excel(file_path, sheet_name="Piston Cap Ball End")
# sleeve_body_df = pd.read_excel(file_path, sheet_name="Sleeve Body")
# piston_df = pd.read_excel(file_path, sheet_name="Piston")

# # Display the dataframes
# print("Piston Cap Ball End:")
# print(piston_cap_ball_end_df.head())
# print("\nSleeve Body:")
# print(sleeve_body_df.head())
# print("\nPiston:")
# print(piston_df.head())

# Output:
# Piston Cap Ball End:
#   Part Number  Count                   Assemblies    Type  Ball Diameter  Ball To Shelf  Shelf to Piston Stop  Ball to Piston Stop
# 0   00-049426      2   ['00-049430', '00-050024']    Male              8            3.2                 0.665                3.865
# 1   00-048395      2  ['00-050025A', '00-050025']  Female              8            3.2                 2.800                6.000
# 2   00-049133      1                ['00-050013']  Female              8            3.2                 5.810                9.010
# 3   00-050361      1                ['00-050016']    Male              8            3.2                 2.790                5.990

# Sleeve Body:
#   Part Number  Count                  Assemblies  Plug Shelf to Piston Shelf  Piston Shelf to Annulus Close Edge  Piston Shelf to Annulus Far Edge     OAL
# 0   00-050017      2  ['00-050016', '00-050025']                      15.180                             9.09999                           12.6746  32.155
# 1   00-049721      1               ['00-049430']                      14.095                             9.07499                           13.5506  32.400
# 2   00-050205      1               ['00-050013']                      16.450                             8.23499                           17.4550  39.200
# 3   00-050014      1               ['00-050024']                      18.636                             8.13239                           16.8202  39.190
# 4  00-050017A      1              ['00-050025A']                      15.500                             9.97837                           13.8140  33.600

# Piston:
#   Part Number  Count                  Assemblies  Ball to Top Surface  Stop Shelf Thickness  Top Surface to Pallet Top  Stop Shelf to Pallet Top  Stop Shelf to Pallet Bottom  Top Surface to Top Retainer
# 0   00-050015      2  ['00-050013', '00-050024']               45.070                   1.5                     18.885                    17.385                       14.845                       38.464
# 1   00-050018      2  ['00-050016', '00-050025']               35.020                   1.5                     14.670                    13.170                       10.630                       28.264
# 2   00-049720      1               ['00-049430']               37.505                   2.0                     15.850                    13.850                       11.310                       30.200
# 3  00-050018A      1              ['00-050025A']               36.625                   2.0                     15.645                    13.645                       11.105                       29.875

def extended_b2b_distance(piston_ball_to_top_surface, piston_stop_shelf_thickness, sleeve_plug_shelf_to_piston_shelf, piston_cap_ball_end_ball_to_shelf, sleeve_annulus_top_edge_to_piston_stop, piston_stop_shelf_to_pallet_top):
    # Calculate the extended ball to ball distance
    # Piston Ball to Top Surface - Piston Stop Shelf Thickness + Sleeve Plug Shelf to Piston Shelf + Piston Cap Ball End Ball to Shelf
    # If Sleeve Body Piston Shelf to Annulus Far Edge - Stop Shelf to Pallet Top < 0.16 then the combination is invalid
    
    # if (sleeve_annulus_top_edge_to_piston_stop - piston_stop_shelf_to_pallet_top) < 0:
    #     return 0.00
    
    extended_b2b = piston_ball_to_top_surface - piston_stop_shelf_thickness + sleeve_plug_shelf_to_piston_shelf + piston_cap_ball_end_ball_to_shelf
    return extended_b2b

def compressed_b2b_distance(piston_ball_to_top_surface, piston_cap_ball_end_ball_to_piston_stop, sleeve_body_plug_shelf_to_piston_shelf, piston_top_surface_to_pallet_top, piston_cap_ball_end_shelf_to_piston_stop):
    # Calculate the compressed ball to ball distance
    # Piston Ball to Top Surface + Piston Cap Ball End Ball to Piston Stop
    # If Sleeve Body Plug Shelf to Piston Shelf - Ball End Shelf to Piston Stop - Stop Shelf to Pallet Bottom < 0 then the combination is invalid
    pallet_stop_shelf_gap = (piston_top_surface_to_pallet_top - 2.54) - (sleeve_body_plug_shelf_to_piston_shelf - piston_cap_ball_end_shelf_to_piston_stop)
    compressed_b2b = piston_ball_to_top_surface + piston_cap_ball_end_ball_to_piston_stop
    return compressed_b2b, pallet_stop_shelf_gap

def locked_b2b_distance(extended_b2b, piston_stop_shelf_to_pallet_top, sleeve_annulus_top_edge_to_piston_stop):
    # Calculate the locked ball to ball distance
    # Extended Ball to Ball - (Piston Stop Shelf to Pallet Top - Sleeve Annulus Top Edge to Piston Stop) + 2.16663
    locked_b2b = extended_b2b - (piston_stop_shelf_to_pallet_top - sleeve_annulus_top_edge_to_piston_stop) + 2.165
    return locked_b2b

def retainer_clearance_distance(sleeve_OAL, piston_top_to_retainer, plug_shelf_to_piston_stop):
    # Calculate the retainer clearance distance
    # Sleeve OAL - Piston Top to Retainer
    retainer_clearance_calc = piston_top_to_retainer + plug_shelf_to_piston_stop - (sleeve_OAL - 3.2) - 1.75950
    #retainer_clearance = f"{retainer_clearance_calc:.2f} = {piston_top_to_retainer:.2f} + {plug_shelf_to_piston_stop:.2f} - ({sleeve_OAL:.2f} - 3.2 - 1.75950)"
    return retainer_clearance_calc

def extended_wedge_annulus_clearance(sleeve_piston_shelf_to_annulus_far, piston_shelf_to_pallet_top):
    return sleeve_piston_shelf_to_annulus_far - piston_shelf_to_pallet_top

def parts_randomizer(piston_cap_ball_end_df, sleeve_body_df, piston_df):
    # Randomize the parts
    piston_cap_ball_end_random = piston_cap_ball_end_df.sample(frac=1).reset_index(drop=True)
    sleeve_body_random = sleeve_body_df.sample(frac=1).reset_index(drop=True)
    piston_random = piston_df.sample(frac=1).reset_index(drop=True)
    return piston_cap_ball_end_random, sleeve_body_random, piston_random

# Go through every combination of the parts and calculate the distances, then output the results to a new dataframe with the part numbers and the distances

def calculate_distances(piston_cap_ball_end_df, sleeve_body_df, piston_df):
    # Initialize an empty list to store the results
    results = []
    
    # Iterate through each row in the dataframes
    for i in range(len(piston_cap_ball_end_df)):
        for j in range(len(sleeve_body_df)):
            for k in range(len(piston_df)):
                # Get the relevant measurements for the current combination of parts
                piston_cap_ball_end_row = piston_cap_ball_end_df.iloc[i]
                sleeve_body_row = sleeve_body_df.iloc[j]
                piston_row = piston_df.iloc[k]
                
                # Calculate the distances
                extended_b2b = extended_b2b_distance(piston_row['Ball to Top Surface'], piston_row['Stop Shelf Thickness'], sleeve_body_row['Plug Shelf to Piston Shelf'], piston_cap_ball_end_row['Ball To Shelf'], sleeve_body_row['Piston Shelf to Annulus Far Edge'], piston_row['Stop Shelf to Pallet Top'])
                compressed_b2b, pallet_stop_shelf_gap = compressed_b2b_distance(piston_row['Ball to Top Surface'], piston_cap_ball_end_row['Ball to Piston Stop'], sleeve_body_row['Plug Shelf to Piston Shelf'], piston_row['Top Surface to Pallet Top'], piston_cap_ball_end_row['Shelf to Piston Stop'])
                locked_b2b = locked_b2b_distance(extended_b2b, piston_row['Stop Shelf to Pallet Top'], sleeve_body_row['Piston Shelf to Annulus Close Edge'])
                retainer_clearance = retainer_clearance_distance(sleeve_body_row['OAL'], piston_row['Top Surface to Top Retainer'], piston_cap_ball_end_row['Shelf to Piston Stop'])
                extended_wedge_clearance = extended_wedge_annulus_clearance(sleeve_body_row['Piston Shelf to Annulus Far Edge'], piston_row['Stop Shelf to Pallet Top'])
                ball_end_type = piston_cap_ball_end_row['Type']                
                
                # if ball_end_type is male then Activation Pin is 00-048389, or else it is 00-601659
                if ball_end_type == 'Male':
                    activation_pin = '00-048389'
                else:
                    activation_pin = '00-601659'
                
                # Create a dictionary with the part numbers and the calculated distances
                result = {
                    'Piston Cap Ball End': piston_cap_ball_end_row['Part Number'],
                    'Activation Pin Cap': '00-601661',
                    'Activation Pin' : activation_pin,
                    'Sleeve Body': sleeve_body_row['Part Number'],
                    'Piston': piston_row['Part Number'],
                    'Screen' : '00-047064',
                    'Retainer' : '00-049271',
                    'Retainer Clip' : '00-049278',
                    'Extended Ball to Ball Distance': extended_b2b,
                    'Compressed Ball to Ball Distance': compressed_b2b,
                    'Locked Ball to Ball Distance': locked_b2b,
                    'Pallet Stop Shelf Gap': pallet_stop_shelf_gap,
                    'Retainer Clearance Distance': retainer_clearance,
                    'Extended Wedge Annulus Clearance': extended_wedge_clearance,
                    'Ball End Type': ball_end_type
                }
                
                # Append the result to the list
                results.append(result)
    
    # Create a new dataframe from the list of results
    results_df = pd.DataFrame(results)
    return results_df

def return_combinations(wedge_size, retainer_clearance, wedge_annulus_clearance):
    # Read the data into dataframes
    if wedge_size == "17mm":
        file_path = "output_measurements_17mm.xlsx"
    elif wedge_size == "128mm":
        file_path = "output_measurements_128mm.xlsx"
    else:
        return "Invalid wedge size"
    
    piston_cap_ball_end_df = pd.read_excel(file_path, sheet_name="Piston Cap Ball End")
    sleeve_body_df = pd.read_excel(file_path, sheet_name="Sleeve Body")
    piston_df = pd.read_excel(file_path, sheet_name="Piston")
    
    # Randomize the parts
    piston_cap_ball_end_random, sleeve_body_random, piston_random = parts_randomizer(piston_cap_ball_end_df, sleeve_body_df, piston_df)
    
    # Calculate the distances
    combinations_df = calculate_distances(piston_cap_ball_end_random, sleeve_body_random, piston_random)
    
    # Filter the combinations based on the retainer clearance and wedge annulus clearance
    combinations_df = combinations_df[combinations_df['Retainer Clearance Distance'] > retainer_clearance]
    combinations_df = combinations_df[combinations_df['Extended Wedge Annulus Clearance'] > wedge_annulus_clearance]
    
    # Sort the combinations by the Extended Ball to Ball Distance
    combinations_df = combinations_df.sort_values(by='Extended Ball to Ball Distance')
    
    # Save the combinations to a new csv file
    combinations_df.to_csv("combinations.csv", index=False)
    
    return redirect("combinations.csv")

# combinations_df = calculate_distances(piston_cap_ball_end_df, sleeve_body_df, piston_df)

# combinations_df = combinations_df[combinations_df['Retainer Clearance Distance'] > -0.2]
# combinations_df = combinations_df[combinations_df['Extended Wedge Annulus Clearance'] > -0.4]

# # Display the calculated distances sorted by the Extended Ball to Ball Distance
# print("\nCalculated Distances:")
# print(combinations_df.sort_values(by='Extended Ball to Ball Distance'))
# print("\n NUMBER OF VALID COMBINATIONS: ", len(combinations_df))

# # Print the frquency of each part number in the calculated distances by category
# print("\nFrequency of Part Numbers:")
# print(combinations_df['Piston Cap Ball End'].value_counts())
# print(combinations_df['Sleeve Body'].value_counts())
# print(combinations_df['Piston'].value_counts())

# # Print parts that have not been used in the combinations
# print("\nParts not used in the combinations:")
# print("Piston Cap Ball End:")
# print(piston_cap_ball_end_df[~piston_cap_ball_end_df['Part Number'].isin(combinations_df['Piston Cap Ball End'])])
# print("\nSleeve Body:")
# print(sleeve_body_df[~sleeve_body_df['Part Number'].isin(combinations_df['Sleeve Body'])])
# print("\nPiston:")
# print(piston_df[~piston_df['Part Number'].isin(combinations_df['Piston'])])

# # Sort Extended Wedge Annulus Clearance from smallest to largest
# combinations_df = combinations_df.sort_values(by='Extended Ball to Ball Distance')

# # Save the combinations to a new csv file 
# combinations_df.to_csv(output_path, index=False)


