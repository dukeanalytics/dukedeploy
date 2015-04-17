from distutils.core import setup

setup(
    # Application name:
    name="dukedeploy",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Duke Analytics",
    author_email="duke@dukeanalytics.com",

    # Packages
    packages=["dukedeploy"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://www.dukeanalytics.com/products/dukedeployPython.php",

    #
    # license="LICENSE.txt",
    description="Useful towel-related stuff.",

    # long_description=open("README.txt").read(),
    # Dependent packages (distributions)
    #install_requires=[
    #    "flask",
    #]
     ,
)