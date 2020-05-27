import mysql.connector
from mysql.connector import errorcode
import config

class SqlConnector:
    dbConnection = None
    connectionCursor = None

    def __init__(self):
        try:
            self.dbConnection = mysql.connector.connect(user = config.db['username'],
                                                        password = config.db['password'])
            self.connectionCursor = self.dbConnection.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise Exception("Error: Incorrect username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise Exception("Error: Unknown database")
            else:
                raise Exception(err)
        else:
            print("Success: Connection established")

    def runStatements(self, fileName):
        """
        reads given sql file and runs the statements in the file
        :return:
        """
        try:
            with open(fileName) as sqlFile:
                statements = sqlFile.read().split(';')
                for statement in statements:
                    statement = statement.replace('\n', '').replace('\r', '').strip()
                    if statement:
                        self.connectionCursor.execute(statement)
        except Exception as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise Exception("Error: Incorrect username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise Exception("Error: Unknown database ")
            else:
                raise Exception(err)
        else:
            print("Success: Statements executed successfully")

    def insertValues(self, dbName, table, columns, valuesDict):
        """
        Inserts the given values in the corresponding columns of the given table
        :param dbName: database name
        :param table: table to insert values
        :param columns: columns of table
        :param valuesDict: values to insert
        :return:
        """
        try:
            insertQuery = "INSERT INTO {}.{} (".format(dbName, table)
            values = []
            for column in columns:
                if column in valuesDict:
                    insertQuery += column
                    insertQuery += ","
            insertQuery = insertQuery[:-1] + ") values ("
            for column in columns:
                if column in valuesDict:
                    values.append(valuesDict[column])
                    insertQuery += "%s,"
            insertQuery = insertQuery[:-1] + ");"
            self.connectionCursor.execute(insertQuery, values)
        except mysql.connector.Error as err:
            raise Exception(err)

    def getRows(self, dbName, table):
        """
        Retrieves all the rows from the given table 
        :param dbName: database name
        :param table: table name
        :return:
        """
        try:
            selectQuery = "Select * from {}.{};".format(dbName, table)
            self.connectionCursor.execute(selectQuery)
            result = self.connectionCursor.fetchall()
            return result 
        except mysql.connector.Error as err:
            raise Exception(err)

    def rowExists(self, dbName, table, columns, values):
        """
        Checks if row with given column values exists

        :param dbName: database name
        :param table: table to insert values
        :param columns: columns of table
        :param valuesDict: values to check
        :return:
        """
        try:
            if len(columns) != len(values):
                raise Exception("Error: Number of columns and values should match. ")
            selectQuery = "Select count(*) from {}.{} where ".format(dbName, table)
            for i in range(len(columns)):
                selectQuery += " {} = '{}' and".format(columns[i], values[i])
            selectQuery = selectQuery[:-3] + ";"
            self.connectionCursor.execute(selectQuery)
            result = self.connectionCursor.fetchone()
            if result[0] == 0:
                return False
            else:
                return True
        except mysql.connector.Error as err:
            raise Exception(err)

# ALTER DATABASE amazon CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
# ALTER TABLE reviews CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# ALTER TABLE reviews CHANGE review_body text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

