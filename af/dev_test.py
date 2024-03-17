import time
import boto3
import config
import os
  
mongo_uri = os.environ['MONGO_URI']
emr = boto3.client('emr')


def create_cluster(emr):
    response = emr.run_job_flow(
        Name='Lambda EMR Cluster',
        ReleaseLabel='emr-6.7.0',
        LogUri='s3://boeing-b787-databases-v1/logs',
        Applications=[{'Name': 'Spark'}],
        Instances={
            'InstanceGroups': [
                {
                    'Name': 'Master nodes',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 't4g.medium',# 't4g.medium',
                    'InstanceCount': 1,
                },
                {
                    'Name': 'Slave nodes',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'CORE',
                    'InstanceType': 't4g.medium', # 't4g.medium',
                    'InstanceCount': 2,
                }
            ],
            'KeepJobFlowAliveWhenNoSteps': True,
            'TerminationProtected': False,
            'Ec2SubnetId': config.EC2_SUBNET_ID
        },
        Configurations=[
            {
                "Classification": "spark",
                "Properties": {
                    ## This can be set to true to run with the minimal amount of executors as possible in the cluster, maximizing the number of cores and memory for those executors.
                    ## Typically, for our General Purpose cluster instances, however, this means that we get executors with way too many cores, which introduces overhead. A more optimized approach
                    ## would increase the number of executors instead.
                     "maximizeResourceAllocation": "true"
                }
            },
            {
                "Classification": "spark-defaults",
                "Properties": {
                    ## Executor config, remove this if maximizeResourceAllocation is set to true above
                    ## m4.16xlarge has 64 cores and 256 GiB memory.
                    ## Leaving 4 cores for overhead, we can assign 60 cores per node for executors.
                    ## Using the recommendation to only use 4 or 5 cores per executor, this means we can have
                    ## 12 executors per node (12 * 5 cores = 60).
                    ## Leaving an overhead of 18.75% memory, we have 208 GiB memory to work with on our executors.
                    ## With 12 executors per node, that gives us around 17 GiB memory per executor. Let's round that down
                    ## to the more usual 16 GiB.
                    ## See also https://aws.github.io/aws-emr-best-practices/applications/spark/best_practices/#bp-516-tune-driverexecutor-memory-cores-and-sparksqlshufflepartitions-to-fully-utilize-cluster-resources
                    # "spark.executor.cores": "5",  # Recommended to run few cores on many executors
                    # "spark.executor.instances": "48", # 12 executors per node = 12 * 4 = 48 nodes
                    # "spark.executor.memory": "16G",

                    # Other config
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.hadoop.mapreduce.fileoutputcomitter.algorithm.version": "2",
                    "spark.yarn.maxAppAttempts": "1",
                    "spark.eventLog.enabled": "true",
                    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
                    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                    "spark.sql.datetime.java8API.enabled": "true",
                    "spark.sql.parquet.fs.optimized.committer.optimization-enabled": "true",
                    "spark.streaming.backpressure.enabled": "true",
                    # "spark.scheduler.mode": "FAIR"
                }
            }
        ],
        VisibleToAllUsers=True,
        ServiceRole=config.EMR_SERVICE_ROLE,
        JobFlowRole=config.EMR_JOB_FLOW_ROLE,
    )
    return response['JobFlowId']


def wait_for_cluster_ready(emr, cluster_id):
    while True:
        response = emr.describe_cluster(ClusterId=cluster_id)
        status = response['Cluster']['Status']['State']
        print('status is: ' + status)
        if status == 'WAITING':
            break
        time.sleep(15)


def submit_spark_job(emr, cluster_id):
    args_preprocessor = ['--class', 'com.linkit.em.prophet.preprocessor.Preprocessor',
            '--master', 'yarn',
            '--deploy-mode', 'cluster',
            '--files', 's3://w-emr-code-deployment/main/log4j.properties',
            '--conf', 'spark.sql.parquet.fs.optimized.committer.optimization-enabled=true',
            '--conf', 'spark.streaming.backpressure.enabled=true',
            's3://w-emr-code-deployment/main/prophet-preprocessor_2.12-1.3.0-assembly.jar',
            '-p', 'Aws',
            '-e', 'Dev',
            '-s', 'Ags',
            '-c', 'va',
            '--checkpoint-path', 's3://boeing-b787-databases-v1/preprocessor-checkpoints-16',
            # '--input-folder', 's3://lnkt-flat-bucket-c8-dev/{G-VNEW,G-VBEL}/*.csv', 
            '--input-folder', 's3://lnkt-flat-bucket-c8-dev/{G-VNEW,G-VBEL}/*-0-*.csv', # This only picks files that start from Timestamp 0, and excludes "continuation" files
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
            '--files', 's3://w-emr-code-deployment/main/log4j.properties',
            's3://w-emr-code-deployment/main/prophet-parser_2.12-10.3.1-assembly.jar',
            '-p', 'Aws',
            '-e', 'Dev',
            '-s', 'Ags',
            '-a', 'B787',
            '-m','Unprocessed',
            '-c', 'va',
            '--input-folder', 's3://boeing-b787-databases-v1/preprocessed/ags/B787/raw',
            '--output-table-name', 's3://boeing-b787-databases-v1/parsed_ags_b787']
    
    args_transformer = ['--class', 'com.linkit.em.prophet.transformer.Transformer',
            '--master', 'yarn',
            '--deploy-mode', 'cluster',
            '--files', 's3://w-emr-code-deployment/main/log4j.properties',
            's3://w-emr-code-deployment/main/prophet-transformer_2.12-9.6.3-assembly.jar',
            '-p', 'Aws',
            '-e', 'Dev',
            '-s', 'Ags',
            '-a', 'B787',
            '-m','Unprocessed',
            '-c', 'va',
            '--input-table-name', 's3://boeing-b787-databases-v1/parsed_ags_b787',
            '--output-table-name', 's3://boeing-b787-databases-v1/enriched_ags_b787',
            '--invalid-table-name', 's3://boeing-b787-databases-v1/invalid_ags_b787']
            
    args_models = ['--master', 'yarn',
            '--deploy-mode', 'cluster',
            '--archives', 's3://w-emr-code-deployment/main/prophet-env-10.1.1.tar.gz#python_env',
            '--packages', 'io.delta:delta-core_2.12:2.0.2',
            '--conf', 'spark.yarn.appMasterEnv.PYSPARK_PYTHON=./python_env/bin/python',
            '--py-files', 's3://w-emr-code-deployment/main/prophet-models-10.1.1.whl',
            '--files', 's3://w-emr-code-deployment/main/log4j.properties,s3://w-emr-code-deployment/main/main-10.1.1.py',
            's3://w-emr-code-deployment/main/main-10.1.1.py',
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
            '--files', 's3://w-emr-code-deployment/main/log4j.properties',
            's3://w-emr-code-deployment/main/prophet-publisher_2.12-11.2.3-assembly.jar',
            '-p', 'Aws',
            '-e', 'Dev',
            '--config-file','va/config_mongo_publish.conf',
            '--mongo-uri', mongo_uri,
            '--input-table', 's3://boeing-b787-databases-v1/prophet_computations_delta_lake_dev',
            '--flight-info-path', 's3://boeing-b787-databases-v1/preprocessed/ags/processed',
            '--suffix', 'KL']

    response = emr.add_job_flow_steps(
        JobFlowId=cluster_id,
        Steps=[
            {
                'Name': 'CplPreprocessor Job',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit'] + args_preprocessor
                }
            },
            {
                'Name': 'CplParser Job',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit'] + args_parser
                }
            },
            {
                'Name': 'Transformer Job',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit'] + args_transformer
                }
            },
            {
                'Name': 'Models Job',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit'] + args_models
                }
            },
            {
                'Name': 'Publisher Job',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit'] + args_publisher
                }
            }
        ]
    )
    return response


def lambda_handler(event, context):
    print('Start-up a cluster')
    cluster_id = create_cluster(emr)
    print('wait for the cluster to get-up-and-running.')
    wait_for_cluster_ready(emr, cluster_id)
    print('submit your first spark job')
    submit_spark_job(emr, cluster_id)
    print('finished submitting')
    return {
        'statusCode': 200,
        'body': 'EMR cluster created and job submitted!'
    }
               
