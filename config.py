
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
registrar_pass = "12345"
doctor_pass = "1234"
SECRET_KEY = "askmdhwhcdcmslcmdclacmkckdccmcndclcdncddncdcdcbjssvubc"

def parse_int(value):
        if value in (None, "", " "):
            return None
            
        else:
            if value.isdigit():
                return int(value)
            else:
                return value