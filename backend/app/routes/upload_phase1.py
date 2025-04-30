from flask import request, jsonify, send_file, redirect, url_for, Response
import io
import zipfile
from openpyxl.reader.excel import load_workbook
from ..openai_processing import extract_content_with_openai, add_excel_with_sections, add_excel_with_tables, extract_tables_from_docx_usingpydocx
from flask_jwt_extended import verify_jwt_in_request
import os
import tempfile
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

            print('files recieved !')
            progressbars[upload_id] = 10

            excel_path = None
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                    tmp.write(excel_file.read())
                    excel_path = tmp.name

                sections = extract_content_with_openai(word_file)
                print('extracted section/contents')
                progressbars[upload_id] = 40

                excel_path = add_excel_with_sections(
                    sections, excel_file=excel_path)
                print(excel_path)
                print('added contents in excel')
                progressbars[upload_id] = 60

                print("going to the table extraction function ....")
                tables = extract_tables_from_docx_usingpydocx(word_file)
                print('extracted tables from wordfile')
                progressbars[upload_id] = 80

                print("going to adding tables in excel sheet ....")
                excel_path = add_excel_with_tables(
                    tables, excel_file=excel_path)
                print(excel_path)

                print('added tables in excel ')
                progressbars[upload_id] = 90

            finally:
                # Create an in-memory zip archive and add the processed Excel file to it
                zip_output = io.BytesIO()
                with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(excel_path, 'processed_result.xlsx')

                # Reset the pointer to the start of the buffer
                zip_output.seek(0)
                print('completed !')
                progressbars[upload_id] = 100

                if excel_path and os.path.exists(excel_path):
                    os.remove(excel_path)

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
            if percentage == 100:
                yield f"data:{percentage}\n\n"
                break
            elif percentage != previous_percentage:
                yield f"data: {percentage}\n\n"
                previous_percentage = percentage

    return Response(generate(), mimetype='text/event-stream')
