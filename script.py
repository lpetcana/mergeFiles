import csv
import glob
import sys
import time
import argparse


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


parent_folder = 'Costal area'
elevation_folder = 'Elevation'
bathymetry_folder = 'Bathymetry'
result_folder = 'Results'


def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""

    parser = argparse.ArgumentParser(
        description='Search for input files in Elevation and Bathymetry folders inside the inputDirectory.\n\nSearch for exact number of files in both folders before it starts parsing them.')

    parser.add_argument('inputDirectory',
                        help='Path to the input directory.')
    parser.add_argument('--outputDirectory',
                        help='Path to the output that contains the resumes.')
    parser.print_help()
    try:
        options = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)


def check_input_folders():
    path = '/Users/lucian/PycharmProjects/mergeFiles/Costal area/'

    input_folder_elev = path + '/' + elevation_folder
    input_folder_bath = path + '/' + bathymetry_folder

    input_files_elev = [f for f in glob.glob(input_folder_elev + "**/*.csv", recursive=False)]
    input_files_bath = [f for f in glob.glob(input_folder_bath + "**/*.csv", recursive=False)]
    if len(input_files_elev) != len(input_files_bath):
        print(bcolors.FAIL + "Number of files in source folders is different. Stopping now" + bcolors.ENDC)

    sys.exit(1)


def main():
    create_arg_parser()

    check_input_folders()

    for x in range(1):
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

        filename = str(x) + 'resultfile.csv'
        with open(parent_folder + '/' + result_folder + '/' + filename, mode='w') as csv_file:
            fieldnames = ['CRS_ID', 'Measured_point_ID', 'X', 'Y', 'Z', 'Distance', 'Interval']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(listSize):
                writer.writerow({'CRS_ID': elevList[i]["CRS_ID"], 'Measured_point_ID': elevList[i]['Measured_point_ID'],
                                 'X': elevList[i]['X'], 'Y': elevList[i]['Y'], 'Z': resList[i],
                                 'Distance': elevList[i]['Distance'], 'Interval': elevList[i]['Interval']})


start = time.time()
main()
end = time.time()
print(f'\nDuration of the execution was: {end - start}')
