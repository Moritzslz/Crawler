import pandas as pd
from util.enums import FileTypes

write_df = pd.DataFrame


def append_write_df(data):
    global write_df
    new_df = pd.DataFrame(data)
    if write_df.empty:
        write_df = new_df
    else:
        write_df = pd.concat([write_df, new_df], ignore_index=True)


def get_write_df():
    return write_df


def write_file(file_type, output_path, file_name, sheet_name, df):
    if file_type == FileTypes.CSV:
        csv_file = output_path + "/" + file_name + ".csv"
        df.to_csv(csv_file)
    if file_type == FileTypes.XLSX:
        excel_file = output_path + "/" + file_name + ".xlsx"
        df.to_excel(excel_file, sheet_name=sheet_name, index=False)
    print("DataFrame has been written to " + output_path + "/" + file_name)


def read_file(file_type, file_path, file_name):
    if file_type == FileTypes.CSV.value:
        return pd.read_csv(file_path + "/" + file_name)
    if file_type == FileTypes.XLSX.value:
        return pd.read_excel(file_path + "/" + file_name)
    if file_type == FileTypes.JSON.value:
        return pd.read_json(file_path + "/" + file_name)
