from setuptools import setup, find_packages

setup(
    name="property_management",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cffi>=1.15.0",
    ],
    author="Property Management Team",
    author_email="info@property-management.com",
    description="Python interface for Property Management System",
    keywords="property, real estate, management",
    python_requires=">=3.6",
) 