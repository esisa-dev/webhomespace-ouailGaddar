from service import UserService
import logging
from flask import(
    Flask,
    request,
    render_template,
    redirect,
    session,
    url_for,
)

app = Flask(__name__, template_folder='templates')
app.secret_key='1234'
@app.route('/')
def index():
    return render_template('login.html')
@app.route('/login',methods=['POST'])
def authentificat():
    name=request.form['nom']
    session['name']=name
    pwd=request.form['password']
    res=service_user.authentification(name,pwd)
    if res == True :
        path=f"/home/{name}"
        dicts_files=service_user.list_user_files_and_directories(path)
        return render_template('dashboard.html',directories=dicts_files)
    else :
        return render_template('login.html',error_user='authentificat failure')
@app.route('/browse/<directory>')
def browse_directory(directory):
    
    chemin_recuperer=service_user.toChemine(directory)
    
    chemin_concatener=chemin_recuperer+"/"+directory.split("-")[0].strip()

    result=service_user.isDirectroyOrfile(chemin_concatener)
    if result == "directory" :
        list_info=service_user.list_user_files_and_directories(chemin_concatener)
        return render_template('dashboard.html',directories=list_info)
    else :
        res=service_user.read_file(chemin_concatener)
        return render_template('view.html',file_content=res)
@app.route('/files')
def numberOfFiles() :
    name=session['name']
    res=service_user.count_files(name)
    return render_template('count.html',content=res,genre='fichiers')

@app.route('/Dirs')
def numberOfDirs() :
    name=session['name']
    res=service_user.count_directories_for_user(name)
    return render_template('count.html',content=res,genre='Directory')
@app.route('/Space')
def Space() :
    name=session['name']
    res=service_user.calculate_space_for_user(name)
    return f"la taille de l’espace occupé par l’utilisateur {name} est :{res}"
@app.route('/search')
def search():
    query = request.args.get('q')
    if '.' in query:
        file_parts = query.split('.')
        filenom = file_parts[0]
        extension = file_parts[1]
        list=service_user.find_files(username=session['name'],filename=filenom,extension=extension)
        return render_template('dashboard.html',directories=list)
    else :
        if query =='' :
            list=service_user.find_files(username=session['name'])
            return render_template('dashboard.html',directories=list)
        else :
            list=service_user.find_files(username=session['name'],filename=query)
            return render_template('dashboard.html',directories=list) 
@app.route('/download')
def telechagement() :
    name=session['name']
    service_user.download_directory(name)
    return f'home_{name} est bien telechargé ...'     
@app.route('/logout')
def logout() :
    session.pop('name')
    return render_template("login.html")
@app.route('/dashboard')
def dashboard() :
    path=f"/home/{session['name']}"
    dicts_files=service_user.list_user_files_and_directories(path)
    return render_template('dashboard.html',directories=dicts_files)
   
if __name__=='__main__':
    service_user=UserService()

    app.run(host="0.0.0.0",port=9080,debug=True)