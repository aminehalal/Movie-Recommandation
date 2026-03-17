import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import os
import random
import math

# Import pandas/numpy if available; ML (sklearn) optional.
try:
    import pandas as pd
except ImportError:
    pd = None
try:
    import numpy as np
except ImportError:
    np = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_ML = True
except Exception:
    HAS_ML = False

# ─── Paths ───────────────────────────────────────────────────────────────────
current_path = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_path, "moviesrecommandation.db")
CSV_PATH = os.path.join(current_path, "moviesdata.csv")

# ─── Load movie data (ML optional) ───────────────────────────────────────────
# Always load the CSV if present so search/watchlist UI works even without sklearn.
if os.path.exists(CSV_PATH) and pd is not None:
    moviesdata = pd.read_csv(CSV_PATH)
    if HAS_ML and np is not None:
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(moviesdata['title'])
        similarity = cosine_similarity(tfidf_matrix)
    else:
        vectorizer = None
        tfidf_matrix = None
        similarity = None
else:
    moviesdata = None
    vectorizer = None
    tfidf_matrix = None
    similarity = None

# ─── Design Tokens ───────────────────────────────────────────────────────────
BG        = "#0A0A0F"
BG2       = "#12121A"
BG3       = "#1A1A26"
CARD      = "#1E1E2E"
CARD2     = "#252535"
ACCENT    = "#E50914"
ACCENT2   = "#FF6B6B"
GOLD      = "#F5C518"
TEXT      = "#FFFFFF"
TEXT2     = "#B0B0C0"
TEXT3     = "#6B6B80"
BORDER    = "#2A2A3E"
GREEN     = "#46D369"
BLUE      = "#0080FF"

FONT_TITLE  = ("Georgia", 26, "bold")
FONT_H1     = ("Georgia", 16, "bold")
FONT_H2     = ("Georgia", 13, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_SMALL  = ("Helvetica", 9)
FONT_MONO   = ("Courier", 10, "bold")
FONT_BTN    = ("Helvetica", 10, "bold")
FONT_LARGE  = ("Georgia", 32, "bold")

# ─── DB Helpers ──────────────────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    cr = db.cursor()
    cr.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT, lastname TEXT, gender TEXT,
        birthday DATE, email TEXT,
        username TEXT UNIQUE, password TEXT
    )""")
    cr.execute("""CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, type TEXT, movie TEXT, datetime TEXT,
        FOREIGN KEY (username) REFERENCES accounts(username)
    )""")
    db.commit(); db.close()

# ─── Styled Widget Factories ──────────────────────────────────────────────────
def make_btn(parent, text, command, color=ACCENT, fg=TEXT, width=None, height=36, font=FONT_BTN):
    f = tk.Frame(parent, bg=color, cursor="hand2")
    lbl = tk.Label(f, text=text, bg=color, fg=fg, font=font, padx=16, pady=0, cursor="hand2")
    lbl.pack(fill="both", expand=True, pady=8)
    for w in (f, lbl):
        w.bind("<Button-1>", lambda e: command())
        w.bind("<Enter>", lambda e, w=f: w.config(bg=ACCENT2) or lbl.config(bg=ACCENT2))
        w.bind("<Leave>", lambda e, w=f: w.config(bg=color) or lbl.config(bg=color))
    if width:
        f.config(width=width, height=height)
        f.pack_propagate(False)
    return f

def make_entry(parent, placeholder="", show=None, width=300, font=FONT_BODY):
    frame = tk.Frame(parent, bg=CARD2, highlightbackground=BORDER,
                     highlightthickness=1, highlightcolor=ACCENT)
    inner = tk.Frame(frame, bg=CARD2)
    inner.pack(fill="x", padx=8, pady=6)
    var = tk.StringVar()
    kw = dict(textvariable=var, bg=CARD2, fg=TEXT, font=font,
              insertbackground=TEXT, relief="flat", width=30, bd=0)
    if show:
        kw["show"] = show
    ent = tk.Entry(inner, **kw)
    ent.pack(fill="x")

    # Placeholder
    if placeholder:
        ent.insert(0, placeholder)
        ent.config(fg=TEXT3)
        def on_focus_in(e):
            if ent.get() == placeholder:
                ent.delete(0, "end"); ent.config(fg=TEXT)
        def on_focus_out(e):
            if not ent.get():
                ent.insert(0, placeholder); ent.config(fg=TEXT3)
        ent.bind("<FocusIn>", on_focus_in)
        ent.bind("<FocusOut>", on_focus_out)
        ent._placeholder = placeholder

    frame.bind("<Button-1>", lambda e: ent.focus_set())
    return frame, ent

def separator(parent, color=BORDER, pady=8):
    f = tk.Frame(parent, bg=color, height=1)
    f.pack(fill="x", pady=pady)
    return f

# ─── Scrollable Frame ─────────────────────────────────────────────────────────
class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg=BG2, **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.config(bg=BG3, troughcolor=BG2, activebackground=ACCENT)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self.inner_id, width=e.width)

    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

# ─── Movie Card ───────────────────────────────────────────────────────────────
def make_movie_card(parent, title, on_watchlist=None, on_watched=None, on_remove=None, badge=None):
    card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                    highlightthickness=1, cursor="hand2")
    card.pack(fill="x", padx=12, pady=4)

    inner = tk.Frame(card, bg=CARD)
    inner.pack(fill="x", padx=12, pady=8)

    # Icon
    icon_frame = tk.Frame(inner, bg=ACCENT, width=36, height=36)
    icon_frame.pack_propagate(False)
    icon_frame.pack(side="left", padx=(0, 10))
    tk.Label(icon_frame, text="▶", bg=ACCENT, fg=TEXT, font=("Helvetica", 12)).pack(expand=True)

    # Title
    title_frame = tk.Frame(inner, bg=CARD)
    title_frame.pack(side="left", fill="x", expand=True)
    tk.Label(title_frame, text=title, bg=CARD, fg=TEXT, font=FONT_H2,
             anchor="w", wraplength=260, justify="left").pack(anchor="w")

    if badge:
        tk.Label(title_frame, text=badge, bg=GREEN, fg="#000", font=FONT_SMALL,
                 padx=6, pady=1).pack(anchor="w", pady=(2, 0))

    # Action buttons
    btn_frame = tk.Frame(inner, bg=CARD)
    btn_frame.pack(side="right")

    def icon_btn(parent, text, cmd, color, hover):
        lbl = tk.Label(parent, text=text, bg=CARD, fg=color,
                       font=("Helvetica", 14), cursor="hand2", padx=4)
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>", lambda e: lbl.config(fg=hover))
        lbl.bind("<Leave>", lambda e: lbl.config(fg=color))
        return lbl

    if on_watchlist:
        icon_btn(btn_frame, "🔖", on_watchlist, TEXT2, GOLD)
    if on_watched:
        icon_btn(btn_frame, "✓", on_watched, TEXT2, GREEN)
    if on_remove:
        icon_btn(btn_frame, "✕", on_remove, TEXT2, ACCENT)

    return card

# ─── Paginator ───────────────────────────────────────────────────────────────
class Paginator:
    def __init__(self, parent, items, page_size, render_fn):
        self.parent = parent
        self.items = items
        self.page_size = page_size
        self.render_fn = render_fn
        self.page = 0
        self.total_pages = max(1, math.ceil(len(items) / page_size))

        self.list_frame = tk.Frame(parent, bg=BG2)
        self.list_frame.pack(fill="both", expand=True)

        self.nav_frame = tk.Frame(parent, bg=BG3, pady=6)
        self.nav_frame.pack(fill="x", side="bottom")

        self._build_nav()
        self.render()

    def _build_nav(self):
        for w in self.nav_frame.winfo_children():
            w.destroy()

        def nav_btn(text, cmd, enabled=True):
            fg = TEXT if enabled else TEXT3
            bg = CARD if enabled else BG3
            lbl = tk.Label(self.nav_frame, text=text, bg=bg, fg=fg,
                           font=FONT_BTN, padx=10, pady=4, cursor="hand2" if enabled else "arrow")
            lbl.pack(side="left", padx=2)
            if enabled:
                lbl.bind("<Button-1>", lambda e: cmd())
                lbl.bind("<Enter>", lambda e: lbl.config(bg=CARD2))
                lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))

        nav_btn("◀◀", self.first, self.page > 0)
        nav_btn("◀", self.prev, self.page > 0)

        # Page numbers
        start = max(0, self.page - 2)
        end = min(self.total_pages, start + 5)
        for i in range(start, end):
            active = (i == self.page)
            bg = ACCENT if active else CARD
            lbl = tk.Label(self.nav_frame, text=str(i + 1), bg=bg, fg=TEXT,
                           font=FONT_BTN, padx=8, pady=4, cursor="hand2")
            lbl.pack(side="left", padx=1)
            if not active:
                p = i
                lbl.bind("<Button-1>", lambda e, p=p: self.goto(p))
                lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg=CARD2))
                lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg=CARD))

        nav_btn("▶", self.next, self.page < self.total_pages - 1)
        nav_btn("▶▶", self.last, self.page < self.total_pages - 1)

        info = tk.Label(self.nav_frame,
                        text=f"  Page {self.page+1} / {self.total_pages}  ({len(self.items)} results)",
                        bg=BG3, fg=TEXT3, font=FONT_SMALL)
        info.pack(side="right", padx=8)

    def render(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        start = self.page * self.page_size
        end = start + self.page_size
        for item in self.items[start:end]:
            self.render_fn(self.list_frame, item)
        self._build_nav()

    def goto(self, p):
        self.page = p; self.render()
    def first(self): self.goto(0)
    def last(self): self.goto(self.total_pages - 1)
    def prev(self): self.goto(max(0, self.page - 1))
    def next(self): self.goto(min(self.total_pages - 1, self.page + 1))

    def update_items(self, items):
        self.items = items
        self.page = 0
        self.total_pages = max(1, math.ceil(len(items) / self.page_size))
        self.render()

# ─── Sign Up Page ─────────────────────────────────────────────────────────────
class SignUpPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Account")
        self.root.geometry("520x620+400+60")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self.root, bg=ACCENT, height=60)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🎬  CREATE ACCOUNT", bg=ACCENT, fg=TEXT,
                 font=("Georgia", 14, "bold")).pack(expand=True)

        scroll = ScrollableFrame(self.root, bg=BG)
        scroll.pack(fill="both", expand=True)
        body = scroll.inner
        body.config(bg=BG)

        def field(label, placeholder, show=None):
            tk.Label(body, text=label, bg=BG, fg=TEXT2, font=FONT_SMALL,
                     anchor="w").pack(fill="x", padx=30, pady=(12, 2))
            frm, ent = make_entry(body, placeholder, show=show)
            frm.pack(fill="x", padx=30)
            return ent

        self.firstname = field("FIRST NAME", "Enter first name")
        self.lastname  = field("LAST NAME",  "Enter last name")
        self.email     = field("EMAIL",      "your@email.com")
        self.username  = field("USERNAME",   "Choose a username")
        self.password  = field("PASSWORD",   "Min 6 characters", show="*")

        # Gender
        tk.Label(body, text="GENDER", bg=BG, fg=TEXT2, font=FONT_SMALL,
                 anchor="w").pack(fill="x", padx=30, pady=(12, 2))
        gframe = tk.Frame(body, bg=BG); gframe.pack(fill="x", padx=30)
        self.gender = tk.StringVar(value="male")
        for val, lbl in [("male", "♂  Male"), ("female", "♀  Female")]:
            rb = tk.Radiobutton(gframe, text=lbl, variable=self.gender, value=val,
                                bg=BG, fg=TEXT, selectcolor=BG3, activebackground=BG,
                                font=FONT_BODY)
            rb.pack(side="left", padx=10)

        # Terms
        self.agreed = tk.BooleanVar()
        check_frame = tk.Frame(body, bg=BG); check_frame.pack(fill="x", padx=30, pady=16)
        tk.Checkbutton(check_frame, text=" I agree to the Terms & Conditions",
                       variable=self.agreed, bg=BG, fg=TEXT2, selectcolor=BG3,
                       activebackground=BG, font=FONT_BODY).pack(side="left")

        separator(body)

        btn = make_btn(body, "CREATE ACCOUNT", self._signup, color=ACCENT)
        btn.pack(fill="x", padx=30, pady=(0, 20))

        self.msg_var = tk.StringVar()
        self.msg_lbl = tk.Label(body, textvariable=self.msg_var, bg=BG, fg=ACCENT2,
                                font=FONT_BODY, wraplength=400)
        self.msg_lbl.pack(padx=30, pady=4)

    def _get(self, entry):
        v = entry.get()
        if hasattr(entry, '_placeholder') or hasattr(entry, 'master'):
            # check placeholder
            pass
        return v.strip()

    def _signup(self):
        if not self.agreed.get():
            self.msg_var.set("⚠  Please agree to the terms first."); return

        fn = self.firstname.get().strip()
        ln = self.lastname.get().strip()
        em = self.email.get().strip()
        un = self.username.get().strip()
        pw = self.password.get().strip()

        # Strip placeholders
        placeholders = {"Enter first name", "Enter last name", "your@email.com",
                        "Choose a username", "Min 6 characters"}
        if any(v in placeholders or not v for v in [fn, ln, em, un, pw]):
            self.msg_var.set("⚠  Please fill in all fields."); return
        if len(pw) < 6:
            self.msg_var.set("⚠  Password must be at least 6 characters."); return

        try:
            db = get_db(); cr = db.cursor()
            cr.execute("SELECT id FROM accounts WHERE username=?", (un,))
            if cr.fetchone():
                self.msg_var.set("⚠  Username already taken."); db.close(); return
            cr.execute("""INSERT INTO accounts (firstname,lastname,gender,email,username,password)
                          VALUES (?,?,?,?,?,?)""", (fn, ln, self.gender.get(), em, un, pw))
            db.commit(); db.close()
            self.msg_var.set("✓  Account created! You can now log in.")
            self.msg_lbl.config(fg=GREEN)
            self.root.after(1500, self.root.destroy)
        except Exception as ex:
            self.msg_var.set(f"Error: {ex}")


# ─── Main App ─────────────────────────────────────────────────────────────────
class MoviesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 CineMatch — Movie Recommendations")
        self.root.geometry("1100x750+80+20")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.current_user = None
        init_db()
        self._build_login()

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    def _build_login(self):
        self._clear_root()

        # Left panel — branding
        left = tk.Frame(self.root, bg=ACCENT, width=360)
        left.pack(side="left", fill="y"); left.pack_propagate(False)

        tk.Frame(left, bg=ACCENT).pack(expand=True)
        tk.Label(left, text="🎬", bg=ACCENT, fg=TEXT, font=("Helvetica", 56)).pack()
        tk.Label(left, text="CineMatch", bg=ACCENT, fg=TEXT, font=FONT_LARGE).pack(pady=(0, 4))
        tk.Label(left, text="Your personal movie universe", bg=ACCENT, fg=TEXT,
                 font=("Georgia", 11, "italic")).pack()

        separator(left, color="#FF6B6B", pady=20)

        for line in ["🤖  AI-powered recommendations",
                     "📋  Watchlist & History",
                     "🔍  Smart search with filters"]:
            tk.Label(left, text=line, bg=ACCENT, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(padx=30, pady=3, fill="x")

        tk.Frame(left, bg=ACCENT).pack(expand=True)

        # Right panel — form
        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        center = tk.Frame(right, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="WELCOME BACK", bg=BG, fg=ACCENT, font=("Georgia", 20, "bold")).pack()
        tk.Label(center, text="Sign in to continue", bg=BG, fg=TEXT3,
                 font=("Georgia", 10, "italic")).pack(pady=(4, 24))

        # Username
        tk.Label(center, text="USERNAME", bg=BG, fg=TEXT2, font=FONT_SMALL).pack(anchor="w")
        _, self.login_user = make_entry(center, "Enter your username")
        _.config(width=320); _.pack(pady=(4, 16))

        # Password
        tk.Label(center, text="PASSWORD", bg=BG, fg=TEXT2, font=FONT_SMALL).pack(anchor="w")
        _, self.login_pass = make_entry(center, "Enter your password", show="*")
        _.config(width=320); _.pack(pady=(4, 24))

        self.login_msg = tk.Label(center, text="", bg=BG, fg=ACCENT2, font=FONT_BODY)
        self.login_msg.pack(pady=(0, 8))

        btn_login = make_btn(center, "SIGN IN", self._do_login)
        btn_login.config(width=320, height=44); btn_login.pack()

        separator(center, pady=16)

        row = tk.Frame(center, bg=BG); row.pack()
        tk.Label(row, text="Don't have an account? ", bg=BG, fg=TEXT2,
                 font=FONT_BODY).pack(side="left")
        link = tk.Label(row, text="Sign up", bg=BG, fg=ACCENT,
                        font=(FONT_BODY[0], FONT_BODY[1], "bold", "underline"),
                        cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._open_signup())

        self.root.bind("<Return>", lambda e: self._do_login())

    def _do_login(self):
        u = self.login_user.get().strip()
        p = self.login_pass.get().strip()
        placeholders = {"Enter your username", "Enter your password"}
        if u in placeholders or p in placeholders or not u or not p:
            self.login_msg.config(text="⚠  Please enter username and password."); return
        db = get_db(); cr = db.cursor()
        cr.execute("SELECT * FROM accounts WHERE username=? AND password=?", (u, p))
        row = cr.fetchone(); db.close()
        if row:
            self.current_user = u
            self._build_main()
        else:
            self.login_msg.config(text="✕  Incorrect username or password.")

    def _open_signup(self):
        w = tk.Toplevel(self.root)
        SignUpPage(w)

    # ── MAIN APP ──────────────────────────────────────────────────────────────
    def _build_main(self):
        self._clear_root()
        self.root.unbind("<Return>")

        # Top nav bar
        navbar = tk.Frame(self.root, bg=BG2, height=56)
        navbar.pack(fill="x"); navbar.pack_propagate(False)

        tk.Label(navbar, text="🎬 CineMatch", bg=BG2, fg=ACCENT,
                 font=("Georgia", 14, "bold")).pack(side="left", padx=20)

        nav_right = tk.Frame(navbar, bg=BG2); nav_right.pack(side="right", padx=20)
        tk.Label(nav_right, text=f"👤  {self.current_user}", bg=BG2, fg=TEXT2,
                 font=FONT_BODY).pack(side="left", padx=12)
        make_btn(nav_right, "Log out", self._logout, color=BG3, fg=TEXT2).pack(side="left")

        separator(self.root, color=BORDER, pady=0)

        # 3-column layout
        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True)

        # ── Left Column: Search & Suggestions ────────────────────────────────
        left_col = tk.Frame(content, bg=BG2, width=370)
        left_col.pack(side="left", fill="y"); left_col.pack_propagate(False)

        # Search bar
        search_box = tk.Frame(left_col, bg=BG3, pady=12, padx=12)
        search_box.pack(fill="x")

        tk.Label(search_box, text="SEARCH MOVIES", bg=BG3, fg=TEXT3,
                 font=("Helvetica", 8, "bold")).pack(anchor="w", pady=(0, 4))

        row = tk.Frame(search_box, bg=BG3); row.pack(fill="x")
        _, self.search_entry = make_entry(row, "Search by title…")
        _.pack(side="left", fill="x", expand=True, padx=(0, 6))

        make_btn(row, "🔍", self._search, color=ACCENT, width=40).pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self._search())

        # Suggest button
        suggest_btn = tk.Frame(left_col, bg=BG2, pady=8, padx=12)
        suggest_btn.pack(fill="x")
        make_btn(suggest_btn, "✨  Get Recommendations", self._suggest,
                 color="#2D2D5E").pack(fill="x")

        # Results header
        self.results_header = tk.Label(left_col, text="RESULTS  (0)", bg=BG2, fg=TEXT3,
                                       font=("Helvetica", 8, "bold"), anchor="w")
        self.results_header.pack(fill="x", padx=14, pady=(6, 2))

        separator(left_col, color=BORDER, pady=0)

        # Paginated list
        self.search_list_frame = tk.Frame(left_col, bg=BG2)
        self.search_list_frame.pack(fill="both", expand=True)
        self._search_paginator = None

        # ── Middle Column: Watchlist ──────────────────────────────────────────
        mid_col = tk.Frame(content, bg=BG, width=350)
        mid_col.pack(side="left", fill="y"); mid_col.pack_propagate(False)

        tk.Frame(mid_col, bg=BORDER, width=1).pack(side="left", fill="y")

        mid_inner = tk.Frame(mid_col, bg=BG); mid_inner.pack(fill="both", expand=True)

        hdr = tk.Frame(mid_inner, bg=BG3, height=40, pady=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="🔖  WATCHLIST", bg=BG3, fg=GOLD,
                 font=("Helvetica", 9, "bold")).pack(side="left", padx=12, expand=True)
        self.wl_count = tk.Label(hdr, text="0", bg=ACCENT, fg=TEXT,
                                  font=("Helvetica", 9, "bold"), padx=6)
        self.wl_count.pack(side="right", padx=8, pady=8)

        wl_scroll = ScrollableFrame(mid_inner, bg=BG)
        wl_scroll.pack(fill="both", expand=True)
        self.watchlist_frame = wl_scroll.inner

        # ── Right Column: Watched ─────────────────────────────────────────────
        right_col = tk.Frame(content, bg=BG)
        right_col.pack(side="left", fill="both", expand=True)

        tk.Frame(right_col, bg=BORDER, width=1).pack(side="left", fill="y")

        right_inner = tk.Frame(right_col, bg=BG); right_inner.pack(fill="both", expand=True)

        hdr2 = tk.Frame(right_inner, bg=BG3, height=40, pady=0)
        hdr2.pack(fill="x"); hdr2.pack_propagate(False)
        tk.Label(hdr2, text="✓  WATCHED", bg=BG3, fg=GREEN,
                 font=("Helvetica", 9, "bold")).pack(side="left", padx=12, expand=True)
        self.wd_count = tk.Label(hdr2, text="0", bg=GREEN, fg="#000",
                                  font=("Helvetica", 9, "bold"), padx=6)
        self.wd_count.pack(side="right", padx=8, pady=8)

        wd_scroll = ScrollableFrame(right_inner, bg=BG)
        wd_scroll.pack(fill="both", expand=True)
        self.watched_frame = wd_scroll.inner

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready  •  Welcome back, " + self.current_user,
                                   bg=BG3, fg=TEXT3, font=FONT_SMALL, anchor="w", padx=12, pady=4)
        self.status_bar.pack(fill="x", side="bottom")

        self._refresh_lists()
        self._suggest()

    # ── Actions ───────────────────────────────────────────────────────────────
    def _set_status(self, msg):
        self.status_bar.config(text=msg)

    def _search(self):
        term = self.search_entry.get().strip()
        if term in {"Search by title…", ""}:
            self._set_status("Please enter a search term."); return

        if moviesdata is not None:
            mask = moviesdata['title'].str.contains(term, case=False, na=False)
            results = moviesdata[mask]['title'].tolist()
        else:
            results = []

        self.results_header.config(text=f"RESULTS  ({len(results)})")
        self._set_status(f'Found {len(results)} results for "{term}"')
        self._render_search_results(results)

    def _suggest(self):
        db = get_db(); cr = db.cursor()
        cr.execute("SELECT movie FROM operations WHERE type='Watched' AND username=?",
                   (self.current_user,))
        watched = [r[0] for r in cr.fetchall()]
        db.close()

        if moviesdata is None:
            self._render_search_results([])
            self.results_header.config(text="RESULTS  (0)")
            return

        if not watched:
            idx = random.sample(range(len(moviesdata)), min(40, len(moviesdata)))
            titles = [moviesdata.iloc[i].title for i in idx]
        else:
            titles = self._compute_recommendations(watched)

        self.results_header.config(text=f"SUGGESTIONS  ({len(titles)})")
        self._set_status(f"Showing {len(titles)} recommendations based on your watch history")
        self._render_search_results(titles)

    def _compute_recommendations(self, watched_list):
        if similarity is None or moviesdata is None:
            return []
        watched_lower = [t.lower() for t in watched_list]
        indices = []
        for title in watched_lower:
            try:
                idx = moviesdata[moviesdata['title'].str.lower().str.contains(title, regex=False)].index[0]
                indices.append(idx)
            except IndexError:
                continue
        if not indices:
            return []

        scores = np.zeros(len(moviesdata))
        for idx in indices:
            distances = similarity[idx]
            for i, score in enumerate(distances):
                scores[i] += score

        # Exclude already watched
        watched_titles = set(t.lower() for t in watched_list)
        top = np.argsort(scores)[::-1]
        result = []
        for i in top:
            t = moviesdata.iloc[i].title
            if t.lower() not in watched_titles:
                result.append(t)
            if len(result) >= 40:
                break
        return result

    def _render_search_results(self, titles):
        for w in self.search_list_frame.winfo_children():
            w.destroy()

        if not titles:
            tk.Label(self.search_list_frame, text="No results found",
                     bg=BG2, fg=TEXT3, font=FONT_BODY).pack(pady=20)
            return

        def render_card(parent, title):
            make_movie_card(parent, title,
                            on_watchlist=lambda t=title: self._add_watchlist(t),
                            on_watched=lambda t=title: self._add_watched(t))

        scroll_container = ScrollableFrame(self.search_list_frame, bg=BG2)
        scroll_container.pack(fill="both", expand=True)

        self._search_paginator = Paginator(
            scroll_container.inner, titles, page_size=10,
            render_fn=render_card
        )

    def _add_watchlist(self, movie):
        db = get_db(); cr = db.cursor()
        cr.execute("SELECT id FROM operations WHERE username=? AND type='Watchlist' AND movie=?",
                   (self.current_user, movie))
        if not cr.fetchone():
            cr.execute("INSERT INTO operations (username,type,movie,datetime) VALUES (?,?,?,?)",
                       (self.current_user, "Watchlist", movie, str(datetime.datetime.now())[:19]))
            db.commit()
            self._set_status(f"Added to Watchlist: {movie}")
        else:
            self._set_status(f'"{movie}" is already in your Watchlist')
        db.close()
        self._refresh_lists()

    def _add_watched(self, movie):
        db = get_db(); cr = db.cursor()
        cr.execute("SELECT id FROM operations WHERE username=? AND type='Watched' AND movie=?",
                   (self.current_user, movie))
        if not cr.fetchone():
            cr.execute("INSERT INTO operations (username,type,movie,datetime) VALUES (?,?,?,?)",
                       (self.current_user, "Watched", movie, str(datetime.datetime.now())[:19]))
            # Also remove from watchlist if present
            cr.execute("DELETE FROM operations WHERE username=? AND type='Watchlist' AND movie=?",
                       (self.current_user, movie))
            db.commit()
            self._set_status(f"Marked as watched: {movie}")
        else:
            self._set_status(f'"{movie}" is already in your Watched list')
        db.close()
        self._refresh_lists()

    def _remove_watchlist(self, movie):
        db = get_db(); cr = db.cursor()
        cr.execute("DELETE FROM operations WHERE username=? AND type='Watchlist' AND movie=?",
                   (self.current_user, movie))
        db.commit(); db.close()
        self._set_status(f"Removed from Watchlist: {movie}")
        self._refresh_lists()

    def _remove_watched(self, movie):
        db = get_db(); cr = db.cursor()
        cr.execute("DELETE FROM operations WHERE username=? AND type='Watched' AND movie=?",
                   (self.current_user, movie))
        db.commit(); db.close()
        self._set_status(f"Removed from Watched: {movie}")
        self._refresh_lists()

    def _watchlist_to_watched(self, movie):
        self._remove_watchlist(movie)
        self._add_watched(movie)

    def _refresh_lists(self):
        db = get_db(); cr = db.cursor()

        # Watchlist
        cr.execute("SELECT movie FROM operations WHERE type='Watchlist' AND username=? ORDER BY id DESC",
                   (self.current_user,))
        wl = [r[0] for r in cr.fetchall()]

        # Watched
        cr.execute("SELECT movie FROM operations WHERE type='Watched' AND username=? ORDER BY id DESC",
                   (self.current_user,))
        wd = [r[0] for r in cr.fetchall()]
        db.close()

        # Render watchlist
        for w in self.watchlist_frame.winfo_children():
            w.destroy()
        self.wl_count.config(text=str(len(wl)))
        for movie in wl:
            make_movie_card(self.watchlist_frame, movie,
                            on_watched=lambda m=movie: self._watchlist_to_watched(m),
                            on_remove=lambda m=movie: self._remove_watchlist(m))

        # Render watched
        for w in self.watched_frame.winfo_children():
            w.destroy()
        self.wd_count.config(text=str(len(wd)))
        for movie in wd:
            make_movie_card(self.watched_frame, movie, badge="Watched",
                            on_remove=lambda m=movie: self._remove_watched(m))

    def _logout(self):
        self.current_user = None
        self._build_login()

    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()


# ─── Launch ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = MoviesApp(root)

    # Style ttk scrollbars if possible
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar", background=CARD, troughcolor=BG2,
                    arrowcolor=TEXT3, borderwidth=0)
    root.mainloop()