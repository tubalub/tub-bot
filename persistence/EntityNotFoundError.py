class EntityNotFoundError(Exception):
    def __init__(self, query: str, message: str = None):
        self.query = query
        self.message = message if message else f"Entity not found for query: {query}"
        super().__init__(self.message)
