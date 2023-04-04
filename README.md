# dlm-spider
## Warning
Web scraping puts a load on the target website. When using this program, please comply with the site's terms of use and proceed at your own risk within the bounds of common sense.

## Overview
This is a program that scrapes information from the product details pages of [DLsite.com](https://www.dlsite.com/index.html) and saves it to an SQLite database.

## Usage
Install all necessary packages.

```bash
pip install -r requirements.txt
```

In main.py, modify the arguments for the number of items to fetch, the wait time between each fetch, and whether or not to reset the database as needed. After that, simply run main.py.

```bash
python main.py
```