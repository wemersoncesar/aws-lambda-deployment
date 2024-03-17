from config import Config


class InstancesConfig:
    config = Config()

    instances = {
        'InstanceGroups': [
            {
                'Name': 'Master nodes',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 't4g.medium',  # 't4g.medium',
                'InstanceCount': 1,
            },
            {
                'Name': 'Slave nodes',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 't4g.medium',  # 't4g.medium',
                'InstanceCount': 2,
            }
        ],
        'KeepJobFlowAliveWhenNoSteps': False,
        'TerminationProtected': False,
        'Ec2SubnetId': config.ec2_subnet_id
    }

    configuration = [{
        "Classification": "spark",
        "Properties": {
            "maximizeResourceAllocation": "true"
        }
    }, {
        "Classification": "spark-defaults",
        "Properties": {
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
    }]
