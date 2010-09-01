try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

etcpath = "/etc/func"
conffile = "func-inventory-notifier.conf"

setup(
    name='func-inventory-notifier',
    version='0.2.2',
    description='Send colorized HTML notifications of func-inventory',
    long_description=open('README.md').read(),
    author='Ralph Bean',
    author_email='ralph.bean@gmail.com',
    url='http://github.com/ralphbean/func-inventory-notifier',
    install_requires=[
        "ansi2html",
        #"func",
        "pytidylib",
        "python-premailer",
    ],
    packages=find_packages(),
    scripts=['scripts/func-inventory-notifier'],
    data_files = [(etcpath, ["etc/%s" % conffile])],
    include_package_data = True
)
