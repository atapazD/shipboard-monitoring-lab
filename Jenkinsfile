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
        sh 'docker build --no-cache -t $PRODUCER_IMAGE -f app/producer/Dockerfile app/producer'
        sh 'docker build --no-cache -t $CONSUMER_IMAGE -f app/consumer/Dockerfile app/consumer'
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
        sh '''
          kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard
          kubectl apply -f k8s/consumer-deployment.yaml --namespace shipboard

          # Restart deployments to ensure pods are refreshed
          kubectl rollout restart deployment/producer -n shipboard
          kubectl rollout restart deployment/consumer -n shipboard
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '*.txt,*.json', allowEmptyArchive: true
    }
  }
}