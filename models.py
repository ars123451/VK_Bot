import pony.orm
from pony.orm import Json

from settings import DB_CONFIG

db = pony.orm.Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """user state inside the script"""
    user_id = pony.orm.Required(str, unique=True)
    scenario_name = pony.orm.Required(str)
    step_name = pony.orm.Required(str)
    context = pony.orm.Required(Json)


class Registration(db.Entity):
    """application for registration"""
    name = pony.orm.Required(str)
    email = pony.orm.Required(str)


db.generate_mapping(create_tables=True)
