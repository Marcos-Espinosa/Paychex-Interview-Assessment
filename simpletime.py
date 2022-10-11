from tkinter import *
import tkinter.messagebox as messagebox
from datetime import datetime
from tkinter.ttk import Treeview
from db import Database


#Establish database for use with this application. Change filename if needed.
db = Database('timeclockdb.db')

class Employee():

    """ 
    Employee class used following log in verification. 
    
    Class properties includes employee information corresponding to database and bool variables for decision making.

    Class methods connect to database to perform clock in/clock out etc. functions.

    Tkinter message boxes used here for confirmation rather than augmenting the relevant TopLevel screens.

    """
    
    def __init__(self,empID,firstname, lastname, admin: bool, working=False,onbreak=False,onlunch=False,):

        self.empID = empID
        self.firstname = firstname
        self.lastname = lastname
        self.admin = admin
        self.working = working
        self.onbreak = onbreak
        self.onlunch = onlunch
        self.current_shift = ''
        self.current_break = ''
        self.current_lunch = ''

        
    def clock_in(self):

        if not self.working:
            self.working = True
            self.current_shift = db.start_shift(self.empID)
            messagebox.showinfo("Shift started", "Successfully clocked in at " + datetime.now().strftime("%H:%M"))
        else:
            messagebox.showerror("Clock In Error", "You are already clocked in")
        
    
    def clock_out(self):
        if self.working and (not self.onbreak and not self.onlunch or self.admin):
            self.working = False
            db.end_shift(self.current_shift)
            messagebox.showinfo("Clocked Out", "Successfully clocked out at " + datetime.now().strftime("%H:%M"))
        elif self.onbreak:
            messagebox.showerror("Clock Out Error", "Clock Out Error.\nPlease end your break before clocking out.")
        elif self.onlunch:
            messagebox.showerror("Clock Out Error", "Clock Out Error.\nPlease end your lunch before clocking out.")
        else:
           messagebox.showerror("Clock Out Error", "You must be clocked in to be able to clock out")
    
    def take_break(self):
        if (self.working and not self.onbreak and not self.onlunch) or self.admin:
            self.onbreak = True
            self.current_break = db.start_break(self.empID,self.current_shift)
            messagebox.showinfo("Break Start", "Successfully started break at " + datetime.now().strftime("%H:%M"))

        elif not self.working:
            messagebox.showerror("Break Error", "You must be clocked in to be able to take a break")

        elif self.onlunch:
            messagebox.showerror("Break Error", "You are on currently on lunch. Unable to take break")

        else:
            messagebox.showerror("Break Error", "You are already on break")
    
    def end_break(self):
        if self.onbreak:
            self.onbreak = False
            db.end_break(self.current_break)
            messagebox.showinfo("Break Ended", "Successfully ended break at " + datetime.now().strftime("%H:%M"))
        else:
            messagebox.showerror("Break Error", "You are not currently taking a break")
            
    def take_lunch(self):
        if (self.working and not self.onbreak and not self.onlunch) or self.admin:
            self.onlunch = True
            self.current_lunch = db.start_lunch(self.empID, self.current_shift)
            messagebox.showinfo("Lunch Start", "Successfully started lunch at " + datetime.now().strftime("%H:%M"))
        elif not self.working:
            messagebox.showerror("Lunch Error", "You must be clocked in to be able to take a lunch")
        elif self.onbreak:
            messagebox.showerror("Lunch Error", "You are currently on break. Unable to take a lunch")
        else:
            messagebox.showerror("Lunch Error", "You are already on lunch")
    
    def end_lunch(self):
        if self.onlunch:
            self.onlunch = False
            db.end_lunch(self.current_lunch)
            messagebox.showinfo("Lunch Ended", "Successfully ended lunch at " + datetime.now().strftime("%H:%M"))
        else:
            messagebox.showerror("Lunch Error", "You are not currently taking a lunch")

    def get_report(self):
        pass

    def __str__(self):
        return f"Employee ID: {self.empID}\tEmployee Name: {self.firstname} {self.lastname} {self.admin}"

def main_screen(): 
    """
    This function creates the main screen for the application.

    Program is laid out with additional screens as TopLevel objects over the main_screen. Consider using OOP approach for additional screens.
    """
    global screen
    screen = Tk()
    screen.geometry("300x250")
    screen.title("SimpleTime")
    Label(text = "SimpleTime", bg = "grey", width = "300", height = "2", font = ("Calibri", 14)).pack()
    Label(text = "").pack()
    Button(text = "Login", width = "30", height = "2", command = login).pack()
    Label(text = "").pack()
    Button(text = "Register", width = "30", height = "2", command = register).pack()

    screen.mainloop()

def register():

    """ 
    This function generates the Registration Screen as a Toplevel object.

    Global variables are needed for use with register_user function. - Consider using OOP approach and having register_user as a method.
    """

    global screen1 #Consider using OOP approach for TopLevel screens to reduce need for globalized variables.
    screen1 = Toplevel(screen)
    screen1.grab_set()
    screen1.title("Register")
    screen1.geometry("300x300")

    global username
    global firstname
    global lastname
    global password
    global admin

    username = StringVar()
    firstname = StringVar()
    lastname = StringVar()
    password = StringVar()
    admin = IntVar()

    Label(screen1, text = "SimpleTime", bg = "grey", width = "300", height = "2", font = ("Calibri", 14)).pack()
    Label(screen1, text = "Username *").pack()
    username_entry = Entry(screen1, textvariable=username)
    username_entry.pack()
    Label(screen1, text = "First Name *").pack()
    firstname_entry = Entry(screen1, textvariable=firstname)
    firstname_entry.pack()
    Label(screen1, text = "Last Name *").pack()
    lastname_entry = Entry(screen1, textvariable=lastname)
    lastname_entry.pack()
    Label(screen1, text = "Password *").pack()
    password_entry = Entry(screen1, textvariable=password, show="*")
    password_entry.pack()
    admin_entry = Checkbutton(screen1, text = "Admin Account?", variable=admin, onvalue =1, offvalue = 0, height = 1, width = 30)
    admin_entry.pack()
    Button(screen1, text = "Register", width = 10, height =1, command=register_user).pack()
    
def register_user():
    """
    Function to enter user info obtained in registration window as a new user into database

    Consider adding some encryption for storing of password information
    """

    username_info = username.get()
    firstname_info = firstname.get()
    lastname_info = lastname.get()
    password_info = password.get()
    admin_info = admin.get()

    registration = db.register(username = username_info, firstname= firstname_info,lastname = lastname_info, password= password_info,admin = admin_info)

    if registration == 1:
        messagebox.showerror("Registration Error", "Registration Error.\nPlease try again.")
    else:
        screen1.destroy()

        messagebox.showinfo("Registration Successful", "Registration Successful")

def login():
    """
    Function to create log in screen. Used in tandem with login_verify to initiate login session.
    
    """

    global screen2
    screen2 = Toplevel(screen)
    screen2.grab_set()
    screen2.title("Login")
    screen2.geometry("300x250")
    
    global username_verify
    global password_verify

    username_verify = StringVar()
    password_verify = StringVar()

    Label(screen2, text = "SimpleTime", bg = "grey", width = "300", height = "2", font = ("Calibri", 14)).pack()
    Label(screen2, text = "Please enter your login credentials below:").pack()
    Label(screen2, text = "Username *").pack()
    username_entry = Entry(screen2, textvariable = username_verify)
    username_entry.pack()
    Label(screen2, text = "").pack()
    Label(screen2, text = "Password *").pack()
    password_entry = Entry(screen2, textvariable= password_verify, show="*")
    password_entry.pack()
    Label(screen2, text = "").pack()
    Button(screen2, text = "Login", width = 10, height = 1, command = login_verify).pack()
    
def login_verify():
    """
    Function to verify log in. Checks credentials with database information

    Creates instance of Employee class called current_user to be used in the session.

    """

    username_info = username_verify.get()
    password_info = password_verify.get()
    session = db.login(username_info,password_info)

    if session is not None:

        #messagebox.showinfo("Login Successful", "Login Successful")
        global current_user
        current_user = Employee(session[0], session[2], session[3], session[5])
        screen2.destroy()
        timeclock()
    
    else:
        messagebox.showerror("Unsuccessful Login", "Login unsuccesful.\nPlease Try again")

def timeclock():
    """
    Function to create timeclock Toplevel screen following login verification.

    Uses current_user Employee object for button operations

    """

    screen3 = Toplevel(screen)
    screen3.grab_set()
    screen3.title("SimpleTime - Time Clock")
    screen3.geometry("300x500")
    Label(screen3, text = "SimpleTime", bg = "grey", width = "300", height = "2", font = ("Calibri", 14)).pack()
    Label(screen3, text = f"Welcome {current_user.firstname} {current_user.lastname}\nSelect from the below options:").pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "Start Shift", width = 10, height = 1, command = lambda : current_user.clock_in()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "End Shift", width = 10, height = 1, command = lambda : current_user.clock_out()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "Start Break", width = 10, height = 1, command = lambda : current_user.take_break()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "End Break", width = 10, height = 1, command = lambda : current_user.end_break()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "Start Lunch", width = 10, height = 1, command = lambda : current_user.take_lunch()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "End Lunch", width = 10, height = 1, command = lambda : current_user.end_lunch()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "Report", width = 10, height = 1, command = lambda : shift_report()).pack()
    Label(screen3, text = "").pack()
    Button(screen3, text = "Log Out", width = 10, height = 1, command = lambda : screen3.destroy()).pack()
    Label(screen3, text = "").pack()

def shift_report():
    """
    Function to generate shift_report screen. Used in tandem with shift_report_search for querying of database
    Results organized in Treeview object
    """

    if current_user.admin:
        screen4 = Toplevel(screen)
        screen4.grab_set()

        global empid_search
        global shiftid_search

        empid_search = StringVar()
        shiftid_search = StringVar()
        

        #Buttons and Entry fields for shift_report_search function. Note globalization of variables above.

        screen4.title("SimpleTime - Shift Report")
        screen4.geometry("1100x500")
        Label(screen4, text = "SimpleTime", bg = "grey", width = "300", height = "2", font = ("Calibri", 14)).pack()
        Label(screen4, text = "Enter below information to see shift reports").pack()
        Label(screen4, text = "Employee ID").pack()
        empid_search_entry = Entry(screen4, textvariable = empid_search)
        empid_search_entry.pack()
        Label(screen4, text = "").pack()
        Label(screen4, text = "Shift ID").pack()
        shiftid_search_entry = Entry(screen4, textvariable= shiftid_search)
        shiftid_search_entry.pack()
        Button(screen4, text = "Search", width = 10, height = 1, command = lambda : shift_report_search()).pack()
        Label(screen4, text = "").pack()
        Button(screen4, text = "Close", width = 10, height = 1, command = lambda : screen4.destroy()).pack()
        
        #Creation of Treeview object for displaying SQL query results
        global results_box
        columns = ('Employee ID', 'Shift ID', 'First Name', 'Last Name', 'Shift Date', 'Shift Start', 'Shift End', 'Break ID', 'Break Type', 'Break Start', 'Break End')
        results_box = Treeview(screen4, columns = columns, show='headings', height=8)
        
        results_box.column('Employee ID', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Employee ID', text='Employee ID')
        results_box.column('Shift ID', anchor=CENTER, stretch=YES, width=80)
        results_box.heading('Shift ID', text='Shift ID')
        results_box.column('First Name', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('First Name', text='First Name')
        results_box.column('Last Name', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Last Name', text='Last Name')
        results_box.column('Shift Date', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Shift Date', text='Shift Date')
        results_box.column('Shift Start', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Shift Start', text='Shift Start')
        results_box.column('Shift End', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Shift End', text='Shift End')
        results_box.column('Break ID', anchor=CENTER, stretch=YES, width=80)
        results_box.heading('Break ID', text='Break ID')
        results_box.column('Break Type', anchor=CENTER, stretch=YES, width=80)
        results_box.heading('Break Type', text='Break Type')
        results_box.column('Break Start', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Break Start', text='Break Start')
        results_box.column('Break End', anchor=CENTER, stretch=YES, width=100)
        results_box.heading('Break End', text='Break End')

        #Create scrollbar and associate with Treeview object
        scrollbar = Scrollbar(screen4)
        results_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=results_box.yview)
        results_box.pack(fill = X, side=LEFT)
        scrollbar.pack(side=LEFT)
        
    
    else:
        #Only administrators have access to report function
        messagebox.showerror("Report Error", "You do not have sufficient permissions to access this feature.")

def shift_report_search():
    """
    Function that uses values obtained from shift_report to query database.
    Note: if no values entered: db will select all shifts for all employees
    if only one variable is entered e.g. employeeid or shiftid query everything matching entered id
    if both variables entered will find a specific shift with associated breaks
    """
    empid_info = empid_search.get()
    shiftid_info = shiftid_search.get()
    results = db.shift_report(empid_info, shiftid_info)
    results_box.delete(*results_box.get_children())
    for row in results:
        results_box.insert('', END, values=row)

main_screen()
