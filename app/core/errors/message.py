class MessageNotFoundError(Exception):
    def __init__(self, message_id: str):
        self.message_id = message_id
        self.message = f"Message {message_id} not found"
        super().__init__(self.message)
