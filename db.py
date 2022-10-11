import sqlite3

class Database:
    """ 
    Database class for communication with SQLite database

    """

    def __init__(self, db):
        """
        Initialization of Database object creates required tables for use with simpletime.py
        """
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS employees (
            empid INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL CHECK (username <> ""), 
            firstname TEXT NOT NULL CHECK (firstname <> ""), 
            lastname TEXT NOT NULL CHECK (lastname <> ""), 
            password TEXT NOT NULL CHECK (password <> ""), 
            admin BOOLEAN NOT NULL CHECK (admin IN (0,1)))"""
            )

        self.cur.execute("""CREATE TABLE IF NOT EXISTS shifts (
            shiftid INTEGER PRIMARY KEY, 
            empid INTEGER,
            shift_start INTEGER, 
            shift_end INTEGER,
            FOREIGN KEY(empid) REFERENCES employees(empid))"""
            )

        self.cur.execute("""CREATE TABLE IF NOT EXISTS breaks (
            breakid INTEGER PRIMARY KEY,
            empid INTEGER,
            shiftid INTEGER,
            breaktype TEXT NOT NULL CHECK (breaktype IN ("lunch","break")),
            break_start INTEGER,
            break_end INTEGER,
            FOREIGN KEY(empid) REFERENCES employees(empid),
            FOREIGN KEY(shiftid) REFERENCES shifts(shiftid))"""
            )

        self.conn.commit()

    def register(self, username, firstname, lastname, password, admin):

        """ 
        Function to add new user into database. See register_user function in simpletime

        Args:
            username (str): Username retrieved from simpletime text entry
            firstname (str) : User First Name from simpletime text entry
            lastname (str) : User Last Name from simpletime text entry
            password (str) : User password from simpletime text entry
            admin (bool) : Boolean value for user admin status from simpletime checkbox

        Returns:
            None : registration is successful
            1 : registration was not successful
        """
        try:
            self.cur.execute("INSERT INTO employees VALUES (NULL, ?, ?, ?, ?, ?)", (username, firstname, lastname, password, admin))
            self.conn.commit()
            return None
        except:
            return 1

    def login(self, username, password):
        """
        login function to validate user with database records

        Args:
            username (str): Username retrieved from simpletime text entry
            password (str): Password retrieved from simpletime text entry

        Returns:
            row (tuple) : Row containing employee information for use in creating Employee instance in simpletime
        """

        self.cur.execute("SELECT * FROM employees WHERE username = ? AND password = ?", (username,password))
        row = self.cur.fetchone()
        return row

    def start_shift(self, empid):
        """
        start_shift function to start a shift given employee id

        Args:
            empid (int): employee id to be related to shift

        Returns:
            current_shift int: int value of current_shift's shiftid 
        """

        self.cur.execute("INSERT INTO shifts VALUES (NULL, ?, strftime('%s', 'now', 'localtime'), NULL)", (empid,))
        self.conn.commit()
        current_shift = self.cur.lastrowid
        return current_shift

    def end_shift(self, shiftid):
        """
        end_shift function to end the current shift. Note: shift is already associated with employee.

        Args:
            shiftid (int): value to search for current_shift and update endtime column
        """
        self.cur.execute("UPDATE shifts SET shift_end = strftime('%s', 'now', 'localtime') WHERE shiftid = ?", (shiftid,))
        self.conn.commit()

    def start_break(self, empid, shiftid):
        """start_break function to start a break. employee must be working a shift to start a break as breaks are associated to a shift.

        Args:
            empid (int): employee id to be related to break
            shiftid (int): shift id to be related to break

        Returns:
            current_break (int): primary key representing current break to be used for ending the break
        """
        self.cur.execute("INSERT INTO breaks VALUES (NULL, ?, ?, 'break', strftime('%s', 'now', 'localtime'), NULL)", (empid, shiftid))
        self.conn.commit()
        current_break = self.cur.lastrowid
        return current_break

    def end_break(self, breakid):
        """end_break function to end break given breakid

        Args:
            breakid (int): break id corresponding to current break to be ended
        """
        self.cur.execute("UPDATE breaks SET break_end = strftime('%s', 'now', 'localtime') WHERE breakid = ?", (breakid,))
        self.conn.commit()
        
    def start_lunch(self, empid, shiftid):
        """start_lunch function to start a lunch break. This function is essentially the same as the start_break function

        Args:
            empid (int): employee id to be related to lunch
            shiftid (int): shift id to be related to lunch

        Returns:
            current_lunch (int): primary key representing current lunch to be used for ending the lunch
        """
        self.cur.execute("INSERT INTO breaks VALUES (NULL, ?, ?, 'lunch', strftime('%s', 'now', 'localtime'), NULL)", (empid, shiftid))
        current_lunch = self.cur.lastrowid
        self.conn.commit()
        return current_lunch

    def end_lunch(self, breakid):
        """end_lunch function to end lunch given breakid

        Args:
            breakid (int): breakid corresponding to active lunch to be ended
        """
        
        self.cur.execute("UPDATE breaks SET break_end = strftime('%s', 'now', 'localtime') WHERE breakid = ?", (breakid,))
        self.conn.commit()

    def shift_report(self, empid, shiftid):

        """
        Function for querying database for shift reports. See shift_report_search in simpletime.py

        Args:
            empid (int): employee id used for queries
            shiftid (int): shift id used for queries

        Returns:
            row (tuple) : Row containing shift information for display in simpletime shift report Treeview
        
        """
        if empid == "" and shiftid == "":
            self.cur.execute("""SELECT employees.empid, shifts.shiftid, employees.firstname, employees.lastname, 
            date(shifts.shift_start,'unixepoch'),time(shifts.shift_start,'unixepoch'), time(shifts.shift_end,'unixepoch')
            FROM shifts 
            INNER JOIN employees
            ON employees.empid = shifts.empid """
            )
            rows = self.cur.fetchall()
            return rows
        elif shiftid == "":
            self.cur.execute("""SELECT employees.empid, shifts.shiftid, employees.firstname, employees.lastname, 
            date(shifts.shift_start,'unixepoch'),time(shifts.shift_start,'unixepoch'), time(shifts.shift_end,'unixepoch')
            FROM shifts 
            INNER JOIN employees
            ON employees.empid = shifts.empid
            WHERE shifts.empid = ?""", (empid,))
            rows = self.cur.fetchall()
            return rows
        elif empid == "":
            self.cur.execute("""SELECT employees.empid, shifts.shiftid, employees.firstname, employees.lastname, 
            date(shifts.shift_start,'unixepoch'),time(shifts.shift_start,'unixepoch'), time(shifts.shift_end,'unixepoch'), breaks.breakid, breaks.breaktype, time(breaks.break_start,'unixepoch'), time(breaks.break_end,'unixepoch')
            FROM shifts 
            INNER JOIN employees
            ON employees.empid = shifts.empid
            LEFT JOIN breaks
            ON shifts.shiftid = breaks.shiftid
            WHERE shifts.shiftid = ?""", (shiftid,))
            rows = self.cur.fetchall()
            return rows
        else:
            self.cur.execute("""SELECT employees.empid, shifts.shiftid, employees.firstname, employees.lastname, 
            date(shifts.shift_start,'unixepoch'),time(shifts.shift_start,'unixepoch'), time(shifts.shift_end,'unixepoch'), breaks.breakid, breaks.breaktype, time(breaks.break_start,'unixepoch'), time(breaks.break_end,'unixepoch')
            FROM shifts 
            INNER JOIN employees
            ON employees.empid = shifts.empid
            LEFT JOIN breaks
            ON shifts.shiftid = breaks.shiftid
            WHERE shifts.empid = ? AND shifts.shiftid = ?""", (empid,shiftid))
            rows = self.cur.fetchall()
            return rows

#Can run below to instantiate a database with two test users and a test shift
#db = Database('timeclockdb.db')

#db.register("marcos","Marcos", "Espinosa", "123", 1)
#db.register("test","Winnie", "Espinosa", "123", 0)
#db.start_shift(1)
#db.end_shift(1)
#db.start_break(1,1)
#db.end_break(1)
