class Message:
    def __init__(self, id, content, sender_id, username, department, division, timestamp):
        self.id = id
        self.content = content
        self.sender_id = sender_id
        self.username = username
        self.department = department
        self.division = division
        self.timestamp = timestamp

    @classmethod
    def from_json(cls, data):
        return cls(
            data['id'],
            data['content'],
            data['sender_id'],
            data['username'],
            data.get('department', ''),
            data.get('division', ''),
            data['timestamp']
        )