class DotDict(dict):
    def __init__(self, dictionary):
        super().__init__(dictionary)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"config object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(f"config object has no attribute '{name}'")
