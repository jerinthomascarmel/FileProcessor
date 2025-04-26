from flask import request, jsonify, send_file, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request
import io
import zipfile



def upload_phase2():
    # First verify the user is authenticated
    try:
        verify_jwt_in_request()
    except:
        print("User is not authenticated")
        return redirect(url_for('login'))

    # Expecting a .zip file
    print("Expecting a .zip file")
    zip_file = request.files.get('zip_file')

    if not zip_file:
        print("Missing zip file!")
        return jsonify({'error': 'Missing zip file!'}), 400

    try:
        import time 
        print('before time delay')
        # Simulate a delay of 2 minutes
        time.sleep(120)
        print('after time delay')
        # Create an in-memory buffer to hold the zip file contents
        zip_buffer = io.BytesIO(zip_file.read())

        # Open the zip file and extract its contents
        with zipfile.ZipFile(zip_buffer, 'r') as z:

            zip_output = io.BytesIO()

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
