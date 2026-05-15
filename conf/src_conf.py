# conf/src_conf.py


all_fields_config = {
    'personal': [
        'name_prefix', 'name_(as_in_degree_certificate)','user_id',
        'date_of_birth', 'age', 'gender', 'pan_number', 'pan_number_attachment',
        'aadhar_number', 'aadhar_number_attachment', 'mobile_country_code', 'mobile_number',
        'email_id', 'nationality', 'community','read_language','write_language','speak_language','s/o_d/o_w/o', 'father_name',
        'father_occupation', 'marital_status', 'spouse_name', 'spouse_occupation',
        'date_of_marriage', 'total_no_of_children', 'telephone_no_res','telephone_no_off','contact_number_guardian'
    ],
    'experience_fields' : [
        'experience_type', 'employment_type', 'experience_address', 'designation',
        'institution_name', 'from_date', 'to_date',
        'exp_years', 'exp_months', 'exp_days',
        'relieve_reason', 'relieving_doc'
    ],

    'qualification_fields': [
        'mdms_subject',
        'dmmch_subject',
        'phd_subject',
        'qualification',
        'specialization',
        'college',
        'university',
        'passed_out_year',
        'registration_no',
        'registration_date',
        'state_medical_council'
    ],
    "address_fields" : [
        # Present
        "present_address_type", "present_address_proof", "present_street", "present_street2",
        "present_city", "present_state", "present_zip", "present_country", "present_address_attachment",

        # Permanent
        "permanent_address_type", "permanent_address_proof", "permanent_street", "permanent_street2",
        "permanent_city", "permanent_state", "permanent_zip", "permanent_country", "permanent_address_attachment",

        # Checkbox
        "address_same_as_present"
    ],
    'academic_fields': ['academic_date', 'academic_type', 'academic_topic'],
    'course_fields': [
        'course_name',
        'course_start_date',
        'course_duration',
        'course_institution'
    ],
    "defense_fields": [
        "defense_designation",
        "defense_institution",
        "defense_from_date",
        "defense_to_date",
        "defense_experience",
        "defense_attachment"
    ],
    "mci_fields": [
        # MCI/NMC Inspection
        "mci_subject",
        "mci_designation",
        "mci_college",
        "mci_dates",
        "mci_attachment",

        # MCI/NMC Assessment
        "mci_level",
        "mci_assess_college",
        "mci_same_college",
        "mci_same_designation",
        "mci_retired_govt",
        "mci_retired_designation"
    ],
    "publication_fields": [
        "publication_title",
        "publication_journal",
        "publication_research_type",
        "publication_books",
        "publication_chapters",
        "publication_authorship",
        "publication_date",
        "publication_index_agency",
        "publication_attachment",
    ],
    "research_fields": [
        "research_title",
        "research_body",
        "research_principal",
        "research_coprincipal",
        "research_journal_type",
        "research_date_of_publication",
        "research_attachment"

    ],
    "salary_fields": [
        "salary_month",
        "salary_year",
        "amount_received",
        "tds"
    ],
    "current_appointment_fields": [
        "appointment_order",           # Yes/No
        "department",                  # Drop Down
        "present_designation",        # Drop Down
        "college_institute",          # Drop Down
        "city",                        # Drop Down
        "district",                    # Drop Down
        "appointment_type",           # Drop Down
        "date_of_joining",            # Date Picker
        "current_ctc",                # Text
        "joining_report",             # Yes/No
        "working_hours",              # Drop Down
        "current_appointment_attachment"  # File Upload (single)
    ],
    "other_activities_fields": [
        "other_information",
        "awards",
        "computer_knowledge",
        "presentation_type",
        "conference_type",
        "presentation_details",
        "attended_at_mci_rc",
        "attended_at_college",
        "met_certificates_attachment"
    ]


    # You can later add other sections like:
    # 'experience': [...],
    # 'qualification': [...],
    # etc.
}



form_config = {
    "personal": {
        "field_name_map": {
            "Name Prefix" : "name_prefix",
            'Name(Is in Degree certificate)': 'name_(as_in_degree_certificate)',
            'Employee ID': 'user_id',
            'Mobile Number' : 'mobile_number',
            'Email ID' : 'email_id',
            'S/o D/o W/o': 's/o_d/o_w/o',
            'PAN Number & Attachment': 'pan_number',
            'AADHAR Number & Attachment': 'aadhar_number',
            'Spouse/Father Contact No.': 'contact_number_guardian',
            'Total No. of Children': 'total_no_of_children'
        },
        "dropdowns": {
            'name_prefix': ['Dr.','Test Dr.'],
            's/o_d/o_w/o': ['S/o', 'D/o', 'W/o'],
            'gender': ['Male', 'Female', 'Other'],
            'marital_status': ['Single', 'Married', 'Widowed', 'Other'],
            'nationality': ['Indian'],
            'community': ['BC', 'MBC', 'SC', 'ST', 'OC'],
            "country_codes": ['+91', '+1', '+44', '+61', '+81', '+971', '+86', '+49', '+33' ]
        },

    },

    # Example placeholder for other sections
    "experience": {
        "field_name_map": {},
        "dropdowns": {}
    },
        "qualification": {
        "field_name_map": {},
        "dropdowns": {
            "qualification": ["MBBS", "MD", "MS", "DM", "MCh", "PhD"],
            "specialization": ["General Medicine", "Orthopedics", "ENT"],
            "college": ["AIIMS", "JIPMER"],
            "university": ["Delhi University"],
            "state_medical_council": ["Tamil Nadu", "Maharashtra", "Delhi"]
        }
    },
    "address" :  {
        "field_name_map": {},
        "dropdowns": {
            "address_type": ["Aadhar Card", "Pan Card", "Staff Address", "Other"]
        }
    },
    "research": {
            "field_name_map": { },
            "dropdowns": {
                "research_journal_type": [
                    "-- Select --",
                    "International Journals",
                    "National Journals",
                    "State / Institutional Journals"
                ]
            }
        },
    "current_appointment": {
            "field_name_map": { },
            "dropdowns": {
                "department" : ["General Medicine","Cardiology","Neurology"],
                "present_designation" : ["Junior Resident","Senior Resident","Chief Consultant","Medical Superintendent"],
                "college_institute" : ["C1","C2","Others"],
                "city" : ["chennai","salem","Others"],
                "district" : ["chennai","salem","Others"],
                "appointment_type": [
                    "Full Time",
                    "Contract",
                    "Visiting",
                    "Part Time"
                ],
                "working_hours": [
                    "08:00 A.M. to 04:00 P.M.",
                    "09:00 A.M. to 05:00 P.M."
                ]
            }
        },
    "other_activities": {
        "field_name_map": {},
        "dropdowns": {
            "presentation_type": [
                "Oral",
                "Poster"
            ],
            "conference_type": [
                "Zonal Conference",
                "State Conference",
                "National Conference",
                "International Conference"
            ]
        }
    }

}

