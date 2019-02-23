import json
import csv
from collections import defaultdict
class DAO():
    def get_woeid(self, data):
        woeid_dict = defaultdict(list)
        with open(data) as csv_file:
            ids = csv.reader(csv_file, delimiter=",")
            for line in ids:
                print(line)
                woeid_dict[line[1]].append((line[0],line[2]))
        return woeid_dict

            

if __name__ == "__main__":
    file = "usa_woeid.csv"
    fect_data = DAO()
    fect_data.get_woeid(file)


