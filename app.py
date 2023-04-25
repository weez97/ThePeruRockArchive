from flask import Flask, jsonify, request
from flask_cors import CORS
from flaskext.mysql import MySQL
import pymysql

# configuration
DEBUG = True

# initiate the app
app = Flask(__name__)
app.config.from_object(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'amiguitos23'
app.config['MYSQL_DATABASE_DB'] = 'MUSICA'
app.config['MYSQL_DATABASE_HOST'] = '18.204.219.189'
mysql.init_app(app)

# enable CORS
CORS(app, resources={r'/*':{'origins': '*'}})

# sanity check route
@app.route('/', methods=['GET'])
def welcome():
    return jsonify('Welcome to The Peru Rock Archive!')

@app.route('/artists', methods=['GET'])
def get_artists():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NArtista from Artista")
        artist_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'artist': artist_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/artists/<myArtist>/albums', methods=['GET'])
def get_album_by_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Album.NAlbum from Album JOIN Artista ON Album.CArtista = Artista.CArtista WHERE Artista.NArtista = %s", (myArtist))
        album_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'albums': album_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/artists/<myArtist>/songs', methods=['GET'])
def get_songs_by_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Canciones.NCancion, Canciones.QDuration, Album.NAlbum from Canciones JOIN Album ON Canciones.CAlbum = Album.CAlbum JOIN Artista ON Album.CArtista = Artista.CArtista WHERE Artista.NArtista = %s", (myArtist))
        song_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'songs': song_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()     

@app.route('/albums/<myAlbum>/songs', methods=['GET'])
def get_songs_by_album(myAlbum):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NCancion, QDuration FROM Canciones WHERE CAlbum = (SELECT CAlbum FROM Album WHERE NAlbum = %s)", (myAlbum))
        song_list = cursor.fetchall()
        return jsonify({
            'status': 'success',
            'songs': song_list
        })
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()   

@app.route('/submit/artist', methods=['GET', 'POST'])
def add_artist():
    conn = mysql.connect()
    cursor = conn.cursor()
    response_object = {'status' : 'success'}
    if request.method == 'POST':
        artist_name = request.json['artistName']
        artist_bio = request.json['artistBio']
        artist_q_album = 0
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Artista (NArtista, TBiografia, QAlbumnes) VALUES (%s, %s, %s)", (artist_name, artist_bio, artist_q_album))

        conn.commit()
        response_object['message'] = "Successfully Added!"
    return jsonify(response_object)

@app.route("/delete/<myArtist>", methods=['DELETE'])
def delete_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Artista WHERE NArtista = %s", (myArtist))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message':"Successfully deleted!"})

@app.route("/update/<myArtist>", methods=['PUT'])
def update_artist(myArtist):
    conn = mysql.connect()
    cursor = conn.cursor()
    artist_name = request.json['artistName']
    artist_bio = request.json['artistBio']
    if artist_bio is not '':
        cursor.execute("UPDATE Artista SET TBiografia = %s WHERE NArtista = %s", (artist_bio, myArtist))
    if artist_name is not '':
        cursor.execute("UPDATE Artista SET NArtista = %s WHERE NArtista = %s", (artist_name, myArtist))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Successfully modified!'})

if __name__ == '__main__':
    app.run(debug=True)
