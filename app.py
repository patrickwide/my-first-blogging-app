from flask import Flask,render_template,request,redirect,session
#import pymysql
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import re
#import pandas as pd

app = Flask(__name__)
app.secret_key = "ssfks6787"#just a rundom string of characters.


UPLOAD_FOLDER = "static/img"
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    if "username" in session:
        logout = "logout"
        style_logout = "btn btn-secondary"
        return render_template("index.html",logout = logout,style_logout = style_logout )
    else:
        login = "login"
        register = 'register'
        style_login = "btn btn-success"
        style_register = "btn btn-primary"
        return render_template("index.html",login = login,register = register,style_register = style_register,style_login = style_login)


@app.route("/user_check",methods=['POST','GET'])
def userCheck():
    if "username" in session:
        blogger = str(session['blogerName'])
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM blog_posts WHERE post_by=%s ORDER BY blog_id DESC"
        cur.execute(sql,(blogger))
        if (cur.rowcount >= 1):
           return render_template("profile.html", result=cur.fetchall(),login=loginCheck(),style_logout=styleCheck(),register=registerEliminate(),style_register=styleRegister(),blogger =  session['blogerName'])
        else:
           return render_template('no_posts.html', result="No blog Found",login=loginCheck())
    else:
        return render_template("login.html",login=loginCheck(), style_logout=styleCheck(),register=registerEliminate(), style_register=styleRegister())


@app.route('/gallery',methods=['POST','GET'])
def gallery():
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM blog_posts ORDER BY blog_id DESC"
    cur.execute(sql)
    if(cur.rowcount >= 1):
        return render_template("gallery.html",result = cur.fetchall())
    else:
        return render_template('gallery.html',result = "No blog Found")
def viewBlogWriter():

    prod_id = request.args.get("user")
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM blog_posts WHERE post_by=%s"
    cur.execute(sql,(prod_id))
    if (cur.rowcount >= 1):
        results = cur.fetchall()
        name = results[0][5]
        return str(name)
    else:
        results = cur.fetchall()
        name = results[0][5]
        return str(name)


@app.route("/view_blogs",methods=['POST','GET'])
def viewBlogs():
    prod_id = request.args.get("user")
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM blog_posts WHERE post_by=%s ORDER BY blog_id DESC"
    cur.execute(sql,(prod_id))
    if (cur.rowcount >= 1):
        return render_template("view_blogs.html",result = cur.fetchall(),name = viewBlogWriter())

    elif (cur.rowcount < 1):
        cur.close()
        msg="you have no Blogs"
        return render_template("/user_check",msg2=msg)



@app.route("/view_img",methods=['POST','GET'])
def viewImg():
    prod_id = request.args.get("id")
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM blog_posts WHERE blog_id = %s"
    cur.execute(sql,(prod_id))
    if (cur.rowcount >= 1):
        return render_template("view_img.html",result = cur.fetchall())
    elif (cur.rowcount < 1):
        msg = "sorry!!!, The image could NOT be found"
        return render_template("view_img.html",msg=msg)

def loginCheck():
    if "username" in session:
        return "logout"
    else:
        return "login"

def styleCheck():
    if "username" in session:
        return "btn btn-secondary"
    else:
        return "btn btn-success"
def registerEliminate():
    if "username" in session:
        return ""
    else:
        return "register"

def styleRegister():
    if "username" in session:
        return ""
    else:
        return "btn btn-primary"



@app.route('/home',methods=['POST','GET'])
def home():
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM blog_posts ORDER BY blog_id DESC"
    cur.execute(sql)
    if(cur.rowcount >= 1):
        return render_template("home.html",result = cur.fetchall(),login=loginCheck(),style_logout=styleCheck(),register=registerEliminate(),style_register=styleRegister())
    else:
        return render_template('home.html',result = "No blog Found",login=loginCheck(),style_logout=styleCheck(),register=registerEliminate(),style_register=styleRegister())



@app.route("/profile")
def profile():
    return render_template("/user_check")



@app.route("/delete-blog",methods=['POST','GET'])
def deleteProduct():
    if "username" in session:
        id = request.args.get('id')
        username = str(session['blogerName'])
        conn = makeConnection()
        cur = conn.cursor()
        check_sql = "SELECT `image_path` FROM `blog_posts` WHERE post_by = %s AND blog_id = %s"
        check_cur = conn.cursor()
        check_cur.execute(check_sql,(username,id))
        if (check_cur.rowcount>=1):
            prev_image = check_cur.fetchone()
            if os.path.exists(UPLOAD_FOLDER+'/'+prev_image[0]):
                os.remove(UPLOAD_FOLDER+'/'+prev_image[0])
        sql = "DELETE FROM `blog_posts` WHERE post_by = %s AND blog_id = %s "
        cur.execute(sql, (username, id))
        conn.commit()
        return redirect("/user_check")
    else:
        return render_template("index.html")

@app.route("/update-blog",methods=['POST','GET'])
def updateBlog():
    if "username" in session:
        blogger = str(session['blogerName'])
        prod_id = request.args.get('id')
        username = str(session['blogerName'])
        conn = makeConnection()
        cur = conn.cursor()
        sql = "SELECT * FROM blog_posts WHERE post_by=%s AND blog_id=%s"
        cur.execute(sql,(username,prod_id))
        if (cur.rowcount == 1):
            return render_template("update-blog.html",blogger=blogger,result=cur.fetchall())
            #return render_template('update-blog.html',result=cur.fetchall())
        else:
            return redirect("index.html")
    else:
        return render_template("index.html")

@app.route("/perform-update",methods=['POST','GET'])
def performUpdate():

    if request.method == "POST":
        title = str(request.form["title"])
        blog_content = str(request.form["blog_content"])
        blog_id = str(request.form['id'])
        prev_img = str(request.form['prev_img'])
        file = request.files['my_image']
        myFilename = secure_filename(file.filename)
        if title == "" or blog_content == "":
            return redirect('/update-blog?id='+blog_id)
        else:
            if myFilename == "":
                conn = makeConnection()
                cur = conn.cursor()
                sql = "UPDATE blog_posts SET title=%s,blog_content=%s WHERE blog_id=%s"
                cur.execute(sql,(title,blog_content,blog_id))
                conn.commit()
                return redirect("/user_check")

            else:
                if os.path.exists(UPLOAD_FOLDER+'/'+prev_img):
                    os.remove(UPLOAD_FOLDER+'/'+prev_img)
                    conn = makeConnection()
                    cur = conn.cursor()
                    sql = "UPDATE blog_posts SET title=%s,blog_content = %s,image_path = %s WHERE `blog_id`=%s"
                    cur.execute(sql,(title,blog_content,myFilename,blog_id))
                    conn.commit()
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"],myFilename))
                    return redirect("/user_check")
                else:
                    conn = makeConnection()
                    cur = conn.cursor()
                    sql = "UPDATE blog_posts SET title=%s,`blog_content`=%s,image_path=%s WHERE blog_id=%s"
                    cur.execute(sql,(title,blog_content,myFilename,blog_id))
                    conn.commit()
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"],myFilename))
                    return redirect('/user_check')
    else:
        return "hello am not working"





























@app.route("/register",methods =["POST","GET"])
def register():
    return render_template("register.html")





@app.route("/add_user_to_db",methods =["POST","GET"])
def addUsers():
    if request.method == "POST":
        fname = str(request.form["fname"])
        lname = str(request.form["lname"])
        username = str(request.form["username"])
        phone = str(request.form["phone"])
        email = str(request.form["email"])
        password_1 = str(request.form["password_1"])
        password_2 = str(request.form["password_2"])


        if fname == "" or lname == "" or username =="" or phone == "" or email == "" or password_1 == "" or password_2 == "" :
            msg = "please ensure you fill all the fields"
            return render_template("register.html",msg1 = msg)
        if password_1 != password_2:
            msg = "please check your passwords"
            msg1 = "please check this field"
            return render_template("register.html",msg1 = msg,msg_pass = msg1)

        else:

            conn = makeConnection()
            cur = conn.cursor()
            check_sql = "SELECT email FROM users WHERE email=%s"
            check_phone = "SELECT phone FROM users WHERE phone=%s"
            check_userName = "SELECT username FROM users WHERE username=%s"
            cur_phone = conn.cursor()
            cur_username = conn.cursor()
            cur.execute(check_sql,(email))
            cur_phone.execute(check_phone, (phone))
            cur_username.execute(check_userName,(username))


            if cur.rowcount >= 1:
                msg = f"The email ({(email)}) is in use, please try using another email"
                return render_template("register.html",msg2 = msg)

            elif cur_phone.rowcount >= 1:
                msg = f"the phone number ({(phone)}) is in use, please try using another phone number"
                return render_template("register.html",msg2 = msg)


            elif cur_username.rowcount >= 1:
                msg = f"the username ({(username)}) is in use please try using another username,you can try combining your name with a unique number"
                return render_template("register.html",msg2 = msg)



            else:
                sql = "INSERT INTO users(fname,lname,phone,username,email,password_1,password_2) values(%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(sql,(fname,lname,phone,username,email,password_1,password_2))
                conn.commit()
                msg = "YOU REGISTERED SUCCESSFULLY, PLEASE LOGIN"
                return render_template("login.html",msg2 = msg)


    else:
        #if all the info code is not meet the we will be returend to the same page
        return render_template("register.html",)


@app.route("/login",methods=["POST","GET"])
def login():
    return render_template("login.html")

@app.route("/login-user",methods=["POST","GET"])
def loginUsers():
    if request.method == "POST":
        email = str(request.form["email"])
        password = str(request.form["password"])
        email_run = forEmail()
        phone_run = forPhone()

        if email == "" or password == "":
            msg = "please ensure no field is emppty"
            return render_template("login.html",msg1 = msg)

        if len(re.findall("[\w._%+-]{2,20}@[\w.-]{2,20}.[A-Za-z]{2,3}",email)):
            return email_run

        if len(re.findall("[0-9]{10,11}",email)):
            return phone_run

        else:
            msg = "please check your phone/email"
            return render_template("login.html",msg1 = msg)
    else:
        return render_template()



def forEmail():
    email = str(request.form["email"])
    password = str(request.form["password"])
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM users WHERE email = %s AND password_2 = %s"
    cur.execute(sql, (email, password))

    if cur.rowcount >= 1:
        results = cur.fetchall()
        session['blogerName'] = results[0][3]
        session['username'] = email
        return redirect("/user_check")
    else:

        msg = "the email combination is incorrect"
        return render_template("login.html", msg1=msg)

def forPhone():
    email = str(request.form["email"])
    password = str(request.form["password"])
    conn = makeConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM users WHERE phone = %s AND password_2 = %s"
    cur.execute(sql, (email, password))
    if cur.rowcount >= 1:
        results = cur.fetchall()
        session['blogerName'] = results[0][3]
        session['username'] = email
        return redirect("/user_check")
    else:
        msg = "the phone combination is incorrect"
        return render_template("login.html", msg1=msg)


@app.route("/logout",methods =['POST','GET'])
def logoutUser():
    session.pop("username", None)
    return redirect("/")


@app.route('/add_blog',methods=['POST','GET'])
def addblog():
    if request.method == "POST":
        blogger = session['blogerName']
        post_by = str(blogger)
        title = str(request.form['title'])
        file = request.files['my_image']
        blog_content = str(request.form['blog_content'])
        myFilename = secure_filename(file.filename)

        if title == "" or blog_content == "" or myFilename == "" or post_by == "":
            msg = "Please ensure no field is empty"
            return redirect("/user_check")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO blog_posts(title,blog_content,image_path,post_by)VALUES(%s,%s,%s,%s)"
            cur.execute(sql,(title,blog_content,myFilename,post_by))
            conn.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], myFilename))


            return redirect("/user_check")
    else:
        return redirect('/home')
@app.route("/repost",methods=['POST','GET'])
def repost():

    if request.method == "POST":
        title = str(request.form['title'])
        file = request.files['my_image']
        blog_content = str(request.form['blog_content'])
        myFilename = secure_filename(file.filename)
        if title == "" or blog_content == "" or myFilename == "":
            return render_template("repost.html",msg="Ensure no field is empty")
        else:
            conn = makeConnection()
            cur = conn.cursor()
            sql = "INSERT INTO blog_posts(title,blog_content,image_path)VALUES(%s,%s,%s)"
            cur.execute(sql,(title,blog_content,myFilename))
            conn.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], myFilename))
            return render_template("repost.html",msg="Blog Added Successfully")
    else:
        return render_template("repost.html")






def makeConnection():
    host = "127.0.0.1"
    user = "root"
    password = ""
    database = "blog_db"#This is the name of my database
    return pymysql.connect(host,user,password,database)


if __name__ == "__main__":
    app.run(debug=True,port=2000)