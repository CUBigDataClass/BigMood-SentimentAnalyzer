UN="root"
PW="jpvm2019BigMoodMONG0DB"
HOST = "34.66.216.216"


CACHE_UN="root"
CACHE_PW="CACHE_MONGO_LAT_LON_BM_2019"
CACHE_HOST = "34.66.251.179"


MONGO = {
"URI" : "mongodb://"+UN+":"+PW+"@"+HOST,
"URI_CACHE" : "mongodb://"+CACHE_UN+":"+CACHE_PW+"@"+CACHE_HOST
}

#Every 300 seconds
DUMP_INTERVAL = {
    'dump_interval': 300
}