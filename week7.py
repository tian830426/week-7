#引入套件
from flask import Flask,request,render_template,redirect,session,url_for,make_response
import mysql.connector
import json
from flask import jsonify

app = Flask(__name__,
    static_folder="static",
    static_url_path="/")

#設定 session 密鑰
app.secret_key='tian12345'

# mysql.connector 引入方式
new = mysql.connector.connect(
  host="localhost",
  user="root",
  password="tian0426",
  database="signin" 
)
# index.route - index.html
@app.route('/')
def index():
    return render_template("index.html")

#index.html - signup.route
@app.route('/signup',methods=['POST'])
def signup():
    name = request.form['name']
    user = request.form['username']
    psw = request.form['password']
    mycursor = new.cursor()
    sql='SELECT username, password FROM member WHERE username = %(user)s'
    mycursor.execute(sql,{"user":user} )
    myresult = mycursor.fetchall() 
        
    if (mycursor.rowcount != 0) :
        return redirect("http://127.0.0.1:4000/error?message=帳號已經被註冊")
    else:
        mycursor = new.cursor()
        sql2='INSERT INTO member(name, username, password) VALUES(%s, %s, %s)'
        val=(name, user, psw)
        mycursor.execute(sql2,val)
        new.commit()
        return redirect('/')

#註冊後回到首頁 #index.html - signin.route
@app.route('/signin', methods =['POST'])
def signin():
    user = request.form['username']
    psw = request.form['password']
    session["username"]= user
    session["password"]= psw
    mycursor = new.cursor()
    sql='SELECT name, username, password FROM member WHERE username = %s and password = %s' 
    mycursor.execute(sql,(user,psw))
    myresult = mycursor.fetchall()

    if  mycursor.rowcount!=0 and myresult[0][1] == user and myresult[0][2] == psw:
        name = request.args.get("name","")       
        session['name'] = myresult[0][0]
        session['enter'] = 'open'
        return redirect(url_for("member")) 
    else:        
        return redirect("http://127.0.0.1:4000/error?message=帳號、或密碼輸入錯誤") 

#signin.route -  member.route
@app.route('/member')
def member():
    if "open" == session['enter']:
        name = session['name'] 
        return render_template("member.html",name = name)
    else:
        return redirect('/')

@app.route('/error')
def error():
    data = request.args.get('message',"")
    return render_template("error.html", data = data)
    
@app.route('/signout',)
def signout():
     session['enter'] = 'close'
     return redirect('/')

# week-7
@app.route('/api/member',methods=["PATCH","GET"])
def apply():
    if request.method == "GET":
        user = request.args.get('username')
        print("user:","123")
        mycursor = new.cursor()
        sql='SELECT id, name, username FROM member WHERE username = %(user)s'
        mycursor.execute(sql,{"user":user} )
        myresult = mycursor.fetchall()
        if (mycursor.rowcount != 0):
            data={"data":{
                "id":myresult[0][0],
                "name":myresult[0][1],
                "username":myresult[0][2]
            }}    
            return jsonify(data)
        else:      
            return jsonify({
                "data": None
            })
    else:
        entry=json.loads(request.data)
        name = session['name']
        print (name)
        new_name = entry["name"]
        mycursor = new.cursor()
        
        if new_name == "" or session['enter'] != "open":                  
            return jsonify({"error":True})
        else:
            sql = "UPDATE member set name = %s WHERE name = %s"
            mycursor.execute(sql, (new_name, name))
            myresult = mycursor.fetchone()
            new.commit() 
            return jsonify({"ok":True})

if __name__ == "__main__":
    app.run(port=4000,debug=True)


