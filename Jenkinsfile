pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: docker
                image: docker:26-dind
                securityContext:
                  privileged: true
                args: ["--storage-driver=vfs"]
                tty: true
              - name: deployer
                image: elevy99927/k8s-deployer:latest
                command: ["cat"]
                tty: true
            '''
        }
    }
    
    triggers {
        // Tells Jenkins to check Git for changes every minute
        pollSCM('* * * * *')
    }
    
    environment {
        // Add this line to fix the permission denied error
        HOME = "${WORKSPACE}"

        // Define variables to reuse throughout the pipeline
        DOCKER_IMAGE     = "moshebittan/my-web-app"
        IMAGE_TAG        = "v${BUILD_NUMBER}" // Automatically increments per build (v1, v2, v3...)
        REGISTRY_CREDS   = 'dockerhub-creds'
        GITHUB_CREDS     = 'github-token'
        GITOPS_REPO_URL  = 'https://github.com/MosheBittan/my-app-gitops.git' 
    }

    stages {
        // Step 1: Clone Code
        stage('Checkout Code') {
            steps {
                echo "Checking out code from Developer Git Repository..."
                checkout scm
            }
        }

        // Step 2: Build Docker Image
        stage('Build Docker Image') {
            steps {
                // We must explicitly route this step into the DinD container
                container('docker') {
                    echo "Building Docker Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} ."
                }
            }
        }

        // Step 3: Security Scan using Trivy
        stage('Trivy Security Scan') {
            steps {
                container('docker') {
                    echo "Running Vulnerability Scan on Image..."
                    // This works seamlessly because the DinD container has its own docker.sock
                    sh """
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy image --severity HIGH,CRITICAL --exit-code 0 ${DOCKER_IMAGE}:${IMAGE_TAG}
                    """
                }
            }
        }

        // Step 4: Push Image to DockerHub
        stage('Push to DockerHub') {
            steps {
                container('docker') {
                    echo "Logging into DockerHub and pushing image..."
                    withCredentials([usernamePassword(credentialsId: REGISTRY_CREDS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
                        sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    }
                }
            }
        }

        // Step 5: Render Helm Template and Export to GitOps Repo
        stage('Update GitOps Repo') {
            steps {
                // Switch to the instructor's custom deployer container for Git/Helm tasks
                container('deployer') {
                    echo "Rendering Helm chart and pushing to GitOps repo..."
                    script {
                        withCredentials([usernamePassword(credentialsId: GITHUB_CREDS, usernameVariable: 'GH_USER', passwordVariable: 'GH_TOKEN')]) {
                            // 1. Clean up old directory
                            sh "rm -rf my-app-gitops"
                            
                            // 2. Clone the GitOps repository
                            sh '''
                                git clone https://${GH_USER}:${GH_TOKEN}@github.com/MosheBittan/my-app-gitops.git
                            '''
                            
                            // 3. Ensure the target directory exists
                            sh "mkdir -p my-app-gitops/app/dev"
                            
                            // 4. Render the Helm template
                            sh "helm template my-release ./my-app --set image.tag=${IMAGE_TAG} > my-app-gitops/app/dev/rendered-manifest.yaml"
                            
                            // 5. Commit and Push the new manifest
                            dir('my-app-gitops') {
                                sh "git config user.email 'jenkins@company.com'"
                                sh "git config user.name 'Jenkins CI'"
                                
                                sh '''
                                    // שורה 73 - מוסיפים את הקובץ המקורי ל-Staging
                                    git add app/dev/rendered-manifest.yaml
                                    git commit -m "Jenkins CI: Update rendered manifests for ${IMAGE_TAG} [skip ci]" || echo 'No changes to commit'
                                    git push origin main
                                '''
                            }
                        }
                    }
                }
            }
        }
    }
}
