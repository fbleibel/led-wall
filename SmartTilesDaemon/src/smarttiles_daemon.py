#!/usr/bin/env python
### BEGIN INIT INFO
# Provides:          smart-tiles
# Required-Start:    $remote_fs $syslog $networking $ntp
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Simple script to start a program at boot
# Description:       A simple script which will start / stop a program a boot / shutdown.
### END INIT INFO

"""
This is a daemon-style wrapper.
Suggested set-up: symlink this file to /etc/init.d/smart-tiles, and use
'sudo update-rc.d smart-tiles defaults' to register as a start-up daemon.
"""
from daemon import runner
import logging
import os
from datetime import datetime, timedelta
import json
import re
import subprocess
import time

LOG_DIR = "/var/log/smart-tiles"
EMAIL_CONFIG_FILE = "/etc/smart-tiles-email-config"

class SmartTilesApp(object):
    """
    Our main app instance. Call run() to start the server.
    """
    def __init__(self):
        """
        """
        # Daemon configuration
        self.pidfile_path =  '/var/run/smart-tiles.pid'
        self.pidfile_timeout = 5
        self.stdin_path = '/dev/null'
        # There must be a better place to put these files...
        self.stdout_path = '/var/log/smart-tiles/stdout'
        self.stderr_path = '/var/log/smart-tiles/stderr'
        self.log = logging.getLogger("smart-tiles")
        
        # Read configuration
        with open(EMAIL_CONFIG_FILE, "r") as file_:
            self.config = json.load(file_)
            
        # Send heartbeat messages regularly
        self.heartbeat_period = timedelta(minutes=30)
        
    def _get_ifconfig_addrs(self):
        """Returns the list of all ipv4 addresses found in "ifconfig".
        """
        process = subprocess.Popen("ifconfig", stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        process.wait()
        addrs = re.findall("inet addr:(\d+\.\d+\.\d+\.\d+)\s", stdout)
        return addrs
    
    def run(self):
        """Run in an infinite loop - this process will usually be killed with
        SIGKILL.
        """
        # Tell the world we're starting up
        self.email_feed.send_heartbeat("Ready to go!".format(
            ", ".join(self._get_ifconfig_addrs())))
        self.last_heartbeat = datetime.now()
        
        # Note: you must kill (e.g. Ctrl+C) pipumpkin to terminate it.
        while True:
            # Don't take too much processor time if we're not speaking                    
            time.sleep(0.5)
            now = datetime.now()
        
            # Send regular heartbeat messages
            if now - self.last_heartbeat > self.heartbeat_period:
                self.email_feed.send_heartbeat("I am still alive! My IP addresses "
                "are {0}. Love, smart-tiles.".format(
                ", ".join(self._get_ifconfig_addrs())))
                self.last_heartbeat = now
            
def main():
    """Use a PID lock file.
    """
    # Set-up file logger
    logger = logging.getLogger("smart-tiles")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create directory for log if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    
    # Add stderr handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # Start daemon
    app = SmartTilesApp()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()

if __name__ == "__main__":
    main()
