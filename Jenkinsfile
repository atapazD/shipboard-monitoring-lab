pipeline {
  agent any

  environment {
    PRODUCER_IMAGE = 'doz23/disney-producer:latest'
    CONSUMER_IMAGE = 'doz23/disney-consumer:latest'
    BUILD_IMAGE = 'false'
  }

  stages {
    stage('Check for Changes') {
      steps {
        script {
          def changes = sh(
            script: "git diff --name-only HEAD~1 HEAD | grep -E '^Dockerfile|^producer/|^consumer/' || true",
            returnStdout: true
          ).trim()

          if (changes) {
            echo "Changes detected:\n${changes}"
            currentBuild.description = "Changes in app directories – building images"
            env.BUILD_IMAGE = "true"
          } else {
            echo "No relevant app changes – skipping image build"
            currentBuild.description = "No app changes"
          }
        }
      }
    }

    stage('Build Producer Image') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
      steps {
        script {
          docker.build("${PRODUCER_IMAGE}", "./producer")
        }
      }
    }

    stage('Build Consumer Image') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
      steps {
        script {
          docker.build("${CONSUMER_IMAGE}", "./consumer")
        }
      }
    }

    stage('Push Producer Image') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
          script {
            sh """
              echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
              docker push ${PRODUCER_IMAGE}
            """
          }
        }
      }
    }

    stage('Push Consumer Image') {
      when {
        expression { env.BUILD_IMAGE == 'true' }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
          script {
            sh """
              echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
              docker push ${CONSUMER_IMAGE}
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