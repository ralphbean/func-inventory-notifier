
try:
    import configparser
except ImportError, e:
    import ConfigParser as configparser

import os
import pprint
from datetime import datetime
from socket import gethostname, getfqdn

import ansi2html
import tidylib
import pypremailer
import smtplib
from email.MIMEText import MIMEText

from func.overlord import inventory as func_inventory
from func.minion import sub_process
from func.minion.sub_process import PIPE

class FuncInventoryNotifier(object):
    def __init__(self):
        self.config = FuncInventoryNotifierConfig()

    def __str__(self):
        return "FuncInventoryNotifier:\n" + pprint.pformat(self.config)

    def log(self, msg):
        print msg

    def git_diff(self):
        cwd = os.getcwd()
        os.chdir(self.config['git_repo'])

        cmd = "/usr/bin/git log -p --since='5 minutes ago' --color"
        proc = sub_process.Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE)
        output, error = proc.communicate()

        os.chdir(cwd)

        if proc.returncode is not 0:
            raise Exception, "Error in git diff: '%s' %s" % ( error, output )

        return output

    def mail(self, html):
        server = smtplib.SMTP(self.config['smtp_server'])
        
        msg = MIMEText(html, 'html')

        _s = 'Func Inventory Notifier %s' % datetime.today().isoformat(' ')
        msg['Subject'] =  _s
        _f = "'%s' <%s>" % (self.config['from_name'], self.config['from_email'])
        msg['From'] = _f

        msg['X-Generated-By'] = 'Python'
        msg['Content-Disposition'] = 'inline'

        for to_email in self.config['to_emails']:
            self.log( "Emailing %s" % to_email )
            msg['To'] = to_email
            _msg = msg.as_string()
            server.sendmail( _f, to_email, _msg )

        server.quit()

    def run(self):
        # Run the inventory
        inventory = func_inventory.FuncInventory()
        inventory.run(
            [
                'func-inventory',
                '--tree=%s' % self.config['git_repo'],
                '--modules=%s' % ','.join(self.config['modules'])
            ])

        diff = self.git_diff()
        if not diff:
            self.log('No changes detected.  Sleeping.')
        else:
            self.log('CHANGE DETECTED in func-inventory.')

            kw = dict(dark_bg=self.config['dark_bg'],
                      font_size=self.config['font_size'])
            html = ansi2html.Ansi2HTMLConverter(**kw).convert(diff)

            html, errors = tidylib.tidy_document(html)

            html = pypremailer.Premailer(html).premail()

            self.mail(html)

            self.log('Done mailing changes.')

class FuncInventoryNotifierConfig(dict):
    def __init__(self, cfg_filename='func-inventory-notifier.conf'):
        super(FuncInventoryNotifierConfig, self).__init__()
        
        # The hostname on which this code is executing (overlord)
        hostname = getfqdn()
    
        # Look in /etc, ~/, and the path working directory
        locations = ['/etc/func/%s']#, os.path.expanduser('~/.%s'), '%s']
        locations = [loc % cfg_filename for loc in locations]
    
        defaults = {
            'to_emails' : 'root@%s' % hostname,
            'modules' : 'filetracker hardware service system rpms',
            'from_name' : 'Func Inventory Notifier',
            'from_email' : 'root@%s' % hostname,
            'git_repo' : '/var/lib/func/inventory',
            'smtp_server' : 'localhost',
            'dark_bg' : "Yes",
            'font_size' : 'normal',
            'hostname' : hostname
        }

        # Open and read the config
        config = configparser.SafeConfigParser(defaults)
        config.read(locations)

        # Extract a dict
        section = 'func-inventory-notifier'
        opts = dict(config.items(section))

        # Split up space-separated options
        opts['modules'] = opts['modules'].split()
        opts['to_emails'] = opts['to_emails'].split()

        # Mangle "yes" to True
        opts['dark_bg'] = opts['dark_bg'].lower() == "yes"

        # Check for unexpected keys and store
        for k, v in opts.iteritems():
            if k not in defaults:
                raise ValueError, "Key %s not expected in config file." % k
            self[k] = v

