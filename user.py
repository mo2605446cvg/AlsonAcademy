class User:
    def __init__(self, code, username, department, division, role):
        self.code = code
        self.username = username
        self.department = department
        self.division = division
        self.role = role

    @classmethod
    def from_json(cls, data):
        return cls(data['code'], data['username'], data['department'], data['division'], data['role'])