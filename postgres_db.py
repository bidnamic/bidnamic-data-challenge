#import module to facilitate working with postgresSQL database
import psycopg2

#Connect to PostgresSQL database = shopping_data
conn = psycopg2.connect (database="shopping_data",
    user="postgres",
    password="Tobore",
    host="localhost",
    port="5432")


conn.autocommit = True
cursor = conn.cursor()

#Now create the tables to ingest the Google Ads API data
cursor.execute(''' DROP TABLE IF EXISTS adgroups;
                       CREATE TABLE adgroups
                       (AD_GROUPS_ID BIGINT,
                        CAMPAIGN_ID BIGINT PRIMARY KEY, 
                        ALIAS TEXT, 
                        STATUS TEXT);''')


cursor.execute(''' DROP TABLE IF EXISTS campaigns;
                       CREATE TABLE campaigns
                       (CAMPAIGN_ID BIGINT PRIMARY KEY, 
                        STRUCTURE TEXT, 
                        STATUS TEXT);''')


cursor.execute(''' DROP TABLE IF EXISTS search_terms;
                   CREATE TABLE search_terms
                   (SEARCH_DATE DATE NOT NULL,
                    AD_GROUP_ID BIGINT, 
                    CAMPAIGN_ID BIGINT PRIMARY KEY,
                    CLICKS INT,
                    COST REAL,
                    CONVERSION_VALUE REAL,
                    CONVERSIONS INT,
                    SEARCH_TERM TEXT);''')


cursor.execute('''SET DateStyle TO European;''')

cur = conn.cursor()

#Copy table contents
with open(r'C:\Users\tobor\OneDrive\Desktop\Binamic_raw_data\SEARCH_TERMS.csv') as fr:
    next(fr) 
    cur.copy_from(fr, 'search_terms', sep=',')

with open(r'C:\Users\tobor\OneDrive\Desktop\Binamic_raw_data\ADGROUPS.csv') as fc:
    next(fc)
    cur.copy_from(fc, 'adgroups', sep=',')

with open(r'C:\Users\tobor\OneDrive\Desktop\Binamic_raw_data\CAMPAIGNS.csv') as fb:
    next(fb)
    cur.copy_from(fb, 'campaigns', sep=',')

#Combine the tables

sql_='''SELECT search_date, clicks, cost, (conversion_value/cost) as ROAS, conversions, search_term, ad_group_id, cp.campaign_id,cp.status, ag.alias
        
        FROM search_terms as st INNER JOIN adgroups as ag
        ON st.campaign_id = ag.campaign_id
        INNER JOIN campaigns cp
        ON ag.campaign_id = cp.campaign_id
        ORDER BY search_date
        ''';

cursor.execute(sql_)

sql_c= '''DROP TABLE IF EXISTS campaigns_ROAS;
          CREATE TABLE CAMPAIGNS_ROAS AS SELECT search_date, clicks, cost, (conversion_value/cost) as ROAS, conversions, search_term, ad_group_id, cp.campaign_id,cp.status, ag.alias
          FROM search_terms as st INNER JOIN adgroups as ag
          ON st.campaign_id = ag.campaign_id
          INNER JOIN campaigns cp
          ON ag.campaign_id = cp.campaign_id
          ORDER BY search_date
          ''';

cursor.execute(sql_c)

#Query the aggregated table to get the ROAS
cursor.execute("SELECT alias, ROAS FROM campaigns_roas WHERE alias LIKE '%LOW%' AND alias LIKE '%GB%'");
print(cursor.fetchall());

conn.close()