from datetime import datetime

class dailyTracking:

    def __init__(self, db, session):
        self.db = db
        self.session =  session

    def saveTimeLog(self, type, info):
        timestamp = datetime.now()
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info FROM timelog WHERE user_id ={user} and strftime('%d', timestamp) == strftime('%d', date('now','localtime')) and info = '{info}';")
        if len(rows) == 0:
            self.db.executePush("INSERT INTO timelog (user_id,  timestamp, type, info) VALUES(?,?,?,?);", [user, timestamp, type, info])

    def getTodayTrackings(self):
        #day = datetime.today().date() 
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info FROM timelog WHERE user_id ={user} and strftime('%d', timestamp) == strftime('%d', date('now','localtime'));")
        return rows
    
    def awailableActions2List(self, actions):
        result = []
        for action in actions:
            for item in action:
                result.append(item) 
        return list(set(result))
    
    def checkAvailableActions(self, actions) -> dict:
        result = {"startDay":True, 
                  "startLunch":True,
                  "finishLunch":True,
                  "finishDay":True}
        actionList = self.awailableActions2List(actions)
        for item in actionList:
            result[item] = False
        return result