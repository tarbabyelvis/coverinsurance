from openpyxl import Workbook
from io import BytesIO


def mock_upload_excel():
    # Create a new workbook
    wb = Workbook()

    # Get the active sheet
    sheet = wb.active

    # Add some data to the sheet
    sheet["A1"] = "First Name"
    sheet["B1"] = "Middlename"
    sheet["C1"] = "Last Name"
    sheet["D1"] = "ID Number"
    sheet["E1"] = "ID Type"
    sheet["F1"] = "Entity Type"
    sheet["G1"] = "Gender"
    sheet["H1"] = "Marital Status"
    sheet["I1"] = "Date of Birth"
    sheet["J1"] = "Email"
    sheet["K1"] = "Phone number"
    sheet["L1"] = "Address Street"
    sheet["M1"] = "Address Suburb"
    sheet["N1"] = "Address Town"
    sheet["O1"] = "Address Province"

    # Add sample data
    data = [
        ["John", "Doe", "Smith", 1234567, "Passport", "Individual", "Male", "Single", "1990-01-01", "john@example.com", "1234567890", "Street", "Suburb", "Town", "Province"]
    ]

    for row in data:
        sheet.append(row)

    # Create an in-memory file to save the workbook
    excel_buffer = BytesIO()
    wb.save(excel_buffer)

    # Move to the beginning of the buffer
    excel_buffer.seek(0)

    return excel_buffer
