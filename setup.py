try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from setuptools.command.install import install as _install

etcpath = "/etc/func"
conffile = "func-inventory-notifier.conf"

class install(_install):
    def run(self):
        _install.run(self)
        # Just add a nice, helpful post-install message
        msg = "Modify %s/%s to customize" % ( etcpath, conffile )
        print "*" * len(msg)
        print msg

setup(
    cmdclass={'install': install},
    name='func.overlord.inventory.notifier',
    version='0.1',
    description='Send colorized HTML notifications of func-inventory',
    long_description=open('README.md').read(),
    author='Ralph Bean',
    author_email='ralph.bean@gmail.com',
    url='http://github.com/ralphbean/func.overlord.inventory.notifier',
    install_requires=[
        "ansi2html",
        #"func",
        "pytidylib",
        "python-premailer",
    ],
    packages=find_packages(),
    namespace_packages = ['func'],
    scripts=['scripts/func-inventory-notifier'],
    data_files = [(etcpath, ["etc/%s" % conffile])]
)
