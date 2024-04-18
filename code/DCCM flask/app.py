import os
from flask import Flask, render_template, request, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pyrebase
from cryptography.fernet import Fernet
config={
  "apiKey": "AIzaSyAxuBZVataL7Nu87Rptv2pMCvF6IHYaLPo",
  "authDomain": "dccm-c824c.firebaseapp.com",
  "projectId": "dccm-c824c",
  "databaseURL": "",
  "storageBucket": "dccm-c824c.appspot.com",
  "messagingSenderId": "795066573501",
  "appId": "1:795066573501:web:52076aa9adb6a62a8f4dd4",
  "measurementId": "G-FTY8S2M80N"
}
firebase=pyrebase.initialize_app(config)
storage= firebase.storage()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///admin.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='20eg105430@anurag.edu.in'
app.config['MAIL_PASSWORD']='phani@2003'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)
db =SQLAlchemy(app)
# db.init_app(app)
class ADMIN(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(300), nullable=False)
    deadline=db.Column(db.Integer, nullable=False)
    content=db.Column(db.String(10000), nullable=False)
    key=db.Column(db.String(10000), nullable=False)
    encrypted_text= db.Column(db.String(10000), nullable=False)
    cost=db.Column(db.Integer, nullable=False)
    uploaded= db.Column(db.Boolean)
    requested= db.Column(db.Boolean)
    accepted=  db.Column(db.Boolean)
    

    def __repr__(self) -> str:
        return f"{self.sno}-{self.filename}"
class VMInstance:
    def __init__(self, name, cost_per_unit_time, compute_power):
        self.name = name
        self.cost_per_unit_time = cost_per_unit_time
       
        self.compute_power=compute_power
vm1 = VMInstance("Standard VM",3.35, 1000) 
vm2 = VMInstance("High Memory VM", 6.12, 2000) 
vm3 = VMInstance("High Performance VM",10.55, 4000)
vm4 = VMInstance("Highier Performance VM",13.27, 8000)
vm5 = VMInstance("Highest Performance VM",17.82, 14000)

vm_list = [vm1, vm2, vm3, vm4, vm5]
def get_file_size_mb(file_path):
    file_size_bytes = os.path.getsize(file_path)
    return file_size_bytes
def upload_file(file_size, deadline, vm_list):
    sorted_vms = sorted(vm_list, key=lambda vm: vm.cost_per_unit_time)
    deadline=int(deadline)
    for vm in sorted_vms:
        uploadtime3=file_size/vm.compute_power
        print(uploadtime3, 'deadlineee')
        upload_time = file_size * vm.cost_per_unit_time
        upload_time2=1/deadline*0.99
        if uploadtime3 <= deadline:
            total_cost = upload_time + upload_time2
            return total_cost/100000, vm.name

    return None, None  

def write_string_to_file(string_to_write, filename):
  with open(filename, 'wb') as file:
    file.write(string_to_write)
def write_string_to_file2(string_to_write, filename):
  
  with open(filename, 'w') as file:
    file.write(string_to_write)
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/admin.html', methods=['GET','POST'])
def admin_world():
    if request.method=='POST':
        name=request.form['filename']
        deadline=request.form['deadline']
        files=request.form['file']
        if files:
                with open(files, "r") as file: 
                    files_string = file.read()
        key = Fernet.generate_key() 
        with open('myTopSecretKey.key', 'wb') as file:
            file.write(key)
        with open('myTopSecretKey.key', 'rb') as file:
            Key = file.read()
        fe = Fernet(key)
        encryptedData = fe.encrypt(bytes(files_string, encoding='utf8'))
        with open('myTopSecretInfo.txt', 'wb') as file:
            file.write(encryptedData)
        with open('myTopSecretInfo.txt', 'rb') as file:
            encryptedData = file.read()
        print(encryptedData)
        file_size= get_file_size_mb(files)
        total_cost, selected_vm = upload_file(file_size, deadline, vm_list)
        print(total_cost, 'anna eyy')
        admin=ADMIN(filename=name, deadline=deadline,cost=total_cost, content=files_string,key=Key,encrypted_text=encryptedData, uploaded=False, requested=False, accepted=False)
        db.session.add(admin)
        db.session.commit()
    return render_template('admin.html')
@app.route('/viewfilesadmin.html')
def view_file():
    allFiles=ADMIN.query.all()
    print(allFiles)
    return render_template('viewfilesadmin.html', allFiles=allFiles)


    return render_template('admin.html')
@app.route('/delete/<int:sno>')
def delete(sno):
    file= ADMIN.query.filter_by(sno=sno).first()
    db.session.delete(file)
    db.session.commit()
    return redirect('/viewfilesadmin.html')

@app.route('/upload/<int:sno>', methods=['GET','POST'])
def upload(sno):
    
    
    file= ADMIN.query.filter_by(sno=sno).first()
    file.uploaded=True
    db.session.add(file)
    db.session.commit()
    path_on_cloud=f"cloud1/{file.filename}.txt"
    print(file.content)
    write_string_to_file(file.encrypted_text, "output.txt")
    path_local="output.txt"
    storage.child(path_on_cloud).put(path_local)
    print('completed')
        
    return redirect('/viewfilesadmin.html')


@app.route('/user.html')
def view_file_user():
    allFiles=ADMIN.query.all()
    print(allFiles)
    return render_template('/user.html', allFiles=allFiles)

@app.route('/request/<int:sno>')
def requestt(sno):
    file= ADMIN.query.filter_by(sno=sno).first()
    file.requested=True
    db.session.add(file)
    db.session.commit()
        
    return redirect('/user.html')


@app.route('/viewrequests.html')
def view_requests():
    allFiles=ADMIN.query.all()
    print(allFiles)
    return render_template('/viewrequests.html', allFiles=allFiles)

@app.route('/accept/<int:sno>')
def accepttt(sno):
    files= ADMIN.query.filter_by(sno=sno).first()
    files.accepted=True
    db.session.add(files)
    db.session.commit()
    return redirect('/viewrequests.html')

@app.route('/download/<int:sno>', methods=['GET','POST'])
def download(sno):
    filer= ADMIN.query.filter_by(sno=sno).first()
    msg= Message("File Download Key", sender='mvamshikrishna17@gmail.com', recipients=['20eg105430@anurag.edu.in'])
    msg.body= filer.key
    mail.send(msg)
    return render_template('/decrypt.html', allFiles=filer)

@app.route('/downloadfiles.html')
def download_files():
    allFiles=ADMIN.query.all()
    print(allFiles)
    return render_template('/downloadfiles.html', allFiles=allFiles)
@app.route('/dd/<int:sno>', methods=['GET','POST'])
def dd(sno):
    if request.method=='POST':
        er=False
        filer= ADMIN.query.filter_by(sno=sno).first()
        filename=request.form['name']
        print(filename)
        key=request.form['key']
        print(filer.key.decode(),"keysssssss")
        print(key,"nsnjc")
        x=filer.key.decode()
        y=key
        if x==y:
            er=True
            encryptedData= filer.encrypted_text
            f = Fernet(filer.key)
            decryptedData = f.decrypt(encryptedData)
            decryptedData= decryptedData.decode()
            print(decryptedData)
            write_string_to_file2(decryptedData,f'{filename}.txt')
            file_path = f'{filename}.txt'
            return send_file(file_path, as_attachment=True)
            return redirect('/downloadfiles.html')
        return redirect('/downloadfiles.html')
if __name__=='__main__':
    app.run(debug=True)