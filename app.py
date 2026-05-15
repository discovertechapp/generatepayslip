
# Project: VEI Hospital Management System

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
import pandas as pd
import os
import pdfkit
from io import BytesIO
from datetime import datetime
import csv
from werkzeug.utils import secure_filename
from flask import request, render_template, redirect, url_for, flash, send_from_directory
from PyPDF2 import PdfMerger
import pandas as pd
import os
from datetime import datetime
from conf.src_conf import form_config, all_fields_config
# from src.hms_src import process_personal_details
from src.bio_data.create_bio_data_src import process_personal_details,process_experience_details,process_qualification_details,process_address_details,process_academic_activities,process_course_details,process_defense_details,process_mci_details, process_publication_details, process_research_details, process_salary_details, process_current_appointment_details, process_other_activities_details
# from src_conf import all_fields_config


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Paths
# BIODATA_CSV = 'doctorsbiodata.csv'

# Dummy login credentials
USERNAME = 'admin'
PASSWORD = 'admin'

import logging
import sys

# Set up debug logging
LOG_FILE = os.path.join(app.root_path, "hospital_debug.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # for console
    ]
)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('home'))
        flash("Invalid credentials", 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/doctor-biodata')
def doctor_biodata():
    return render_template('doctor_biodata.html')

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}
BIODATA_CSV = 'biodata.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# UPLOAD_FOLDER = os.path.join(app.root_path, 'data')
# DATA_FOLDER = os.path.join(app.root_path, 'data')
UPLOAD_FOLDER = os.path.join(app.root_path)
DATA_FOLDER = os.path.join(app.root_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/export_template')
def export_template():
    import csv
    from flask import Response

    # All your field names in exact order as used in the form
    columns = [
        # Personal Details
        'name_prefix', 'name_as_in_degree_certificate', 'user_id', 's_o_d_o_w_o',
        'date_of_birth', 'age', 'gender', 'present_address', 'permanent_address',
        # Add all other sections here...
        # Experience, Language, Qualifications, Course, Indian Defense, etc.
        # Salary
        'month', 'year', 'amount_received', 'tds'
    ]

    def generate():
        yield ','.join(columns) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=biodata_template.csv'})




@app.route('/upload_biodata_file', methods=['POST'])
def upload_biodata_file():
    file = request.files.get('biodata_file')
    if file and allowed_file(file.filename):
        # Parse and extract data
        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
        # Store in session or pass to template
        session['prefills'] = df.to_dict(orient='records')[0]  # Assuming first row
        return redirect(url_for('biodata_form'))
    flash('Invalid file or no data found.')
    return redirect(url_for('biodata_form'))



@app.route('/download_template')
def download_template():
    # Define the full list of form fields
    columns = [
        # Personal Details
        # 'name_prefix','name_(as_in_degree_certificate)', 'user_id', 's/o_d/o_w/o', 'date_of_birth', 'age', 'speciality', 'department', 'present_designation',
        # 'mobile_number', 'email_id', 'present_address',
        'name_prefix', 'name_(as_in_degree_certificate)', 'user_id', 's/o_d/o_w/o', 'age', 'present_address',
        'pan_number', 'aadhar_number', 'speciality', 'department', 'present_designation', 'telephone_no_res',
        'telephone_no_off', 'mobile_number', 'email_id', 'nationality', 'community', 'father_name', 'father_occupation',
        'spouse_name', 'spouse_occuapation', 'no_of_children:_male', 'no_of_children:_female', 'class_studying:_male',
        'class_studying:_female', 'contact_no.(spouse/father/guardian)', 'name_of_previous_college/institution',
        'last_designation', 'last_worked_relieving_reason', 'computer_knowledge', 'appointment', 'nature_of_employment',
        'practice_type', 'ug/pg/any_other', 'mci_nmc_college_name', 'practice_at', 'practice_city', 'practice_state',
        'practice_from_time', 'practice_to_time',

        # Experience
        'designation[]', 'order_of_experience_to_print[]', 'name_of_institution[]',
        'exp_in__years[]', 'exp_in__months[]', 'exp_in__days[]',

        # Known Languages
        'languages[]', 'read[]', 'write[]', 'speak[]',

        # Address
        'address_type[]', 'address_proof[]', 'street[]', 'street2[]', 'city[]', 'state[]', 'zip[]', 'country[]',

        # Qualification
        'qualification[]', 'specialization[]', 'college[]', 'university[]',
        'year[]', 'registration_no[]', 'registration_date[]', 'name_of_the_state_medical_council[]',

        # Course
        'course[]', 'date__duration[]', 'name_of_institution[]',

        # Indian Defense
        'designation_defense[]', 'from_defense[]', 'to_defense[]',

        # Publication
        'title_of_the_publication[]', 'name_of_journal[]', 'research_type[]', 'no_of_books[]',
        'no_of_chapters_in_book[]', 'authorship_details[]', 'date_of_publication[]', 'index_agency[]',

        # Research Projects
        'title_of_the_project[]', 'month[]', 'amount_received[]', 'tds[]',

        # Salary
        'month', 'year', 'amount_received', 'tds'
    ]

    df = pd.DataFrame(columns=columns)

    # Convert to CSV and return as download
    import io
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=biodata_template.csv"
    response.headers["Content-type"] = "text/csv"
    return response



@app.route('/autofill-biodata', methods=['POST'])
def autofill_biodata():
    file = request.files.get('file')
    if not file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})

    try:
        # Detect format
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file format'})

        if df.empty:
            return jsonify({'status': 'error', 'message': 'Empty file'})

        # Get first row of the file to auto-fill form
        values = df.iloc[0].to_dict()

        # Normalize keys
        normalized = {k.strip(): v for k, v in values.items() if pd.notna(v)}

        return jsonify({'status': 'success', 'values': normalized})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os

import csv



from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os

import csv
print("test")
@app.route('/doctor-biodata/new', methods=['GET', 'POST'])
def new_biodata():
    prefills = {}
    print("1")
    print(f"request.method:{request.method}")
    if request.method == 'POST':
        print(f"request.method:{request.method}")
        if 'csv_file' in request.files and request.files['csv_file'].filename:
            file = request.files['csv_file']

            # df = pd.read_csv(file)
            # if not df.empty:
            #     prefills = df.iloc[0].to_dict()
            #     flash("CSV uploaded successfully. Please review and submit.", 'info')

            try:
                content = file.read().decode('utf-8')  # decode bytes to string
                df = pd.read_csv(io.StringIO(content))  # wrap as in-memory file
                print(df.head())
            except Exception as e:
                print(f"[ERROR] reading CSV: {e}")
                flash('Error reading CSV. Please check encoding or format.', 'danger')
                return redirect(url_for('new_biodata'))


        else:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(os.path.join(app.root_path, 'data'), exist_ok=True)
            os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)

            form_data = {
                k: (v.strip() if v.strip() else 'na')
                for k, v in request.form.items()
                if not k.endswith('[]')
            }


            user_id = form_data.get('user_id', 'na').replace(' ', '_')
            name = form_data.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')
            pan_number = form_data.get('pan_number', 'na')
            aadhar_number = form_data.get('aadhar_number', 'na')

            # ------------------------- Check for duplicates first -------------------------
            personal_csv = os.path.join(app.root_path, 'database', 'biodata_personal.csv')
            if os.path.exists(personal_csv):
                try:
                    df = pd.read_csv(personal_csv, dtype=str).fillna('')
                    if ((df['user_id'] == user_id) & (df['name_(as_in_degree_certificate)'] == name)).any():
                        print("User already exists — skipping save")
                        return jsonify({'status': 'exists'})
                except Exception as e:
                    print(f"Error reading CSV: {e}")
                    return jsonify({'status': 'error', 'message': str(e)}), 500

            print("✅ New user — saving data")

            # Languages are multi-select
            form_data['read_language'] = request.form.getlist('read_language')
            form_data['write_language'] = request.form.getlist('write_language')
            form_data['speak_language'] = request.form.getlist('speak_language')

            # Pass to external handler
            process_personal_details(
                form_data=form_data,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Personal details saved successfully!', 'success')

            process_experience_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )
            print('Experience details saved successfully!', 'success')

            process_qualification_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Qualification details saved successfully!', 'success')

            process_address_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )
            print('Address details saved successfully!', 'success')

            process_academic_activities(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Academic details saved successfully!', 'success')

            process_course_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Course details saved successfully!', 'success')

            process_defense_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Defense details saved successfully!', 'success')

            process_mci_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )
            print('MCI details saved successfully!', 'success')

            process_publication_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Publication details saved successfully!', 'success')

            process_research_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )
            print('Research details saved successfully!', 'success')

            process_salary_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )
            print('Salary details saved successfully!', 'success')

            process_current_appointment_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Current Appointment details saved successfully!', 'success')

            process_other_activities_details(
                raw_form=request.form,
                request_files=request.files,
                app_root=app.root_path,
                upload_folder=app.config['UPLOAD_FOLDER'],
                all_fields_config=all_fields_config
            )

            print('Current Appointment details saved successfully!', 'success')

            print("✅ All sections saved")
            return jsonify({'status': 'success'})

            flash("Personal details saved successfully.", 'success')
            return redirect(url_for('doctor_biodata'))

    return render_template('biodata_form.html',form_config=form_config,
                           prefills=prefills, datetime=datetime)







@app.route('/doctor-biodata/view')
def view_biodata():
    if not os.path.exists(BIODATA_CSV):
        flash("No data found.", 'warning')
        return redirect(url_for('doctor_biodata'))

    df = pd.read_csv(BIODATA_CSV)
    return render_template('view_biodata.html', data=df.to_dict(orient='records'))

@app.route('/doctor-biodata/edit/<int:row_id>', methods=['GET', 'POST'])
def edit_biodata(row_id):
    df = pd.read_csv(BIODATA_CSV)

    if request.method == 'POST':
        for key in request.form:
            df.at[row_id, key] = request.form[key]
        df.to_csv(BIODATA_CSV, index=False)
        flash('Data updated successfully', 'success')
        return redirect(url_for('view_biodata'))

    row_data = df.iloc[row_id].to_dict()

    def get_fields(prefix):
        return [col for col in df.columns if col.startswith(prefix.lower())]

    return render_template('edit_biodata.html',
        data=row_data,
        personal_fields=[c for c in df.columns if not any(c.startswith(p) for p in ['bio_', 'languages_known', 'proofofaddress', 'salary_details', 'indian_defence', 'mcinmc'])],
        experience_fields=get_fields('bio_teaching_experience'),
        language_fields=get_fields('languages_known'),
        proof_fields=get_fields('proofofaddress'),
        qualification_fields=get_fields('bio_qualification'),
        course_fields=get_fields('bio_course'),
        defense_fields=get_fields('indian_defence_service'),
        mcinmc_fields=get_fields('mcinmc'),
        publication_fields=get_fields('bio_research_publication'),
        research_fields=get_fields('bio_research_project'),
        salary_fields=get_fields('salary_details')
    )



from flask import render_template, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime, timedelta
from PyPDF2 import PdfMerger
from io import BytesIO
from zipfile import ZipFile
import os

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
DATA_FOLDER = os.path.join(app.root_path, 'data')
MERGE_FOLDER = os.path.join(app.root_path, 'static', 'merge_file')
# BIODATA_CSV = os.path.join(app.root_path, 'static', 'csv', 'biodata.csv')
download_history_file = os.path.join(DOWNLOAD_FOLDER, 'download_history.csv')








# @app.route('/doctor-biodata/download', methods=['GET', 'POST'])
# def download_biodata():
#     BIODATA_CSV = os.path.join(app.root_path, 'database', 'biodata_personal.csv')

#     if not os.path.exists(BIODATA_CSV):
#         flash("No data to download.", 'warning')
#         return redirect(url_for('doctor_biodata'))

#     df = pd.read_csv(BIODATA_CSV, dtype={'user_id': str},on_bad_lines='warn')
#     df.columns = [col.lower() for col in df.columns]
#     df['user_id_name'] = df.apply(lambda row: f"{row['user_id']}_{row['name_(as_in_degree_certificate)']}", axis=1)

#     names = sorted(df['name_(as_in_degree_certificate)'].dropna().unique().tolist())
#     # departments = sorted(df['department'].dropna().unique().tolist())
#     # colleges = sorted(df['mci_nmc_college_name'].dropna().unique().tolist())
#     user_id_names = sorted(df['user_id_name'].dropna().unique().tolist())

#     appointment_csv = os.path.join(app.root_path, 'database', 'biodata_current_appointment.csv')
#     departments = []
#     colleges = []

#     if os.path.exists(appointment_csv):
#         df_appoint = pd.read_csv(appointment_csv, dtype={'user_id': str}, on_bad_lines='warn')
#         df_appoint.columns = [col.lower() for col in df_appoint.columns]

#         if 'department' in df_appoint.columns:
#             departments = sorted(df_appoint['department'].dropna().unique().tolist())

#         if 'college_institute' in df_appoint.columns:
#             colleges = sorted(df_appoint['college_institute'].dropna().unique().tolist())
            
#     logging.info(f"user_id_names   : {user_id_names}")

#     selected_sections = []
#     filtered = False

#     if request.method == 'POST':
#         college_filter = request.form.get('college', '').strip()
#         department_filter = request.form.get('department', '').strip()
#         user_id_filter = request.form.get('user_id', '').strip()

#         ordered_sections_str = request.form.get('ordered_sections', '')
#         ordered_sections = ordered_sections_str.split(',') if ordered_sections_str else []

#         # ✅ Use ordered_sections directly
#         selected_sections = ordered_sections

#         logging.info(f"Ordered Sections: {ordered_sections, selected_sections}")

#         logging.info("\n--- User Selection ---")
#         logging.info(f"College   : {college_filter or 'All'}")
#         logging.info(f"Department: {department_filter or 'All'}")
#         logging.info(f"User ID   : {user_id_filter or 'All'}")
#         logging.info(f"Sections  : {', '.join(selected_sections) or 'All'}")

#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         section_keywords = {
#             'exp_attachment': 'experience',
#             'experience_attachments': 'experience',
#             'qualification': 'qualification',
#             'proof': 'proof',
#             'course': 'course',
#             'defense': 'defense',
#             'mci_mnc': 'mci_mnc',
#             'publication': 'publication',
#             'research': 'research',
#             'salary': 'salary',
#             'languages': 'languages',
#             'personal': 'personal'
#         }

#         os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
#         os.makedirs(MERGE_FOLDER, exist_ok=True)

#         all_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
#         user_file_map = {}

#         logging.info("\n--- Files Accepted After Filtering ---")
#         logging.info(f"📂 Total files in data folder: {len(all_files)}")
#         logging.info(f"📂 All PDF files: {all_files}")
#         logging.info(f"🎯 Selected Sections: {selected_sections}")


#         for fname in all_files:
#             try:
#                 basename = os.path.splitext(fname)[0]
#                 basename = basename.lower()
#                 section = None
#                 for key, value in section_keywords.items():
#                     if key in basename:
#                         section = value
#                         break
#                 logging.debug(f"📄 File: {fname} | Parsed section: {section}")

#                 # ✅ Skip if section not in selected_sections
#                 if selected_sections and section not in selected_sections:
#                     logging.debug(f"⛔ Skipping {fname} (section not selected): {section}")
#                     continue

#                 parts = fname.split('_')
#                 if len(parts) < 3:
#                     logging.warning(f"⚠️ Skipping {fname}: Not enough parts")
#                     continue

#                 user_id = parts[0]
#                 name = parts[1]
#                 user_key = f"{user_id}_{name}"

#                 user_row = df[df['user_id'] == user_id]
#                 if user_row.empty:
#                     logging.warning(f"⚠️ Skipping {fname}: User ID {user_id} not in biodata CSV")
#                     continue

#                 user_data = user_row.iloc[0]
#                 if college_filter and user_data['mci_nmc_college_name'] != college_filter:
#                     logging.debug(f"⛔ Skipping {fname}: College mismatch")
#                     continue
#                 if department_filter and user_data['department'] != department_filter:
#                     logging.debug(f"⛔ Skipping {fname}: Department mismatch")
#                     continue
#                 if user_id_filter and user_data['user_id'] != user_id_filter:
#                     logging.debug(f"⛔ Skipping {fname}: User ID mismatch")
#                     continue

#                 if user_key not in user_file_map:
#                     user_file_map[user_key] = {
#                         'user_id': user_id,
#                         'name': name,
#                         'files': [],
#                         'row': user_data,
#                         'section_file_map': {}
#                     }

#                 # ✅ Only add the file now
#                 user_file_map[user_key]['files'].append(fname)
#                 if section:
#                     user_file_map[user_key]['section_file_map'].setdefault(section, []).append(fname)

#                 logging.info(f"✅ Picked: {fname}")

#             except Exception as e:
#                 logging.warning(f"⚠️ Skipped {fname} due to error: {e}")

#         zip_buffer = BytesIO()
#         with ZipFile(zip_buffer, 'w') as zipf:
#             for user_key, data in user_file_map.items():
#                 uid = data['user_id']
#                 uname = data['name'].replace(' ', '_')

#                 # ✅ Get only section-mapped files that match selected_sections
#                 file_list = []
#                 for section in selected_sections:
#                     section_files = data.get('section_file_map', {}).get(section, [])
#                     file_list.extend(section_files)

#                 if not file_list:
#                     continue

#                 # ✅ Sort file_list based on section order
#                 def section_key(filename):
#                     basename = os.path.splitext(filename)[0].lower()
#                     for key, value in section_keywords.items():
#                         if key in basename and value in selected_sections:
#                             return selected_sections.index(value)
#                     return len(selected_sections) + 1

#                 file_list.sort(key=section_key)

#                 merger = PdfMerger()

#                 for f in file_list:
#                     fpath = os.path.join(DATA_FOLDER, f)
#                     try:
#                         merger.append(fpath)
#                         logging.info(f"   ➕ Merged: {f}")
#                     except Exception as e:
#                         logging.warning(f"   ❌ Merge failed for {f}: {e}")

#                 merged_filename = f"{uid}_{uname}_{timestamp}.pdf"
#                 merged_path = os.path.join(MERGE_FOLDER, merged_filename)

#                 try:
#                     with open(merged_path, 'wb') as out:
#                         merger.write(out)
#                     merger.close()

#                     with open(merged_path, 'rb') as f:
#                         zipf.writestr(merged_filename, f.read())

#                     logging.info(f"✅ Merged PDF written: {merged_path}")
#                 except Exception as e:
#                     logging.error(f"❌ Failed to write merged PDF for {uid}: {e}")

#         zip_filename = f"{college_filter or 'all'}_{department_filter or 'all'}_{user_id_filter or 'all'}_{timestamp}.zip".replace(" ", "_")
#         zip_path = os.path.join(DOWNLOAD_FOLDER, zip_filename)
#         with open(zip_path, 'wb') as f:
#             f.write(zip_buffer.getvalue())

#         # selection_summary = f"College: {college_filter or 'All'} | Department: {department_filter or 'All'} | UserID: {user_id_filter or 'All'} | Sections: {', '.join(selected_sections) or 'All'}"
#         selection_summary = f"College: {college_filter or 'All'} | Department: {department_filter or 'All'} | UserID: {user_id_filter or 'All'} | Sections: {', '.join(ordered_sections) or 'All'}"
#         history_entry = pd.DataFrame([{
#             'filename': zip_filename,
#             'timestamp': export_time,
#             'status': 'Completed',
#             'selection': selection_summary
#         }])

#         if os.path.exists(download_history_file):
#             history_entry.to_csv(download_history_file, mode='a', header=False, index=False)
#         else:
#             history_entry.to_csv(download_history_file, index=False)

#         flash("ZIP download generated successfully.", 'success')
#         filtered = True

#     history = []
#     if os.path.exists(download_history_file):
#         history_df = pd.read_csv(download_history_file)
#         history_df.columns = [col.lower() for col in history_df.columns]

#         if 'selection' not in history_df.columns:
#             history_df['selection'] = ''

#         history_df['time'] = pd.to_datetime(history_df['timestamp'], errors='coerce')
#         history_df = history_df.sort_values(by='time', ascending=False)
#         history_df = history_df[history_df['time'] > datetime.now() - timedelta(days=14)]
#         history = history_df.head(50).to_dict(orient='records')

#     return render_template('download_biodata.html',
#                            names=names,
#                            departments=departments,
#                            colleges=colleges,
#                            user_ids=user_id_names,
#                            selected_sections=selected_sections,
#                            filtered=filtered,
#                            download_history=history,
#                            history_note="Note: Download history shows only the last 2 weeks or the most recent 50 entries.")


from PIL import Image

# def convert_image_to_pdf(img_path):
#     try:
#         img = Image.open(img_path).convert('RGB')
#         pdf_path = os.path.splitext(img_path)[0] + ".pdf"
#         img.save(pdf_path)
#         return os.path.basename(pdf_path)
#     except Exception as e:
#         logging.warning(f"⚠️ Failed to convert image {img_path} to PDF: {e}")
#         return None

def convert_image_to_pdf(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        pdf_path = os.path.splitext(img_path)[0] + ".pdf"
        img.save(pdf_path)
        os.remove(img_path)  # 🔥 Remove original image
        logging.info(f"Converted and removed original image: {img_path}")
        return os.path.basename(pdf_path)
    except Exception as e:
        logging.warning(f"⚠️ Failed to convert image {img_path} to PDF: {e}")
        return None



@app.route('/doctor-biodata/download', methods=['GET', 'POST'])
def download_biodata():
    appointment_csv = os.path.join(app.root_path, 'database', 'biodata_current_appointment.csv')

    if not os.path.exists(appointment_csv):
        flash("No appointment data to download.", 'warning')
        return redirect(url_for('doctor_biodata'))

    df = pd.read_csv(appointment_csv, dtype={'user_id': str}, on_bad_lines='warn')
    df.columns = [col.lower() for col in df.columns]

    df = df.dropna(subset=['user_id'])

    df['user_id_name'] = df.apply(lambda row: f"{row['user_id']}_{row['name']}", axis=1)

    names = sorted(df['name'].dropna().unique().tolist())
    departments = sorted(df['department'].dropna().unique().tolist()) if 'department' in df.columns else []
    colleges = sorted(df['college_institute'].dropna().unique().tolist()) if 'college_institute' in df.columns else []
    user_id_names = sorted(df['user_id_name'].dropna().unique().tolist())

    logging.info(f"user_id_names   : {user_id_names}")

    selected_sections = []
    filtered = False

    if request.method == 'POST':
        college_filter = request.form.get('college', '').strip()
        department_filter = request.form.get('department', '').strip()
        user_id_filter = request.form.get('user_id', '').strip()

        ordered_sections_str = request.form.get('ordered_sections', '')
        ordered_sections = ordered_sections_str.split(',') if ordered_sections_str else []

        selected_sections = ordered_sections

        logging.info(f"Ordered Sections: {ordered_sections, selected_sections}")

        logging.info("\n--- User Selection ---")
        logging.info(f"College   : {college_filter or 'All'}")
        logging.info(f"Department: {department_filter or 'All'}")
        logging.info(f"User ID   : {user_id_filter or 'All'}")
        logging.info(f"Sections  : {', '.join(selected_sections) or 'All'}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        section_keywords = {
            'exp_attachment': 'experience',
            'experience_attachments': 'experience',
            'qualification': 'qualification',
            'proof': 'proof',
            'course': 'course',
            'defense': 'defense',
            'mci_mnc': 'mci_mnc',
            'publication': 'publication',
            'research': 'research',
            'salary': 'salary',
            'languages': 'languages',
            'personal': 'personal'
        }

        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        os.makedirs(MERGE_FOLDER, exist_ok=True)

        #all_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
        all_files = []
        for fname in os.listdir(DATA_FOLDER):
            fpath = os.path.join(DATA_FOLDER, fname)
            if fname.lower().endswith('.pdf'):
                all_files.append(fname)
            elif fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                converted = convert_image_to_pdf(fpath)
                if converted:
                    all_files.append(converted)
        
        user_file_map = {}

        logging.info(f"Converted and collected files: {all_files}")

        logging.info("\n--- Files Accepted After Filtering ---")
        logging.info(f"📂 Total files in data folder: {len(all_files)}")
        logging.info(f"📂 All PDF files: {all_files}")
        logging.info(f"🎯 Selected Sections: {selected_sections}")

        for fname in all_files:
            try:
                basename = os.path.splitext(fname)[0].lower()

                section = None
                for key, value in section_keywords.items():
                    if key in basename:
                        section = value
                        break
                logging.debug(f"📄 File: {fname} | Parsed section: {section}")

                if selected_sections and section not in selected_sections:
                    logging.debug(f"⛔ Skipping {fname} (section not selected): {section}")
                    continue

                parts = fname.split('_')
                if len(parts) < 3:
                    logging.warning(f"⚠️ Skipping {fname}: Not enough parts")
                    continue

                user_id = parts[0]
                name = parts[1]
                user_key = f"{user_id}_{name}"

                user_row = df[df['user_id'] == user_id]
                if user_row.empty:
                    logging.warning(f"⚠️ Skipping {fname}: User ID {user_id} not in appointment CSV")
                    continue

                user_data = user_row.iloc[0]

                if college_filter and user_data.get('college_institute', '').strip() != college_filter:
                    logging.debug(f"⛔ Skipping {fname}: College mismatch")
                    continue
                if department_filter and user_data.get('department', '').strip() != department_filter:
                    logging.debug(f"⛔ Skipping {fname}: Department mismatch")
                    continue
                if user_id_filter and user_data['user_id'] != user_id_filter:
                    logging.debug(f"⛔ Skipping {fname}: User ID mismatch")
                    continue

                if user_key not in user_file_map:
                    user_file_map[user_key] = {
                        'user_id': user_id,
                        'name': name,
                        'files': [],
                        'row': user_data,
                        'section_file_map': {}
                    }

                user_file_map[user_key]['files'].append(fname)
                if section:
                    user_file_map[user_key]['section_file_map'].setdefault(section, []).append(fname)

                logging.info(f"✅ Picked: {fname}")

            except Exception as e:
                logging.warning(f"⚠️ Skipped {fname} due to error: {e}")

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zipf:
            for user_key, data in user_file_map.items():
                uid = data['user_id']
                uname = data['name'].replace(' ', '_')

                file_list = []
                for section in selected_sections:
                    section_files = data.get('section_file_map', {}).get(section, [])
                    file_list.extend(section_files)

                if not file_list:
                    continue

                def section_key(filename):
                    basename = os.path.splitext(filename)[0].lower()
                    for key, value in section_keywords.items():
                        if key in basename and value in selected_sections:
                            return selected_sections.index(value)
                    return len(selected_sections) + 1

                file_list.sort(key=section_key)

                merger = PdfMerger()

                for f in file_list:
                    fpath = os.path.join(DATA_FOLDER, f)
                    try:
                        merger.append(fpath)
                        logging.info(f"   ➕ Merged: {f}")
                    except Exception as e:
                        logging.warning(f"   ❌ Merge failed for {f}: {e}")

                merged_filename = f"{uid}_{uname}_{timestamp}.pdf"
                merged_path = os.path.join(MERGE_FOLDER, merged_filename)

                try:
                    with open(merged_path, 'wb') as out:
                        merger.write(out)
                    merger.close()

                    with open(merged_path, 'rb') as f:
                        zipf.writestr(merged_filename, f.read())

                    logging.info(f"✅ Merged PDF written: {merged_path}")
                except Exception as e:
                    logging.error(f"❌ Failed to write merged PDF for {uid}: {e}")

        zip_filename = f"{college_filter or 'all'}_{department_filter or 'all'}_{user_id_filter or 'all'}_{timestamp}.zip".replace(" ", "_")
        zip_path = os.path.join(DOWNLOAD_FOLDER, zip_filename)
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        selection_summary = f"College: {college_filter or 'All'} | Department: {department_filter or 'All'} | UserID: {user_id_filter or 'All'} | Sections: {', '.join(ordered_sections) or 'All'}"
        history_entry = pd.DataFrame([{
            'filename': zip_filename,
            'timestamp': export_time,
            'status': 'Completed',
            'selection': selection_summary
        }])

        if os.path.exists(download_history_file):
            history_entry.to_csv(download_history_file, mode='a', header=False, index=False)
        else:
            history_entry.to_csv(download_history_file, index=False)

        flash("ZIP download generated successfully.", 'success')
        filtered = True

    history = []
    if os.path.exists(download_history_file):
        history_df = pd.read_csv(download_history_file)
        history_df.columns = [col.lower() for col in history_df.columns]

        if 'selection' not in history_df.columns:
            history_df['selection'] = ''

        history_df['time'] = pd.to_datetime(history_df['timestamp'], errors='coerce')
        history_df = history_df.sort_values(by='time', ascending=False)
        history_df = history_df[history_df['time'] > datetime.now() - timedelta(days=14)]
        history = history_df.head(50).to_dict(orient='records')

    return render_template('download_biodata.html',
                           names=names,
                           departments=departments,
                           colleges=colleges,
                           user_ids=user_id_names,
                           selected_sections=selected_sections,
                           filtered=filtered,
                           download_history=history,
                           history_note="Note: Download history shows only the last 2 weeks or the most recent 50 entries.")






from flask import send_from_directory
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)




import os, csv, zipfile
import pdfkit
from datetime import datetime
from flask import send_file, request, redirect, render_template, url_for
from flask import Flask
from num2words import num2words

# app = Flask(__name__)
# app.secret_key = "your-secret-key"

# === Folder paths ===
app.config['PAYLOAD_UPLOAD_FOLDER'] = 'uploads/payroll_uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads/payroll_zip'

PAYSLIP_TEMPLATE = 'static/templates/payslip_template.csv'
TEMP_PDF_FOLDER = 'temp_pdfs'

# @app.route("/payroll")
# def payroll():
#     return render_template("payroll.html")

@app.route("/payroll")
def payroll():
    zip_filename = session.pop('zip_filename', None)
    return render_template('payroll.html', zip_filename=zip_filename)

@app.route("/download-payslip-template")
def download_payslip_template():
    return send_file(PAYSLIP_TEMPLATE, as_attachment=True)

@app.route('/downloads/payroll_zip/<filename>')
def serve_zip_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

# @app.route('/generate-payslips', methods=['POST'])
# def generate_payslip():
#     file = request.files.get('payroll_file')

#     # ✅ Validate file
#     if not file or not file.filename.endswith('.csv'):
#         return redirect(url_for('payroll', banner_message='Please upload a valid CSV file.', banner_type='danger'))

#     # ✅ Save uploaded file
#     os.makedirs(app.config['PAYLOAD_UPLOAD_FOLDER'], exist_ok=True)
#     upload_path = os.path.join(app.config['PAYLOAD_UPLOAD_FOLDER'], 'latest_payroll.csv')
#     file.save(upload_path)

#     # ✅ Prepare folders
#     os.makedirs(TEMP_PDF_FOLDER, exist_ok=True)
#     os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

#     pdf_files = []

#     # ✅ Setup wkhtmltopdf
#     # wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
#     wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'
#     pdf_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

#     import base64
#     # Load logo and convert to base64
#     logo_path = os.path.join(app.root_path, 'static', 'logo', 'logo.jpg')
#     with open(logo_path, 'rb') as image_file:
#         logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#     try:
#         with open(upload_path, newline='', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             for i, row in enumerate(reader, start=1):
#                 emp_code = row.get('Emp.Code', f'emp_{i}')
#                 name = row.get('Name', 'Employee')
#                 full_name = f"{emp_code}_{name}".replace(' ', '_')

#                 # ✅ Fix account number formatting
#                 if 'A/c No' in row:
#                     try:
#                         account_val = row['A/c No']
#                         row['A/c No'] = str(int(float(account_val))) if account_val else ''
#                     except Exception:
#                         row['A/c No'] = account_val  # fallback to original

                

#                 net_pay = row.get('Net pay', '0').replace(',', '').strip()
#                 try:
#                     net_pay_int = int(float(net_pay))
#                 except ValueError:
#                     net_pay_int = 0

#                 # Convert number to words in Indian format
#                 net_pay_in_words = num2words(net_pay_int, lang='en_IN').title() + " Rupees Only"

#                 html_content = render_template('payslip_template.html', data=row,logo_base64=logo_base64,net_pay_in_words=net_pay_in_words)

#                 pdf_path = os.path.join(TEMP_PDF_FOLDER, f"{full_name}.pdf")
#                 pdfkit.from_string(html_content, pdf_path, configuration=pdf_config)
#                 pdf_files.append(pdf_path)

#     except Exception as e:
#         return redirect(url_for('payroll', banner_message=f'Error processing CSV: {e}', banner_type='danger'))

#     # ✅ Bundle PDFs into ZIP
#     zip_filename = f"payslips_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
#     zip_path = os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename)

#     try:
#         with zipfile.ZipFile(zip_path, 'w') as zipf:
#             for pdf in pdf_files:
#                 zipf.write(pdf, os.path.basename(pdf))
#     except Exception as e:
#         return redirect(url_for('payroll', banner_message=f'Error creating ZIP file: {e}', banner_type='danger'))

#     # ✅ Clean up temp PDFs
#     for pdf in pdf_files:
#         try:
#             os.remove(pdf)
#         except Exception:
#             pass

#     # ✅ Store result in session and redirect cleanly
#     session['banner_message'] = 'Payslip ZIP generated successfully.'
#     session['zip_filename'] = zip_filename
#     return redirect(url_for('payroll'))

#     # ✅ Redirect with success message and downloadable file
#     # return redirect(url_for('payroll', banner_message='Payslip ZIP generated successfully.'))
#     # return redirect(url_for('payroll',
#     #                         banner_message='Payslip ZIP generated successfully.',
#     #                         zip_filename=zip_filename
#     #                         ))

from flask import request, redirect, url_for, session, render_template
import os, csv, zipfile, pdfkit, base64
from datetime import datetime
from num2words import num2words

@app.route('/generate-payslips', methods=['POST'])
def generate_payslip():
    file = request.files.get('payroll_file')

    # ✅ Validate file
    if not file or not file.filename.endswith('.csv'):
        return redirect(url_for('payroll', banner_message='Please upload a valid CSV file.', banner_type='danger'))

    # ✅ Save uploaded file
    os.makedirs(app.config['PAYLOAD_UPLOAD_FOLDER'], exist_ok=True)
    upload_path = os.path.join(app.config['PAYLOAD_UPLOAD_FOLDER'], 'latest_payroll.csv')
    file.save(upload_path)

    # ✅ Prepare folders
    TEMP_PDF_FOLDER = os.path.join(app.root_path, 'temp_pdfs')
    os.makedirs(TEMP_PDF_FOLDER, exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

    pdf_files = []

    # ✅ Setup wkhtmltopdf config
    wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'  # Adjust path if needed
    pdf_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # ✅ Encode logo image
    logo_path = os.path.join(app.root_path, 'static', 'logo', 'logo.jpg')
    with open(logo_path, 'rb') as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # ✅ Helper function to generate individual PDF
    def generate_pdf_from_row(row, index):
        emp_code = row.get('Emp.Code', f'emp_{index}')
        name = row.get('Name', 'Employee')
        full_name = f"{emp_code}_{name}".replace(' ', '_')

        if 'A/c No' in row:
            try:
                account_val = row['A/c No']
                row['A/c No'] = str(int(float(account_val))) if account_val else ''
            except Exception:
                row['A/c No'] = account_val

        net_pay = row.get('Net pay', '0').replace(',', '').strip()
        try:
            net_pay_int = int(float(net_pay))
        except ValueError:
            net_pay_int = 0

        net_pay_in_words = num2words(net_pay_int, lang='en_IN').title() + " Rupees Only"

        html_content = render_template(
            'payslip_template.html',
            data=row,
            logo_base64=logo_base64,
            net_pay_in_words=net_pay_in_words
        )

        pdf_path = os.path.join(TEMP_PDF_FOLDER, f"{full_name}.pdf")
        pdfkit.from_string(html_content, pdf_path, configuration=pdf_config)
        return pdf_path

    # ✅ Process CSV in batches
    try:
        with open(upload_path, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))

        BATCH_SIZE = 20
        for batch_start in range(0, len(reader), BATCH_SIZE):
            batch = reader[batch_start:batch_start + BATCH_SIZE]
            for i, row in enumerate(batch, start=batch_start + 1):
                try:
                    pdf_path = generate_pdf_from_row(row, i)
                    pdf_files.append(pdf_path)
                except Exception as pdf_error:
                    print(f"[ERROR] Failed to generate PDF for row {i}: {pdf_error}")

    except Exception as e:
        return redirect(url_for('payroll', banner_message=f'Error processing CSV: {e}', banner_type='danger'))

    if not pdf_files:
        return redirect(url_for('payroll', banner_message='No payslips were generated. Please check the CSV data.', banner_type='danger'))

    # ✅ Create ZIP archive
    zip_filename = f"payslips_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    zip_path = os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in pdf_files:
                zipf.write(pdf, os.path.basename(pdf))
    except Exception as e:
        return redirect(url_for('payroll', banner_message=f'Error creating ZIP file: {e}', banner_type='danger'))

    # ✅ Clean up temp PDFs
    for pdf in pdf_files:
        try:
            os.remove(pdf)
        except Exception:
            pass

    session['banner_message'] = 'Payslip ZIP generated successfully.'
    session['zip_filename'] = zip_filename
    return redirect(url_for('payroll'))












if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
    # app.run(debug=True, port=5009)





