pkg update && pkg upgrade -y
pkg install python git curl -y
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
pkg install tur-repo -y
pkg install binutils rust clang make python-cryptography -y
pip install --upgrade pip setuptools wheel
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
|pkg update && pkg upgrade -y && pkg install openssh -y
pkg update && pkg upgrade -y && pkg install openssh -y
pkg install python -y && curl -sSL https://sdk.cloud.google.com | bash
pkg install curl wget -y
curl -sSL https://sdk.cloud.google.com | bash
pkg install tur-repo -y && pkg install google-cloud-sdk -y
pip install google-cloud-cli
pkg update && pkg upgrade -y
pkg install python python-pip curl debianutils -y
curl -sSL https://sdk.cloud.google.com | bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-arm.tar.gz && tar -xf google-cloud-cli-linux-arm.tar.gz
tar -xf google-cloud-cli-linux-arm.tar.gz && ./google-cloud-sdk/install.sh --quiet
source ./google-cloud-sdk/path.bash.inc && gcloud auth login
gcloud projects list
gcloud projects create my-yt-app-project --name="My YouTube App"
gcloud projects create yt-app-saksham-9988 --name="My YouTube App"
