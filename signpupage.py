from tkinter import *
from tkcalendar import Calendar, DateEntry
import sqlite3
from random import randint
from PIL import Image,ImageTk

class SingUpPage :
    def __init__(self,root): 
        self.root = root
        self.root.title("Sign Up")
        self.root.geometry ("610x600+300+16")

        db = sqlite3.connect(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\moviesrecommandation.db")
        cr = db.cursor()
        db.commit()

        def opendb():
            db = sqlite3.connect(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\moviesrecommandation.db")
            cr = db.cursor()
            cr.execute("create table if not exists accounts (id integer primary key autoincrement,firstname text , lastname text ,gender text,birthday date ,email text , username text, password text , watched text ,watchlist text)")
            cr.execute("create table if not exists activite (id_activate integer primary key autoincrement, username text, type text , movie text ,datetime text,foreign key (username) references accounts(username))")
            db.commit()    
        def closedb():
            db.close()

        #methodes
        def signup ():
            opendb()
            if varacc.get() == 1 :
                firstname = firstnamea.get()
                lastname = lastnamea.get()
                gender = vargender.get()
                birthday = birthdaya.get_date()
                email = emaila.get()
                username = usernamea.get()
                password = passworda.get()
                exite = cr.execute(f"select * from accounts where username == '{username}' ")
                if not exite.fetchone():
                    print("im here")
                    cr.execute(f"insert into accounts (firstname , lastname , gender,birthday,email, username, password) values ('{firstname}','{lastname}','{gender}','{birthday}','{email}','{username}','{password}')")
                    db.commit()
                    db.close()
            
                    framnew = Frame(self.root , bd=4 , relief=RIDGE)
                    framnew.place (x=50 , y= 5 , width=517 , height=80 )

                    labelnew = Label(framnew, text="Done", font=("Courier New",18,"bold") ,fg="red" , bd=4 , relief=RIDGE)
                    labelnew.place(x = 0 , y = 0 , width=517,height=80)

                    closedb()

                else :
                    print("this user already in")
                    db.close()
                    framnew = Frame(self.root , bd=4 , relief=RIDGE)
                    framnew.place (x=50 , y= 10 , width=517 , height=80 )

                    labelnew = Label(framnew, text="This account is already existe", font=("Courier New",20,"bold") ,fg="red" , bd=4 , relief=RIDGE)
                    labelnew.place(x = 0 , y = 0 , width=517,height=80)

                    closedb()
               
                firstnamea.delete(0, END)
                lastnamea.delete(0, END)
                username.delete(0, END)
                emaila.delete(0,END)
                password.delete(0, END)
                rdbtn["value"] = 0

            else :
                print("Error !")
            

        #MainFrame
        mainframesign = Frame(self.root , bd=4 , relief=RIDGE)
        mainframesign.place (x=50 , y= 60 , width=517 , height=530)

        #Picture
        imgmainframe = Image.open(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\images\mainframe.jpg")
        imgmainframe = imgmainframe.resize((515,525),Image.ANTIALIAS)
        self.photoimgmainframe = ImageTk.PhotoImage(imgmainframe)

        lblimgmainframe = Label(mainframesign,image=self.photoimgmainframe,bd=2,relief=RIDGE)
        lblimgmainframe.place(x=0,y=0,width=515,height=525)

        #Info
        lblname = Label(mainframesign , text="First Name",font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblname.place(x=25,y=20,width=200)

        firstnamea = Entry(mainframesign,font=("Courier New",18,"bold"),width=50)
        firstnamea.place(x=25 , y=65 , width=200, height=40)

        lblsname = Label(mainframesign , text="Last Name",font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblsname.place(x=285,y=20,width=200)

        lastnamea = Entry(mainframesign,font=("Courier New",18,"bold"),width=50)
        lastnamea.place(x=285 , y=65 , width=200, height=40)

        vargender = StringVar()    
        gender_label = Label(mainframesign,text='Gender',font=("Courier New",18, "bold"),fg="white",bg="black")
        male = Radiobutton(mainframesign,text='Male', font=("Courier New",14,"bold") ,fg="black",variable=vargender,value='male')
        female = Radiobutton(mainframesign,text='Female',  font=("Courier New",14,"bold") ,fg="black",variable=vargender,value='female')
        
        gender_label.place(x=25 , y=115 , width=200, height=40)
        male.place (x=25 , y=165 ,width=80)
        female.place (x=130 , y=165 ,width=95)

        lblbirthday = Label(mainframesign , text="Birthday",font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblbirthday.place(x=285,y=115,width=200)

        birthdaya = DateEntry(mainframesign,font=("Courier New",15,"bold"),width=50)
        birthdaya.place(x=285 , y=160 , width=200, height=40)

        lblemail = Label(mainframesign, text="Email" , font=("Courier New",18,"bold") , bg="black",fg="white" , bd=4 , relief=RIDGE)
        lblemail.place(x = 150 , y = 210 , width=200)

        emaila = Entry(mainframesign , font=("Courier New" , 14 , "bold") , width=200)
        emaila.place ( x= 50 , y = 255 , height = 40 , width=400)

        lblusername = Label(mainframesign , text="Username",font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblusername.place(x=25,y=305,width=200)

        usernamea = Entry(mainframesign,font=("Courier New",18,"bold"),width=50)
        usernamea.place(x=25 , y=350 , width=200, height=40)

        lblpass = Label(mainframesign , text="Password",font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblpass.place(x=285,y=305,width=200)

        passworda = Entry(mainframesign,font=("Courier New",18,"bold"),show="*",width=50)
        passworda.place(x=285 , y=350 , width=200, height=40)

        varacc = IntVar() 
        rdbtn = Radiobutton (mainframesign ,variable= varacc , value=1, text="I agree to the user terms" , font=("times new roman",18,"bold") ,fg="black" , relief=RIDGE)
        rdbtn.place (x = 50 ,  y = 410 , height = 40 , width=400)

        btnsignup = Button(mainframesign, command=signup,text="Sign Up" , font=("times new roman",18,"bold") , bg="black",fg="gold" , bd=4 , relief=RIDGE)
        btnsignup.place(x = 150 , y = 460 , width=200)



if __name__ == "__main__" :
    root=Tk()
    obj=SingUpPage(root)
    root.mainloop()
