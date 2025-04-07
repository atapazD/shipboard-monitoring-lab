pipeline {
  agent any

  environment {
    PRODUCER_IMAGE = 'doz23/disney-producer:latest'
    CONSUMER_IMAGE = 'doz23/disney-consumer:latest'
  }

  stages {
    stage('Build Producer Image') {
      steps {
        script {
          docker.build("${PRODUCER_IMAGE}", "./producer")
        }
      }
    }

    stage('Push Producer Image') {
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

    stage('Build Consumer Image') {
      steps {
        script {
          docker.build("${CONSUMER_IMAGE}", "./consumer")
        }
      }
    }

    stage('Push Consumer Image') {
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

    stage('Deploy Producer') {
      steps {
        sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
      }
    }

    stage('Deploy Consumer') {
      steps {
        sh 'kubectl apply -f k8s/consumer-deployment.yaml --namespace shipboard'
      }
    }
  }
}