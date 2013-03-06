from setuptools import setup

VERSION = '0.0.1'
NAME = 'inliner'

setup(
        name = NAME,
        version = VERSION,
        description = "Inline CSS into HTML style attributes",
        long_description = "",
        license = 'BSD',
        author = "Dave Cranwell, Dana Woodman, Eric Shull, Johannes Steger",
        author_email = 'jss@coders.de',
        url = 'https://github.com/johaness/%s' % (NAME,),
        zip_safe = True,
        py_modules = [NAME,],
        install_requires = ['cssutils', 'lxml',],
        entry_points = {
            'console_scripts': [
                '%s=%s:main' % (NAME, NAME,),
                ],
            },
        )

