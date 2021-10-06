 # install required packages in buildstage
 "phases": {
                  "install": {
                    "runtime-versions": {
                      "java": "corretto11",
                      "python": 3.8
                    },
             
# login to ECR with Docker-Account
f"docker login -u $DOCKER_ID -p $DOCKER_PW",
f"$(aws ecr get-login --region {self.region} --no-include-email)",

# build spring-boot app and export Image_Name and Image_TAG
 """mvn spring-boot:build-image \
                      -Dartifactory.username=$ARTIFACTORY_USERNAME \
                      -Dartifactory.password=$ARTIFACTORY_APIKEY""",

"export TAG=$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout)",
"export IMAGE_NAME=$(mvn help:evaluate -Dexpression=project.artifactId -q -DforceStdout)",

# build and push docker image
"docker build . --tag $IMAGE_NAME:$TAG",
"docker tag $IMAGE_NAME:$TAG $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$TAG",
"docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$TAG",
