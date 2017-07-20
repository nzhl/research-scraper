from setuptools import setup, find_packages

setup(
        name='florida',
        #packages=['florida'],
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'flask',
        ],
)
