import ansi2html
import smtplib
import pypremailer
from tidylib import tidy_document
import pprint
import os
import ConfigParser as configparser
from socket import gethostname
import func.overlord.inventory as func_inventory
import func
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
        server = smtplib.SMTP('localhost')
        server.set_debuglevel(3)
        self.config['to_emails'] = ['ralph.bean@gmail.com']
        # TODO - see the following link for info about options to pass
        # Need to figure out how to specify that this is HTML
        # http://docs.python.org/library/smtplib#smtplib.SMTP.sendmail
        server.sendmail(
            "'%s' <%s>" % (self.config['from_name'], self.config['from_email']),
            self.config['to_emails'],
            html
        )
        server.quit()
        pass

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
            html = ansi2html.Ansi2HTMLConverter().convert(diff)
            html, errors = tidy_document(html)
            html = pypremailer.Premailer(html).premail()
            self.mail(diff)
            self.log('Done mailing changes.')

class FuncInventoryNotifierConfig(dict):
    def __init__(self, cfg_filename='func-inventory-notifier.conf'):
        super(FuncInventoryNotifierConfig, self).__init__()
        
        # The hostname on which this code is executing (overlord)
        hostname = gethostname()
    
        # Look in /etc, ~/, and the path working directory
        locations = ['/etc/func/%s']#, os.path.expanduser('~/.%s'), '%s']
        locations = [loc % cfg_filename for loc in locations]
    
        defaults = {
            'to_emails' : 'root@%s' % hostname,
            'modules' : 'filetracker hardware service system rpms',
            'from_name' : 'Func Inventory Notifier',
            'from_email' : 'func-inventory-notifier@%s' % hostname,
            'git_repo' : '/var/lib/func/inventory',
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

        # Check for unexpected keys and store
        for k, v in opts.iteritems():
            if k not in defaults:
                raise ValueError, "Key %s not expected in config file." % k
            self[k] = v

