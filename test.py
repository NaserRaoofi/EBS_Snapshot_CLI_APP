import os
import pickle

# 🚨 Dangerous usage
def delete_data(filename):
    os.system("rm -rf " + filename)

# 🚨 Dangerous deserialization
def load_user_data(data):
    return pickle.loads(data)
