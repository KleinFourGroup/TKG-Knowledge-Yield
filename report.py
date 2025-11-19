from math import floor

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

import datetime

from records import Database

class PDFReport:
    def __init__(self, db: Database, path: str, margin: float = inch) -> None:
        self.db = db
        self.pdf = canvas.Canvas(path, pagesize=letter)
        self.lineSpace = 1.3
        self.calculateMargins(margin)
        self.pageNum = 1
        self.setFont("Times-Roman", 12)

    def calculateMargins(self, margin: float):
        self.margin = margin
        self.top = letter[1] - self.margin
        self.bottom = self.margin
        self.left = self.margin
        self.right = letter[0] - self.margin

    def setupPage(self):
        self.lastLine = self.top
    
    def nextPage(self):
        self.pdf.showPage()
        self.pageNum += 1
        self.setupPage()
    
    def setFont(self, font: str, size: int):
        self.pdf.setFont(font, size)
        self.font = font
        self.fontSize = size
    
    def skipLines(self, numLines):
        self.lastLine -= self.fontSize * self.lineSpace * numLines
    
    def drawText(self, text: str):
        self.pdf.drawString(self.left, self.lastLine - self.fontSize, text)
        self.skipLines(1)
    
    def drawTitle(self, text: str):
        oldFont = (self.font, self.fontSize)
        self.setFont("Times-Bold", 24)
        self.drawText(text)
        self.setFont(*oldFont)
    
    def drawSubtitle(self, text: str):
        oldFont = (self.font, self.fontSize)
        self.setFont("Times-Bold", 20)
        self.drawText(text)
        self.setFont(*oldFont)
    
    def drawSection(self, text: str):
        oldFont = (self.font, self.fontSize)
        self.setFont("Times-Bold", 18)
        self.drawText(text)
        self.setFont(*oldFont)
    
    def drawTable(self, data: list[list[str]], headers: list[str] | None = None, widths: list[float] | None = None):
        hasHeader = not headers == None
        columns = len(widths) if not widths == None else len(headers) if hasHeader else len(data[0]) if len(data) > 0 else 1

        if widths == None:
            widths = [(self.right - self.left) / columns for i in range(columns)]

        totalWidth = 0
        for width in widths:
            totalWidth += width

        startX = self.left + ((self.right - self.left - totalWidth) / 2.0)
        xVals = [startX]
        for width in widths:
            xVals.append(xVals[-1] + width)
        
        padding = self.fontSize / 3
        rowHeight = self.fontSize + 1.5 * padding
        # includes header
        maxRows = floor((self.lastLine - self.bottom) / rowHeight)
        rows = min((1 if hasHeader else 0) + len(data), maxRows)
        if rows == 0:
            return 0
        
        yVals = [self.lastLine - i * rowHeight for i in range(rows + 1)]

        self.pdf.grid(xVals, yVals)

        if hasHeader:
            oldFont = (self.font, self.fontSize)
            self.setFont("Times-Bold", self.fontSize)
            drawY = yVals[1]
            for i in range(columns):
                self.pdf.drawString(xVals[i] + padding, drawY + padding, headers[i])
            self.setFont(*oldFont)
        
        drawn = 0
        for row in range(2 if hasHeader else 1, len(yVals)):
            drawY = yVals[row]
            dataRow = data[row - (2 if hasHeader else 1)]
            for i in range(columns):
                self.pdf.drawString(xVals[i] + padding, drawY + padding, dataRow[i])
            drawn += 1
        self.lastLine = yVals[-1] - self.fontSize * self.lineSpace
        return drawn
    
    def employeePointsReport(self, id):
        if id in self.db.employees:
            employee = self.db.employees[id]
            points = self.db.attendance[id]
            assert(not employee.lastName == None)
            
            headers = ["Date", "Points", "Reason"]
            data = [[
                "{}".format(entry.date.isoformat() if not entry.date == None else "ERROR"),
                "{}".format(entry.value),
                "{}".format(entry.reason)

            ] for entry in points.currentPointsList(datetime.date.today())]
            olen = len(data)

            if len(data) == 0:
                self.setupPage()
                self.drawTitle(f"TKG Attendance Report ({datetime.date.today().isoformat()})")
                self.drawSubtitle(f"{employee.lastName.upper()} {employee.firstName} ({id})")
                self.skipLines(2)

                self.drawSection(f"Attendance Details")

                self.drawTable([], ["Total", f"{points.currentPoints(datetime.date.today())}", ""])
            while len(data) > 0:
                self.setupPage()
                self.drawTitle(f"TKG Attendance Report ({datetime.date.today().isoformat()})")
                self.drawSubtitle(f"{employee.lastName.upper()} {employee.firstName} ({id})")
                self.skipLines(2)

                self.drawSection(f"Attendance Details{" -- Continued" if not len(data) == olen else ""}")
                drawn = self.drawTable(data, headers)

                if drawn == len(data):
                    self.drawTable([], ["Total", f"{points.currentPoints(datetime.date.today())}", ""])
                
                data = data[drawn:]
                self.nextPage()
            self.pdf.save()
            
    def employeePTOReport(self, id):
        if id in self.db.employees:
            employee = self.db.employees[id]
            PTO = self.db.PTO[id]
            assert(not employee.lastName == None)
            assert(not employee.anniversary == None)

            headers = ["Start", "End", "Hours"]
            data = [[
                "{}".format(PTO.PTO[entry].start.isoformat()), # type: ignore
                "{}".format(PTO.PTO[entry].end.isoformat() if isinstance(PTO.PTO[entry].end, datetime.date) else PTO.PTO[entry].end), # type: ignore
                "{}{}".format("" if isinstance(PTO.PTO[entry].end, datetime.date) else "", PTO.PTO[entry].hours)

            ] for entry in PTO.PTO if isinstance(PTO.PTO[entry].end, datetime.date)]
            data.sort(key=lambda row: (row[0], row[1]))
            olen = len(data)
            
            today = datetime.date.today()

            unusedType = PTO.getCarryType(datetime.date.today().year)

            status = "None"
            if unusedType == "CARRY":
                status = "Carried over"
            elif unusedType == "CASH":
                status = "Cashed out"
            elif unusedType == "DROP":
                status = "Dropped"
            
            self.setupPage()
            self.drawTitle(f"TKG PTO Report ({datetime.date.today().isoformat()})")
            self.drawSubtitle(f"{employee.lastName.upper()} {employee.firstName} ({id})")
            self.skipLines(2)

            self.drawSection(f"PTO Overview")
            self.drawText(f"PTO hours in {datetime.date.today().year}: {PTO.getAvailableHours(employee.anniversary, self.db.attendance[id], today)} {"" if (today - employee.anniversary).days >= 180 else f"(available {(employee.anniversary + datetime.timedelta(days=180)).isoformat()})"}")
            self.drawText(f"Base PTO in {datetime.date.today().year}: {PTO.getAvailableBaseHours(employee.anniversary, today.year)}")
            self.drawText(f"PTO attendance bonus in {datetime.date.today().year}: {PTO.getQuarterHours(employee.anniversary, self.db.attendance[id], today)}")
            self.drawText(f"PTO carryover from {datetime.date.today().year - 1}: {PTO.getCarryHours(today.year)} ({status})")
            self.skipLines(1)
            self.drawText(f"PTO used in {datetime.date.today().year}: {PTO.getUsedHours(today.year)}")
            self.skipLines(1)
            self.drawText(f"PTO remaining in {datetime.date.today().year}: {PTO.getAvailableHours(employee.anniversary, self.db.attendance[id], today) - PTO.getUsedHours(today.year)}")
            self.skipLines(2)

            if len(data) == 0:
                self.drawSection(f"PTO Details")

                self.drawTable([], ["Total Used", "", f"{PTO.getUsedHours(today.year)}"])
            while len(data) > 0:
                if not len(data) == olen:
                    self.setupPage()
                    self.drawTitle(f"TKG PTO Report ({datetime.date.today().isoformat()})")
                    self.drawSubtitle(f"{employee.lastName.upper()} {employee.firstName} ({id})")
                    self.skipLines(2)

                self.drawSection(f"PTO Details{" -- Continued" if not len(data) == olen else ""}")
                drawn = self.drawTable(data, headers)

                if drawn == len(data):
                    self.drawTable([], ["Total Used", "", f"{PTO.getUsedHours(today.year)}"])
                
                data = data[drawn:]
                self.nextPage()
            self.pdf.save()
    
    def employeeActiveReport(self):
        headers = ["ID", "Name", "Points", "Remaining PTO"]
        data = [[
            "{}".format(id),
            "{} {}".format(self.db.employees[id].lastName.upper(), self.db.employees[id].firstName), # type: ignore
            "{}".format(self.db.attendance[id].currentPoints(datetime.date.today())),
            "{}".format(self.db.PTO[id].getAvailableHours(self.db.employees[id].anniversary, self.db.attendance[id], datetime.date.today()) - self.db.PTO[id].getUsedHours(datetime.date.today().year) if self.db.employees[id].fullTime else "N/A") # type: ignore
        ] for id in self.db.employees if self.db.employees[id].status]
        olen = len(data)

        if len(data) == 0:
            self.setupPage()
            self.drawTitle(f"TKG Active Employees Report ({datetime.date.today().isoformat()})")
            self.skipLines(2)

            self.drawSection(f"Details")

            self.drawTable([], ["Total Employees", f"{olen}"])
        while len(data) > 0:
            self.setupPage()
            self.drawTitle(f"TKG Active Employees Report ({datetime.date.today().isoformat()})")
            self.skipLines(2)

            self.drawSection(f"Details{" -- Continued" if not len(data) == olen else ""}")
            drawn = self.drawTable(data, headers)

            if drawn == len(data):
                self.drawTable([], ["Total Employees", f"{olen}"])
            
            data = data[drawn:]
            self.nextPage()
        self.pdf.save()