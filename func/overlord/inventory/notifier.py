import ansi2html
from tidylib import tidy_document
import pprint
import os
import ConfigParser as configparser
from socket import gethostname
import func.overlord.inventory as func_inventory
import func
from func.minion import sub_process

class FuncInventoryNotifier(object):
    def __init__(self):
        self.config = FuncInventoryNotifierConfig()

    def __str__(self):
        return "FuncInventoryNotifier:\n" + pprint.pformat(self.config)

    def log(self, msg):
        print msg

    def git_diff(self):
        cmd = sub_process.Popen(
            [
                "/usr/bin/git",
                "--git-dir=%s" % self.config['git_repo'],
                "log",
                "-p",
                "--since='5 minutes ago'",
                "--color"
            ],
            shell=True, stdout=sub_process.PIPE)
        output = cmd.communicate()[0]
        def _check_for_errors(o):
            # TODO - to some error checking and raise exceptions
            pass
        _check_for_errors(output)
        return output

    def ansi2html(self, ansi):
        return ansi2html.Ansi2HTMLConverter().convert(ansi)

    def tidy(self, html):
        html, errors = tidy_document(html)
        print type(html)
        return html

    def premail(self, html):
        # TODO - implement
        return html

    def mail(self, html):
        # TODO - implement
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
            diff = self.ansi2html(diff)
            diff = self.tidy(diff)
            diff = self.premail(diff)
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

