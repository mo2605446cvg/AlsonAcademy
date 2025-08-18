class Content:
    def __init__(self, id, title, file_path, file_type, uploaded_by, department, division, upload_date, description):
        self.id = id
        self.title = title
        self.file_path = file_path
        self.file_type = file_type
        self.uploaded_by = uploaded_by
        self.department = department
        self.division = division
        self.upload_date = upload_date
        self.description = description

    @classmethod
    def from_json(cls, data):
        return cls(
            data['id'],
            data['title'],
            data['file_path'],
            data['file_type'],
            data['uploaded_by'],
            data['department'],
            data['division'],
            data['upload_date'],
            data['description']
        )