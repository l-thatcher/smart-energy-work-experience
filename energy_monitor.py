from os import path
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from enum import Enum
from ntpath import basename
import re
import csv
import plotly
import plotly.graph_objs as go
import datetime
from collections import OrderedDict
import pandas as pd
import os
import time


# We have an enum defined here so we can use it instead of the strings 'gas' and 'electricity'
class FuelType(Enum):
    electricity = 1
    gas = 2




class EnergyMonitor():

    def __init__(self, parent):
        self.parent = parent
        self.fileDir = ''
        self.file = ''

        self.data_container = OrderedDict()
        self.monthly_data = OrderedDict()
        self.loaded_ids = []
        self.loaded_fuels = []

        self.welcome_label = tk.Label(self.parent, text='Welcome to the Energy Monitor!', font=('Calibri', 32))
        self.welcome_label.configure(background='#c6e2ff')
        self.welcome_label.pack()

        self.message_label = tk.Label(self.parent, text='Please use the dialog below to load a CSV file, which will be displayed ' +
                                          'in the box below.', font=('Calibri', 14), wraplength=540)
        self.message_label.configure(background='#c6e2ff')
        self.message_label.pack(pady=20)

        self.btn_file = tk.Button(self.parent, text="Load file", command=self.load_file)
        self.btn_file.pack(pady=20)

        self.scrolled_text = tk.scrolledtext.ScrolledText(self.parent, width=40, height=10)
        self.scrolled_text.pack()


        self.btn_graph_annual = tk.Button(self.parent, text='Annual Daily Usage',
                                          command=self.generate_annual_graph_singlehouse)
        self.btn_graph_annual.pack_forget()


        self.btn_graph_multi_annual = tk.Button(self.parent, text='Annual Daily Multihouse Usage',
                                          command=self.generate_annual_graph_multihouse)
        self.btn_graph_multi_annual.pack_forget()

        self.btn_Generate_monthly = tk.Button(self.parent, text='Generate Monthly Data',
                                          command=self.generate_single_monthly_data)
        self.btn_Generate_monthly.pack_forget()

        self.btn_Generate_multi_monthly = tk.Button(self.parent, text='Generate Multiple Monthly Data',
                                          command=self.generate_multi_monthly_data)
        self.btn_Generate_multi_monthly.pack_forget()




    # This method handles the loading of a simple file, and processing the data in it into a data storage
    def load_file(self, file=None):
        self.scrolled_text.delete(1.0, tk.END)
        if file is None:
            file = filedialog.askopenfilename(initialdir=path.dirname('C:\\Users\\l-thatcher\\GIT\\smart-energy-usage\\resources\\electricity_daily.csv"'))
            self.fileDir =os.path.dirname(file)
            self.file = file
        elif not path.isfile(file):
            raise ValueError("This file does not exist or is not readable.")

        print(file)

        re_single_house = re.compile('^(.*?)_both_daily')
        re_multiple_houses = re.compile('^(gas|electricity)_daily')

        filename = basename(file).split('.')[0]
        single_match = re_single_house.search(filename)
        multiple_match = re_multiple_houses.search(filename)

        if single_match is not None:
            self.process_single_file(file, single_match.group(1))
        elif multiple_match is not None:
            fuel_type = FuelType[multiple_match.group(1)]
            self.process_multiple_file(file)
        else:
            raise ValueError("File format is not correct, must be one of '{fuel-type}_daily.csv"
                              + " or '{house-id}_both_daily.csv is invalid")

        if single_match is not None:
            try:
                self.btn_graph_multi_annual.pack_forget()
                self.btn_Generate_monthly.pack_forget()
                self.btn_Generate_multi_monthly.pack_forget()
                self.btn_graph_annual.pack(pady=5)
                self.btn_Generate_monthly.pack(pady=5)
            except:
                self.btn_graph_annual.pack(pady=5)
                self.btn_Generate_monthly.pack(pady=5)
        elif multiple_match is not None:
            try:
                self.btn_graph_multi_annual.pack_forget()
                self.btn_Generate_monthly.pack_forget()
                self.btn_Generate_multi_monthly.pack_forget()
                self.btn_graph_multi_annual.pack(pady=5)
                self.btn_Generate_multi_monthly.pack(pady=5)
            except:
                self.btn_graph_multi_annual.pack(pady=5)
                self.btn_Generate_multi_monthly.pack(pady=5)


    # This method is a separation fo the previous method that could potentially handle
    # different sorts of files, whereas this is specific to this single file
    def process_single_file(self, file, house_id):
        print("This file is one house with multiple fuel types. The house id is '%s'." % house_id)
        print("Deleting old data")
        self.data_container.clear()
        self.loaded_ids.clear()
        self.loaded_fuels.clear()

        with open(file, 'r') as file_contents:
            reader = csv.reader(file_contents)
            header = next(reader, None)

            if header[1].lower() != 'electricity' or header[2].lower() != 'gas':
                raise ValueError('File is not in correct format. First column must be electricity, second must be gas.')

            for row in reader:
                self.scrolled_text.insert(tk.INSERT, (row))
                self.scrolled_text.insert(tk.INSERT, '\n\n')
                this_date = datetime.datetime.strptime(row[0], '%Y%m%d').date()

                self.data_container[this_date] = {house_id: {FuelType.electricity: float(row[1]),
                                                             FuelType.gas: float(row[2])}}

            # Since we have only loaded one file, set the id directly
            self.loaded_ids.append(house_id)
            self.loaded_fuels.extend([FuelType.electricity, FuelType.gas])


    def process_multiple_file(self, file):
        print("This file has many houses with one fuel type.")
        print("Deleting old data")
        self.data_container.clear()
        self.loaded_ids.clear()
        self.loaded_fuels.clear()

        global houselist

        houselist = []
        with open(file) as f:
            reader = csv.reader(f)
            houselist = next(reader)
            houselist.pop(0)

        try:
            self.scrolled_text.delete(1.0, tk.END)
            with open(file, 'r') as file_contents:
                reader = csv.reader(file_contents)
                header = next(reader, None)

                if header[0].lower() != 'date':
                    self.scrolled_text.insert(tk.INSERT, 'The first column must be for dates')
                    raise ValueError('The first column must be date.')

                for row in reader:
                    self.scrolled_text.insert(tk.INSERT, (row))
                    self.scrolled_text.insert(tk.INSERT, '\n\n')

                    self.scrolled_text.insert(tk.INSERT, '\n\n')
                    this_date = datetime.datetime.strptime(row[0], '%Y%m%d').date()
                    housenumber = 0
                    self.data_container[this_date] = {}
                    while housenumber < len(houselist):
                        houseName = houselist[housenumber]
                        # self.data_container[this_date] = {houseName: float(row[housenumber + 1])}
                        self.data_container[this_date][houseName] = float(row[housenumber + 1])
                        housenumber += 1



        except:
            self.scrolled_text.delete(1.0, tk.END)
            with open(file, 'r') as file_contents:
                reader = csv.reader(file_contents)
                header = next(reader, None)

                if header[0].lower() != 'date':
                    self.scrolled_text.insert(tk.INSERT, 'The first column must be for dates')
                    raise ValueError('The first column must be date.')

            df = pd.read_csv(file)
            col = houselist
            df[col] = df[col].ffill()
            df[col] = df[col].bfill()

            print(self.fileDir)
            df.to_csv(self.fileDir + '/fixed_data.csv', encoding='utf-8',index=False)
            file = (self.fileDir + '/fixed_data.csv')
            self.file = file
            self.scrolled_text.insert(tk.INSERT, "missing data has been corrected using \nsurrounding data\n \n")

            with open(file, 'r') as file_contents:
                reader = csv.reader(file_contents)
                header = next(reader, None)


                for row in reader:
                    self.scrolled_text.insert(tk.INSERT, (row))
                    self.scrolled_text.insert(tk.INSERT, '\n\n')

                    self.scrolled_text.insert(tk.INSERT, '\n\n')
                    this_date = datetime.datetime.strptime(row[0], '%Y%m%d').date()
                    housenumber = 0
                    houselist = []
                    with open(file) as f:
                        reader = csv.reader(f)
                        houselist = next(reader)
                        houselist.pop(0)
                    self.data_container[this_date] = {}
                    while housenumber < len(houselist):
                        houseName = houselist[housenumber]
                        # self.data_container[this_date] = {houseName: float(row[housenumber + 1])}
                        self.data_container[this_date][houseName] = float(row[housenumber + 1])
                        housenumber += 1

    def generate_single_monthly_data(self):
        house_id =  self.loaded_ids
        self.monthly_data.clear()
        self.loaded_fuels.clear()

        with open(self.file, 'r') as file_contents:
            reader = csv.reader(file_contents)
            header = next(reader, None)


            for row in reader:
                self.scrolled_text.insert(tk.INSERT, (row))
                self.scrolled_text.insert(tk.INSERT, '\n\n')
                this_date = datetime.datetime.strptime(row[0], '%Y%m%d').date()
                self.monthly_data[this_date] = {'house_a': {FuelType.electricity: float(row[1]),
                                                             FuelType.gas: float(row[2])}}

            print(self.monthly_data)



    def generate_multi_monthly_data(self):
        print('Generating monthly data')
        self.monthly_data.clear()
        self.loaded_ids.clear()
        self.loaded_fuels.clear()

        with open(self.file, 'r') as file_contents:
            reader = csv.reader(file_contents)
            header = next(reader, None)

            for row in reader:
                this_date = datetime.datetime.strptime(row[0], '%Y%m%d').date()
                housenumber = 0
                self.monthly_data[this_date] = {}
                while housenumber < len(houselist):
                    houseName = header[housenumber]
                    self.monthly_data[this_date][houseName] = float(row[housenumber + 1])
                    housenumber += 1


    def generate_metrics(self):
        print("Metrics")


    def generate_graph(self):
        print("Stub method for generating graphs. Use this to spin off other methods for different graphs.")


    # This mehod uses plotly to generate graphs, which open in a browser window.
    def generate_annual_graph_multihouse(self):
        os.remove(self.fileDir + '/fixed_data.csv')
        date_range = list(self.data_container.keys())
        housenumber = 0
        newtrace = []
        while housenumber < len(houselist):
            houseName = houselist[housenumber]
            housenumber += 1
            house_value = []



            for date in date_range:
                house_value.append(self.data_container[date][houseName])

            newtrace.append(go.Scatter(
            x=date_range,
            y=house_value,
            name=(houseName)
            ))

        graph_data = newtrace

        layout = go.Layout(
            title='Multiple houses, one fuel',
            yaxis=dict(
            title='Usage (kWh)'
            ),

        )

        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)





    def generate_annual_graph_singlehouse(self):

        house_id = self.loaded_ids[0]

        date_range = list(self.data_container.keys())
        (gas_values, electricity_values) = ([], [])

        for date in date_range:

            if FuelType.gas not in self.data_container[date][house_id] \
                    or FuelType.electricity not in self.data_container[date][house_id]:

                raise KeyError("Both fuel values must be present to display this graph correctly.")

            gas_values.append(self.data_container[date][house_id][FuelType.gas])
            electricity_values.append(self.data_container[date][house_id][FuelType.electricity])

        gas_trace = go.Scatter(
            x=date_range,
            y=gas_values,
            name='gas trace'
        )

        electricity_trace = go.Scatter(
            x=date_range,
            y=electricity_values,
            name='electricity trace',
        )
        graph_data = [gas_trace, electricity_trace]

        layout = go.Layout(
            title='Single House Both Fuels',
            yaxis=dict(
                title='Usage (kWh)'
            ),

        )

        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Energy Monitor")
    root.geometry('600x750')
    root.configure(background='#c6e2ff')

    plotly.tools.set_credentials_file(username='Louis.thatcher', api_key='VS3z97LjO5nGy1qdrbT1')
    print(plotly.__version__)

    gui = EnergyMonitor(root)
    root.mainloop()
