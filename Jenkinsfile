pipeline {
  agent any

  environment {
    IMAGE_NAME = 'doz23/disney-producer:latest'
  }

  stages {
    stage('Clone Repo') {
      steps {
        git credentialsId: 'github-creds', url: 'https://github.com/atapazD/shipboard-monitoring-lab'
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          docker.build("${IMAGE_NAME}")
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

    // Optional: Deploy to K3s
    // stage('Deploy to K3s') {
    //   steps {
    //     sh 'kubectl apply -f k8s/producer-deployment.yaml'
    //   }
    // }
  }
}