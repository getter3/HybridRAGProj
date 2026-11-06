pipeline {
    agent { label 'docker-agent-alpine'}

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'echo Building...'
                sh 'ls -lh'
                sh 'pwd'
            }
        }
    }
    
}