import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_path + "/../")

if not os.path.exists("fixtures/data.parquet.gzip"):
    skip = True 
else:
    skip = False 
