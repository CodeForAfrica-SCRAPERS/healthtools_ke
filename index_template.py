template = """
 {"type": "add",
  "id":   "%s",
  "fields": {
      "address": "%s",
      "facility": "%s",
      "name": "%s",
      "practice_type": "%s",
      "qualification": "%s",
      "registration_date": "%s",
      "registration_number": "%s",
      "specialty": "%s",
      "sub_specialty": "%s",
      "type": "%s"
  }
 }
"""

delete_template = '{"type": "delete","id":"%s"}'

health_facilities_template = """
    {"type": "add",
     "id":   "%s",
     "fields": {
              "name": "%s",
              "facility_type_name": "%s",
              "approved": "%s",
              "sub_county_name": "%s",
              "service_names": "%s",
              "county_name": "%s",
              "open_public_holidays": "%s",
              "keph_level_name": "%s",
              "open_whole_day": "%s",
              "owner_name": "%s",
              "constituency_name": "%s",
              "regulatory_body_name": "%s",
              "operation_status_name": "%s",
              "open_late_night": "%s",
              "open_weekends": "%s",
              "ward_name": "%s"
            }
     }"""
