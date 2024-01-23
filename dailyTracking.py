from datetime import timedelta, datetime
from constants import constants

class DailyTracking:

    def __init__(self, db, session):
        self.db = db
        self.session =  session

    def save_time_log(self, type, info, date = None):
        if date is None:
            timestamp = datetime.now()
        else:
            timestamp = date
        user = self.session["user_id"]
        rows = self.db.execute("""
                               SELECT info 
                               FROM timelog 
                               WHERE user_id = ? 
                               AND strftime('%Y-%m-%d', timestamp) == strftime('%Y-%m-%d', date('now','localtime')) 
                               AND info = ?;
                               """, [user, info])
        if len(rows) == 0:
            self.db.execute("""
                            INSERT INTO timelog (user_id,  timestamp, type, info) 
                            VALUES(?,?,?,?);
                            """, [user, timestamp, type, info])
        
    def check_not_finished_day(self):    
        rows = self.last_start_marker()
        if len(rows) == 0:
            return False
        isLastDayFinished = self.last_finish_marker()
        dateStr = rows[0][0]
        dateObj = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f")
        dateObj = dateObj.strftime("%Y-%m-%d")
        now = datetime.now()
        if not isLastDayFinished and dateObj < now.strftime("%Y-%m-%d"):
            dateObj = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f")
            dateObj = dateObj.replace(hour=23, minute=59, second=0, microsecond=0)
            date = dateObj.strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"date: {date}")
            self.save_time_log(constants.STOP_TYPE, constants.FINISH_DAY, date)
        return True
        
    def last_finish_marker(self):
        user = self.session["user_id"]
        rows = self.db.execute("""
                                SELECT info
                                FROM timelog 
                                WHERE user_id = ?
                                AND strftime('%Y-%m-%d', timestamp) = (
                                    SELECT MAX(strftime('%Y-%m-%d', timestamp)) 
                                    FROM timelog 
                                    WHERE user_id = ?)
                                    AND info = ?;
                                """, [user, user, constants.FINISH_DAY])
        return len(rows) > 0
    
    def last_start_marker(self):
        user = self.session["user_id"]
        rows = self.db.execute("""
                               SELECT timestamp 
                               FROM timelog
                               WHERE user_id = ?
                               AND strftime('%Y-%m-%d', timestamp)=(
                                    SELECT MAX(strftime('%Y-%m-%d', timestamp))
                                    FROM timelog
                                    WHERE user_id = ?)
                                    AND info = ?;
                                """, [user, user, constants.START_DAY])
        return rows

    def today_trackings(self):
        user = self.session["user_id"]
        rows = self.db.execute("""
                               SELECT info, timestamp 
                               FROM timelog 
                               WHERE user_id =? 
                               AND strftime('%Y-%m-%d', timestamp) == strftime('%Y-%m-%d', date('now','localtime'));
                               """, [user])
        return rows
        
    def select_date_trackings(self, selectedDate):
        user = self.session["user_id"]
        rows = self.db.execute("""
                               SELECT info, timestamp 
                               FROM timelog 
                               WHERE user_id =?
                               AND strftime('%Y-%m-%d', timestamp) = ?;
                               """, [user, selectedDate])
        return rows
    
    def convert_points_2_list(self, actions):
        result = []
        for action in actions:
            for item in action:
                result.append(item) 
        return list(set(result))
    
    def check_available_points(self, actions) -> dict:
        result = {constants.START_DAY:True, 
                  constants.START_LUNCH:True,
                  constants.FINISH_LUNCH:True,
                  constants.FINISH_DAY:True}
        actionList = self.convert_points_2_list(actions)
        for item in actionList:
            result[item] = False
        return result
    
    def time_points_list_of_dict(self, actions) -> dict:
        result = []
        for action in actions:
            time = self.get_time_from_date_to_string(action[1])
            result.append({"info":action[0], "time":time})
        return result
    
    def calc_day_hours(self, actions)-> timedelta:
        if len(actions) == 0:
            return timedelta()
        actionsDict = {}
        actionList = self.time_points_list_of_dict(actions)
        for item in actionList:
            actionsDict[item["info"]] = item["time"]
        
        dayHours = timedelta()
        lunchHours = timedelta()
        if constants.FINISH_DAY in actionsDict and constants.START_DAY in actionsDict:   
            dayHours = datetime.strptime(actionsDict[constants.FINISH_DAY], "%H:%M") - datetime.strptime(actionsDict[constants.START_DAY], "%H:%M")
        if constants.FINISH_LUNCH in actionsDict and constants.START_LUNCH in actionsDict:
            lunchHours = datetime.strptime(actionsDict[constants.FINISH_LUNCH], "%H:%M") - datetime.strptime(actionsDict[constants.START_LUNCH], "%H:%M")
            return dayHours - lunchHours
        else:
            return dayHours

    def get_time_from_date_to_string(self, timestamp):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        date_obj = datetime.strptime(timestamp, date_format)
        return date_obj.time().isoformat('minutes')
    
    
    