import os
import arcpy
import pandas as pd
layer1poly = arcpy.GetParameter(0)
layer2points = arcpy.GetParameter(1)
# Output feature class
outputPath = arcpy.GetParameter(2)
# field for statistics calculation
quantity_field = arcpy.GetParameter(3)
# Create an empty pandas dataframe called table1
table1 = pd.DataFrame(columns=['Name', 'count', 'sum'])
# Extract the name fields from layer1poly and save to list1
list1 = []
with arcpy.da.SearchCursor(layer1poly, ['Name']) as cursor:
    for row in cursor:
        list1.append(row[0])
# Use list1 as indices for table1
table1['Name'] = list1
def PointsPolyStats(layer1poly, layer2points):
    # Create empty lists for count and sum
    countList = []
    sumList = []
    # Iterate through each record in the polygon layer
    with arcpy.da.SearchCursor(layer1poly, ['SHAPE@', 'Name']) as cursor:
        for row in cursor:
            # Select points within the current polygon using Select By Location
            arcpy.SelectLayerByLocation_management(layer2points, 'WITHIN', row[0])            
            arcpy.AddMessage(f'selected by location {row[1]}')
            # Use summary statistics to calculate count and sum
            stats = arcpy.analysis.Statistics(layer2points, 'in_memory/stats_output', [[quantity_field,'COUNT'], [quantity_field,'SUM']])
            fieldsStats = arcpy.ListFields(stats)
            stat_fields_lists = []
            for fields in fieldsStats:
                if '.' in fields.name:
                    field_name = fields.name.replace('.', '_')
                else:
                    field_name = fields.name
                stat_fields_lists.append(field_name)
                #arcpy.AddMessage(stat_fields_lists)
            with arcpy.da.SearchCursor(stats, [stat_fields_lists[2], stat_fields_lists[3]]) as stat_cursor:
                for stat_row in stat_cursor:
                    count = stat_row[0]
                    sum_value = stat_row[1]
##            # Append count and sum to their respective lists
            countList.append(count)
            sumList.append(sum_value)
##            # Clear the selection for the next iteration
            arcpy.SelectLayerByAttribute_management(layer2points, 'CLEAR_SELECTION')
##        # Populate count and sum columns in table1
        table1['count'] = countList
        table1['sum'] = sumList
        arcpy.AddMessage(table1)        
    return table1
PointsPolyStats(layer1poly, layer2points)
output_csv = str(outputPath)
if os.path.exists(output_csv):
    os.remove(output_csv)
table1.to_csv(output_csv)
