from setuptools import setup, find_packages
 
setup(
    name='django-inline-styler',
    version='0.4',
    description='Converts CSS rules into inline style attributes for easier '
        'HTML email development',
    author='Dave Cranwell',
    # author_email='',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
