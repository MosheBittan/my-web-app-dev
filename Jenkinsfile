pipeline {
    agent any

    environment {
        // Define variables to reuse throughout the pipeline
        DOCKER_IMAGE     = "your_dockerhub_moshebittan/my-web-app"
        IMAGE_TAG        = "v${BUILD_NUMBER}" // Automatically increments per build (v1, v2, v3...)
        REGISTRY_CREDS   = 'dockerhub-creds'
        GITHUB_CREDS     = 'github-token'
        GITOPS_REPO_URL  = 'https://github.com/MosheBittan/my-app-gitops.git' 
    }

    stages {
        // Step 1: Clone Code (Handled automatically by Jenkins from SCM configuration)
        stage('Checkout Code') {
            steps {
                echo "Checking out code from Developer Git Repository..."
            }
        }

        // Step 2: Build Docker Image
        stage('Build Docker Image') {
            steps {
                echo "Building Docker Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} ."
                }
            }
        }

        // Step 3: Security Scan using Trivy
        stage('Trivy Security Scan') {
            steps {
                echo "Running Vulnerability Scan on Image..."
                // Runs Trivy scanning. --exit-code 0 ensures the build continues even if issues are found
                sh "trivy image --severity HIGH,CRITICAL --exit-code 0 ${DOCKER_IMAGE}:${IMAGE_TAG}"
            }
        }

        // Step 4: Push Image to DockerHub
        stage('Push to DockerHub') {
            steps {
                echo "Logging into DockerHub and pushing image..."
                script {
                    withCredentials([usernamePassword(credentialsId: REGISTRY_CREDS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
                        sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    }
                }
            }
        }

        // Step 5: Update values.yaml inside DevOps GitOps Repository
        stage('Update GitOps Repo') {
            steps {
                echo "Modifying values.yaml in GitOps repo to use tag ${IMAGE_TAG}..."
                script {
                    withCredentials([usernamePassword(credentialsId: GITHUB_CREDS, usernameVariable: 'GH_USER', passwordVariable: 'GH_TOKEN')]) {
                        // Clean up any old directory if it exists from a previous run
                        sh "rm -rf my-app-gitops"
                        
                        // Clone the GitOps repository using the token for authentication
                        sh "git clone https://${GH_USER}:${GH_TOKEN}@${GITOPS_REPO_URL}"
                        
                        dir('my-app-gitops') {
                            // Use sed to find 'tag: ' and replace whatever follows it with our new version tag
                            sh "sed -i 's/tag:.*/tag: ${IMAGE_TAG}/g' my-app/values.yaml"
                            
                            // Configure local git identity for this commit
                            sh "git config user.email 'jenkins@company.com'"
                            sh "git config user.name 'Jenkins CI'"
                            
                            // Check if a change was actually made, then commit and push
                            sh """
                                git add my-app/values.yaml
                                git commit -m 'Jenkins CI: Update application image tag to ${IMAGE_TAG} [skip ci]' || echo 'No changes to commit'
                                git push origin main
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up local build workspace..."
            // Remove local images to save storage space on the EC2 host
            sh "docker rmi ${DOCKER_IMAGE}:${IMAGE_TAG} || true"
        }
    }
}