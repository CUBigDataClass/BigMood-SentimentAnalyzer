#!bin/bash
echo "running deploy script"
set -e
ls -l

docker build -t gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT .
docker tag gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:latest

echo "docker build done"
gcloud auth activate-service-account --key-file ./My-project-key.json

echo "Login success in gcloud."

gcloud --quiet config set project $PROJECT_NAME
gcloud --quiet config set container/cluster $CLUSTER_NAME
gcloud --quiet config set compute/zone ${CLOUDSDK_COMPUTE_ZONE}
gcloud --quiet container clusters get-credentials $CLUSTER_NAME

gcloud docker -- push gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}

yes | gcloud beta container images add-tag gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:latest

kubectl config view
kubectl config current-context


kubectl set image deployment.apps/${CLUSTER_NAME} ${CLUSTER_NAME}=gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT

echo "script Complete"

