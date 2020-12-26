class User:
    
    def __init__(self,id_str,name,email):
        self.id_str=id_str
        self.name=name
        self.email=email
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.id_str
