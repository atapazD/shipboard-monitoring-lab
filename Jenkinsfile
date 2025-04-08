pipeline {
  agent {
    docker {
      image 'doz23/devsecops-agent:latest'
      label 'docker'
      args '-u root:root' // Run as root if needed to access Docker, file writes, etc.
    }
  }

  environment {
    IMAGE_NAME = 'doz23/disney-producer:latest'
  }

  stages {
    stage('Static Code Analysis') {
      steps {
        sh 'bandit -r app/ -o bandit-report.txt || true'
      }
    }

    stage('Secrets Detection') {
      steps {
        sh 'trufflehog filesystem . --no-update > trufflehog-report.json || true'
      }
    }

    stage('Generate SBOM') {
      steps {
        sh 'syft . -o table > sbom.txt || true'
      }
    }

    stage('Scan for Vulnerabilities') {
      steps {
        sh 'grype . -o table > grype-report.txt || true'
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          docker.build("${IMAGE_NAME}", "./app")
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push ${IMAGE_NAME}
          """
        }
      }
    }

    stage('Deploy to K3s') {
      steps {
        sh 'kubectl apply -f k8s/producer-deployment.yaml --namespace shipboard'
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '**/*.txt, **/*.json', fingerprint: true
    }
  }
}