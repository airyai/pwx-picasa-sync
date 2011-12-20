import os
from setuptools import setup
config_file_path = os.path.join(os.getcwd(), 'picasasync.conf'),
setup(
        name = "pwx-picasa-sync",
        version = "0.1b2",
        packages = ["picasasync", ],
        package_dir = {'picasasync':'src'},
        scripts = ["picasasync", ],
        include_package_data = True,

        install_requires = ['gdata>=2.0'],

        author = "pwx",
        author_email = "airyai@gmail.com",
        description = "",
        long_description = open("README", "r").read(),
        keywords = "picasa sync pwx",
        url = "https://github.com/airyai/pwx-picasa-sync",
)
