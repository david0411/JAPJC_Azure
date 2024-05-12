import logging
from datetime import datetime
import pyodbc


class DBConnectionAzure:
    def __init__(self):
        try:
            self.server = 'tcp:japjc.database.windows.net,1433'
            self.database = 'JAPJC'
            self.username = 'japjc'
            self.password = 'P@ssw0rd'
            self.conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={self.server};Database={self.database};Uid={self.username};Pwd={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            self.conn = pyodbc.connect(self.conn_str)
            self.c = self.conn.cursor()
        except Exception as e:
            print('Database connection error')
            logging.warning(e)

        self.sql_horse_list = "SELECT HORSE_ID FROM japjc.JAPJC_HORSE"
        self.sql_first_fixture = "SELECT MIN(FIXTURE) FROM japjc.JAPJC_FIXTURES"
        self.sql_last_fixture = "SELECT MAX(FIXTURE) FROM japjc.JAPJC_FIXTURES"

        self.sql_first_horse_record_date = "SELECT MIN(日期) FROM japjc.JAPJC_HORSE_RESULT WHERE ID = ?"
        self.sql_last_horse_record_date = "SELECT MAX(日期) FROM japjc.JAPJC_HORSE_RESULT WHERE ID = ?"

        self.sql_first_race_result_date = "SELECT MIN(日期) FROM japjc.JAPJC_RESULT2"
        self.sql_last_race_result_date = "SELECT MAX(日期) FROM japjc.JAPJC_RESULT2"

        self.sql_prev_rd = "SELECT FIXTURE, FEATURE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE <= ? ORDER BY FIXTURE DESC"
        self.sql_next_rd = "SELECT FIXTURE, FEATURE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE >= ? ORDER BY FIXTURE"
        self.sql_future_rd_date_list = "SELECT FIXTURE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE >= ?"
        self.sql_venue = "SELECT FEATURE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE = ?"

        self.sql_race_num = ("SELECT MAX(場次) FROM japjc.JAPJC_CARD WHERE 日期 "
                             "IN(SELECT FIXTURE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE >= ?)")
        self.sql_race_num2 = "SELECT MAX(場次) FROM japjc.JAPJC_CARD WHERE 日期 = ?"
        self.sql_last_odds_time = "SELECT COUNT(*) FROM japjc.JAPJC_JCODDS WHERE 日期 = ? AND 賠率時間 = ? AND 場次 = ?"
        self.sql_last_pool_time = "SELECT COUNT(*) FROM japjc.JAPJC_JCPOOL WHERE 日期 = ? AND 投注額時間 = ? AND 場次 = ?"

        self.sql_check_fixture = "SELECT COUNT(*) FROM japjc.JAPJC_FIXTURES WHERE FIXTURE = ?"
        self.sql_check_card = "SELECT COUNT(*) FROM japjc.JAPJC_CARD WHERE 日期 = ? AND 場次 = ?"
        # HORSE_ID, HORSE_NAME
        self.sql_import_horse = "INSERT INTO japjc.JAPJC_HORSE VALUES(?,?)"
        # 日期,場次,馬匹編號,六次近績,綵衣,馬名,負磅,騎師,檔位,練馬師,評分,評分加減,排位體重,優先參賽次序,配備
        self.sql_import_card = "INSERT INTO japjc.JAPJC_CARD VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        # FIXTURE, FEATURE
        self.sql_import_fixture = "INSERT INTO japjc.JAPJC_FIXTURES VALUES(?,?)"
        # 日期,場次,投注額時間,Win,PLA,QIN,QPL,FCT,TCE,TRI,F_F,DBL,TBL,D_T,T_T,6UP
        self.sql_import_jcpool = "INSERT INTO japjc.JAPJC_JCPOOL VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        # 日期,賠率時間,場次,馬號,綵衣,馬名,檔位,負磅,騎師,練馬師,獨贏,位置,EMT
        self.sql_import_jcodds = "INSERT INTO japjc.JAPJC_JCODDS VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
        # ID, 場次, 名次, 日期, 馬場跑道賽道, 途程, 場地狀況, 賽事班次, 檔位, 評分, 練馬師, 騎師,
        # 頭馬距離, 獨贏賠率, 實際負磅, 沿途走位, 完成時間, 排位體重, 配備, 賽事重播, LAST_UPDATE
        self.sql_import_horse_result = ("INSERT INTO japjc.JAPJC_HORSE_RESULT VALUES (?,?,?,?,?,?,?,"
                                        "?,?,?,?,?,?,?,?,?,?,?,?,?)")
        # 日期, 時間, 途程, 賽事班次
        self.sql_import_race_details = "INSERT INTO japjc.JAPJC_RACE_DETAILS VALUES(?,?,?)"
        # 日期, 場次, 場號, 賽事班次, 途程, 場地狀況, 賽事名稱, 馬場跑道, 馬場賽道, 時間1, 時間2, 時間3, 時間4, 時間5, 時間6,
        # 分段時間1, 分段時間2, 分段時間3, 分段時間4, 分段時間5, 分段時間6, 分段時間7, 分段時間8, 分段時間9, 分段時間10
        self.sql_import_race_result1 = ("INSERT INTO japjc.JAPJC_RESULT VALUES(?,?,?,?,?,?,?,?,?,?,?,?,"
                                        "?,?,?,?,?,?,?,?,?,?,?,?,?)")
        # 日期, 場次, 名次, 馬號, 馬名, 騎師, 練馬師, 負磅, 排位體重, 檔位, 頭馬距離, 沿途走位, 完成時間, 獨贏賠率
        self.sql_import_race_result2 = "INSERT INTO japjc.JAPJC_RESULT2 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

        self.sql_delete_fixture = "DELETE FROM japjc.JAPJC_FIXTURES WHERE FIXTURE>=?"
        self.sql_delete_jcpool = "DELETE FROM japjc.JAPJC_JCPOOL WHERE 日期 != ?"
        self.sql_delete_jcodds = "DELETE FROM japjc.JAPJC_JCODDS WHERE 日期 != ?"

    def get_horse_list(self):
        self.c.execute(self.sql_horse_list)
        return [item[0] for item in self.c.fetchall()]

    def get_first_horse_record_date(self, target_horse_id):
        self.c.execute(self.sql_first_horse_record_date, target_horse_id)
        return self.c.fetchone()[0]

    def get_last_horse_record_date(self, target_horse_id):
        self.c.execute(self.sql_last_horse_record_date, target_horse_id)
        return self.c.fetchone()[0]

    def get_first_fixture(self):
        self.c.execute(self.sql_first_fixture)
        return self.c.fetchone()[0]

    def get_last_fixture(self):
        self.c.execute(self.sql_last_fixture)
        return self.c.fetchone()[0]

    def check_card(self, target_date, race_num):
        self.c.execute(self.sql_check_card, [target_date, race_num])
        return self.c.fetchone()[0]

    def get_first_race_result_date(self):
        self.c.execute(self.sql_first_race_result_date)
        return self.c.fetchone()[0]

    def get_last_race_result_date(self):
        self.c.execute(self.sql_last_race_result_date)
        return self.c.fetchone()[0]

    def get_prev_rd(self):
        self.c.execute(self.sql_prev_rd, [datetime.now()])
        return self.c.fetchone()

    def get_next_rd(self):
        self.c.execute(self.sql_next_rd, [datetime.now().date()])
        return self.c.fetchone()

    def get_next_rd2(self, target_date):
        self.c.execute(self.sql_future_rd_date_list, [target_date])
        return [item[0] for item in self.c.fetchall()]

    def get_next_venue2(self, target_date):
        self.c.execute(self.sql_venue, [target_date])
        for row in self.c.fetchone():
            return row.split(' ')[0]

    def get_race_num(self):
        self.c.execute(self.sql_race_num, [datetime.now().date()])
        return self.c.fetchone()[0]

    def get_race_num2(self, race_date):
        self.c.execute(self.sql_race_num2, [race_date])
        return self.c.fetchone()[0]

    def get_last_odds_time(self, race_num, server_time, race_date):
        self.c.execute(self.sql_last_odds_time, [race_date, server_time, race_num])
        return self.c.fetchone()[0]

    def get_last_pool_time(self, race_num, server_time, race_date):
        self.c.execute(self.sql_last_pool_time, [race_date, server_time, race_num])
        return self.c.fetchone()[0]

    def import_data(self, data_format, data_type, data):
        import_sql = None
        if data_type == 'horse':
            import_sql = self.sql_import_horse
        elif data_type == 'card':
            import_sql = self.sql_import_card
        elif data_type == 'fixtures':
            import_sql = self.sql_import_fixture
        elif data_type == 'result1':
            import_sql = self.sql_import_race_result1
        elif data_type == 'result2':
            import_sql = self.sql_import_race_result2
        elif data_type == 'horse_result':
            import_sql = self.sql_import_horse_result
        elif data_type == 'jcpool':
            import_sql = self.sql_import_jcpool
        elif data_type == 'jcodds':
            import_sql = self.sql_import_jcodds

        if data_format == 'row':
            try:
                self.c.execute(import_sql, data)
                self.conn.commit()
            except ValueError as e:
                print(e)
                pass
        elif data_format == 'df':
            try:
                for i, row in data.iterrows():
                    self.c.execute(import_sql, tuple(row))
                    self.conn.commit()
            except ValueError as e:
                print(e)
                pass
        else:
            try:
                for i, row in data.iterrows():
                    ls = list(row)
                    if ls[1] == '場次' or '馬季' in ls[1]:
                        continue
                    ls[3] = datetime.strptime(ls[3][:6] + '20' + ls[3][6:], "%d/%m/%Y")
                    for j in range(len(ls)):
                        if ls[j] == '--':
                            ls[j] = ''
                    self.c.execute(self.sql_import_horse_result, tuple(ls))
                    self.conn.commit()
            except Exception as e:
                print(e)

    def delete_fixture(self, start_date):
        self.c.execute(self.sql_delete_fixture, [start_date])

    def delete_pool(self):
        self.c.execute(self.sql_delete_jcpool, [datetime.now().date()])
        self.conn.commit()

    def delete_odds(self):
        self.c.execute(self.sql_delete_jcodds, [datetime.now().date()])
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
