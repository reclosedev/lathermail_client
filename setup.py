from setuptools import setup


setup(
    name="lathermail_client",
    url="https://github.com/reclosedev/lathermail_client/",
    version="0.2.0",
    author="Roman Haritonov",
    description="API client for lathermail SMTP Server",
    author_email="reclosedev@gmail.com",
    license="MIT",
    py_modules=["lathermail_client"],
    include_package_data=True,
    install_requires=[
        "requests>=2.0.0,<3.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
