#!/usr/bin/env python

import tempfile
import pprint
import os
import ConfigParser as configparser
from socket import gethostname
import func.overlord.inventory as func_inventory

class FuncInventoryNotifier(object):
    def __init__(self):
        self.config = FuncInventoryNotifierConfig()

    def __str__(self):
        return "FuncInventoryNotifier:\n" + pprint.pformat(self.config)

    def run(self):
        # Make a TemporaryFile for storage.  It deletes itself at the end!
        tmp = tempfile.TemporaryFile()
        
        # Run the inventory
        inventory = func_inventory.FuncInventory()
        modules = ','.join(self.config['modules'])
        inventory.run(['func-inventory', '--modules=%s' % modules])

class FuncInventoryNotifierConfig(dict):
    def __init__(self, cfg_filename='func-inventory-notifier.conf'):
        super(FuncInventoryNotifierConfig, self).__init__()
        
        # The hostname on which this code is executing (overlord)
        hostname = gethostname()
    
        # Look in /etc, ~/, and the path working directory
        locations = ['/etc/func/%s', os.path.expanduser('~/.%s'), '%s']
        locations = [loc % cfg_filename for loc in locations]
    
        defaults = {
            'to_emails' : 'root@%s' % hostname,
            'modules' : 'filetracker hardware service system rpms',
            'from_name' : 'Func Inventory Notifier',
            'from_email' : 'func-inventory-notifier@%s' % hostname,
            'hostname' : hostname
        }

        # Open and read the config
        config = configparser.SafeConfigParser(defaults)
        config.read(['/etc/func/%s.conf' % cfg_filename,
                     os.path.expanduser('~/.%s' % cfg_filename ),
                     cfg_filename])

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

if __name__ == '__main__':
    notif = FuncInventoryNotifier()
    notif.run()

