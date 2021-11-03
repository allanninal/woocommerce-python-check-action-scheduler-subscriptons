What Is This?
-------------

This python script checks if the current Active WooCommerce Subscriptions have the same number of Action Schedulers.


How To Use This
---------------

1. Create site.csv for the details of the site(s)
2. You can add multiple site details.
3. Columns of the csv: Site URL, IP Address, SSH Host, SSH User, Database Name, Database User, Database Password, Database Host, Table Prefix
4. If using pem keys, make sure that your machine is connected or has accesss to the server(s)
5. This creates/copy/rsync the wp-config.php of the sites you want to check.
6. Run `pip install csv`
7. Run `pip install os`
8. Run `pip install pymysql`
9. Run `pip install paramiko`
10. Run `pip install pandas`
11. Run `python action-scheduler-checker.py`
