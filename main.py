from tkinter import *
from PIL import Image,ImageTk
import datetime
#import smtplib
#from email.message import EmailMessage
import sqlite3
from signpupage import SingUpPage
import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features = 5000 , stop_words='english')
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
from sklearn.feature_extraction.text import TfidfVectorizer
import os
current_path = os.path.dirname(os.path.abspath(__file__))
moviesdata_path = "moviesdata.csv"
moviesdata = pd.read_csv(os.path.join(current_path,moviesdata_path))
vectors = cv.fit_transform(moviesdata['tags']).toarray()
similarity = cosine_similarity(vectors)

# Initialize TfidfVectorizer to compute document similarity based on movie titles
vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(moviesdata['title'])

# Compute cosine similarity between movie titles
similarity = cosine_similarity(tfidf_matrix)

class MoviesRecommandation :

    def __init__(self,root) :
        self.root = root
        self.root.title("Movies Recommandation")
        self.root.geometry ("1000x700+109+0")
        database_path = "moviesrecommandation.db"
        db = sqlite3.connect(os.path.join(current_path , database_path))
        cr = db.cursor()


        def opendb():
            db = sqlite3.connect(os.path.join(current_path , database_path))
            cr = db.cursor()

        #Les Methodes
        def login_now() :
            opendb()
            username = usernameput.get()
            password = passwordput.get()

            def logout ():
                new = MoviesRecommandation(root)

            def removeone() :
                movie = watchList.get(watchList.curselection())
                watchList.delete(watchList.curselection())
                opendb()
                cr.execute(f"delete from operations where username=='{username}' and type=='Watchlist' and movie == '{movie}'")
                db.commit()
                getwatchlist()

            def removetwo() :
                movie = watchedList.get(watchedList.curselection())
                watchedList.delete(watchedList.curselection())
                opendb()
                cr.execute(f"delete from operations where username=='{username}' and type=='Watched' and movie == '{movie}'")
                db.commit()
                getwatched()

            def getwatched():
                opendb()
                watchedList.delete(0,END)
                cr.execute(f"select movie from operations where type =='Watched' and username =='{username}'")
                watchedlistmovies = cr.fetchall()
                for i in watchedlistmovies :
                    movie_name = i[0]
                    watchedList.insert(watchedList.size(),movie_name)

            def watchedtwo ():
                movie = watchList.get(watchList.curselection())
                opendb()
                cr.execute(f"insert into operations (username ,type , movie ,datetime) values ('{username}' , 'Watched' ,'{movie}' , '{str(datetime.datetime.now())[:19]}')")
                db.commit()
                watchList.delete(watchList.curselection())
                print(f"the movie is {movie}")
                getwatched()
                #do_it()

            def watchedone ():
                movie = sugList.get(sugList.curselection())
                opendb()
                cr.execute(f"insert into operations (username ,type , movie ,datetime) values ('{username}' , 'Watched' ,'{movie}' , '{str(datetime.datetime.now())[:19]}')")
                db.commit()
                sugList.delete(sugList.curselection())
                print(f"the movie is {movie}")
                getwatched()

            def getwatchlist():
                opendb()
                watchList.delete(0,END)
                cr.execute(f"select movie from operations where type =='Watchlist' and username =='{username}'")
                watchlistmovies = cr.fetchall()
                for i in watchlistmovies :
                    movie_name = i[0]
                    watchList.insert(watchList.size(),movie_name)

            def watchlistone ():
                movie = sugList.get(sugList.curselection())
                opendb()
                cr.execute(f"insert into operations (username ,type , movie ,datetime) values ('{username}' , 'Watchlist' ,'{movie}' , '{str(datetime.datetime.now())[:19]}')")
                db.commit()
                print(str(datetime.datetime.now())[:19])
                sugList.delete(sugList.curselection())
                print(f"the movie is {movie}")
                getwatchlist()

            def search_now() :
                searchmovie = searchbar.get()
                matching_movies = moviesdata[moviesdata['title'].str.contains(searchmovie)]
                sugList.delete(0,END)
                for i in matching_movies['title']:
                    sugList.insert(sugList.size(),i)

            def recommend(movie_list):
                if not movie_list:
                    # recommend 10 random movies
                    random_indices = random.sample(range(len(moviesdata)), k=20)
                    for i in random_indices:
                        sugList.insert(sugList.size(), moviesdata.iloc[i].title)
                    return
                
                # Compute average similarity between movie titles in movie_list
                movie_indices = []
                movie_titles = [title.lower() for title in movie_list]
                for movie_title in movie_titles:
                    try:
                        movie_index = moviesdata[moviesdata['title'].str.lower().str.contains(movie_title, regex=False)].index[0]
                        movie_indices.append(movie_index)
                    except IndexError:
                        continue
                if len(movie_indices) == 0:
                    return
                shared_movies = set(range(len(moviesdata)))
                for movie_index in movie_indices:
                    distances = similarity[movie_index]
                    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:40]
                    shared_movies = shared_movies.intersection(set([i[0] for i in movies_list]))
                
                if len(shared_movies) < 3:
                    shared_movies = set(range(len(moviesdata)))
                    for movie_index in movie_indices:
                        distances = similarity[movie_index]
                        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:40]
                        shared_movies = shared_movies.union(set([i[0] for i in movies_list]))
                
                if len(shared_movies) == 0:
                    return
                
                # Compute similarity between movie titles in movie_list and all other movies
                title_similarity = np.zeros(len(moviesdata))
                for i in shared_movies:
                    title_similarity[i] = np.mean([cosine_similarity(vectorizer.transform([movie_title]), tfidf_matrix[i])[0][0] for movie_title in movie_titles])
                title_similarity = title_similarity / len(movie_titles)
                
                # Recommend movies based on title similarity
                recommendation_indices = np.argsort(title_similarity)[::-1][:20]
                sugList.delete(0,END)
                for i in recommendation_indices:
                    sugList.insert(sugList.size(), moviesdata.iloc[i].title)

            def do_it() :
                opendb()
                cr.execute(f"select movie from operations where type =='Watched' and username =='{username}'")
                movie_list_tuple = cr.fetchall()
                #movie_list = list(movie_list_tuple)
                movie_list = [title[0] for title in movie_list_tuple]
                print(movie_list)
                recommend(movie_list)

            db = sqlite3.connect(os.path.join(current_path , database_path))
            cr = db.cursor()

            exist = cr.execute(f"select * from accounts where username =='{username}' and password=='{password}'")
            if exist.fetchone() :
                #MainFrame
                mainframe = Frame(self.root , bd=4 , relief=RIDGE)
                mainframe.place (x=100 , y= 120 , width=800 , height=550)

                #Labels
                    #SearchBar
                searchbar = Entry(mainframe,font=("Courier New",14,"bold"),width=50)
                searchbar.place(x=20 , y=30 , width=230, height=40)

                btnsearch = Button(mainframe ,text="Search" ,command=search_now,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnsearch.place (x= 20 , y= 80 , width=230 , height=40)

                lblsug = Button(mainframe ,command=do_it, text="Suggest Movies",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
                lblsug.place(x=20 ,y=140, width=230,height= 40)

                sugList = Listbox(mainframe ,font=("Courier New",12,"bold"),bg="white",fg="black",width=40)
                sugList.place(x=20 , y=190 , width=230, height=230)

                btnwatchlist = Button(mainframe ,text="Watchlist" ,command=watchlistone,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnwatchlist.place (x= 20 , y= 430 , width=230 , height=40)

                btnwatched = Button(mainframe ,text="Watched" ,command=watchedone,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnwatched.place (x= 20 , y= 480 , width=230 , height=40)

                    #Wtachlist
                lblwatchlist = Label(mainframe , text="Watchlist",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
                lblwatchlist.place(x=280 ,y=30, width=230)

                watchList = Listbox(mainframe ,font=("Courier New",12,"bold"),bg="white",fg="black",width=40)
                watchList.place(x=280 , y=80 , width=230, height=340)

                btnwatchedtwo = Button(mainframe ,text="Watched" ,command=watchedtwo,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnwatchedtwo.place (x= 280 , y= 430 , width=230 , height=40)

                btnremove = Button(mainframe ,text="Remove",command=removeone ,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnremove.place (x= 280 , y= 480 , width=230 , height=40)

                    #Watched
                lblwatched = Label(mainframe , text="Watched",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
                lblwatched.place(x=530 ,y=30, width=230)

                watchedList = Listbox(mainframe ,font=("Courier New",12,"bold"),bg="white",fg="black",width=40)
                watchedList.place(x=530 , y=80 , width=230, height=340)

                btnremovetwo = Button(mainframe ,text="Remove" ,command=removetwo,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnremovetwo.place (x= 530 , y= 430 , width=230 , height=40)

                btnlogout = Button(mainframe ,text="Log out",command=logout ,font=("Courier New",18,"bold"),bg="black",fg="white",bd=4,relief=RIDGE )
                btnlogout.place (x= 530 , y= 480 , width=230 , height=40)

                #do_it()
                getwatchlist()
                getwatched()
            
            else :
                print("username or password in wrong")

        #Back Ground
        imgbg = Image.open(os.path.join(current_path ,r"images\backfram.jpg"))
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
        imgmainframe = Image.open(os.path.join(current_path , r"images\mainframe.jpg"))
        imgmainframe = imgmainframe.resize((595,495),Image.ANTIALIAS)
        self.photoimgmainframe = ImageTk.PhotoImage(imgmainframe)

        lblimgmainframe = Label(mainframe,image=self.photoimgmainframe,bd=2,relief=RIDGE)
        lblimgmainframe.place(x=0,y=0,width=595,height=495)

        #Log In Chambre
        lblmain = Label(mainframe , text="Log in",font=("Courier New",20,"bold"),bg="black",fg="gold",bd=4,relief=RIDGE)
        lblmain.place(x=200,y=30,width=200)

        lbluser = Label(mainframe , text="Username",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lbluser.place(x=200,y=110,width=200)

        usernameput = Entry(mainframe,font=("Courier New",20,"bold"),width=60)
        usernameput.place(x=200 , y=160 , width=200, height=50)

        lblpswd = Label(mainframe , text="Password",font=("Courier New",20,"bold"),bg="black",fg="white",bd=4,relief=RIDGE)
        lblpswd.place(x=200,y=260,width=200)

        passwordput = Entry(mainframe,font=("Courier New",20,"bold"),width=60,show="*")
        passwordput.place(x=200 , y=310 , width=200, height=50)

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
