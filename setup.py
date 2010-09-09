try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

etcpath = "/etc/func"
conffile = "func-inventory-notifier.conf"

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

setup(
    name='func-inventory-notifier',
    version='0.2.3a10',
    description='Send colorized HTML notifications of func-inventory',
    long_description=long_description,
    author='Ralph Bean',
    author_email='ralph.bean@gmail.com',
    url='http://github.com/ralphbean/func-inventory-notifier',
    install_requires=[
        #"func",
        "ansi2html",
        "pytidylib",
        "python-premailer",
    ],
    packages=find_packages(),
    scripts=['scripts/func-inventory-notifier'],
    data_files = [(etcpath, ["etc/%s" % conffile])],
    include_package_data = True
)
