pipeline {
  agent any

  environment {
    IMAGE_NAME = 'doz23/disney-producer:latest'
  }

  stages {
    stage('Build Docker Image') {
      steps {
        script {
          docker.build("${IMAGE_NAME}","./app")
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
          script {
            sh """
              echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
              docker push ${IMAGE_NAME}
            """
          }
        }
      }
    }

    stage('Deploy to K3s') {
      steps {
        sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
      }
    }
  }
}