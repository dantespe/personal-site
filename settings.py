from google.appengine.ext import ndb
import os

class Settings(ndb.Model):
  name = ndb.StringProperty()
  value = ndb.StringProperty()

  @staticmethod
  def get(name):
    NOT_SET_VALUE = "NOT SET"

    try:
        retval = Settings.query(Settings.name == name).get()
    except:
        return os.environ.get(name, None)

    if not retval:
      retval = Settings()
      retval.name = name
      retval.value = NOT_SET_VALUE
      retval.put()

    if retval.value == NOT_SET_VALUE:
      raise Exception(('Setting %s not found in the database. A placeholder ' +
        'record has been created. Go to the Developers Console for your app ' +
        'in App Engine, look up the Settings record with name=%s and enter ' +
        'its value in that record\'s value field.') % (name, name))

    return retval.value
