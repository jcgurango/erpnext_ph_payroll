from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in erpnext_ph_payroll/__init__.py
from erpnext_ph_payroll import __version__ as version

setup(
	name="erpnext_ph_payroll",
	version=version,
	description="Standard functions, reports, and salary components for PH Payroll.",
	author="JC Gurango",
	author_email="jc@jcgurango.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
