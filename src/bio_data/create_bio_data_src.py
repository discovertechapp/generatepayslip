# src/hms_src.py

import os
import csv



def process_personal_details(form_data, request_files, app_root, upload_folder, all_fields_config):
    user_id = form_data.get('user_id', 'na').replace(' ', '_')
    name = form_data.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')
    pan_number = form_data.get('pan_number', 'na')
    aadhar_number = form_data.get('aadhar_number', 'na')

    # --- Photo Upload ---
    photo_filename = 'na'
    photo_file = request_files.get('photo')
    if photo_file and photo_file.filename:
        ext = os.path.splitext(photo_file.filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png']:
            photo_filename = f"{user_id}_{name}_personal_details.jpg"
            photo_path = os.path.join(app_root, 'static', 'photo', photo_filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            photo_file.save(photo_path)
    form_data['photo'] = photo_filename

    # --- PAN Attachment ---
    pan_attachment_filename = ''
    pan_attachment = request_files.get('pan_number_attachment')
    if pan_attachment and pan_attachment.filename:
        pan_attachment_filename = f"{user_id}_{name}_pan_{pan_number}_personaldetails.pdf"
        pan_path = os.path.join(app_root, 'data', pan_attachment_filename)
        os.makedirs(os.path.dirname(pan_path), exist_ok=True)
        pan_attachment.save(pan_path)
    form_data['pan_number_attachment'] = pan_attachment_filename

    # --- Aadhar Attachment ---
    aadhar_attachment_filename = ''
    aadhar_attachment = request_files.get('aadhar_number_attachment')
    if aadhar_attachment and aadhar_attachment.filename:
        aadhar_attachment_filename = f"{user_id}_{name}_aadhar_{aadhar_number}_personaldetails.pdf"
        aadhar_path = os.path.join(app_root, 'data', aadhar_attachment_filename)
        os.makedirs(os.path.dirname(aadhar_path), exist_ok=True)
        aadhar_attachment.save(aadhar_path)
    form_data['aadhar_number_attachment'] = aadhar_attachment_filename

    # --- Languages ---
    form_data['read_language'] = ', '.join(form_data.get('read_language', [])) or 'na'
    form_data['write_language'] = ', '.join(form_data.get('write_language', [])) or 'na'
    form_data['speak_language'] = ', '.join(form_data.get('speak_language', [])) or 'na'

    # --- CSV Write ---
    personal_fields = ['s_no'] + all_fields_config['personal']
    personal_record = {field: form_data.get(field, 'na') for field in all_fields_config['personal']}

    personal_csv_path = os.path.join(app_root, 'database', 'biodata_personal.csv')
    file_exists = os.path.isfile(personal_csv_path)

    # Determine S.No
    s_no = 1
    if file_exists:
        with open(personal_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            s_no = sum(1 for _ in reader) + 1

    # Insert s_no into the record
    personal_record = {'s_no': s_no, **personal_record}

    with open(personal_csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=personal_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(personal_record)

    return form_data



from werkzeug.utils import secure_filename
import os, csv

def process_experience_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    experience_fields = all_fields_config['experience_fields']
    experience_records = []

    designations = raw_form.getlist('designation')
    total_entries = len(designations)

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        empty_entry = True  # Assume entry is empty initially

        for field in experience_fields:
            values = raw_form.getlist(field)
            value = values[i] if i < len(values) else 'na'
            record[field] = value if value.strip() else 'na'
            if value.strip() and value.strip().lower() != 'na':
                empty_entry = False

        # Handle file upload
        attachments = request_files.getlist('experience_attachments')
        if i < len(attachments):
            uploaded_file = attachments[i]
            if uploaded_file and uploaded_file.filename:
                original_filename = secure_filename(uploaded_file.filename)
                new_filename = f"{user_id}_{name}_experience_attachments_{i + 1}_{original_filename}"
                filepath = os.path.join(upload_folder, new_filename)
                uploaded_file.save(filepath)
                record['experience_attachments'] = new_filename
                empty_entry = False  # File is present, so not empty
            else:
                record['experience_attachments'] = 'na'
        else:
            record['experience_attachments'] = 'na'

        if not empty_entry:
            experience_records.append(record)

    # Save to CSV
    if experience_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_experience.csv')
        all_fields = ['user_id', 'name', 'entry_num'] + experience_fields + ['experience_attachments']
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            if not file_exists:
                writer.writeheader()
            for row in experience_records:
                writer.writerow(row)


from werkzeug.utils import secure_filename
import os, csv

def process_qualification_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    qualification_fields = all_fields_config['qualification_fields']
    qualification_records = []

    mdms_subjects = raw_form.getlist('mdms_subject')
    total_entries = len(mdms_subjects)

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        empty_entry = True

        for field in qualification_fields:
            values = raw_form.getlist(field)
            value = values[i] if i < len(values) else 'na'
            record[field] = value if value.strip() else 'na'
            if value.strip() and value.strip().lower() != 'na':
                empty_entry = False

        # Handle attachment upload
        attachments = request_files.getlist('education_attachment')
        if i < len(attachments):
            uploaded_file = attachments[i]
            if uploaded_file and uploaded_file.filename:
                original_filename = secure_filename(uploaded_file.filename)
                new_filename = f"{user_id}_{name}_qualification_attachment_{i + 1}_{original_filename}"
                filepath = os.path.join(upload_folder, new_filename)
                uploaded_file.save(filepath)
                record['education_attachment'] = new_filename
                empty_entry = False
            else:
                record['education_attachment'] = 'na'
        else:
            record['education_attachment'] = 'na'

        if not empty_entry:
            qualification_records.append(record)

    # Save to CSV
    if qualification_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_qualification_new.csv')
        all_fields = ['user_id', 'name', 'entry_num'] + qualification_fields + ['education_attachment']
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            if not file_exists:
                writer.writeheader()
            for row in qualification_records:
                writer.writerow(row)


from werkzeug.utils import secure_filename
import os, csv

from werkzeug.utils import secure_filename
import os, csv

from werkzeug.utils import secure_filename
import os, csv

# def process_address_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
#     user_id = raw_form.get('user_id', 'na').replace(' ', '_')
#     name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

#     address_fields = all_fields_config['address_fields']
#     address_records = []

#     # We'll use present_address_proof as the base to detect count
#     present_proofs = raw_form.getlist('present_address_proof')
#     total_entries = len(present_proofs)

#     for i in range(total_entries):
#         record = {
#             'user_id': user_id,
#             'name': name,
#             'entry_num': i + 1
#         }

#         is_empty = True

#         for field in address_fields:
#             values = raw_form.getlist(field)
#             value = values[i] if i < len(values) else ''
#             cleaned = value.strip()
#             record[field] = cleaned if cleaned else 'na'

#             # Skip address_type and address_type_permanent in emptiness check
#             if field not in ['present_address_type', 'permanent_address_type']:
#                 if cleaned and cleaned.lower() != 'na':
#                     is_empty = False

#         # Handle file upload (1 per address entry)
#         attachments = request_files.getlist('address_proof_file')
#         if i < len(attachments):
#             file = attachments[i]
#             if file and file.filename:
#                 safe_name = secure_filename(file.filename)
#                 final_name = f"{user_id}_{name}_address_proof_file_{i + 1}_{safe_name}"
#                 filepath = os.path.join(upload_folder, final_name)
#                 file.save(filepath)
#                 record['address_proof_file'] = final_name
#                 is_empty = False
#             else:
#                 record['address_proof_file'] = 'na'
#         else:
#             record['address_proof_file'] = 'na'

#         if not is_empty:
#             address_records.append(record)

#     # Save valid rows only
#     if address_records:
#         csv_path = os.path.join(app_root, 'database', 'biodata_address.csv')
#         all_cols = ['user_id', 'name', 'entry_num'] + address_fields + ['address_proof_file']
#         file_exists = os.path.isfile(csv_path)

#         with open(csv_path, 'a', newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=all_cols)
#             if not file_exists:
#                 writer.writeheader()
#             for row in address_records:
#                 writer.writerow(row)

def process_address_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    address_fields = all_fields_config['address_fields']
    address_records = []


    # We'll use present_address_proof as the base to detect count
    present_proofs = raw_form.getlist('present_address_proof')
    total_entries = len(present_proofs)

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True

        for field in address_fields:
            values = raw_form.getlist(field)
            value = values[i] if i < len(values) else ''
            cleaned = value.strip()
            record[field] = cleaned if cleaned else 'na'

            # Skip address_type and address_type_permanent in emptiness check
            if field not in ['present_address_type', 'permanent_address_type']:
                if cleaned and cleaned.lower() != 'na':
                    is_empty = False

        # Handle file upload (1 per address entry)
        # attachments = request_files.getlist('address_proof_file')
        # if i < len(attachments):
        #     file = attachments[i]
        #     if file and file.filename:
        #         safe_name = secure_filename(file.filename)
        #         final_name = f"{user_id}_{name}_address_proof_file_{i + 1}_{safe_name}"
        #         filepath = os.path.join(upload_folder, final_name)
        #         file.save(filepath)
        #         record['address_proof_file'] = final_name
        #         is_empty = False
        #     else:
        #         record['address_proof_file'] = 'na'
        # else:
        #     record['address_proof_file'] = 'na'

        # Handle individual attachments for present and permanent
        present_file = request_files.getlist('present_address_attachment')
        permanent_file = request_files.getlist('permanent_address_attachment')

        # Present attachment
        if i < len(present_file) and present_file[i] and present_file[i].filename:
            safe_name = secure_filename(present_file[i].filename)
            final_name = f"{user_id}_{name}_present_attachment_{i + 1}_{safe_name}"
            filepath = os.path.join(upload_folder, final_name)
            present_file[i].save(filepath)
            record['present_address_attachment'] = final_name
        else:
            record['present_address_attachment'] = 'na'

        # Permanent attachment
        if i < len(permanent_file) and permanent_file[i] and permanent_file[i].filename:
            safe_name = secure_filename(permanent_file[i].filename)
            final_name = f"{user_id}_{name}_permanent_attachment_{i + 1}_{safe_name}"
            filepath = os.path.join(upload_folder, final_name)
            permanent_file[i].save(filepath)
            record['permanent_address_attachment'] = final_name
        else:
            record['permanent_address_attachment'] = 'na'

        if not is_empty:
            address_records.append(record)

    # Save valid rows only
    if address_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_address.csv')
        # all_cols = ['user_id', 'name', 'entry_num'] + address_fields + ['address_proof_file']
        all_cols = ['user_id', 'name', 'entry_num'] + address_fields + ['present_address_attachment',
                                                                        'permanent_address_attachment']

        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            if not file_exists:
                writer.writeheader()
            for row in address_records:
                writer.writerow(row)


import os
import csv
def process_academic_activities(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    academic_fields = all_fields_config['academic_fields']
    academic_records = []

    base_list = raw_form.getlist('academic_date')  # use to determine entry count
    total_entries = len(base_list)

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True

        for field in academic_fields:
            values = raw_form.getlist(field)
            value = values[i] if i < len(values) else ''
            cleaned = value.strip()
            record[field] = cleaned if cleaned else 'na'

            if cleaned and cleaned.lower() != 'na':
                is_empty = False

        if not is_empty:
            academic_records.append(record)

    # Save only valid entries
    if academic_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_academic.csv')
        all_cols = ['user_id', 'name', 'entry_num'] + academic_fields
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            if not file_exists:
                writer.writeheader()
            for row in academic_records:
                writer.writerow(row)



import os
import csv
from werkzeug.utils import secure_filename

def process_course_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    course_fields = all_fields_config['course_fields']
    course_records = []

    # Get lists of values for each field
    field_values = {field: raw_form.getlist(field) for field in course_fields}
    attachments = request_files.getlist('course_attachment')

    total_entries = max(len(v) for v in field_values.values())

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True
        for field in course_fields:
            values = field_values.get(field, [])
            val = values[i] if i < len(values) else ''
            cleaned = val.strip()
            record[field] = cleaned if cleaned else 'na'

            if cleaned and cleaned.lower() != 'na':
                is_empty = False

        # Handle attachment
        if i < len(attachments):
            file = attachments[i]
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                final_name = f"{user_id}_{name}_course_attachment_{i + 1}_{safe_name}"
                file_path = os.path.join(upload_folder, final_name)
                file.save(file_path)
                record['course_attachment'] = final_name
                is_empty = False
            else:
                record['course_attachment'] = 'na'
        else:
            record['course_attachment'] = 'na'

        if not is_empty:
            course_records.append(record)

    # Save to CSV
    if course_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_course.csv')
        all_columns = ['user_id', 'name', 'entry_num'] + course_fields + ['course_attachment']
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            for row in course_records:
                writer.writerow(row)





import os
import csv
from werkzeug.utils import secure_filename

def process_defense_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    defense_fields = all_fields_config['defense_fields']
    defense_records = []

    # Count based on a repeating field
    designations = raw_form.getlist('defense_designation')
    total_entries = len(designations)

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True

        for field in defense_fields:
            if field == 'defense_attachment':
                # Handle file upload separately below
                continue

            values = raw_form.getlist(field)
            value = values[i] if i < len(values) else ''
            cleaned = value.strip()
            record[field] = cleaned if cleaned else 'na'

            if cleaned and cleaned.lower() != 'na':
                is_empty = False

        # Handle file upload
        attachments = request_files.getlist('defense_attachment')
        if i < len(attachments):
            file = attachments[i]
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                final_name = f"{user_id}_{name}_defense_attachment_{i+1}_{safe_name}"
                filepath = os.path.join(upload_folder, final_name)
                file.save(filepath)
                record['defense_attachment'] = final_name
                is_empty = False
            else:
                record['defense_attachment'] = 'na'
        else:
            record['defense_attachment'] = 'na'

        if not is_empty:
            defense_records.append(record)

    if defense_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_defense.csv')
        all_cols = ['user_id', 'name', 'entry_num'] + defense_fields
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            if not file_exists:
                writer.writeheader()
            for row in defense_records:
                writer.writerow(row)


import csv
import os
from werkzeug.utils import secure_filename


def process_mci_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    mci_fields = all_fields_config['mci_fields']
    mci_record = {
        'user_id': user_id,
        'name': name
    }

    # Handle field values
    for field in mci_fields:
        if field == 'mci_attachment':
            attachments = request_files.getlist(field)
            saved_files = []
            for i, file in enumerate(attachments):
                if file and file.filename:
                    safe_name = secure_filename(file.filename)
                    final_name = f"{user_id}_{name}_{field}_{i + 1}_{safe_name}"
                    filepath = os.path.join(upload_folder, final_name)
                    file.save(filepath)
                    saved_files.append(final_name)
            mci_record[field] = ';'.join(saved_files) if saved_files else 'na'
        else:
            value = raw_form.get(field, '').strip()
            mci_record[field] = value if value else 'na'

    # Save to CSV
    csv_path = os.path.join(app_root, 'database', 'biodata_mci.csv')
    all_cols = ['user_id', 'name'] + mci_fields
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_cols)
        if not file_exists:
            writer.writeheader()
        writer.writerow(mci_record)


import os
import csv
from werkzeug.utils import secure_filename

def process_publication_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    import os
    import csv
    from werkzeug.utils import secure_filename

    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    publication_fields = all_fields_config['publication_fields']
    publication_records = []

    # Get all field values as lists
    field_values = {field: raw_form.getlist(field) for field in publication_fields}
    attachments = request_files.getlist('publication_attachment')

    total_entries = max(len(v) for v in field_values.values()) if field_values else 0

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True
        for field in publication_fields:
            values = field_values.get(field, [])
            val = values[i] if i < len(values) else ''
            cleaned = val.strip()
            record[field] = cleaned if cleaned else 'na'

            if cleaned and cleaned.lower() != 'na':
                is_empty = False

        # Single Attachment
        if i < len(attachments):
            file = attachments[i]
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                final_name = f"{user_id}_{name}_publication_attachment_{i + 1}_{safe_name}"
                file_path = os.path.join(upload_folder, final_name)
                file.save(file_path)
                record['publication_attachment'] = final_name
                is_empty = False
            else:
                record['publication_attachment'] = 'na'
        else:
            record['publication_attachment'] = 'na'

        if not is_empty:
            publication_records.append(record)

    # Save to CSV
    if publication_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_publication.csv')
        all_columns = ['user_id', 'name', 'entry_num'] + publication_fields + ['publication_attachment']
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerows(publication_records)



import os
import csv
from werkzeug.utils import secure_filename

def process_research_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    research_fields = all_fields_config['research_fields']
    research_records = []

    # Get values for each field
    field_values = {field: raw_form.getlist(field) for field in research_fields}
    attachment_files = request_files.getlist('research_attachment')

    total_entries = max(len(vals) for vals in field_values.values())

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True

        for field in research_fields:
            # If this is the attachment field, use the uploaded file
            if field == 'research_attachment':
                if i < len(attachment_files):
                    file = attachment_files[i]
                    if file and file.filename:
                        safe_name = secure_filename(file.filename)
                        final_name = f"{user_id}_{name}_{field}_{i + 1}_{safe_name}"
                        filepath = os.path.join(upload_folder, final_name)
                        file.save(filepath)
                        record[field] = final_name
                        is_empty = False
                    else:
                        record[field] = 'na'
                else:
                    record[field] = 'na'
            else:
                values = field_values.get(field, [])
                val = values[i] if i < len(values) else ''
                cleaned = val.strip()
                record[field] = cleaned if cleaned else 'na'
                if cleaned and cleaned.lower() != 'na':
                    is_empty = False

        if not is_empty:
            research_records.append(record)

    # Save to CSV
    if research_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_research.csv')
        all_columns = ['user_id', 'name', 'entry_num'] + research_fields
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerows(research_records)



def process_salary_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    salary_fields = all_fields_config['salary_fields']
    salary_records = []

    # Gather all lists of values
    field_values = {field: raw_form.getlist(field) for field in salary_fields}
    total_entries = max(len(v) for v in field_values.values())

    for i in range(total_entries):
        record = {
            'user_id': user_id,
            'name': name,
            'entry_num': i + 1
        }

        is_empty = True

        for field in salary_fields:
            values = field_values.get(field, [])
            val = values[i] if i < len(values) else ''
            cleaned = val.strip()
            record[field] = cleaned if cleaned else 'na'

            if cleaned and cleaned.lower() != 'na':
                is_empty = False

        if not is_empty:
            salary_records.append(record)

    if salary_records:
        csv_path = os.path.join(app_root, 'database', 'biodata_salary.csv')
        file_exists = os.path.isfile(csv_path)
        all_columns = ['user_id', 'name', 'entry_num'] + salary_fields

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerows(salary_records)




import os
import csv
from werkzeug.utils import secure_filename

def process_current_appointment_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get("user_id", "na").replace(" ", "_")
    name = raw_form.get("name_(as_in_degree_certificate)", "na").replace(" ", "_")

    current_fields = all_fields_config["current_appointment_fields"]
    record = {
        "user_id": user_id,
        "name": name,
        "entry_num": 1  # only one record for current appointment
    }

    is_empty = True

    # Loop through fields and collect data
    for field in current_fields:
        if field == "current_appointment_attachment":
            file = request_files.get(field)
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                final_name = f"{user_id}_{name}_{field}_{safe_name}"
                file_path = os.path.join(upload_folder, final_name)
                file.save(file_path)
                record[field] = final_name
                is_empty = False
            else:
                record[field] = "na"
        else:
            value = raw_form.get(field, "").strip()
            record[field] = value if value else "na"
            if value and value.lower() != "na":
                is_empty = False

    if not is_empty:
        # Save to CSV
        csv_path = os.path.join(app_root, "database", "biodata_current_appointment.csv")
        file_exists = os.path.isfile(csv_path)
        all_columns = ["user_id", "name", "entry_num"] + current_fields

        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)



import os
import csv
from werkzeug.utils import secure_filename

def process_other_activities_details(raw_form, request_files, app_root, upload_folder, all_fields_config):
    user_id = raw_form.get('user_id', 'na').replace(' ', '_')
    name = raw_form.get('name_(as_in_degree_certificate)', 'na').replace(' ', '_')

    other_fields = all_fields_config['other_activities_fields']

    record = {
        'user_id': user_id,
        'name': name,
        'entry_num': 1  # only one entry expected
    }

    is_empty = True

    for field in other_fields:
        if 'attachment' in field:
            file = request_files.get(field)
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                final_name = f"{user_id}_{name}_{field}_{safe_name}"
                file_path = os.path.join(upload_folder, final_name)
                file.save(file_path)
                record[field] = final_name
                is_empty = False
            else:
                record[field] = 'na'
        else:
            value = raw_form.get(field, '').strip()
            record[field] = value if value else 'na'
            if value and value.lower() != 'na':
                is_empty = False

    if not is_empty:
        csv_path = os.path.join(app_root, 'database', 'biodata_other_activities.csv')
        file_exists = os.path.isfile(csv_path)
        all_columns = ['user_id', 'name', 'entry_num'] + other_fields

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)



