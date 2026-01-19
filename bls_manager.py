import pandas 
import requests
import json
import requests, pandas as pd
import os

class BLS_data:
    
    def __init__(self):
        self.CPI_area_codes = pandas.read_table("data_files/index_files/cpi_area_code_list.txt", sep="\t")
        self.CPI_item_codes = pandas.read_table("data_files/index_files/cpi_item_code_list.txt", sep="\t")
        
        
    def acquire_data(self, series_id):
        
        def int_to_month():
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            return lambda x: months[x-1]
        
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        
        end_year = 2025
        start_year = 1980
        
        rows = []
        
        while end_year > start_year:
            
            current_end = end_year
            
            if end_year - start_year > 9:
                current_start = end_year - 9
            else:
                current_start = start_year

            payload = {"seriesid":series_id, "startyear":str(current_start), "endyear":str(current_end)}
            r = requests.post(url, data=payload)
            r.raise_for_status()
            js = r.json()
        
            if js['status'] != 'REQUEST_SUCCEEDED':
                if os.path.exists(f"data_files/CPI_Data/{series_id}.csv"):
                    os.remove(f"data_files/CPI_Data/{series_id}.csv")
                return False
        
            for item in js['Results']['series'][0]['data']:
                try:
                    rows.append({"year": item['year'], "period": item['period'], "value": float(item['value'])})
                except:
                    os.remove(f"data_files/CPI_Data/{series_id}.csv")
                    return False
            
            end_year = current_start - 1
            
                
        
        df = pd.DataFrame(rows)

        df['period'] = df['period'].map(lambda x: int(x[1:]))
        df['month'] = df['period'].map(int_to_month())
        df['date'] = df.apply(lambda row: f"{row['month']} {row['year']}", axis=1)
        df = df.sort_values(by=['year', 'period'])

        df.to_csv(f"data_files/CPI_Data/{series_id}.csv", index=False)
        return True


    def cpi_data_query(self, area_name, item_code, start_year, end_year):
        
        
        area_code = self.CPI_area_codes[self.CPI_area_codes["area_name"] == area_name]["area_code"].values[0]
        item_code = self.CPI_item_codes[self.CPI_item_codes["item_name"] == item_code]["item_code"].values[0]
        series_id = f"CUUR{area_code}{item_code}"
        
        if not os.path.exists(f"data_files/CPI_Data/{series_id}.csv"):
            success = self.acquire_data(series_id)
            if not success:
                return None
            

        df = pd.read_csv(f"data_files/CPI_Data/{series_id}.csv")
        df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]  
        return df
    
    def ces_data_query(self, industry, data_type, start_year, end_year):
        pass
    
    def availible_cpi_series(self):
        current_list = []
        
        
        for area_code in self.CPI_area_codes['area_code']:
            
            for item_code in self.CPI_item_codes['item_code']:
                
                series_id = f"CUUR{area_code}{item_code}"

                if os.path.exists(f"data_files/CPI_Data/{series_id}.csv"):
                    current_list.append([series_id, self.CPI_area_codes[self.CPI_area_codes["area_code"] == area_code]["area_name"].values[0], self.CPI_item_codes[self.CPI_item_codes["item_code"] == item_code]["item_name"].values[0]])
        
        output = pandas.DataFrame(current_list, columns=["Series ID", "Area", "Item"])
        return output

    def item_codes(self):
        return self.CPI_item_codes
    
    def area_codes(self):
        return self.CPI_area_codes
    
    def available_dates(self):
        return [x for x in range(1980,2026)]