class User():
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email

# should be seprate out to a class
class LineUser(User):
    DEFAULT_PICTURE_URL = 'http://icons.iconarchive.com/icons/graphicloads/flat-finance/256/person-icon.png'
    
    def __init__(self, user_id, name, email, gender,  phone_number, picture_url = DEFAULT_PICTURE_URL):
        User.__init__(self, user_id, name, email)
        self.gender = gender
        self.phone_number = phone_number
        self.picture_url = picture_url