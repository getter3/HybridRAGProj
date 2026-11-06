pipeline {
    agent { label 'docker-agent-alpine'}

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test and lint') {
            steps {
                sh 'uv sync --locked --python 3.12'
                sh 'uv run --locked pytest'
                sh 'uv run --locked ruff check .'
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