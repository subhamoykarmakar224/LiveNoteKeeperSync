from firebase import firebase
from Configuration import *


def insertData(data):
    firebaseDB = firebase.FirebaseApplication(dbUrl, None)
    result = firebaseDB.post(TABLE_NOTES, data)
    return result


def editNode(id, note, v, dm):
    firebaseDB = firebase.FirebaseApplication(dbUrl, None)
    firebaseDB.put(TABLE_NOTES + '/' + str(id).strip(" "), 'note', note)
    firebaseDB.put(TABLE_NOTES + '/' + str(id).strip(" "), 'hashval', v)
    firebaseDB.put(TABLE_NOTES + '/' + str(id).strip(" "), 'lastchanged', dm)


def deleteNote(id, dm):
    firebaseDB = firebase.FirebaseApplication(dbUrl, None)
    firebaseDB.delete(TABLE_NOTES, str(id).strip(" "))


def getAllDataCount():
    result = {}
    firebaseDB = firebase.FirebaseApplication(dbUrl, None)
    result = firebaseDB.get(TABLE_NOTES, '')
    return result


# if __name__ == '__main__':
#     print(getAllDataCount())


# add new data
# result = firebaseDB.post(TABLE_STUDENTS, data)
# print(result)

# Get data
# result = firebaseDB.get(TABLE_ARTISTS, '')
# print(result)

# Update data
# firebaseDB.put(TABLE_STUDENTS + '/' + '-M4tLLj1P6YpBBqLc4xC', 'Name', 'Sam Furgason')
# firebaseDB.put(TABLE_ARTISTS + '/' + '-M4rGLjqQl_gynrukCqI', 'artistName', 'Argha Banerjee')

# Delete Data
# firebaseDB.delete(TABLE_STUDENTS, '-M4tLLj1P6YpBBqLc4xC')