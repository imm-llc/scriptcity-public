try:
    import OpenSSL
except:
    raise Exception("Unable to import OpenSSL. Try running pip3 install -r pipfile")

import ssl
import socket

from datetime import datetime

import configparser

from slack_alert import send_alert

import logging


class TLSChecker:
    def init_logging(self):

        self.logger = logging.getLogger("TLS_Monitor")

        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("/var/log/tls_monitor/app.log")

        self.logger.addHandler(file_handler)

    def check_expiration(self):

        self.init_logging()

        self.logger.info("\nStarting checks at {}\n".format(str(datetime.now())))

        config = configparser.ConfigParser()

        config.read('/etc/tls_monitor/config.cfg')

        ALERT_TIME = int(config['MONITOR']['ALERT_TIME'])

        HOSTS = config['MONITOR']['HOSTS'].split(' ')

        ssl_date_fmt = r'%Y%m%d%H%M%SZ'

        for host in HOSTS:

            try:
                
                retrieved_cert = ssl.get_server_certificate((host, 443))

                x509_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, retrieved_cert)
                
                cert_not_after = x509_cert.get_notAfter()

                friendly_expiration = datetime.strptime(str(cert_not_after)[2:-1], ssl_date_fmt)

                time_now = datetime.now()

                expiration_long = friendly_expiration - time_now

                days_remaining = expiration_long.days

                if days_remaining < ALERT_TIME:

                    self.logger.warning("Certificate for {} expires in {} days. Alerting".format(host, days_remaining))

                    send_alert(host, days_remaining)
                
                self.logger.info("Certificate for {} OK. Expires in {} days".format(host, days_remaining))
            
            except Exception as e:
                print(str(e))


if __name__ == "__main__":

    checker = TLSChecker()

    checker.check_expiration()