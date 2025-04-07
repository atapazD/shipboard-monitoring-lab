pipeline {
  agent any

  environment {
    IMAGE_NAME = 'doz23/disney-producer:latest'
    BUILD_IMAGE = 'false'
  }

  stages {
    stage('Check for Dockerfile or app/ changes') {
      steps {
        script {
          def changes = sh(
            script: "git diff --name-only HEAD~1 HEAD | grep -E '^Dockerfile|^producer/|^consumer/' || true",
            returnStdout: true
          ).trim()

          if (changes) {
            echo "Changes detected:\n${changes}"
            currentBuild.description = "Docker/app changes – building image"
            env.BUILD_IMAGE = "true"
          } else {
            echo "No Dockerfile or app/ changes – skipping image build"
            currentBuild.description = "No Docker changes"
          }
        }
      }
    }

    stage('Build Docker Image') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
      steps {
        script {
          docker.build("${IMAGE_NAME}", "./app")
        }
      }
    }

    stage('Push to Docker Hub') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
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

    stage('Deploy Producer to K3s') {
      steps {
        sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
      }
    }

    stage('Deploy Consumer to K3s') {
      steps {
        sh 'kubectl apply -f k8s/consumer-deployment.yaml --namespace shipboard'
      }
    }
  }
}