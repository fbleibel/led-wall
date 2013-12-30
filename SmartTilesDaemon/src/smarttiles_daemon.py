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
from email.mime.text import MIMEText
import smtplib
import logging
import os
from datetime import datetime, timedelta
import json
import re
import subprocess
import socket
import select
import SimpleHTTPServer
import SocketServer
import sys
import time
import traceback

LOG_DIR = "/var/log/smart-tiles"
EMAIL_CONFIG_FILE = "smart-tiles-config"
EMAIL_CONFIG_DIRS = ["/etc", "."]


class SmartTilesRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    """
    def do_POST(self):
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            self.wfile.write("Success!")
            f.close()
        print "action!"


class SmartTilesApp(object):
    """
    Our main app instance. Call run() to start the server.
    """
    def __init__(self, logstdout=True, port=80):
        """
        """
        self.port = port
        # Daemon configuration: use a PID lock file.
        self.pidfile_path =  '/var/run/smart-tiles.pid'
        self.pidfile_timeout = 5
        self.stdin_path = '/dev/null'
        # There must be a better place to put these files...
        self.stdout_path = '/var/log/smart-tiles/stdout'
        self.stderr_path = '/var/log/smart-tiles/stderr'
        self.log = logging.getLogger("smart-tiles")

        if logstdout:
            handler = logging.StreamHandler(sys.stdout)
            self.log.addHandler(handler)
            self.log.setLevel(logging.DEBUG)
        
        # Read configuration
        config_loaded = False
        for root in EMAIL_CONFIG_DIRS:
            config_path = os.path.join(root, EMAIL_CONFIG_FILE)
            if not os.path.exists(config_path):
                continue
            with open(config_path, "r") as file_:
                config = json.load(file_)
                # Read config
                self.user = config["user"]
                self.password = config["password"]
                self.smtp_server = config["smtp-server"]
                self.html_root = config["html-root"]
                config_loaded = True
        
        if not config_loaded:
            raise RuntimeError("No config file {0} found!".format(
                EMAIL_CONFIG_FILE))

        # Location of files to serve via html
        self.html_root = os.path.expanduser(self.html_root)
        os.chdir(self.html_root)
        
        self.http_server = None
        self.log.info("Starting smart-tiles program. Serving files from {0} at "
                      "localhost:{1}".format(self.html_root, port))
        
        # Send heartbeat messages regularly
        self.heartbeat_period = timedelta(minutes=30)
        # 10 seconds timeout for select on http requests
        self.http_server.timeout = 10
        
    def _get_ifconfig_addrs(self):
        """Returns the list of all ipv4 addresses found in "ifconfig".
        """
        process = subprocess.Popen("ifconfig", stdout=subprocess.PIPE)
        stdout, _ = process.communicate()
        process.wait()
        addrs = re.findall("inet addr:(\d+\.\d+\.\d+\.\d+)\s", stdout)
        return addrs
    
    def send_mail(self, contents):
        """Connect to the specified SMTP server using SSL
        """
        try:
            self.log.info("Connecting to SMTP server {0}".format(self.smtp_server))
            smtp = smtplib.SMTP_SSL(self.smtp_server)
            smtp.login(self.user, self.password)
            msg = MIMEText(contents)
            msg["Subject"] = "Smart-tiles Heartbeat"
            msg["From"] = self.user
            msg["To"] = self.user
            self.log.info("Sending: {0}".format(msg.get_payload()))
            smtp.sendmail(self.user, [self.user], msg.as_string())
            smtp.quit()
            self.log.info("Send successful.")
        except (socket.error, socket.gaierror):
            # Fail silently
            traceback.print_exc()
            return False
        return True
    
    def run(self):
        """Run in an infinite loop - this process will usually be killed with
        SIGKILL.
        """
        # Tell the world we're starting up
        addrs = self._get_ifconfig_addrs()
        msg = "Ready to go! My addresses are {0}".format(", ".join(addrs))
        if self.send_mail(msg):
            self.next_heartbeat = datetime.now() + self.heartbeat_period
        else:
            # Try again in 30 seconds
            self.next_heartbeat = datetime.now() + timedelta(seconds=30)
            self.log.error("Sending heartbeat failed, retrying in 30"
                           " seconds...")
        
        # Note: you must kill (e.g. Ctrl+C) this app to terminate it.
        while True:
            if not self.http_server:
                self.http_server = SocketServer.TCPServer(
                    ("", self.port), SmartTilesRequestHandler)
        
            try:
                self.http_server.handle_request()
            except select.error:
                traceback.print_exc()
                # We may not be connected yet. If not, wait for a bit.
                time.sleep(5)
                self.http_server = None
            now = datetime.now()
            # Send regular heartbeat messages
            if now > self.next_heartbeat:
                self.send_mail("I am still alive! My IP addresses "
                "are {0}. Love, smart-tiles.".format(
                ", ".join(self._get_ifconfig_addrs())))
                self.next_heartbeat = now + self.heartbeat_period
            
def main():
    """
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
    app = SmartTilesApp(logstdout=False)
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()

if __name__ == "__main__":
    main()
