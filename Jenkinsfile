pipeline {
    agent { label 'checkpoint-agent'}
    environment {
        REPO = "liorruslander"
        // extract latest path from the git url - use it as image name
        CONTAINER_NAME = sh(script: "echo \$GIT_URL | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1", returnStdout: true).trim()

        // extract 'version' from package.json file (use it as docker tag)
        TAGNAME = sh(script: "jq '.version' ./version.json  -r", returnStdout: true).trim()
    }
    stages{
        stage('Info'){
            steps{
                echo "GIT_BRANCH: ${env.GIT_BRANCH}"
                echo "CONTAINER_NAME: ${CONTAINER_NAME}"
                echo "TAGNAME: ${TAGNAME}"
                echo "REPO: ${REPO}"
            }
        }
  
        stage('Build and Release dev'){
            when { expression {GIT_BRANCH == 'dev'} }
            steps {
                echo "build image from source code and push to prod..."
                script {
                def devImage = "${REPO}/${CONTAINER_NAME}-dev:${TAGNAME}"
                def promotedImage="${REPO}/${CONTAINER_NAME}:${TAGNAME}"
                // build the image from source Dockerfile + tag it with version
                sh """! docker pull ${promotedImage} """ 
                sh """docker build -t ${devImage} ."""
                sh """docker push ${devImage} """           
                }	
            }
        }
        stage('Build and Release main '){
            when { expression {GIT_BRANCH == 'main'} }
            steps {
                echo "build image from source code and push to prod..."
                script {
                    def devImage = "${REPO}/${CONTAINER_NAME}-dev:${TAGNAME}"
                    def promotedImage="${REPO}/${CONTAINER_NAME}:${TAGNAME}"
                    // build the image from source Dockerfile + tag it with version
                    sh """! docker pull ${promotedImage} """
                    sh """ docker pull ${devImage} """
                    sh """ docker tag ${devImage} ${promotedImage}"""
                    sh """ docker push ${promotedImage}"""
                }	
            }
        }      
        stage('Build PR'){
            when { expression {GIT_BRANCH =~"PR*"}}
            steps {
                echo "build image from source code and push to prod..."
                script {
                    def devImage = "${REPO}/${CONTAINER_NAME}-dev:${env.GIT_BRANCH}"
                    def promotedImage = "${REPO}/${CONTAINER_NAME}:${TAGNAME}"
                    // check not stable or possible promoted not exist
                    sh """! docker pull ${promotedImage}"""
                    
                    // build the image from source Dockerfile + tag it with version
                    sh """docker build -t ${devImage} ."""
                    sh """docker rmi ${devImage} """
                }	
            }	
        }
    }
}