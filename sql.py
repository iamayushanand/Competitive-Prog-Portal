import sqlite3


# A clean function to prevent SQL injections.
def clean(string):
    return string.replace("'", '').replace('"', '')


class Column:
    def __init__(self, name, type, primary_key=False, not_null=True):
        self.name = name
        self.type = type
        self.primary_key = primary_key
        self.not_null = not_null

    def __str__(self):
        out = f'''{self.name} {self.type}'''
        if self.primary_key:
            out += " PRIMARY KEY"
        if self.not_null:
            out += " NOT NULL"
        return out


class Database:

    def __init__(self, database: str):
        self.conn = sqlite3.connect(database,check_same_thread=False)
        self.c = self.conn.cursor()


class Table:
    def __init__(self, database, name, columns: list):
        self.name = name
        self.columns = columns
        self.db = database
        try:
            self.db.c.execute(f'''SELECT * FROM {self.name}''')
        except sqlite3.OperationalError:
            self.db.c.execute(f'''CREATE TABLE {self.name} ( {self.get_def()})''')
    
    def get_columns(self):
        return [col.name for col in self.columns]
    
    def get_def(self):
        return ", ".join(map(lambda col: str(col), self.columns))
    
    def get(self, id_str, columns: str = '*'):

        self.db.c.execute(
            clean(
                "SELECT {0} FROM {1} WHERE id=:id".format(
                    columns, self.name)), {'id': id_str})
        return self.db.c.fetchone()

    def get_all(self, columns: str = '*'):
        self.db.c.execute(
            clean(
                "SELECT {0} FROM {1}".format(columns, self.name))
        )
        return self.db.c.fetchall()

    def add_element(self, id_str, values: dict = None):
        if values is None:
            values = {}

        values['id'] = id_str
        for column in self.columns:
            if column.name not in values:
                values[column.name] = 0  # sets default value 0

        with self.db.conn:
            self.db.c.execute(
                clean(
                    "INSERT INTO {0} VALUES {1}".format(
                        self.name,
                        tuple(map(lambda col: ':' + col, self.get_columns()))
                    )),
                values
            )
        return values

    def update(self, id_str, values: dict):
        values['id'] = id_str

        with self.db.conn:
            self.db.c.execute(
                clean(
                    "UPDATE {0} SET {1} WHERE id=:id".format(
                        self.name,
                        ", ".join(map(lambda col: col + ' = :' + col, values))
                    )),
                values
            )
        return values
    def delete(self, id_str):

        with self.db.conn:
            self.db.c.execute(
                clean(
                    f"DELETE from {self.name} where id = {id_str};"
                ))


"""db = Database('data.db')
user = Table(db, 'user',[
    Column('id', 'INTEGER'),
    Column('name', 'STRING'),
    Column('score','STRING')
])""" 
#user.add_element(1,{'name': "manav",'score':'10'})
#print(user.get_all())
#print(user.get(1)[2])
#user.update(1,{'name': "manav kapoor"})
#user.delete(1)
