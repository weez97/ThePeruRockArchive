from flask import Flask, jsonify, request, render_template,session,url_for,redirect
from flask_cors import CORS
from flaskext.mysql import MySQL
import pymysql


# configuration
DEBUG = True


# initiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "super secret key"

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'amiguitos23'
app.config['MYSQL_DATABASE_DB'] = 'MUSICA'
app.config['MYSQL_DATABASE_HOST'] = '3.86.219.96'
app.config['SESSION_TYPE'] = 'filesystem'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
# enable CORS
CORS(app, resources={r'/*':{'origins': '*'}})
@app.route('/')
def home():
    return render_template('index.html',logged_in=False)

@app.route('/index')
def index():
    if session['loggedin']:
     return render_template('index.html',logged_in=session['loggedin'],user=session['username'])
    else:
      return render_template('index.html',logged_in=session['loggedin']  )
    


@app.route('/login', methods =['GET', 'POST'])
def login():

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM Usuario WHERE username = % s AND password = % s', (username, password, ))
        account=cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username']=username
            session['id']=account[0]
            
            return redirect(url_for("index"))
        else:
            return render_template('signIn.html')
    else:
        return render_template('signIn.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
  
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        sql = "INSERT INTO Usuario (name, username, password, email) VALUES (%s,%s, %s, %s)"
        val = (name,username, password, email)
        cursor.execute(sql, val)
        conn.commit()
        return redirect(url_for("index"))
    else:
        return render_template('register.html')
    

@app.route("/logout")
def logout():
    session.pop("username", None)
    session['loggedin']=False
    return redirect(url_for("index"))

#list artists
@app.route('/newArtists', methods=['GET'])
def get_newArtists():

    cursor.execute("SELECT NArtista,TBiografia from Artista")
    artist_list = cursor.fetchall()
    cursor.close()
    conn.close()

    if session['loggedin']:
        return render_template('newArtist.html', artist_list=artist_list,logged_in=session['loggedin'],user=session['username'])
    else: 
        return render_template('newArtist.html', artist_list=artist_list,logged_in=session['loggedin'])

#add new artists
@app.route('/submit/newArtist', methods=['GET', 'POST'])
def add_newArtist():

    if session['loggedin']:
        
        if request.method == 'POST':
            artistName = request.form['artistName']
            bio = request.form['bio']
            artist_q_album = 0
            #image=request.files['image'].read()
            image=None
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Artista (NArtista, TBiografia, QAlbumnes,image) VALUES (%s, %s, %s, %s)", (artistName, bio, artist_q_album,image))
            conn.commit()
            return redirect(url_for("get_newArtists"))
        else:
            return render_template('addArtist.html',user=session['username'])
    else:
         return redirect(url_for("login"))
       

@app.route('/favorites', methods=['GET'])
def favorites():

    cursor.execute("SELECT Canciones.NCancion, Canciones.QDuration,Artista.NArtista,FavCancion.id from FavCancion INNER JOIN Canciones ON Canciones.CCancion = FavCancion.CCancion INNER JOIN Album ON Canciones.CAlbum=Album.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE FavCancion.id_usuario =%s",(session['id']))
    song_list=cursor.fetchall()

    cursor.execute("SELECT Album.NAlbum, Artista.NArtista,FavAlbum.id from FavAlbum INNER JOIN Album ON Album.CAlbum= FavAlbum.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE FavAlbum.id_usuario =%s",(session['id']))
    album_list=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('favorites.html',song_list=song_list,user=session['username'],album_list=album_list)

@app.route('/delete/<id>',  methods=['POST','DELETE'])
def delete_FavoriteSong(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM FavCancion WHERE id=%s",(id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("favorites"))

@app.route('/deleteAlbum/<id>',  methods=['POST','DELETE'])
def delete_FavoriteAlbum(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM FavAlbum WHERE id=%s",(id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("favorites"))

@app.route('/add/<id>',  methods=['POST'])
def add_FavoriteSong(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO FavCancion(CCancion,id_usuario) VALUES (%s,%s)",(id,session['id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("favorites"))


@app.route('/search', methods=['GET'])
def search():
    name = request.args.get('q')
    cursor.execute("SELECT Canciones.NCancion, Canciones.QDuration,Artista.NArtista,Canciones.CCancion from Canciones INNER JOIN Album ON Canciones.CAlbum=Album.CAlbum INNER JOIN Artista ON Album.CArtista=Artista.CArtista WHERE Canciones.NCancion=%s",name)
    song_list=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('search.html',song_list=song_list,user=session['username'])

@app.route('/artists/<myArtist>/albums', methods=['GET'])
def get_album_by_artist(myArtist):
    
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
