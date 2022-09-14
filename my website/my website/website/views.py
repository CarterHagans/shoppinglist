from inspect import currentframe
import json
from operator import truediv
from pkgutil import iter_modules
from re import L
from flask import Blueprint, render_template, request,flash,redirect,session,url_for
import datetime
from .models import User,Families
from . import db
from flask_sqlalchemy import SQLAlchemy


views = Blueprint("views", __name__)




@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")




@views.route("/start")
def start():
    return render_template("start.html")







@views.route("/login" ,methods=["POST","GET"])
def login():
    if request.method == "POST":
        canLogin = False
        username = request.form.get("username")
        password = request.form.get("password")
        for entry in User.query.all():
            if entry.name == username and entry.password == password:
                canLogin = True
        if canLogin == True:
            flash("You are now logged in!")
            session['username'] = username
            session['password'] = password
            return redirect("/families")
        elif canLogin == False:
            flash("You were not logged in, please check your username and password.")
            return redirect("/login")
    elif request.method == "GET":
        if session.get("username") != None:
            return redirect('/families')
        else:
            
            return render_template("login.html")








@views.route("/families",methods=["POST","GET"])
def families():
    if request.method == "GET": # when the user enters the page that shows the  families
        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")

        username = session.get("username") # their username is stored in their session, get their username

        for user in User.query.all(): # searching for that username in the database
            if user.name == username: # finding the user, making sure is the right user
                families = user.families # accessing the families they are in
                list_of_families = json.loads(families) # changing the list from a string to an actual list
                length_of_families = len(list_of_families) # getting the amount of families they are in
                lists_being_sent_to_page = []
                for family in Families.query.all():
                    if username in family.members or username in family.admins or username == family.creator_name:
                        lists_being_sent_to_page.append(family)

            

        return render_template("families.html",num_of_families=length_of_families,users_families = lists_being_sent_to_page,username=username) # sending the num of families as well as the list of families








@views.route('/families/<id>')
def view_family(id):
    if request.method == "GET": 
        canAccess = False
        canManageFamily = False
        currentFamily = Families.query.filter_by(_id=id).first()
        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:
            current_user = session.get("username")
            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.admins or current_user == currentFamily.creator_name:
                        canAccess = True
                        canManageFamily = True
                    elif current_user in currentFamily.members:
                        canAccess = True

        if canAccess == True:
            
            return render_template("view_family.html",family=currentFamily,user_has_permissions=canManageFamily)
        else: 
            return redirect("/")






@views.route('/families/<id>/list')
def family_list(id):
    if request.method == "GET": 
        canAccess = False
        canManageFamily = False
        currentFamily = Families.query.filter_by(_id=id).first()
        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:
            current_user = session.get("username")
            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.admins or current_user == currentFamily.creator_name:
                        canAccess = True
                        canManageFamily = True
                    elif current_user in currentFamily.members:
                        canAccess = True
                
        if canAccess == True:
            lengthOfList = len(json.loads(currentFamily.shopping_list))
            shoppingList = json.loads(currentFamily.shopping_list)
            return render_template("list.html",list=shoppingList,family=currentFamily,user_has_permissions=canManageFamily,length_of_list=lengthOfList)
        else: 
            return redirect("/")
    
    
    

@views.route('/families/<id>/list/audit-log',methods=["POST","GET"])
def shopping_audit_log(id):
    currentFamily = Families.query.filter_by(_id=id).first()
    families_auditLog = json.loads(currentFamily.audit_log)
    length_of_audit_log = len(families_auditLog)
    if request.method == "GET":

        canAccess = False
        canManageFamily = False

        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:
            current_user = session.get("username")
            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.admins or current_user == currentFamily.creator_name:
                        canAccess = True
                        canManageFamily = True
                    elif current_user in currentFamily.members:
                        canAccess = True
        if canAccess == True:
            return render_template("list_auditlog.html",family=currentFamily,auditLog=families_auditLog,auditLogLength=length_of_audit_log)
        else: 
            return redirect("/")
    
    
@views.route('/families/<id>/list/add',methods=["POST","GET"])
def add_item_to_list(id):
    current_user = session.get("username")
    currentFamily = Families.query.filter_by(_id=id).first()
    if request.method == "GET":

        canAccess = False
        canManageFamily = False

        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:
            
            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.admins or current_user == currentFamily.creator_name:
                        canAccess = True
                        canManageFamily = True
                    elif current_user in currentFamily.members:
                        canAccess = True
        if canAccess == True:
            return render_template("add_item.html",family=currentFamily,user_has_permissions=canManageFamily)
        else: 
            return redirect("/")
    elif request.method == "POST":
        name_of_item = request.form.get("item_name")
        amount_of_item = int(request.form.get("quantity"))
        converted_list = json.loads(currentFamily.shopping_list)
        length_of_existing_list = currentFamily.num_of_items
        for x in range(amount_of_item):
            converted_list.append(name_of_item +f" :{length_of_existing_list}")
            length_of_existing_list +=1
        completed_list = json.dumps(converted_list)
        currentAuditLog = json.loads(currentFamily.audit_log)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        currentAuditLog.append(f'{formatted_time}: {current_user} has added {amount_of_item} of {name_of_item}(s)')
        currentFamily.audit_log = json.dumps(currentAuditLog)


        currentFamily.shopping_list = completed_list
        currentFamily.num_of_items = length_of_existing_list
        db.session.commit()
        
        return redirect(f"/families/{id}/list")
            




@views.route('/families/<id>/list/remove/<item_id>',methods=["POST","GET"])
def remove_item(id,item_id):
    currentFamily = Families.query.filter_by(_id=id).first()
    if request.method == "GET":
        auditLogItem = None
        canAccess = False
        canManageFamily = False

        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:
            current_user = session.get("username")
            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.admins or current_user == currentFamily.creator_name:
                        canAccess = True
                        canManageFamily = True
                    elif current_user in currentFamily.members:
                        canAccess = True
        if canAccess == True and  canManageFamily == True:
            families_list = json.loads(currentFamily.shopping_list)
            for item in families_list:
                if item.split(':',1)[1] == item_id:
                    families_list.remove(item)
                    auditLogItem = item.split(':',1)[0]
            currentAuditLog = json.loads(currentFamily.audit_log)
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            currentAuditLog.append(f'{formatted_time}: {current_user} has removed {auditLogItem} from the list ')
            currentFamily.audit_log = json.dumps(currentAuditLog)
            currentFamily.shopping_list = json.dumps(families_list)
            db.session.commit()
            return redirect(f'/families/{id}/list')
        else:
            return redirect(f'/families/{id}/list')
    return redirect(f"/families/{id}/list")






@views.route('/families/<id>/list/edit/<item_id>',methods=["POST","GET"])
def edit_item(id,item_id):
    currentFamily = Families.query.filter_by(_id=id).first()
    current_user = session.get("username")
    if request.method == "GET":

        canAccess = False

        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        else:


            for user in User.query.all():
                if user.name == current_user:
                    if current_user in currentFamily.members:

                        canAccess = True

        if canAccess == True:
            item_to_send = None
            quantity = 0
            for item in json.loads(currentFamily.shopping_list):
                
                if item.split(':',1)[1] == item_id:
                    item_to_send = item.split(':',1)[0]
                    
                    
            for item in json.loads(currentFamily.shopping_list):
                if item.split(':',1)[0] == item_to_send.split(':',1)[0]:
                    
                    quantity+=1 
            return render_template("edit.html",family=currentFamily, item=item_to_send,quantity=quantity)
        else:
            return redirect('/')
    elif request.method == "POST":
        index = 0
        count = 0
        add_item_index = currentFamily.num_of_items
        current_item = None
        current_name = ""
        new_name = request.form.get("item")
        new_amount = request.form.get("quantity")


        for item in json.loads(currentFamily.shopping_list):
            if item.split(':',1)[1] == item_id:
                current_item = item.split(':',1)[1]
                current_name = item.split(':',1)[0]
                for x in json.loads(currentFamily.shopping_list):
                    if x.split(':',1)[0] == current_name:
                        count+=1
        if new_name != current_name:
            for item in json.loads(currentFamily.shopping_list):
                if item.split(':',1)[1] == item_id:
                    new_list =json.loads(currentFamily.shopping_list)
                    new_list[index] = new_name + f":{item_id}"
                    currentFamily.shopping_list = json.dumps(new_list)
                    db.session.commit()
                    index+=1
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            currentAuditLog = json.loads(currentFamily.audit_log)
            currentAuditLog.append(f'{formatted_time}: {current_user} has edited of an item with the name {current_name} to a new name of {new_name}')
            currentFamily.audit_log = json.dumps(currentAuditLog)
            db.session.commit()

        if new_amount != count:
            for item in json.loads(currentFamily.shopping_list):
                if item.split(':',1)[1] == item_id:
                    items_name = item.split(':',1)[0]
                    for x in json.loads(currentFamily.shopping_list):
                        if x.split(':',1)[0] == current_name:
                            loaded_list =json.loads(currentFamily.shopping_list)
                            loaded_list.remove(x)
                            currentFamily.shopping_list = json.dumps(loaded_list)
                            db.session.commit()
                    for num_of_items in range (int(new_amount)):
                        loaded_list =json.loads(currentFamily.shopping_list)
                        loaded_list.append(f'{current_name}:{add_item_index}')
                        add_item_index +=1
                        currentFamily.shopping_list = json.dumps(loaded_list)
                        currentFamily.num_of_items = add_item_index
                        db.session.commit()
            
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            currentAuditLog = json.loads(currentFamily.audit_log)
            currentAuditLog.append(f'{formatted_time}: {current_user} has edited of an item with the name {current_name} that had a quantity of {count} to have a new quantity of {new_amount}')
            currentFamily.audit_log = json.dumps(currentAuditLog)
            db.session.commit()
        
        return redirect(f'/families/{id}/list')
        
    
    
    


@views.route("/create-family",methods=["POST","GET"])
def create_family():
    if request.method == "GET":
        if session.get("username") == None:
            flash("You must be logged in!")
            return redirect("/")
        
        return render_template("create_family.html")
    elif request.method == "POST":
        can_create = True
        family_name =  request.form.get("familyname")
        family_owner = session.get("username")
        for family in Families.query.all():
            if family.name == family_name:
                flash("A famly with this name already exists please choose a different name.")
                can_create = False
                return redirect("/create-family")
        if can_create == True:
            for user in User.query.all():
                if user.name == family_owner:
                    owners_email = user.email
                    users_families = json.loads(user.families)
                    users_families.append(family_name)
                    user.families = json.dumps(users_families)
                    db.session.commit()
            family_to_be_created = Families(family_name,family_owner,owners_email,json.dumps([family_owner]),json.dumps([]),json.dumps([]),json.dumps([]),0,json.dumps([]))

            db.session.add(family_to_be_created)
            db.session.commit()
            flash("Family created!")
            return redirect("/families")
        
        




@views.route('/signup',methods=["POST","GET"])
def signup():
    if request.method == "POST":
        canCreateAccount = True
        invalidUsername = False
        invalidEmail = False
        username =  request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        for entry in User.query.all():
            if username == entry.name:
                canCreateAccount = False
                invalidUsername = True
            elif email == entry.email:
                canCreateAccount = False
                invalidEmail = True
        if canCreateAccount == True:
            user = User(username,email,password,json.dumps([]))
            db.session.add(user)
            db.session.commit()
            flash("You are signed in!")
            session['email'] = email
            session['username'] = username
            return redirect("/families")
        else:
            if invalidEmail == True:
                flash('You cannot create an account with this email as it already has been used!')
                return redirect("/signup")
            elif invalidUsername == True:
                flash("You cannot create an account with this username as it already has been used!")
                return redirect("/signup")
            else:
                flash("There was an error creating your account, please try again.")
                return redirect("/signup")



    else:
        
     return render_template("signup.html")