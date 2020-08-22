import quandl as q
import numpy as np
import os
import quandl.errors.quandl_error as q_errors
from datetime import datetime
import csv

q.ApiConfig.api_key = '{KEY}'


class initialize:

    def __init__(self, filename):

        self.hoods = np.loadtxt("codes/" + filename, delimiter=',', dtype='str', skiprows=1, usecols=(0,))
        self.codes = np.loadtxt("codes/" + filename, delimiter=',', dtype='str', skiprows=1, usecols=(1,))

        self.core_data = []
        self.core_data.append(['Neighborhood','MVSF','RZSF','1B','2B'])

        self.growth_data = []
        self.growth_data.append(['Neighborhood','Price 5Y','Price 3Y','Price 1Y', 'Price 5Y Error', 'Price 3Y Error', 'Price 1Y Error'])

        self.rent_growth_data = []
        self.rent_growth_data.append(['Neighborhood', 'Rent 5Y', 'Rent 3Y', 'Rent 1Y', 'Rent 5Y Error', 'Rent 3Y Error', 'Rent 1Y Error'])

        self.regression_outputs = []
        self.regression_outputs.append(['Neighborhood', 'Price Appreciation 3 YR', 'Rent / Price', 'Project IRR 3 YR', 'Price Appreciation 1 YR', 'Rent / Price', 'Project IRR 1 YR'])

        self.hoods_analyzed = 0

    def get_values(self):

        self.request_values()
        print('Count: ' + str(self.hoods_analyzed))
        return self.core_data, self.growth_data, self.rent_growth_data, self.regression_outputs

    def request_values(self):

        count = 0
        metric1 = '_MVSF'
        metric2 = '_RZSF'
        metric3 = '_1B'
        metric4 = '_2B'
        for hood in self.hoods:
            if count > 92:
                break
            # print count
            # print hood
            code1 = 'ZILL/N' + self.codes[count] + metric1
            code2 = 'ZILL/N' + self.codes[count] + metric2
            code3 = 'ZILL/N' + self.codes[count] + metric3
            code4 = 'ZILL/N' + self.codes[count] + metric4

            try:
                data1 = q.get(code1, returns="numpy")
            except q_errors.NotFoundError as error:
                # print hood + ',' + ',' + ',' + ','
                self.core_data.append([hood, np.nan, np.nan, np.nan, np.nan])
                count += 1
                continue
            try:
                data2 = q.get(code2, returns="numpy")
            except q_errors.NotFoundError as error:
                price = data1[len(data1) - 1][1]
                # print hood + ',' + str(price) + ',' + ',' + ','
                self.core_data.append([hood, price, np.nan, np.nan, np.nan])
                rent_pv = 0
                self.growth_calculation(data1, hood, rent_pv)
                count += 1
                continue
            try:
                data3 = q.get(code3, returns="numpy")
            except q_errors.NotFoundError as error:
                price = data1[len(data1) - 1][1]
                rent = data2[len(data2) - 1][1]
                rent_pv = rent / price

                # print hood + ',' + str(price) + ',' + str(rent) + ',' + ','
                self.core_data.append([hood, price, rent, np.nan, np.nan])
                self.growth_calculation(data1, hood, rent_pv)
                self.rent_growth_calculation(data2, hood)
                count += 1
                continue
            try:
                data4 = q.get(code4, returns="numpy")
            except q_errors.NotFoundError as error:
                price = data1[len(data1) - 1][1]
                rent = data2[len(data2) - 1][1]
                one_bed = data3[len(data3) - 1][1]
                rent_pv = rent / price

                # print hood + ',' + str(price) + ',' + str(rent) + ',' + str(one_bed) + ','
                self.core_data.append([hood, price, rent, one_bed, np.nan])
                self.growth_calculation(data1, hood, rent_pv)
                self.rent_growth_calculation(data2, hood)
                count += 1
                continue

            price = data1[len(data1) - 1][1]
            rent = data2[len(data2) - 1][1]
            one_bed = data3[len(data3) - 1][1]
            two_bed = data4[len(data4) - 1][1]

            rent_pv = rent / price
            self.growth_calculation(data1, hood, rent_pv)

            self.core_data.append([hood, price, rent, one_bed, two_bed])
            self.growth_calculation(data1, hood, rent_pv)
            self.rent_growth_calculation(data2, hood)


            # if not no_growth:
            #     print hood + ',' + str(price) + ',' + str(rent) + ',' + str(one_bed) + ',' + str(two_bed) + ',' + str(growth_5) + ',' + str(growth_3) + ',' + str(growth_1)
            # else:
            #     print hood + ',' + str(price) + ',' + str(rent) + ',' + str(one_bed) + ',' + str(two_bed) + ',' + ',' + ','

            count += 1

        self.hoods_analyzed = count
        return 0

    def growth_calculation(self, data1, hood, rent_pv):

        no_growth = False
        growth_5 = 0
        growth_3 = 0
        growth_1 = 0
        growth_5_error = False
        growth_3_error = False
        growth_1_error = False

        if data1[0][0] < datetime(2012, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2012, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_5 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1.0/5.0)) - 1   # issue
            if (index + 59) < (len(data1) - 2):
                growth_5_error = True

        if data1[0][0] < datetime(2014, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2014, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_3 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1.0/3.0)) - 1   # issue
            if (index + 35) < (len(data1) - 2):
                growth_3_error = True

        if data1[0][0] < datetime(2016, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2016, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_1 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1/1)) - 1   # issue
            if (index + 11) < (len(data1) - 2):
                growth_1_error = True
        else:
            no_growth = True

        if not no_growth:
            self.growth_data.append([hood, growth_5, growth_3, growth_1, growth_5_error, growth_3_error, growth_1_error])
        else:
            self.growth_data.append([hood, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])

        projected_irr_3 = -0.44 + (2.57 * growth_3) + (45.39 * rent_pv)
        projected_irr_1 = -0.44 + (2.57 * growth_1) + (45.39 * rent_pv)
        self.regression_outputs.append([hood, growth_3, rent_pv, projected_irr_3, growth_1, rent_pv, projected_irr_1])

        return no_growth

    def rent_growth_calculation(self, data1, hood):

        no_growth = False
        growth_5 = 0
        growth_3 = 0
        growth_1 = 0
        growth_5_error = False
        growth_3_error = False
        growth_1_error = False

        if data1[0][0] < datetime(2012, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2012, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_5 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1.0/5.0)) - 1   # issue
            if (index + 59) < (len(data1) - 2):
                growth_5_error = True

        if data1[0][0] < datetime(2014, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2014, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_3 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1.0/3.0)) - 1   # issue
            if (index + 35) < (len(data1) - 2):
                growth_3_error = True

        if data1[0][0] < datetime(2016, 2, 1, 0, 0):
            index = 0
            for i in range(len(data1) - 1):
                if data1[i][0] == datetime(2016, 1, 31, 0, 0):
                    index = i
                    break
            # index = data1.where(data1 == datetime(2012, 1, 1, 0, 0))
            growth_1 = ((data1[len(data1) - 2][1] / data1[index][1]) ** (1/1)) - 1   # issue
            if (index + 11) < (len(data1) - 2):
                growth_1_error = True
        else:
            no_growth = True

        if not no_growth:
            self.rent_growth_data.append([hood, growth_5, growth_3, growth_1, growth_5_error, growth_3_error, growth_1_error])
        else:
            self.rent_growth_data.append([hood, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])

        return no_growth

for root, dirs, files in os.walk('codes/'):
    for name in files:
        if name == '.DS_Store':
            continue

        print name, '\n\n----------------------------------\n'

        core, growth, rent_growth, regression = initialize(name).get_values()

        with open("atlanta_core_output.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(core)
        print "Core done"
        with open("atlanta_growth_output.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(growth)
        print "Growth done"
        with open("atlanta_rent_growth_output.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(rent_growth)
        print "Rent Growth done"
        with open("atlanta_regression.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(regression)
        print "Regression done"




