import copy
import csv
import sys
import time

start = time.time()

parent_folder = 'Costal area'
elevation_folder = 'Elevation'
bathymetry_folder = 'Bathymetry'

for x in range(100):
    elevList = []
    bathList = []

    resList = []
    with open('Costal area/Elevation/S5_01_001&3952.csv', mode='r', encoding='utf-8-sig') as elev_csv_file:
        csv_reader = csv.DictReader(elev_csv_file)
        for row in csv_reader:
            elevList.append(row)

    with open('Costal area/Bathymetry/S5_01_001&3952.csv', mode='r') as bath_csv_file:
        csv_reader = csv.DictReader(bath_csv_file)
        for row in csv_reader:
            bathList.append(row)

    if len(elevList) != len(bathList):
        sys.exit('Error: files do not contain same number of points. Aborting execution.')

    for i in range(len(elevList)):
        resList.append(float(9999))

    listSize = len(resList)

    for i in range(listSize):
        elev = float(elevList[i]["Z"])
        bath = float(bathList[i]["Z"])
        result = float(9999)

        if elev == 0 and bath == 0:
            result = 0

        if elev > 0:
            result = elev

        if elev == 0 and bath < 0:
            if i == 0:
                if elev == 0 and float(elevList[i + 1]["Z"]) > 0:
                    result = 0
                else:
                    result = bath
            if i == listSize - 1:
                if elev == 0 and float(elevList[i - 1]["Z"]) > 0:
                    result = 0
                else:
                    result = bath

            if 0 < i < listSize - 1:
                if float(elevList[i - 1]["Z"]) == 0 and float(elevList[i + 1]["Z"]) == 0:
                    result = bath
                else:
                    result = 0

        resList[i] = result

    filename = str(x)+'resultfile.csv'
    print(filename)
    with open(filename, mode='w') as csv_file:
        fieldnames = ['CRS_ID', 'Measured_point_ID', 'X', 'Y', 'Z', 'Distance', 'Interval']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(listSize):
            writer.writerow({'CRS_ID': elevList[i]["CRS_ID"], 'Measured_point_ID': elevList[i]['Measured_point_ID'],
                             'X': elevList[i]['X'], 'Y': elevList[i]['Y'], 'Z': resList[i],
                             'Distance': elevList[i]['Distance'], 'Interval': elevList[i]['Interval']})

end = time.time()
print(end - start)
