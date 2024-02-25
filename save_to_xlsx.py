import xlsxwriter
from typing import List, Dict


def save_to_xlsx(data: List[Dict], filename: str):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    for i, cell in enumerate(data[0].keys()):
        worksheet.write(0, i, cell)
    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            worksheet.write(i + 1, j, row[cell])

    workbook.close()


if __name__ == "__main__":
    pass
