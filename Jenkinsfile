// pipeline {
//   agent any

//   environment {
//     IMAGE_NAME = 'doz23/disney-producer:latest'
//   }

//   stages {
//     stage('Static Code Analysis') {
//       steps {
//         sh '''
//           docker run --rm -v $(pwd):/src doz23/devsecops-agent bandit -r /src/app -o /src/bandit-report.txt || true
//         '''
//       }
//     }

//     stage('Generate SBOM') {
//       steps {
//         sh '''
//           docker run --rm -v $(pwd):/src doz23/devsecops-agent syft /src -o table > sbom.txt || true
//         '''
//       }
//     }

//     stage('Scan for Vulnerabilities') {
//       steps {
//         sh '''
//           docker run --rm -v $(pwd):/src doz23/devsecops-agent grype /src -o table > grype-report.txt || true
//         '''
//       }
//     }

//     stage('Build Docker Image') {
//       steps {
//         sh 'docker build -t $IMAGE_NAME -f app/producer/Dockerfile app/producer'
//         sh 'docker build -t $IMAGE_NAME -f app/consumer/Dockerfile app/consumer'
//       }
//     }

//     stage('Push to Docker Hub') {
//       steps {
//         withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
//           sh '''
//             echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
//             docker push $IMAGE_NAME
//           '''
//         }
//       }
//     }

//     stage('Deploy to K3s') {
//       steps {
//         sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
//         sh 'kubectl apply -f k8s/consumer-deployment.yaml --namespace shipboard'
//       }
//     }
//   }

//   post {
//     always {
//       archiveArtifacts artifacts: '*.txt,*.json', allowEmptyArchive: true
//     }
//   }
// }

pipeline {
  agent any

  environment {
    PRODUCER_IMAGE = 'doz23/disney-producer:latest'
    CONSUMER_IMAGE = 'doz23/disney-consumer:latest'
  }

  stages {
    stage('Static Code Analysis') {
      steps {
        sh '''
          docker run --rm -v $(pwd):/src doz23/devsecops-agent bandit -r /src/app -o /src/bandit-report.txt || true
        '''
      }
    }

    stage('Generate SBOM') {
      steps {
        sh '''
          docker run --rm -v $(pwd):/src doz23/devsecops-agent syft /src -o table > sbom.txt || true
        '''
      }
    }

    stage('Scan for Vulnerabilities') {
      steps {
        sh '''
          docker run --rm -v $(pwd):/src doz23/devsecops-agent grype /src -o table > grype-report.txt || true
        '''
      }
    }

    stage('Build Docker Images') {
      steps {
        sh 'docker build -t $PRODUCER_IMAGE -f app/producer/Dockerfile app/producer'
        sh 'docker build -t $CONSUMER_IMAGE -f app/consumer/Dockerfile app/consumer'
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push $PRODUCER_IMAGE
            docker push $CONSUMER_IMAGE
          '''
        }
      }
    }

    stage('Deploy to K3s') {
      steps {
        sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
        sh 'kubectl apply -f k8s/consumer-deployment.yaml --namespace shipboard'
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '*.txt,*.json', allowEmptyArchive: true
    }
  }
}