#!bin/bash

set -e

docker build -t gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT .
docker tag gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:latest

echo GCLOUD_SERVICE_KEY | base64 --decode -i > ${HOME}/gcloud-service-key.json
gcloud auth activate-service-account --key-file ${HOME}/gcloud-service-key.json

gcloud --quiet config set project $PROJECT_NAME
gcloud --quiet config set container/cluster $CLUSTER_NAME
gcloud --quiet config set compute/zone ${CLOUDSDK_COMPUTE_ZONE}
gcloud --quiet container clusters get-credentials $CLUSTER_NAME

gcloud docker push gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}

yes | gcloud beta container images add-tag gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:latest

kubectl config view
kubectl config current-context

kubectl apply -f pod.yml

kubectl set image deployment/${CLUSTER_NAME} ${CLUSTER_NAME}=gcr.io/${PROJECT_NAME}/${CLUSTER_NAME}:$TRAVIS_COMMIT

echo $DEMO_GREETING

