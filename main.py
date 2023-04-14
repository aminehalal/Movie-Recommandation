from tkinter import *
from PIL import Image,ImageTk
import datetime
#import smtplib
#from email.message import EmailMessage
import sqlite3
from signpupage import SingUpPage

class MoviesRecommandation :

    def __init__(self,root) :
        self.root = root
        self.root.title("Movies Recommandation")
        self.root.geometry ("1000x700+109+0")

        db = sqlite3.connect(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\moviesrecommandation.db")
        cr = db.cursor()


        def opendb():
            db = sqlite3.connect(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\moviesrecommandation.db")
            cr = db.cursor()

        #Les Methodes
        def login_now() :
            pass

        #Back Ground
        imgbg = Image.open(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\images\backfram.jpg")
        imgbg = imgbg.resize((1000,700),Image.ANTIALIAS)
        self.photoimgbg = ImageTk.PhotoImage(imgbg)

        lblimgbg = Label(self.root,image=self.photoimgbg,bd=4,relief=RIDGE)
        lblimgbg.place(x=0,y=0,width=1000,height=700)

        #Title
        lbltitle = Label(self.root , text="Movie Recommandation",font=("Courier New",38,"bold"),fg="White" , bg= "black",bd=4,relief=RIDGE)
        lbltitle.place(x=180,y=40,width=650,height=60) 


        #MainFrame
        mainframe = Frame(self.root , bd=4 , relief=RIDGE)
        mainframe.place (x=200 , y= 120 , width=600 , height=500)

        #PicinMainFrame
        imgmainframe = Image.open(r"C:\Users\lenevo\Desktop\Langage\Python Projects\Project\Movie Recommandation\images\mainframe.jpg")
        imgmainframe = imgmainframe.resize((595,495),Image.ANTIALIAS)
        self.photoimgmainframe = ImageTk.PhotoImage(imgmainframe)

        lblimgmainframe = Label(mainframe,image=self.photoimgmainframe,bd=2,relief=RIDGE)
        lblimgmainframe.place(x=0,y=0,width=595,height=495)

        #Log In Chambre
        lblmain = Label(mainframe , text="Log in",font=("Courier New",20,"bold"),bg="black",fg="gold",bd=4,relief=RIDGE)
        lblmain.place(x=200,y=30,width=200)

        lbluser = Label(mainframe , text="Username",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lbluser.place(x=200,y=110,width=200)

        username = Entry(mainframe,font=("Courier New",20,"bold"),width=60)
        username.place(x=200 , y=160 , width=200, height=50)

        lblpswd = Label(mainframe , text="Password",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblpswd.place(x=200,y=260,width=200)

        password = Entry(mainframe,font=("Courier New",20,"bold"),width=60,show="*")
        password.place(x=200 , y=310 , width=200, height=50)

        login = Button(mainframe ,text="Login" ,command=login_now,font=("Courier New",18,"bold"),bg="black",fg="gold",bd=4,relief=RIDGE )
        login.place (x= 50 , y= 390 , width=200 , height=50)

        signup = Button(mainframe ,text="Sign Up",command=self.signup_now ,font=("Courier New",18,"bold"),bg="black",fg="gold",bd=4,relief=RIDGE )
        signup.place (x= 350 , y= 390 , width=200 , height=50)

        
    def signup_now (self) :
        self.new_windows = Toplevel(self.root)
        self.app = SingUpPage(self.new_windows)

if __name__ == "__main__" :
    root=Tk()
    obj=MoviesRecommandation(root)
    root.mainloop()
