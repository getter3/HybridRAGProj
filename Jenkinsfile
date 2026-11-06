pipeline {
    agent { label 'hybridrag-jenkin-agent'}

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test and lint') {
            steps {
                sh 'uv sync --locked --python 3.12'
            }
        }

        stage('Build') {
            steps {
                sh 'echo Building...'
                sh 'ls -lh'
                sh 'pwd'
                sh 'docker -v'
            }
        }
    }
    
}