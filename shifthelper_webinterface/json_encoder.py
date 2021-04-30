from flask.json import JSONEncoder
from datetime import date

class ISODateJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)

