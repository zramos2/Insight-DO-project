from pyspark.sql import *
import pyspark.sql.functions as f
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.ml import Pipeline
from pyspark.ml.feature import RegexTokenizer, NGram, HashingTF, MinHashLSH

from io import BytesIO

import boto3
import pretty_midi
import os
import sys
import time
import config

s3_bucket = 'lmd-midi'
df_filename_instrument_name = 'filename_instrument_run3'
df_matches_name = 'filepair_similarity_run3'
spark_app_name = 'process_midi_files'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/lib")

time_seq = []

# Define Spark Configuration
def spark_conf():
    conf = SparkConf().setAppName(spark_app_name)
    sc = SparkContext(conf=conf)
    spark = SparkSession.builder.getOrCreate()
    return spark

spark = spark_conf()

# Function to write spark-dataframe to PostgreSQL
def write_df_to_pgsql(df, table_name):
    postgresql_user = os.environ.get('POSTGRES_USER')
    postgresql_password = os.environ.get('POSTGRES_PASSWORD')
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://pg-postgresql/lmd") \
        .option("dbtable", table_name) \
        .option("user", postgresql_user) \
        .option("password", postgresql_password) \
        .save()

# Compute Similarity Score for song pairs
def process_df(df):
    time_seq.append(['start process-df', time.time()])
    model = Pipeline(stages = [
                                RegexTokenizer(pattern = " ", inputCol = "instruments", outputCol = "instruments_tokenized", minTokenLength = 1),
                                NGram(n = 1, inputCol = "instruments_tokenized", outputCol = "instruments_ngrams"),
                                HashingTF(inputCol = "instruments_ngrams", outputCol = "instruments_vectors"),
                                MinHashLSH(inputCol = "instruments_vectors", outputCol = "instruments_lsh", numHashTables = 10)
                              ]).fit(df)

    df_hashed = model.transform(df)
    df_matches = model.stages[-1].approxSimilarityJoin(df_hashed, df_hashed, 0.5, distCol="distance") \
        .filter("datasetA.filename != datasetB.filename AND datasetA.filename < datasetB.filename") \
        .select(f.col('datasetA.filename').alias('filename_A'),
                f.col('datasetB.filename').alias('filename_B'),
                f.col('distance'))
    time_seq.append(['process-df df_matches', time.time()])
    write_df_to_pgsql(df_matches, df_matches_name)
    time_seq.append(['write pgsql', time.time()])
    print('time_seq', time_seq)

# Read all MIDI files from S3 bucket
def read_midi_files():
    time_seq.append(['start-read-midi', time.time()])
    
    invalid_files = []
    number_of_files = 0
    number_of_valid_files = 0
    filename_instruments_seq = []

    # Set s3-boto config
    s3 = boto3.resource('s3')
    boto_client = boto3.client('s3')
    bucket = s3.Bucket(s3_bucket)

    # DataFrame schema
    File_Instruments = Row("filename", "instruments")
    Filename_Instrument = Row("filename", "instrument")
    
    # Stores (filename, list(instrument))
    filename_instruments_seq = []
    
    # Stores (filename, instrument) This is denormalized format of above. 
    # A filename will have an entry for each instrument.
    filename_instrument_seq = []

    # Read each MIDI file from AWS S3 bucket
    for obj in bucket.objects.all():
        
        if (number_of_files % 20 == 0):
            print('Current number of processed files:', number_of_files)
        
        number_of_files += 1
        s3_key = obj.key
        midi_obj_stream = boto_client.get_object(Bucket=s3_bucket, Key=s3_key)
        midi_obj = BytesIO(midi_obj_stream['Body'].read())
        
        try:
            # Try required as a few MIDI files are invalid.
            pretty_midi_obj = pretty_midi.PrettyMIDI(midi_obj)
            number_of_valid_files+=1
            filename = s3_key[2:]
            instruments_list = list(map(lambda x: str(x.program), pretty_midi_obj.instruments))
            instruments_list_set = set(instruments_list)
            instruments_list_uniq = list(instruments_list_set)
            for instrument in instruments_list_uniq:
                filename_instrument_seq.append(Filename_Instrument(filename, instrument))
            instruments_str = " ".join(instruments_list_uniq)
            if (len(instruments_list_uniq) >=3):
                filename_instruments_seq.append(File_Instruments(filename,instruments_str))
        except:
            # Invalid MIDI files are stored.
            invalid_files.append(s3_key)

    print('Total number of processed files:', number_of_files)
    print('Total number of valid processed files:', number_of_valid_files)

    time_seq.append(['end read-file', time.time()])
    df_filename_instrument = spark.createDataFrame(filename_instrument_seq)
    print(df_filename_instrument)
    write_df_to_pgsql(df_filename_instrument, df_filename_instrument_name)
    df_song_instrument = spark.createDataFrame(filename_instruments_seq)
    process_df(df_song_instrument)

if __name__ == '__main__':
    time_seq.append(['start', time.time()])
    read_midi_files()
