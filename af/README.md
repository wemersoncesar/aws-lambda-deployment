# Prognos Cloud Repository

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

Prognos is an end-to-end maintenance predictive and anomaly detection application for aircrafts.

This repository provides stable codes to launch Prognos pipelines with an on-demand EMR (ElasticMapReduced) on the AWS Cloud.

Owners :
- OR Team (Data Science)
- BI Team (Data Engineering)

## Get Started

### Install Prognos Cloud

First of all, make sure you have configured your credentials AWS with the AWS CLI :
```shell
$ aws configure
```
Type the access and secret keys of the IAM User `bitbucket`, then type the location where the repository is stored (eu-west-1) and the output format (json).

Then, install the following package :
```shell
$ pip install git-remote-codecommit
```

To install this project on your working development environment, you can now clone the repository.
```shell 
$ git clone codecommit::eu-west-1://prognos-ro-pipelines
```

It is recommended to install the development requirements before starting working on the project.
```shell
$ pip install -r dev-requirements.txt
```

### Run Tests

```shell

```

## Contribution guidelines

To contribute to Prognos Cloud, be sure to review the
[contribution guidelines](CONTRIBUTING.md).

We use [Jira](https://jira.devnet.klm.com/) ticketing for
tracking requests and bugs.

