import os

raw_env = ["CHARON_APIKEY={}".format(os.environ['CHARON_APIKEY'])]
bind = "0.0.0.0:5000"
