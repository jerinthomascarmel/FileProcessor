from flask import request, jsonify, send_file, redirect, url_for, Response
import io
import zipfile
from openpyxl.reader.excel import load_workbook
from ..openai_processing import extract_content_with_openai, apply_wrap_text, break_text_into_lines
from flask_jwt_extended import verify_jwt_in_request

progressbars = {}


def upload_phase1():
    try:
        verify_jwt_in_request()
    except:
        print("User is not authenticated")
        return redirect(url_for('login'))

    # Expecting a .zip file
    zip_file = request.files.get('zip_file')
    upload_id = request.form['upload_id']

    if not zip_file:
        return jsonify({'error': 'Missing zip file!'}), 400

    try:
        # Create an in-memory buffer to hold the zip file contents
        zip_buffer = io.BytesIO(zip_file.read())

        # Open the zip file and extract its contents
        with zipfile.ZipFile(zip_buffer, 'r') as z:
            word_file = None
            excel_file = None

            # Loop through the files inside the zip and find the Word and Excel files
            for file_name in z.namelist():
                if file_name.endswith('.docx') or file_name.endswith('.doc'):
                    word_file = io.BytesIO(z.read(file_name))
                elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    excel_file = io.BytesIO(z.read(file_name))

            # Check if both files were found
            if not word_file or not excel_file:
                return jsonify({'error': 'Both Word and Excel files are required inside the zip.'}), 400

            # print('files recieved !')
            progressbars[upload_id] = 10

            sections = extract_content_with_openai(word_file)

            # Load the Excel file
            wb = load_workbook(excel_file)
            ws = wb.active

            # Headers
            ws["A1"] = "Header"
            ws["B1"] = "Subheader"
            ws["C1"] = "Requirements"
            ws["D1"] = "Page Limit"
            for cell in ["A1", "B1", "C1", "D1"]:
                apply_wrap_text(ws[cell])

            row_num = 2

            for item in sections:
                header = item.get("header", "")
                subheader = item.get("subheader", "")
                requirements = "\n".join(item.get("requirements", []))
                page_limit = item.get("page_limit", "0")

                # Column A - Header
                cell = ws[f"A{row_num}"]
                cell.value = break_text_into_lines(header)
                apply_wrap_text(cell)

                # Column B - Subheader
                cell = ws[f"B{row_num}"]
                cell.value = break_text_into_lines(subheader or "N/A")
                apply_wrap_text(cell)

                # Column C - Requirements
                cell = ws[f"C{row_num}"]
                cell.value = break_text_into_lines(requirements)
                apply_wrap_text(cell)

                # Column D - Page Limit
                cell = ws[f"D{row_num}"]
                cell.value = page_limit
                apply_wrap_text(cell)

                row_num += 1

            # print('files recieved !')
            progressbars[upload_id] = 60
            # Create an in-memory buffer to store the modified Excel file
            excel_output = io.BytesIO()
            wb.save(excel_output)
            # Reset the pointer to the start of the buffer
            excel_output.seek(0)

            # Create an in-memory zip archive and add the processed Excel file to it
            zip_output = io.BytesIO()
            with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('processed_result.xlsx', excel_output.getvalue())

            zip_output.seek(0)  # Reset the pointer to the start of the buffer

            # print('completed !')
            progressbars[upload_id] = 100
            # Send the zip file back to the client
            return send_file(
                zip_output,
                as_attachment=True,
                download_name='processed_files.zip',
                mimetype='application/zip'
            )

    except Exception as e:
        print(e)
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500


def progress(upload_id):
    def generate():
        previous_percentage = progressbars.get(upload_id, 0)
        while True:
            percentage = progressbars.get(upload_id, 0)
            if percentage != previous_percentage:
                yield f"data: {percentage}\n\n"
                previous_percentage = percentage
            elif percentage == 100:
                yield f"data:{percentage}\n\n"
                break

    return Response(generate(), mimetype='text/event-stream')
