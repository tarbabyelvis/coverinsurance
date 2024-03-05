from openpyxl import Workbook
from io import BytesIO


def mock_upload_excel():
    # Create a new workbook
    wb = Workbook()

    # Get the active sheet
    sheet = wb.active

    # Add some data to the sheet
    sheet["A1"] = "first_name"
    sheet["B1"] = "middle_name"
    sheet["C1"] = "last_name"
    sheet["D1"] = "id_number"
    sheet["E1"] = "id_type"
    sheet["F1"] = "entity_type"
    sheet["G1"] = "gender"
    sheet["H1"] = "status"
    sheet["I1"] = "dob"
    sheet["J1"] = "email"
    sheet["K1"] = "phone_number"
    sheet["L1"] = "address_street"
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

    columns = {
        "first_name": "first_name",
        "middle_name": "middle_name",
        "last_name": "last_name",
        "primary_id_number": "id_number",
        "primary_id_document_type": "id_type",
        "entity_type": "entity_type",
        "gender": "gender",
        "marital_status": "status",
        "date_of_birth": "dob",
        "email": "email",
        "phone_number": "phone_number",
        "address_street": "address_street",
        "address_suburb": "address_suburb",
        "address_town": "address_town",
        "address_province": "address_province"
    }

    return excel_buffer, columns
