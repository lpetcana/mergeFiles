import csv
import glob
import os
import sys
import time
import argparse
import subprocess


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


parent_folder = 'Costal area/'
elevation_folder = 'Elevation'
bathymetry_folder = 'Bathymetry'
result_folder = 'Results/'

input_files_elev = []
input_files_bath = []

path = ""
input_folder_elev = ""
input_folder_bath = ""


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', autosize=False):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        autosize    - Optional  : automatically resize the length of the progress bar to the terminal window (Bool)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    styling = '%s |%s| %s%% %s' % (prefix, fill, percent, suffix)
    if autosize:
        columns, stderr = subprocess.Popen("tput cols", stdout=subprocess.PIPE, stderr=None, shell=True).communicate()
        length = int(columns) - len(styling)
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s' % styling.replace(fill, bar), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""

    parser = argparse.ArgumentParser(
        description='Search for input files in Elevation and Bathymetry folders inside the inputDirectory.\n\nSearch for exact number of files in both folders before it starts parsing them.')

    parser.add_argument('inputDirectory',
                        help='Path to the input directory.')
    parser.add_argument('--outputDirectory',
                        help='Path to the output that contains the resumes.')
    # parser.print_help()
    try:
        options = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)


def check_input_folders():
    global path
    path = '/Users/lucian/PycharmProjects/mergeFiles/Costal area/'

    global input_folder_elev, input_folder_bath
    input_folder_elev = path + elevation_folder
    input_folder_bath = path + bathymetry_folder

    global input_files_elev, input_files_bath
    input_files_elev = [f for f in glob.glob(input_folder_elev + "**/*.csv", recursive=False)]
    input_files_bath = [f for f in glob.glob(input_folder_bath + "**/*.csv", recursive=False)]
    if len(input_files_elev) != len(input_files_bath):
        print(bcolors.FAIL + "Number of files in source folders is different. Stopping now" + bcolors.ENDC)
        sys.exit(1)


def main():
    create_arg_parser()

    check_input_folders()

    printProgressBar(0, len(input_files_elev), prefix='Progress:', suffix='Complete', length=50)


    for x in range(len(input_files_elev)):
        #print(os.path.basename(input_files_elev[x]))
        printProgressBar(x + 1, len(input_files_elev), prefix='Progress:', suffix='Complete', length=50)
        elevList = []
        bathList = []

        resList = []
        with open(input_files_elev[x], mode='r', encoding='utf-8-sig') as elev_csv_file:
            csv_reader = csv.DictReader(elev_csv_file)
            for row in csv_reader:
                elevList.append(row)

        with open(input_folder_bath+'/'+os.path.basename(input_files_elev[x]), mode='r') as bath_csv_file:
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

        with open(parent_folder + result_folder + os.path.basename(input_files_elev[x]), mode='w') as csv_file:
            fieldnames = ['CRS_ID', 'Measured_point_ID', 'X', 'Y', 'Z', 'Distance', 'Interval']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(listSize):
                writer.writerow({'CRS_ID': elevList[i]["CRS_ID"], 'Measured_point_ID': elevList[i]['Measured_point_ID'],
                                 'X': elevList[i]['X'], 'Y': elevList[i]['Y'], 'Z': resList[i],
                                 'Distance': elevList[i]['Distance'], 'Interval': elevList[i]['Interval']})


start = time.time()
print('Starting doing magic')
main()
end = time.time()
print(f'\nDuration of the execution was: {end - start}')
