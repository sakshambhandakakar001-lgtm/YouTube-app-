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
ls
nano templates/index.html
mkdir -p templates
nano templates/index.html
git add .
git commit -m "Add Bootstrap to index.html"
git push origin main
git push origin master
git remote -v
git remote add origin https://github.com/sakshambhandakakar001-lgtm/YouTube-app-.git
git push -u origin main
git remote set-url origin https://github.com/sakshambhandakakar001-lgtm/YouTube-app-.git
git push -u origin master
git rm --cached yt-cloud-data/media/1305.mp4
git commit -m "Remove large video file exceeding GitHub limit"
git push -u origin master
git rm -r --cached yt-cloud-data/media/
echo "yt-cloud-data/media/" >> .gitignore
git add .gitignore
git commit -m "Ignore media folder and remove large files"
git push -u origin master
git status
git add templates/index.html
git commit -m "Add Bootstrap CDN to index.html"
git push -u origin master
rm -rf .git
git init
git branch -M master
git remote add origin https://github.com/sakshambhandakakar001-lgtm/YouTube-app-.git
git add .
git rm --cached yt-app-data/media
git commit -m "Initial clean commit with Bootstrap UI"
git push -u origin master --force
python app.py
ls
find . -name "*.py"
cd yt-app-data/media
python app.py
nano .env
rm .envv
cat .env
pip install python-dotenv
nano app.py
python app.py
nano app.py
python app.py
nano app.py
python app.py
nano app.py
python app.py         
nano app.py
python app.py
nano app.py
cat app.py
less app.py
git status
git add .
git commit -m "Added authentication and new features"
git push origin main
nano requirements.txt
git add requirements.txt
git commit -m "Add python-dotenv to requirements"
git push origin main
nano deploy.sh
chmod +x deploy.sh
cd ~/android
# 1. Gradle wrapper ko wapas latest 8.14.3 par set karein
sed -i 's/gradle-7.5-bin.zip/gradle-8.14.3-bin.zip/g' gradle/wrapper/gradle-wrapper.properties
# 2. AGP version ko wapas 8.x par laane ke liye build.gradle theek karein
find . -name "build.gradle" -type f -exec sed -i 's/7\.4\.2/8.13.0/g' {} +
# 3. Native ARM64 aapt2 ka path nikalein aur gradle.properties mein aapt2 ignore rule dalein
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
sed -i '/android.aapt2Path/d' gradle.properties
echo "android.aapt2Path=$NATIVE_AAPT2" >> gradle.properties
# 4. Saari cache saaf karke clean build chalu karein
rm -rf ~/.gradle/caches/
./gradlew clean assembleDebug --no-daemon
cd ~/android
# Root build.gradle ke andar AarResourcesCompilerTransform ko bypass karne ke liye global block add karein
cat << 'EOF' >> build.gradle

allprojects {
    configurations.all {
        resolutionStrategy {
            eachDependency { details ->
                if (details.requested.group == 'androidx.appcompat' || details.requested.group == 'androidx.core') {
                    // Force latest stable versions that avoid broken transforms if possible
                }
            }
        }
    }
}
EOF

# Gradle ki aapt2 jar file ko hitermux ke native aapt2 se permanently replace karne ka script
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# Gradle libraries ke andar jahan bhi aapt2 binary chhipi hai, use dhoondh kar native se badal dein
find ~/.gradle/caches/ -name "aapt2-*.jar" -o -name "aapt2" 2>/dev/null | while read path; do     if [ -f "$path" ]; then         cp -f "$NATIVE_AAPT2" "$path";         chmod +x "$path";         echo "Patched: $path";     fi; done
# Build chalayein
./gradlew assembleDebug --no-daemon
cd ~/android
# 1. Gradle wrapper ko stable version 7.5 par set karein
mkdir -p gradle/wrapper
cat << 'EOF' > gradle/wrapper/gradle-wrapper.properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

# 2. Root build.gradle mein AGP ko 7.4.2 aur google-services ko 4.3.15 par fix karein
find . -name "build.gradle" -type f -exec sed -i 's/com\.android\.tools\.build:gradle:[0-9]\.[0-9]\.[0-9]/com.android.tools.build:gradle:7.4.2/g' {} +
find . -name "build.gradle" -type f -exec sed -i 's/8\.[0-9]\.[0-9]/7.4.2/g' {} +
find . -name "build.gradle" -type f -exec sed -i 's/com\.google\.gms:google-services:[0-9]\.[0-9]\.[0-9]/com.google.gms:google-services:4.3.15/g' {} +
# 3. Native ARM64 aapt2 path ko gradle.properties mein pakka set karein
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
cat << 'EOF' > gradle.properties
org.gradle.jvmargs=-Xmx2g
android.useAndroidX=true
android.enableJetifier=true
EOF

echo "android.aapt2Path=$NATIVE_AAPT2" >> gradle.properties
# 4. Saari purani corrupt cache poori tarah saaf karke clean build chalayein
rm -rf ~/.gradle/caches/
rm -rf ~/.gradle/daemon/
rm -rf app/build/
rm -rf build/
./gradlew clean assembleDebug --no-daemon
cd ~/android
# JVM heap size ko 2GB se kam karke 512MB kar dein taaki daemon easily start ho jaye
sed -i 's/-Xmx2g/-Xmx512m/g' gradle.properties
# Agar gradle.properties mein nahi hai toh direct add kar dein
if ! grep -q "org.gradle.jvmargs" gradle.properties; then     echo "org.gradle.jvmargs=-Xmx512m -Dfile.encoding=UTF-8" >> gradle.properties; fi
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
# Ab build run karein
./gradlew assembleDebug --no-daemon
cd ~/android
# 1. Gradle wrapper ko 7.5 par pakka set karein
cat << 'EOF' > gradle/wrapper/gradle-wrapper.properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

# 2. Root build.gradle mein AGP version ko 7.4.2 par forcefully set karein
sed -i 's/com\.android\.tools\.build:gradle:.*/com.android.tools.build:gradle:7.4.2'\''/g' build.gradle
sed -i 's/com\.android\.tools\.build:gradle:[0-9]\.[0-9]\.[0-9]/com.android.tools.build:gradle:7.4.2/g' build.gradle
sed -i 's/8\.[0-9]\.[0-9]/7.4.2/g' build.gradle
# 3. Native ARM64 aapt2 path set karein
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
sed -i '/android.aapt2Path/d' gradle.properties
echo "android.aapt2Path=$NATIVE_AAPT2" >> gradle.properties
# 4. Cache saaf karke fresh build chalayein
rm -rf ~/.gradle/caches/
./gradlew clean assembleDebug --no-daemon
cd ~/android
# Capacitor android module ke andar VERSION_21 ko VERSION_17 se replace karein
find node_modules/@capacitor/android -name "*.gradle" -type f -exec sed -i 's/VERSION_21/VERSION_17/g' {} +
find node_modules/@capacitor/android -name "*.gradle" -type f -exec sed -i 's/VERSION_1_21/VERSION_1_17/g' {} +
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
./gradlew assembleDebug --no-daemon
cd ~/
# Sahi path (project ke root folder) se node_modules ke andar VERSION_21 ko VERSION_17 karein
find node_modules/@capacitor/android -name "*.gradle" -type f -exec sed -i 's/VERSION_21/VERSION_17/g' {} +
find node_modules/@capacitor/android -name "*.gradle" -type f -exec sed -i 's/VERSION_1_21/VERSION_1_17/g' {} +
cd ~/android
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
./gradlew assembleDebug --no-daemon
cd ~/android
# Root build.gradle ke andar problematic AndroidX libraries ko AGP 7.4.2 compatible versions par force karein
cat << 'EOF' >> build.gradle

subprojects {
    afterEvaluate { project ->
        project.configurations.all {
            resolutionStrategy {
                force 'androidx.core:core:1.10.1'
                force 'androidx.core:core-ktx:1.10.1'
                force 'androidx.activity:activity:1.7.2'
                force 'androidx.appcompat:appcompat:1.6.1'
                force 'androidx.webkit:webkit:1.7.0'
                force 'androidx.core:core-splashscreen:1.0.1'
            }
        }
    }
}
EOF

export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
# Build chalayein
./gradlew assembleDebug --no-daemon
cd ~/android
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# 1. Build ko ek baar background/partial chalne dein taaki transforms-3 folder ban jaye
./gradlew assembleDebug --no-daemon || true
# 2. transforms-3 ke andar jitni bhi aapt2 binaries bani hain, un sab ko native ARM64 se replace karke lock kar dein
find ~/.gradle/caches/transforms-3/ -type f -name "aapt2" 2>/dev/null | while read file; do     rm -f "$file";     cp -f "$NATIVE_AAPT2" "$file";     chmod 555 "$file";     echo "Replaced and locked: $file"; done
# 3. Ab bina clean kiye build run karein
./gradlew assembleDebug --no-daemon
cd ~/android
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# 1. Background mein ek ultra-fast watcher loop shuru karein jo aapt2 ko turant override karegi
while true; do     find ~/.gradle/caches/transforms-3/ -type f -name "aapt2" 2>/dev/null | while read file; do         if ! cmp -s "$NATIVE_AAPT2" "$file"; then             cp -f "$NATIVE_AAPT2" "$file";             chmod 755 "$file";         fi;     done;     sleep 0.05; done &
WATCH_PID=$!
# 2. Ab build chalayein
./gradlew assembleDebug --no-daemon
# 3. Build khatam hote hi background loop ko band kar dein
kill $WATCH_PID 2>/dev/null || true
cd ~/android
# 1. Root build.gradle mein aar transforms ko disable karne ke liye global extension add karein
cat << 'EOF' >> build.gradle

import com.android.build.gradle.AppExtension
subprojects {
    afterEvaluate { project ->
        if (project.hasProperty("android")) {
            project.android {
                if (defaultConfig != null) {
                    // Disable library Aar transforms if possible by forcing resource prefix or AAPT options
                }
            }
        }
    }
}
EOF

# 2. Aapt2 binary ko aisi jagah copy karein jahan transform engine use directly access kare
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# 3. Transform cache directory ke andar jitni bhi folders hain, un sabhi mein aapt2 create karke write-protect kar do
mkdir -p ~/.gradle/caches/transforms-3/
find ~/.gradle/caches/transforms-3/ -type d -name "transformed" 2>/dev/null | while read dir; do     cp -f "$NATIVE_AAPT2" "$dir/aapt2";     chmod 555 "$dir/aapt2"; done
# 4. Clean karke build chalayein
./gradlew clean assembleDebug --no-daemon
cd ~/android
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# 1. Ek baar build ko chalne dein taaki aapt2 jars cache mein download ho jayein
./gradlew assembleDebug --no-daemon || true
# 2. Gradle modules cache ke andar jitne bhi aapt2 linux jars hain, unke andar native aapt2 inject kar dein
find ~/.gradle/caches/modules-2/ -name "aapt2-*-linux.jar" 2>/dev/null | while read jarfile; do     echo "Patching maven jar: $jarfile";     cp "$NATIVE_AAPT2" ./aapt2;     chmod +x ./aapt2
    zip -u "$jarfile" aapt2;     rm -f ./aapt2; done
# 3. Purani transforms cache ko uda dein taaki naye patched jars se fresh extract ho
rm -rf ~/.gradle/caches/transforms-3/
# 4. Final clean build chalayein
./gradlew assembleDebug --no-daemon
pkg install zip
cd ~/android
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# 1. Ek baar build ko chalne dein taaki aapt2 jars cache mein download ho jayein
./gradlew assembleDebug --no-daemon || true
# 2. Gradle modules cache ke andar jitne bhi aapt2 linux jars hain, unke andar native aapt2 inject kar dein
find ~/.gradle/caches/modules-2/ -name "aapt2-*-linux.jar" 2>/dev/null | while read jarfile; do     echo "Patching maven jar: $jarfile";     cp "$NATIVE_AAPT2" ./aapt2;     chmod +x ./aapt2
    zip -u "$jarfile" aapt2;     rm -f ./aapt2; done
# 3. Purani transforms cache ko uda dein taaki naye patched jars se fresh extract ho
rm -rf ~/.gradle/caches/transforms-3/
# 4. Final clean build chalayein
./gradlew assembleDebug --no-daemon
cd ~/android
# Root build.gradle mein AarResourcesCompilerTransform ko null/noop banane ke liye custom task/transform block add karein
cat << 'EOF' >> build.gradle

allprojects {
    afterEvaluate { project ->
        project.configurations.all {
            resolutionStrategy.eachDependency { details ->
                // Prevent transform execution by intercepting core transform dependencies if possible
            }
        }
    }
}

// Disable aapt2 daemon checks for external transforms via gradle properties
EOF

# aapt2 environment variables ko directly export karein taaki system-wide override ho jaye
export ANDROID_HOME=/data/data/com.termux/files/home/android-sdk
export JAVA_HOME=$(echo /data/data/com.termux/files/usr/lib/jvm/java-17-openjdk*)
NATIVE_AAPT2=$(find $ANDROID_HOME/build-tools -name "aapt2" -type f | head -n 1)
# Gradle properties mein absolute aapt2 path set karein
grep -q "android.aapt2Path" gradle.properties && sed -i 's|android.aapt2Path=.*|android.aapt2Path='"$NATIVE_AAPT2"'|' gradle.properties || echo "android.aapt2Path=$NATIVE_AAPT2" >> gradle.properties
# Sabse important: transforms-3 directory ko read-only permission de dein taaki x86_64 binary wahan write hi na ho paye, 
# aur uski jagah apni native file ka symbolic link ya direct copy rakh dein.
rm -rf ~/.gradle/caches/transforms-3/
mkdir -p ~/.gradle/caches/transforms-3/
# Clean build run karein
./gradlew clean assembleDebug --no-daemon
nano app.py
pkg update && pkg upgrade -y
pkg install gh -y
gh auth login
gh workflow run python-app.yml
ls -la
git status
git add core.py requirements.txt .github/
git commit -m "Add core app and workflow files"
git push origin main
gh workflow run python-app.yml
git add .github/
git commit -m "Add workflow directory and python-app.yml"
git push origin main
ls -la .github/workflows/
gh workflow run build.yml
nano .github/workflows/build.yml
git add .github/workflows/build.yml
git commit -m "Add workflow_dispatch safely"
git push origin main
gh workflow run build.yml
gh workflow run "Build Android APK"
cat .github/workflows/build.yml
gh workflow list
gh workflow run 354185153
