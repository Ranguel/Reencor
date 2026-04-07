class EntityIdGenerator:
    _next_id = 1

    @classmethod
    def next(cls):
        i = cls._next_id
        cls._next_id += 1
        return i
