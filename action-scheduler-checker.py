import csv
import os
import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser

# sites.csv is of this format
# Site URL, IP Address, SSH Host, SSH User, Database Name, Database User, Database Password, Database Host, Table Prefix
# www.example.com,xxx.xxx.xxx.xxx,ssh.example.com,user,dbname,dbuser,dbpass,localhost,wp_
with open('sites.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        line_print = row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3] + ','
        # Edit this part if you will get the updated wp-config.php from your servers
        # make sure that you have the right access to the server(s)
        # just comment this in case you have all the data on your sites.csv
        # command = "rsync -az" + row[3] + "@" + row[2]+":/www/wp-config.php wp-configs/config-" + row[0]+".php"
        # os.system(command)
        with open('wp-configs/config-' + row[0] + '.php') as f:
            datafile = f.readlines()

            for line in datafile:
                if 'DB_NAME' in line:
                    sql_main_database = line.strip()[19:-3]
                if 'DB_USER' in line:
                    sql_username = line.strip()[19:-3]
                if 'DB_PASSWORD' in line:
                    sql_password = line.strip()[23:-3]
                if 'DB_HOST' in line:
                    sql_hostname = line.strip()[19:-3]
                if 'table_prefix' in line:
                    table_prefix = line.strip()[18:-2]

            sql_port = 3306
            ssh_host = row[2]
            ssh_user = row[3]
            ssh_port = 22
            sql_ip = sql_hostname

            with SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    # your ssh key here
                    ssh_pkey='/your/sssh/.ssh/id_xxxx',
                    remote_bind_address=(sql_hostname, sql_port)) as tunnel:
                conn = pymysql.connect(host='localhost', user=sql_username,
                                       passwd=sql_password, db=sql_main_database,
                                       port=tunnel.local_bind_port)

                query = 'SELECT count(ID) as total FROM '+table_prefix+'posts WHERE post_type = "shop_subscription" AND post_status = "wc-active";'
                data = pd.read_sql_query(query, conn)
                TOTAL_ACTIVE_SUBS = data.total[0]

                query = 'SELECT count(ID) as total FROM '+table_prefix+'posts WHERE post_title = "woocommerce_scheduled_subscription_payment" AND post_status = "pending" AND post_type = "scheduled-action";'
                data = pd.read_sql_query(query, conn)
                SCHEDULED_ACTION_post = data.total[0]

                query = 'SELECT count(action_id) as total FROM '+table_prefix+'actionscheduler_actions WHERE hook = "woocommerce_scheduled_subscription_payment" AND status = "pending";'
                data = pd.read_sql_query(query, conn)
                SCHEDULED_ACTION_table = data.total[0]

                if TOTAL_ACTIVE_SUBS == 0:
                    #print("NO active subscriptions")
                    print('')
                elif (TOTAL_ACTIVE_SUBS == SCHEDULED_ACTION_post) or (TOTAL_ACTIVE_SUBS == SCHEDULED_ACTION_table):
                    # print("All ACTIVE subscriptions have scheduled actions")
                    print('')
                else:
                    #print( str( TOTAL_ACTIVE_SUBS - SCHEDULED_ACTION_post ) + ' subscriptions have no scheduled actions' )
                    if SCHEDULED_ACTION_post > 0:
                        print(str(TOTAL_ACTIVE_SUBS - SCHEDULED_ACTION_post) + ' subscriptions ON ' + row[0])
                    else:
                        print(str(TOTAL_ACTIVE_SUBS - SCHEDULED_ACTION_table) + ' subscriptions ON ' + row[0])

                conn.close()