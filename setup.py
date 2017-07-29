from setuptools import setup, find_packages

setup(
        name='web',
        packages=['web'],
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'flask',
            'pymysql',
            'scrapy',
        ],
)
