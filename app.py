# -*- coding: cp1252 -*-
import time
import sqlite3
import HTMLParser
from flask import Flask, render_template,json, redirect, session, request
from flaskext.mysql import MySQL
from datetime import date, timedelta
from contextlib import closing


app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=60)

#my database access conf
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lenDB18*ApP'
app.config['MYSQL_DATABASE_DB'] = 'adneomblog'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Default setting
pageLimit = 5

#my app route in the url

@app.errorhandler(404)
def page_not_found(err):
    return render_template('error.html',error = "Page not found")

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/post')
def samplepost():
    return render_template('post.html')

@app.route("/post/<string:title>/")
def getPostById(title):
    try:
        # All Good, let's call the MySQL
            with closing(mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:
                    #connect to mysql
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.callproc('sp_GetPostById',(title,))
                    result = cursor.fetchall()
                    
                    title =result[0][1]
                    subtitle=result[0][2]
                    author =result[0][3]
                    _when=result[0][6].date().strftime("%a, %d %b %Y")
                    content = result[0][4]
                    
            return render_template('blogpost.html',**locals()) # on passe nos variables locales dans la requete post coté client
    except Exception as e:
        return render_template('error.html',error = "Page not found")

@app.route('/admin')
def adminLogin():
    if session.get('user'):
        return redirect('admin/home')
    else:
        return render_template('admin/templates/signIn.html')
    
@app.route('/admin/home')
def adminHome():
    if session.get('user'):
        return render_template('admin/templates/index.html')
    else:
        return redirect('/admin')

@app.route('/admin/createpost')
def createPost():
    if session.get('user'):
        today = date.today() # recuperer la date du jour
        return render_template('admin/templates/addpost.html', **locals()) # on passe nos variables locales dans la requete post coté client
    else:
        return redirect('/admin')
    
@app.route('/logout')
def logout():
    session.pop('user',None) #supp la variable de connection
    return redirect('/admin')


#my app method GET
@app.route('/getAllPosts')
def getAllPosts():
    try:
         with closing(mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.callproc('sp_GetAllPost')
                    result = cursor.fetchall()
                    blogposts_dict = []
                    for blogpost in result:
                        blogpost_dict = {
                                'Id': blogpost[0],
                                'Title': blogpost[1],
                                'Subtitle': blogpost[2],
                                'Author': blogpost[3],
                                'Date': blogpost[4].date().strftime("%a, %d %b %Y")}
                        blogposts_dict.append(blogpost_dict)
                    return json.dumps(blogposts_dict)
    except Exception as e:
        return render_template('admin/templates/error.html',error = str(e))
         
    

#get all blog post from admin page
@app.route('/getBlogPostOld')
def getBlogPostOld():
    try:
        if session.get('user'):
            _user = session.get('user')
 
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetBlogByUser',(_user,))
            blogPosts = cursor.fetchall()
 
            blogPosts_dict = []
            for blogPost in blogPosts:
                blogPost_dict = {
                        'Id': blogPost[0],
                        'Title': blogPost[1]}
                blogPosts_dict.append(blogPost_dict)
            return json.dumps(blogPosts_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))



#my app method post
    
#get all blog post from admin page
@app.route('/getBlogPost', methods=['POST'])
def getBlogPost():
    try:
        if session.get('user'):
            _user = session.get('user')
            _limit = pageLimit
            _offset = request.form['offset']
            _total_records = 0
 
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetBlogByUser',(_user,_limit,_offset,_total_records))
            blogPosts = cursor.fetchall()
            cursor.close()

            cursor = con.cursor()
            cursor.execute('SELECT @_sp_GetBlogByUser_3')
            outParam = cursor.fetchall()

            response = []
            blogPosts_dict = []
            for blogPost in blogPosts:
                blogPost_dict = {
                        'Id': blogPost[0],
                        'Title': blogPost[1]}
                blogPosts_dict.append(blogPost_dict)

            response.append(blogPosts_dict)
            response.append({'total':outParam[0][0]})
            print(response)
            return json.dumps(response)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e)) # a ne pas faire -> fuite d'information serveurs utile pour un attaquant 

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:

    #recuperer les parametres de connexions
        _useremail = request.form['inputEmail']
        _password = request.form['inputPassword']
        
    # validate the received values
        if _useremail and _password:

            # All Good, let's call the MySQL

            with closing(mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:

                    #connect to mysql
                        con = mysql.connect()
                        cursor = con.cursor()
                        cursor.callproc('sp_validateLogin',(_useremail,))
                        data = cursor.fetchall()
                        
                        if len(data) > 0:
                            #Verifier les informations sur le serveur
                            if _password == str(data[0][2]):
                                #rediriger les infos sur si Ok et cree ne variable de session
                                session.permanent = True
                                session['user'] = data[0][0]
                                return redirect('/admin/home')
                            else:
                                return redirect('/admin')

    except Exception as e:
        return redirect('/admin')


@app.route('/addPost',methods=['POST'])
def addPost():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _subtitle = request.form['inputSubtitle']
            _author = request.form['inputAuthor']
            _content = request.form['inputContent']
            _user = session.get('user')
            
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addPost',(_title,_subtitle,_author,_content,_user))
            data = cursor.fetchall()
            print(data)
            if len(data) is 0:
                conn.commit()
                return redirect('/admin/home')
            else:
                return render_template('error.html',error = 'An error occurred!')
 
        else:
            return render_template('admin/templates/error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('admin/templates/error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getBlogPostById',methods=['POST'])
def getBlogPostById():
    try:
        if session.get('user'):
 
            _id = request.form['id']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetBlogPostById',(_id,_user))
            result = cursor.fetchall()
 
            blogPost = []
            blogPost.append({'Id':result[0][0],'Title':result[0][1],'Subtitle':result[0][2],'Author':result[0][3],'Content':result[0][4]})
 
            return json.dumps(blogPost)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/updateBlogPost', methods=['POST'])
def updateBlogPost():
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _subtitle = request.form['subtitle']
            _author = request.form['author']
            _content = request.form['content']
            _post_id = request.form['id']

            with closing(mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:

                    #connect to mysql
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.callproc('sp_updateBlogPost',(_title,_subtitle,_author,_content,_post_id,_user))
                    data = cursor.fetchall()
 
                    if len(data) is 0:
                        conn.commit()
                        return json.dumps({'status':'OK'})
                    else:
                        return json.dumps({'status':'ERROR'})
    except Exception as e:
        return json.dumps({'status':'Unauthorized access'})


@app.route('/deleteBlogPost',methods=['POST'])
def deleteBlogPost():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteBlogPost',(_id,_user))
            result = cursor.fetchall()
 
            if len(result) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(port=5002)
