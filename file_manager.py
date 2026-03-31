import sqlite3

from app import MainWindow
from records import Employee, EmployeeReviewsDB, EmployeeTrainingDB, EmployeePointsDB, EmployeePTODB, EmployeeNotesDB, EmployeeReview, EmployeeTrainingDate, EmployeePoint, EmployeePTORange, EmployeeNote, HolidayObservance
import datetime
# from records import Material, Mixture, Package, Part

class FileManager:
    def __init__(self, mainApp: MainWindow) -> None:
        self.mainApp = mainApp
        self.filePath = None
        self.dbFile = None

    def initFile(self):
        assert(not self.filePath == None)
        EXPECTED_TABLES = {"globals", "employees", "reviews", "training", "attendance", "PTO", "notes", "holidays", "observances"}
        try:
            self.dbFile = sqlite3.connect(self.filePath)
            res = self.dbFile.execute("SELECT name FROM sqlite_master")
            tables = [row[0] for row in res.fetchall()]
            tableNames = set([t for t in tables if not t.startswith("sqlite_")])
            print(f"Initialization: found {len(tables)} entries, tables: {tableNames}")

            if len(tables) == 0:
                self.dbFile.execute("CREATE TABLE globals(name PRIMARY KEY, value)") # Future proofing
                self.dbFile.execute("CREATE TABLE employees(idNum PRIMARY KEY, lastName, firstName, anniversary, role, shift, addressLine1, addressLine2, addressCity, addressState, addressZip, addressTel, addressEmail, status)")
                self.dbFile.execute("CREATE TABLE reviews(idNum, date, nextReview, details, UNIQUE(idNum, date))")
                self.dbFile.execute("CREATE TABLE training(idNum, training, date, comment, UNIQUE(idNum, training, date))")
                self.dbFile.execute("CREATE TABLE attendance(idNum, date, reason, value, UNIQUE(idNum, date))")
                self.dbFile.execute("CREATE TABLE PTO(idNum, start, end, hours, UNIQUE(idNum, start, end))")
                self.dbFile.execute("CREATE TABLE notes(idNum, date, time, details, UNIQUE(idNum, date, time))")
                self.dbFile.execute("CREATE TABLE holidays(holiday PRIMARY KEY, month)")
                self.dbFile.execute("CREATE TABLE observances(holiday, shift, date, UNIQUE(holiday, shift, date))")
                self.dbFile.execute("INSERT INTO globals VALUES ('db_version', '2')")
                self.dbFile.commit()
                return True
            elif EXPECTED_TABLES.issubset(tableNames):
                return True
            elif (EXPECTED_TABLES - {"notes"}).issubset(tableNames) and "notes" not in tableNames:
                print(f"Migration: adding notes table to {self.filePath}")
                self.dbFile.execute("CREATE TABLE notes(idNum, date, time, details, UNIQUE(idNum, date, time))")
                self.dbFile.execute("INSERT OR REPLACE INTO globals VALUES ('db_version', '2')")
                self.dbFile.commit()
                return True
            else:
                print(f"Initialization error: wrong tables in {self.filePath}")
                print(f" * Expected: {", ".join(sorted(EXPECTED_TABLES))}")
                print(f" * Found: {", ".join(sorted(tableNames))}")
                self.dbFile.close()
                return False
        except Exception as e:
            print(f"Initialization error: {repr(e)}")
            self.dbFile.close()
            return False

    def saveFile(self):
        assert((not self.filePath == None) and (not self.dbFile == None))
        db = self.mainApp.db
        print(f"Saving globals to {self.filePath}")
        # Future proofing

        #####

        print(f"Saving employees to {self.filePath}")
        for idNum in db.employees:
            vals = db.employees[idNum].getTuple()
            try:
                self.dbFile.execute("INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", vals)
                print(f" * Saving {vals}")
            except Exception as e:
                print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum FROM employees")
        deleted = [vals for vals in res.fetchall() if not vals[0] in db.employees]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM employees WHERE idNum=?", deleted)
                print(f" * Deleting old entries {", ".join([f"{idNum[0]}" for idNum in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"{idNum[0]}" for idNum in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving reviews to {self.filePath}")
        for idNum in db.reviews:
            valsList = db.reviews[idNum].getTuples()
            for vals in valsList:
                try:
                    self.dbFile.execute("INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?)", vals)
                    print(f" * Saving {vals}")
                except Exception as e:
                    print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum, date FROM reviews")

        deleted = [vals for vals in res.fetchall() if not vals[0] in db.reviews or not datetime.date.fromisoformat(vals[1]) in db.reviews[vals[0]].reviews]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM reviews WHERE (idNum, date)=(?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({vals[0]}, {vals[1]})" for vals in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({vals[0]}, {vals[1]})" for vals in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving training to {self.filePath}")
        for idNum in db.training:
            valsList = db.training[idNum].getTuples()
            for vals in valsList:
                try:
                    self.dbFile.execute("INSERT OR REPLACE INTO training VALUES (?, ?, ?, ?)", vals)
                    print(f" * Saving {vals}")
                except Exception as e:
                    print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum, training, date FROM training")

        deleted = [vals for vals in res.fetchall() if not vals[0] in db.training or not vals[1] in db.training[vals[0]].training or not datetime.date.fromisoformat(vals[2]) in db.training[vals[0]].training[vals[1]]]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM training WHERE (idNum, training, date)=(?, ?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[2]})" for vals in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[1]})" for vals in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving attendance to {self.filePath}")
        for idNum in db.attendance:
            valsList = db.attendance[idNum].getTuples()
            for vals in valsList:
                try:
                    self.dbFile.execute("INSERT OR REPLACE INTO attendance VALUES (?, ?, ?, ?)", vals)
                    print(f" * Saving {vals}")
                except Exception as e:
                    print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum, date FROM attendance")

        deleted = [vals for vals in res.fetchall() if not vals[0] in db.attendance or not datetime.date.fromisoformat(vals[1]) in db.attendance[vals[0]].points]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM attendance WHERE (idNum, date)=(?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({vals[0]}, {vals[1]})" for vals in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({vals[0]}, {vals[1]})" for vals in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving PTO to {self.filePath}")
        for idNum in db.PTO:
            valsList = db.PTO[idNum].getTuples()
            for vals in valsList:
                try:
                    self.dbFile.execute("INSERT OR REPLACE INTO PTO VALUES (?, ?, ?, ?)", vals)
                    print(f" * Saving {vals}")
                except Exception as e:
                    print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum, start, end FROM PTO")

        deleted = [vals for vals in res.fetchall() if not vals[0] in db.PTO or not (datetime.date.fromisoformat(vals[1]), vals[2] if vals[2] in ["CARRY", "CASH", "DROP"] else datetime.date.fromisoformat(vals[2])) in db.PTO[vals[0]].PTO]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM PTO WHERE (idNum, start, end)=(?, ?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[2]})" for vals in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[1]})" for vals in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving notes to {self.filePath}")
        for idNum in db.notes:
            valsList = db.notes[idNum].getTuples()
            for vals in valsList:
                try:
                    self.dbFile.execute("INSERT OR REPLACE INTO notes VALUES (?, ?, ?, ?)", vals)
                    print(f" * Saving {vals}")
                except Exception as e:
                    print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT idNum, date, time FROM notes")

        deleted = [vals for vals in res.fetchall() if not vals[0] in db.notes or not (datetime.date.fromisoformat(vals[1]), vals[2]) in db.notes[vals[0]].notes]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM notes WHERE (idNum, date, time)=(?, ?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[2]})" for vals in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({vals[0]}, {vals[1]}, {vals[2]})" for vals in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving holidays to {self.filePath}")
        for vals in db.holidays.getDefaultTuples():
            try:
                self.dbFile.execute("INSERT OR REPLACE INTO holidays VALUES (?, ?)", vals)
                print(f" * Saving {vals}")
            except Exception as e:
                print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT holiday FROM holidays")
        deleted = [vals for vals in res.fetchall() if not vals[0] in db.holidays.defaults]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM holidays WHERE holiday=?", deleted)
                print(f" * Deleting old entries {", ".join([f"{holiday[0]}" for holiday in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"{holiday[0]}" for holiday in deleted])}: {repr(e)}")
        self.dbFile.commit()

        #####

        print(f"Saving observances to {self.filePath}")
        for vals in db.holidays.getObservanceTuples():
            try:
                self.dbFile.execute("INSERT OR REPLACE INTO observances VALUES (?, ?, ?)", vals)
                print(f" * Saving {vals}")
            except Exception as e:
                print(f" * Error saving {vals}: {repr(e)}")
        self.dbFile.commit()

        res = self.dbFile.execute(f"SELECT holiday, shift, date FROM observances")
        deleted = [vals for vals in res.fetchall() if not datetime.date.fromisoformat(vals[2]).year in db.holidays.observances or
                                                      not vals[0] in db.holidays.observances[datetime.date.fromisoformat(vals[2]).year] or
                                                      not vals[1] in db.holidays.observances[datetime.date.fromisoformat(vals[2]).year][vals[0]] or
                                                      not db.holidays.observances[datetime.date.fromisoformat(vals[2]).year][vals[0]][vals[1]].date.isoformat() == vals[2]]
        if len(deleted) > 0:
            try:
                res.executemany(f"DELETE FROM observances WHERE (holiday, shift, date)=(?, ?, ?)", deleted)
                print(f" * Deleting old entries {", ".join([f"({observance[0]}, {observance[1]}, {observance[2]})" for observance in deleted])}")
            except Exception as e:
                print(f" * Error deleting old entries {", ".join([f"({observance[0]}, {observance[1]}, {observance[2]})" for observance in deleted])}: {repr(e)}")
        self.dbFile.commit()

    def loadFile(self):
        assert((not self.filePath == None) and (not self.dbFile == None))
        from records import emptyDB
        self.mainApp.db = emptyDB()
        db = self.mainApp.db

        print(f"Loading globals from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM globals")
        for pair in res.fetchall():
            name, val = pair
            # Future proofing
            print(f" * Loaded {name} = {val}")

        #####

        print(f"Loading employees from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM employees")
        for values in res.fetchall():
            employee = Employee()
            employee.fromTuple(values)
            
            db.addEmployee(employee)
            reviews = EmployeeReviewsDB(employee.idNum)
            db.addEmployeeReviews(reviews)
            training = EmployeeTrainingDB(employee.idNum)
            db.addEmployeeTraining(training)
            points = EmployeePointsDB(employee.idNum)
            db.addEmployeePoints(points)
            PTO = EmployeePTODB(employee.idNum)
            db.addEmployeePTO(PTO)
            notes = EmployeeNotesDB(employee.idNum)
            db.addEmployeeNotes(notes)

            print(f" * Loaded {values}")
            print(f" --> Loaded employee {employee.idNum}")

        #####

        print(f"Loading reviews from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM reviews")
        for values in res.fetchall():
            review = EmployeeReview()
            review.fromTuple(values)
            
            assert(review.idNum in db.reviews)
            db.reviews[review.idNum].reviews[review.date] = review

            print(f" * Loaded {values}")
            print(f" --> Loaded review ({review.idNum}, {review.date})")

        #####

        print(f"Loading training from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM training")
        for values in res.fetchall():
            training = EmployeeTrainingDate()
            training.fromTuple(values)
            
            assert(training.idNum in db.training)
            if not training.training in db.training[training.idNum].training:
                db.training[training.idNum].training[training.training] = {}
            db.training[training.idNum].training[training.training][training.date] = training

            print(f" * Loaded {values}")
            print(f" --> Loaded training ({training.idNum}, {training.training}, {training.date})")

        #####

        print(f"Loading attendance from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM attendance")
        for values in res.fetchall():
            point = EmployeePoint()
            point.fromTuple(values)
            
            assert(point.idNum in db.attendance)
            db.attendance[point.idNum].points[point.date] = point

            print(f" * Loaded {values}")
            print(f" --> Loaded point ({point.idNum}, {point.date})")

        #####

        print(f"Loading PTO from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM PTO")
        for values in res.fetchall():
            pto = EmployeePTORange()
            pto.fromTuple(values)
            
            assert(pto.employee in db.PTO)
            db.PTO[pto.employee].PTO[(pto.start, pto.end)] = pto

            print(f" * Loaded {values}")
            print(f" --> Loaded point ({pto.employee}, {pto.start}, {pto.end})")

        #####

        print(f"Loading notes from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM notes")
        for values in res.fetchall():
            note = EmployeeNote()
            note.fromTuple(values)

            assert(note.idNum in db.notes)
            db.notes[note.idNum].notes[(note.date, note.time)] = note

            print(f" * Loaded {values}")
            print(f" --> Loaded note ({note.idNum}, {note.date}, {note.time})")

        #####

        print(f"Loading holidays from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM holidays")
        for values in res.fetchall():
            holiday = values[0]
            month = values[1]

            db.holidays.defaults[holiday] = month

            print(f" * Loaded {values}")
            print(f" --> Loaded holiday {holiday}")

        #####

        print(f"Loading observances from {self.filePath}")
        res = self.dbFile.execute("SELECT * FROM observances")
        for values in res.fetchall():
            observance = HolidayObservance()
            observance.fromTuple(values)

            db.holidays.setObservance(observance)

            print(f" * Loaded {values}")
            print(f" --> Loaded observance ({observance.holiday}, {observance.date.isoformat()}, {observance.shift})")

    def setFile(self, filePath):
        oldPath = self.filePath
        oldConn = self.dbFile
        self.filePath = filePath
        success = self.initFile()
        if success:
            if not oldConn == None:
                oldConn.close()
        else:
            print(f"Failed to initialize {filePath}")
            self.filePath = oldPath
            self.dbFile = oldConn
        return success