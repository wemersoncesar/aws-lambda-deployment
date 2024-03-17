import os


class Submit:
    mongo_uri = os.environ['MONGO_URI']


    args_preprocessor = ['--class', 'com.linkit.em.prophet.preprocessor.Preprocessor',
                         '--master', 'yarn',
                         '--deploy-mode', 'cluster',
                         '--files', 's3://livraison-prophet-cloud-c8/main/log4j.properties',
                         '--conf', 'spark.sql.parquet.fs.optimized.committer.optimization-enabled=true',
                         '--conf', 'spark.streaming.backpressure.enabled=true',
                         's3://livraison-prophet-cloud-c8/main/prophet-preprocessor_2.12-1.3.0-assembly.jar',
                         '-p', 'Aws',
                         '-e', 'Dev',
                         '-s', 'Ags',
                         '-c', 'va',
                         '--checkpoint-path', 's3://boeing-b787-databases-v1/preprocessor-checkpoints-16',
                         # '--input-folder', 's3://lnkt-flat-bucket-c8-dev/{G-VNEW,G-VBEL}/*.csv',
                         '--input-folder', 's3://lnkt-flat-bucket-c8-dev/{G-VNEW,G-VBEL}/*-0-*.csv',
                         # This only picks files that start from Timestamp 0, and excludes "continuation" files
                         # '--input-folder', 's3://lnkt-flat-bucket-c8-dev/G-VNEW/G-VNEW_20240108*.csv', # single file testing
                         # '--input-folder', 's3://linkit-boeing-test-raw/2024-01-29/*.zip', # zip testing
                         '--output-path', 's3://boeing-b787-databases-v1/preprocessed/ags',
                         '--ignore-days-before', '2023-01-01',
                         '--allow-reprocessing',
                         '--as-batch',
                         '--max-files-per-trigger',
                         '5']

    args_parser = ['--class', 'com.linkit.em.prophet.parser.CplParser',
                   '--master', 'yarn',
                   '--deploy-mode', 'cluster',
                   '--files', 's3://livraison-prophet-cloud-c8/main/log4j.properties',
                   's3://livraison-prophet-cloud-c8/main/prophet-parser_2.12-10.3.1-assembly.jar',
                   '-p', 'Aws',
                   '-e', 'Dev',
                   '-s', 'Ags',
                   '-a', 'B787',
                   '-m', 'Unprocessed',
                   '-c', 'va',
                   '--input-folder', 's3://boeing-b787-databases-v1/preprocessed/ags/B787/raw',
                   '--output-table-name', 's3://boeing-b787-databases-v1/parsed_ags_b787']

    args_transformer = ['--class', 'com.linkit.em.prophet.transformer.Transformer',
                        '--master', 'yarn',
                        '--deploy-mode', 'cluster',
                        '--files', 's3://livraison-prophet-cloud-c8/main/log4j.properties',
                        's3://livraison-prophet-cloud-c8/main/prophet-transformer_2.12-9.6.3-assembly.jar',
                        '-p', 'Aws',
                        '-e', 'Dev',
                        '-s', 'Ags',
                        '-a', 'B787',
                        '-m', 'Unprocessed',
                        '-c', 'va',
                        '--input-table-name', 's3://boeing-b787-databases-v1/parsed_ags_b787',
                        '--output-table-name', 's3://boeing-b787-databases-v1/enriched_ags_b787',
                        '--invalid-table-name', 's3://boeing-b787-databases-v1/invalid_ags_b787']

    args_models = ['--master', 'yarn',
                   '--deploy-mode', 'cluster',
                   '--archives', 's3://livraison-prophet-cloud-c8/main/prophet-env-10.1.1.tar.gz#python_env',
                   '--packages', 'io.delta:delta-core_2.12:2.0.2',
                   '--conf', 'spark.yarn.appMasterEnv.PYSPARK_PYTHON=./python_env/bin/python',
                   '--py-files', 's3://livraison-prophet-cloud-c8/main/prophet-models-10.1.1.whl',
                   '--files',
                   's3://livraison-prophet-cloud-c8/main/log4j.properties,s3://livraison-prophet-cloud-c8/main/main-10.1.1.py',
                   's3://livraison-prophet-cloud-c8/main/main-10.1.1.py',
                   'execute-models',
                   '--platform', 'AWS',
                   '--env', 'Dev',
                   '--plane-type', 'B787',
                   '--source-data-type', 'Ags',
                   '--sensor_measurements_table_reference', 's3://boeing-b787-databases-v1/enriched_ags_b787',
                   '--computations_table_name', 's3://boeing-b787-databases-v1/prophet_computations_delta_lake_dev']

    args_publisher = ['--class', 'com.linkit.em.prophet.publisher.Publish',
                      '--master', 'yarn',
                      '--deploy-mode', 'cluster',
                      '--files', 's3://livraison-prophet-cloud-c8/main/log4j.properties',
                      's3://livraison-prophet-cloud-c8/main/prophet-publisher_2.12-11.2.3-assembly.jar',
                      '-p', 'Aws',
                      '-e', 'Dev',
                      '--config-file', 'va/config_mongo_publish.conf',
                      '--mongo-uri', mongo_uri,
                      '--input-table', 's3://boeing-b787-databases-v1/prophet_computations_delta_lake_dev',
                      '--flight-info-path', 's3://boeing-b787-databases-v1/preprocessed/ags/processed',
                      '--suffix', 'KL']
