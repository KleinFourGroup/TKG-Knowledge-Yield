import sqlite3
import datetime
from utils import listToString, stringToList, stringToB64, stringFromB64
import defaults

class Employee:
    def __init__(self) -> None:
        self.idNum: int = None
        self.lastName: str = None
        self.firstName: str = None
        self.anniversary: datetime.date = None

        self.role: str = None
        self.shift: int = None
        self.fullTime: bool = True

        self.addressLine1: str = None
        self.addressLine2: str = None
        self.addressCity: str = None
        self.addressState: str = None
        self.addressZip: str = None
        self.addressTel: str = None
        self.addressEmail: str = None

        self.status: bool = True
    
    def setAnniversary(self, date: datetime.date):
        assert(not date == None)
        self.anniversary = date
    
    def setName(self, lastName: str, firstName: str):
        assert(not lastName == None)
        assert(not firstName == None)
        self.lastName = lastName
        self.firstName = firstName

    def setID(self, num: int):
        assert(not num == None)
        assert(num >= 0)
        self.idNum = num
    
    def setJob(self, role: str, shift: int, fullTime: bool):
        self.role = role
        self.shift = shift
        self.fullTime = fullTime
    
    def setAddress(self, addressLine1: str, addressLine2: str, addressCity: str, addressState: str, addressZip: str, addressTel: str, addressEmail: str):
        self.addressLine1 = addressLine1
        self.addressLine2 = addressLine2
        self.addressCity = addressCity
        self.addressState = addressState
        self.addressZip = addressZip
        self.addressTel = addressTel
        self.addressEmail = addressEmail
    
    def setStatus(self, active: bool = False):
        self.status = active
    
    def getTuple(self):
        return (
            self.idNum,
            self.lastName,
            self.firstName,
            self.anniversary.isoformat(),
            self.role,
            f"{self.shift}|{1 if self.fullTime else 0}",
            self.addressLine1,
            self.addressLine2,
            self.addressCity,
            self.addressState,
            self.addressZip,
            self.addressTel,
            self.addressEmail,
            1 if self.status else 0
        )
    
    def fromTuple(self, row: tuple[int, str, str, str, str, int | str, str, str, str, str, str, str, str, int]):
        self.setID(row[0])
        self.setName(row[1], row[2])
        self.setAnniversary(datetime.date.fromisoformat(row[3]))
        if isinstance(row[5], int):
            self.setJob(row[4], row[5], True)
        else:
            jobArgs = row[5].split("|")
            assert(len(jobArgs) == 2)
            self.setJob(row[4], int(jobArgs[0]), jobArgs[1] == "1")
        self.setAddress(row[6], row[7], row[8], row[9], row[10], row[11], row[12])
        self.setStatus(not row[13] == 0)

class EmployeeReview:
    def __init__(self, idNum: int = None, date: datetime.date = None, nextReview: datetime.date = None, details: str = "") -> None:
        assert(idNum == None or idNum >= 0)
        self.idNum: int = idNum
        self.date: datetime.date = date
        self.nextReview: datetime.date = nextReview
        self.details: str = details

    def setID(self, num: int):
        assert(not num == None)
        assert(num >= 0)
        self.idNum = num
    
    def getTuple(self):
        return (
            self.idNum,
            "" if self.date == None else self.date.isoformat(),
            "" if self.nextReview == None else self.nextReview.isoformat(),
            stringToB64(self.details)
        )
    
    def fromTuple(self, row: tuple[int, str, str, str]):
        self.setID(row[0])
        self.date = None if row[1] == "" else datetime.date.fromisoformat(row[1])
        self.nextReview = None if row[2] == "" else datetime.date.fromisoformat(row[2])
        self.details = stringFromB64(row[3])

class EmployeeTrainingDate:
    def __init__(self, idNum: int = None, training: str = None, date: datetime.date = None, comment: str = "") -> None:
        self.idNum: int = idNum
        self.training: str = training
        self.date: datetime.date = date
        self.comment: str = comment

    def setID(self, num: int):
        assert(not num == None)
        assert(num >= 0)
        self.idNum = num
    
    def setTraining(self, training: str):
        assert(self.training == None)
        self.training = training
    
    def setDate(self, date: datetime.date):
        self.date = date
    
    def getTuple(self):
        return (
            self.idNum,
            self.training,
            self.date.isoformat(),
            self.comment
        )
    
    def fromTuple(self, row: tuple[int, str, str, str]):
        self.setID(row[0])
        self.setTraining(row[1])
        self.date = datetime.date.fromisoformat(row[2])
        self.comment = row[3]

class EmployeePTORange:
    def __init__(self, idNum: int = None, start: datetime.date = None, end: datetime.date | str = None, hours: float = 0) -> None:
        self.employee: int = idNum
        self.start: datetime.date = start
        self.end: datetime.date = end
        self.hours: float = hours
    
    def setEmployee(self, num: int):
        assert(not num == None)
        assert(num >= 0)
        self.employee = num
    
    def setDate(self, start: datetime.date, end: datetime.date | str):
        assert(not start == None)
        assert(not end == None)
        if isinstance(end, datetime.date):
            assert(start <= end)
        else:
            assert(end in ["CARRY", "CASH", "DROP"])
        self.start = start
        self.end = end
    
    def setHours(self, hours: float):
        assert(not hours == None)
        assert(hours > 0)
        self.hours = hours
    
    def getTuple(self):
        assert(not self.start == None)
        assert(not self.end == None)
        return (
            self.employee,
            self.start.isoformat(),
            self.end.isoformat() if isinstance(self.end, datetime.date) else self.end,
            self.hours
        )
    
    def fromTuple(self, row: tuple[int, str, str, float]):
        self.setEmployee(row[0])
        if row[2] in ["CARRY", "CASH", "DROP"]:
            self.setDate(datetime.date.fromisoformat(row[1]), row[2])
        else:
            self.setDate(datetime.date.fromisoformat(row[1]), datetime.date.fromisoformat(row[2]))
        self.setHours(row[3])

class EmployeePoint:
    def __init__(self, idNum: int = None, date: datetime.date = None, reason: str = None, value: float = 0) -> None:
        self.idNum: int = idNum
        self.date: datetime.date = date
        self.reason: str = reason
        self.value: float = value
    
    def setEmployee(self, num: int):
        assert(not num == None)
        assert(num >= 0)
        self.idNum = num
    
    def setDate(self, date: datetime.date):
        assert(not date == None)
        self.date = date
    
    def setReason(self, reason: str, value: float):
        self.reason = reason
        if reason in defaults.POINT_VALS:
            assert(value == defaults.POINT_VALS[reason])
        self.value = value
    
    def getTuple(self):
        assert(not self.date == None)
        return (
            self.idNum,
            self.date.isoformat(),
            self.reason,
            self.value
        )
    
    def fromTuple(self, row: tuple[int, str, str, float]):
        self.setEmployee(row[0])
        self.setDate(datetime.date.fromisoformat(row[1]))
        self.setReason(row[2], row[3])

class HolidayObservance:
    def __init__(self, holiday: str = None, date: datetime.date = None, shift: int = 1) -> None:
        self.holiday: str = holiday
        self.date: datetime.date = date
        self.shift: int = shift
    
    def setHoliday(self, holiday: str):
        assert(holiday in defaults.HOLIDAYS)
        self.holiday = holiday
    
    def setDate(self, date: datetime.date, shift: int):
        assert(not date == None)
        self.date = date
        self.shift = shift
    
    def getTuple(self):
        assert(not self.date == None)
        return (
            self.holiday,
            self.shift,
            self.date.isoformat()
        )
    
    def fromTuple(self, row: tuple[str, int, str]):
        self.setHoliday(row[0])
        self.setDate(datetime.date.fromisoformat(row[2]), row[1])

class EmployeeReviewsDB:
    def __init__(self, idNum: int) -> None:
        self.idNum: int = idNum
        self.reviews: dict[datetime.date, EmployeeReview] = {}
    
    def lastReview(self):
        keys = list(self.reviews.keys())
        keys.sort()
        if len(keys) == 0:
            return None
        else:
            return self.reviews[keys[-1]]
    
    def getTuples(self):
        ret = []
        for date in self.reviews:
            assert(self.idNum == self.reviews[date].idNum)
            ret.append(self.reviews[date].getTuple())
        return ret

class EmployeeTrainingDB:
    def __init__(self, idNum: int) -> None:
        self.idNum: int = idNum
        self.training: dict[str, dict[datetime.date, EmployeeTrainingDate]] = {}
        for key in defaults.TRAINING:
            self.training[key] = {}
    
    def getTuples(self):
        ret = []
        for train in self.training:
            for date in self.training[train]:
                assert(self.idNum == self.training[train][date].idNum)
                ret.append(self.training[train][date].getTuple())
        return ret

class EmployeePointsDB:
    def __init__(self, idNum: int) -> None:
        self.idNum: int = idNum
        self.points: dict[datetime.date, EmployeePoint] = {}
    
    def currentPoints(self, today: datetime.date):
        dates = list(self.points.keys())
        dates.sort()
        def filterDates(date: datetime.date):
            diff = (today - date).days
            val = self.points[date].value
            return diff <= 365 and val > 0
        validDates = list(filter(filterDates, dates))
        validDates.append(today) # won't ever be plugged into self.points
        sumPt = 0
        if len(validDates) > 1:
            for ind in range(len(validDates) - 1):
                currDate = validDates[ind]
                nextDate = validDates[ind + 1]
                sumPt += self.points[currDate].value
                diff = (nextDate - currDate).days
                credit = (diff - 1) // 90
                print(f"{diff} days from {currDate.isoformat()} to {nextDate.isoformat()}, deducting {credit} points from a total of {sumPt}!")
                sumPt = max(sumPt - credit, 0)
        return sumPt
    
    def currentPointsList(self, today: datetime.date):
        dates = list(self.points.keys())
        dates.sort()
        def filterDates(date: datetime.date):
            diff = (today - date).days
            val = self.points[date].value
            return diff <= 365 and val > 0
        validDates = list(filter(filterDates, dates))
        validDates.append(today) # won't ever be plugged into self.points
        resPts: list[EmployeePoint] = []
        if len(validDates) > 1:
            for ind in range(len(validDates) - 1):
                currDate = validDates[ind]
                nextDate = validDates[ind + 1]
                resPts.append(self.points[currDate])
                diff = (nextDate - currDate).days
                credit = (diff - 1) // 90
                for i in range(credit):
                    autoDeduct = EmployeePoint(self.idNum, currDate + datetime.timedelta(days=(i + 1)*90), "Automatic deduction", -1)
                    resPts.append(autoDeduct)
        return resPts
    
    def getTuples(self):
        ret = []
        for date in self.points:
            assert(self.idNum == self.points[date].idNum)
            ret.append(self.points[date].getTuple())
        return ret

class EmployeePTODB:
    def __init__(self, idNum: int) -> None:
        self.idNum: int = idNum
        self.PTO: dict[tuple[datetime.date, datetime.date|str], EmployeePTORange] = {}
    
    def getUsedHours(self, year: int):
        total = 0
        for dates in self.PTO:
            if dates[0].year == year and isinstance(dates[1], datetime.date):
                assert(dates[1].year == year)
                total += self.PTO[dates].hours
        return total
    
    def getAvailableBaseHours(self, aniversary: datetime.date, year: int):
        # 6 mos - 40 hrs
        # 1 Year - 40 hrs
        # 2 years - 80 hrs
        # 3 - years - 88 hrs
        # 4 years - 96 hrs
        # 5 years - 104 hrs
        # 6 years - 112 hrs
        # 7 years - 120 hrs
        # > 7 years - 120 hours
        tenure = year - aniversary.year
        if tenure < 0:
            return 0
        elif tenure <= 1:
            return 40
        else:
            return min(120, 80 + (tenure - 2) * 8)
    
    # def getCarryAmount(self, year: int):
    #     count = 0
    #     ret = None
    #     for dates in self.PTO:
    #         if dates[0].year == year:
    #             if dates[1] == "CARRY" or dates[1] == "CASH" or dates[1] == "DROP":
    #                 count += 1
    #                 ret = self.PTO[dates].hours
    #     assert(count <= 1)
    #     return ret
    
    def getCarryType(self, year: int):
        count = 0
        ret = None
        for dates in self.PTO:
            if dates[0].year == year:
                if dates[1] == "CARRY" or dates[1] == "CASH" or dates[1] == "DROP":
                    count += 1
                    ret = dates[1]
        assert(count <= 1)
        return ret
    
    def clearCarry(self, year: int):
        toClear = []
        for dates in self.PTO:
            if dates[0].year == year and dates[1] == "CARRY" or dates[1] == "CASH" or dates[1] == "DROP":
                    toClear.append(dates)
        for dates in toClear:
            del self.PTO[dates]
    
    def getCarryHours(self, year: int):
        count = 0
        ret = 0
        for dates in self.PTO:
            if dates[0].year == year:
                if dates[1] == "CARRY":
                    count += 1
                    ret = self.PTO[dates].hours
                elif dates[1] == "CASH" or dates[1] == "DROP":
                    count += 1
                    ret = 0
        assert(count <= 1)
        return ret
    
    def getQuarterHours(self, aniversary: datetime.date, attendance: EmployeePointsDB, today: datetime.date):
        # NEED WAY MORE DETAIL
        year = today.year
        counts = [0 for i in range(4)]
        for date in attendance.points:
            if (date.year == year or date.year == year - 1) and attendance.points[date].value > 0:
                if date.year == year - 1 and date.month > 9:
                    counts[0] += 1
                elif date.year == year and date.month <= 3:
                    counts[1] += 1
                elif date.year == year and date.month <= 6:
                    counts[2] += 1
                elif date.year == year  and date.month <= 9:
                    counts[3] += 1
        bonuses = 0
        if aniversary < datetime.date(year=year-1, month=10, day=1) and today > datetime.date(year=year-1, month=12, day=31) and counts[0] == 0:
            bonuses += 4
        if aniversary < datetime.date(year=year, month=1, day=1) and today > datetime.date(year=year, month=3, day=31) and counts[1] == 0:
            bonuses += 4
        if aniversary < datetime.date(year=year, month=4, day=1) and today > datetime.date(year=year, month=6, day=30) and counts[2] == 0:
            bonuses += 4
        if aniversary < datetime.date(year=year, month=7, day=1) and today > datetime.date(year=year, month=9, day=30) and counts[3] == 0:
            bonuses += 4
        return bonuses
    
    def getAvailableHours(self, aniversary: datetime.date, attendance: EmployeePointsDB, today: datetime.date):
        year = today.year
        base = self.getAvailableBaseHours(aniversary, year)
        carry = self.getCarryHours(year)
        bonuses = self.getQuarterHours(aniversary, attendance, today)
        return base + carry + bonuses
    
    def getTuples(self):
        ret = []
        for dateRange in self.PTO:
            assert(self.idNum == self.PTO[dateRange].employee)
            ret.append(self.PTO[dateRange].getTuple())
        return ret

class ObservancesDB:
    def __init__(self) -> None:
        self.defaults: dict[str, int] = {}
        self.observances: dict[int, dict[str, dict[int, HolidayObservance]]] = {}
    
    def setDefault(self, holiday: str, month: int):
        assert(1 <= month and month <= 12)
        self.defaults[holiday] = month
    
    def getDefault(self, holiday: str):
        if not holiday in self.defaults:
            return 1
        else:
            return self.defaults[holiday]
    
    def setObservance(self, holiday: HolidayObservance):
        year = holiday.date.year
        if not year in self.observances:
            self.observances[year] = {}
        if not holiday.holiday in self.observances[year]:
            self.observances[year][holiday.holiday] = {}    
        self.observances[year][holiday.holiday][holiday.shift] = holiday
    
    def getObservance(self, year: int, holiday: str, shift: int):
        if not year in self.observances:
            return None
        elif not holiday in self.observances[year]:
            return None
        elif not shift in self.observances[year][holiday]:
            return None
        else:
            return self.observances[year][holiday][shift].date
    
    def delObservance(self, year: int, holiday: str, shift: int):
        if year in self.observances and holiday in self.observances[year] and shift in self.observances[year][holiday]:
            del self.observances[year][holiday][shift]
            if len(self.observances[year][holiday].keys()) == 0:
                del self.observances[year][holiday]
            if len(self.observances[year].keys()) == 0:
                del self.observances[year]
    
    def getHolidays(self, year: int):
        if not year in self.observances:
            return list(self.defaults.keys())
        else:
            used = list(self.observances[year].keys())
            for holiday in self.defaults:
                if not holiday in self.observances[year]:
                    used.append(holiday)
            return used
    
    def getDefaultTuples(self):
        rets = []
        for holiday in self.defaults:
            month = self.defaults[holiday]
            rets.append((holiday, month))
        return rets
    
    def getObservanceTuples(self):
        rets = []
        for year in self.observances:
            for holiday in self.observances[year]:
                for shift in self.observances[year][holiday]:
                    rets.append(self.observances[year][holiday][shift].getTuple())
        return rets

class Database:
    def __init__(self,
                 employees: dict[int, Employee],
                 reviews: dict[int, EmployeeReviewsDB],
                 training: dict[int, EmployeeTrainingDB],
                 attendance: dict[int, EmployeePointsDB],
                 PTO: dict[int, EmployeePTODB],
                 holidays: ObservancesDB) -> None:
        self.employees = employees
        self.reviews = reviews
        self.training = training
        self.attendance = attendance
        self.PTO = PTO
        self.holidays = holidays
    
    def addEmployee(self, employee: Employee):
        assert(not employee.idNum in self.employees)
        self.employees[employee.idNum] = employee
            
    def updateEmployee(self, oldID, newID):
        if not oldID == newID:
            emloyees = {newID if key == oldID else key:val for key, val in self.employees.items()}
            self.employees = emloyees
            self.employees[newID].idNum = newID
            # TODO: replacement logic for other DBs
            if oldID in self.reviews:
                reviews = {newID if key == oldID else key:val for key, val in self.reviews.items()}
                self.reviews = reviews
                self.reviews[newID].idNum = newID
    
    def delEmployee(self, employeeID: int):
        assert(employeeID in self.employees)
        del self.employees[employeeID]
        assert(employeeID in self.reviews)
        del self.reviews[employeeID]
        assert(employeeID in self.training)
        del self.training[employeeID]
        assert(employeeID in self.attendance)
        del self.attendance[employeeID]
        assert(employeeID in self.PTO)
        del self.PTO[employeeID]
    
    def addEmployeeReviews(self, employeeReviews: EmployeeReviewsDB):
        assert(not employeeReviews.idNum in self.reviews)
        self.reviews[employeeReviews.idNum] = employeeReviews
    
    def addEmployeeTraining(self, employeeTraining: EmployeeTrainingDB):
        assert(not employeeTraining.idNum in self.training)
        self.training[employeeTraining.idNum] = employeeTraining
    
    def addEmployeePoints(self, employeePoints: EmployeePointsDB):
        assert(not employeePoints.idNum in self.attendance)
        self.attendance[employeePoints.idNum] = employeePoints
    
    def addEmployeePTO(self, employeePTO: EmployeePTODB):
        assert(not employeePTO.idNum in self.PTO)
        self.PTO[employeePTO.idNum] = employeePTO

def emptyDB():
    return Database({}, {}, {}, {}, {}, ObservancesDB())
