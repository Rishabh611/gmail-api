from setuptools import setup, find_packages

setup(
    name='scripts',          # Replace with your package name
    version='0.1',             # Replace with your package version
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[
        # List your dependencies here
        'db',
        'db-sqlite3',
        'google-auth-oauthlib',
        'google-auth-httplib2', 
        'google-api-python-client', 
        'httplib2',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'fetch = scripts.fetch:main',
            'action = scripts.action:main',  # Replace with your main entry point
        ],
    },
    author='Rishabh Singh',
    author_email='singh.rishabh61198@gmail.com',
    description='A short description of your package',
    url='https://github.com/your_username/your_package',  # Replace with your project's URL
    license='MIT',  # Replace with your package's license
)
