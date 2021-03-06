from os import path
import yaml
from kubernetes import client, config

JOB_NAME = "estrazione-job"


def create_job_object(env_vars={"ENDPOINT":"http://172.17.0.1:9000","MINIO_ACCESS_KEY":"admin","MINIO_SECRET_KEY":"keystone"}):
    env_list = []
    for env_name, env_value in env_vars.items():
        env_list.append( client.V1EnvVar(name=env_name, value=env_value) )


    container = client.V1Container(
        name="estratto",
        image="ziofededocker/estrazionefile:latest",
        command=["python","/app/estrazione.py"],
        env=env_list,
        image_pull_policy="IfNotPresent")


    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "estratto"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))

    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=JOB_NAME),
        spec=spec)

    return job


def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="default")
    print("Job created. status='%s'" % str(api_response.status))


def update_job(api_instance, job):

    job.spec.template.spec.containers[0].image = "ziofededocker/estrazionefile:latest"
    api_response = api_instance.patch_namespaced_job(
        name=JOB_NAME,
        namespace="default",
        body=job)
    print("Job updated. status='%s'" % str(api_response.status))


def main():

    config.load_kube_config()
    batch_v1 = client.BatchV1Api()

    job = create_job_object()

    create_job(batch_v1, job)

    update_job(batch_v1, job)


if __name__ == '__main__':
    main()
