pipeline {
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'stage', 'prod'], description: 'Select Environment')
    }
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
                            sh """
                                mkdir -p my-app-gitops/app/${params.ENVIRONMENT}
                            """
                            
                            // This command uses the parameter to select the right file
                            // If env is 'prod', it uses values-prod.yaml
                            def valuesFile = "my-app/values-${params.ENVIRONMENT}.yaml"
                          
                            // 4. Render the Helm template
                            // This reads the 'name' field from Chart.yaml automatically
                            def APP_NAME = sh(script: "grep '^name:' my-app/Chart.yaml | awk '{print \$2}'", returnStdout: true).trim()
                          
                            sh """
                                helm template my-release ./my-app \
                                -f ${valuesFile} \
                                --set image.tag=${IMAGE_TAG} \
                                > my-app-gitops/app/${params.ENVIRONMENT}/${APP_NAME}-manifest.yaml
                            """
                            
                            // 5. Commit and Push the new manifest
                            dir('my-app-gitops') {
                                sh "git config user.email 'jenkins@company.com'"
                                sh "git config user.name 'Jenkins CI'"
                                
                                sh """
                                    git add app/${params.ENVIRONMENT}/${APP_NAME}-manifest.yaml
                                    git commit -m "Jenkins CI: Update rendered manifests for ${IMAGE_TAG} [skip ci]" || echo 'No changes to commit'
                                    git push origin main
                                """
                            }
                        }
                    }
                }
            }
        }
    }
}
