from marshmallow import Schema, fields, validates_schema, ValidationError


class JobsSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    @validates_schema
    def validate_excel_file(self, data, **kwargs):
        if not data.get("end_date") < data.get("start_date"):
            raise ValidationError("End Date cannot be less that Start Date.")
