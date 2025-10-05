import os

import pandas as pd
from util.enums import FileTypes

write_df = pd.DataFrame


def append_write_df(rows):
    global write_df
    if not rows:
        return

    new_df = pd.DataFrame(rows)
    if write_df.empty:
        write_df = new_df
    else:
        write_df = pd.concat([write_df, new_df], ignore_index=True)


def get_write_df():
    return write_df


def write_file(file_type, output_path, file_name, sheet_name, df):
    # Ensure output folder exists
    os.makedirs(output_path, exist_ok=True)

    if file_type == FileTypes.CSV:
        csv_file = os.path.join(output_path, f"{file_name}.csv")
        df.to_csv(csv_file, index=False)
        print(f"CSV saved: {csv_file}")

    elif file_type == FileTypes.XLSX:
        excel_file = os.path.join(output_path, f"{file_name}.xlsx")
        df.to_excel(excel_file, sheet_name=sheet_name, index=False)
        print(f"Excel saved: {excel_file}")

    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def read_file(file_type, file_path, file_name):
    if file_type == FileTypes.CSV.value:
        return pd.read_csv(file_path + "/" + file_name)
    if file_type == FileTypes.XLSX.value:
        return pd.read_excel(file_path + "/" + file_name)
    if file_type == FileTypes.JSON.value:
        return pd.read_json(file_path + "/" + file_name)
