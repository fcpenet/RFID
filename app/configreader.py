import configparser
import os

class ConfigReader():
    path = 'config'
    username = ''
    pw = ''
    host = ''
    db = ''

    def readconfig(self):
        config = configparser.ConfigParser()
        cwd = os.getcwd();
        if not os.path.isfile(cwd + '/' + self.path):
            return -1

        #check for arguments if exist return appropriate error
        config.read(self.path)
        self.username = config['DEFAULT']['username']
        self.pw = config['DEFAULT']['password']
        self.host = config['DEFAULT']['host']
        self.db = config['DEFAULT']['db']

        #for design setup
        self.port_name = config['DEFAULT']['port_name']
        self.baud_rate = config['DEFAULT']['baud_rate']
        self.serial1 = config['SERIAL1']
        self.serial2 = config['SERIAL2']
        self.serial3 = config['SERIAL3']
        return 0


