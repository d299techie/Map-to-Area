import re

with open('android/variables.gradle') as f:
    c = f.read()

c = re.sub(r'minSdkVersion\s*=\s*\d+', 'minSdkVersion = 24', c)
c = re.sub(r'compileSdkVersion\s*=\s*\d+', 'compileSdkVersion = 34', c)
c = re.sub(r'targetSdkVersion\s*=\s*\d+', 'targetSdkVersion = 34', c)
c = re.sub(r'compileSdk\s*=\s*\d+', 'compileSdk = 34', c)
c = re.sub(r'targetSdk\s*=\s*\d+', 'targetSdk = 34', c)

with open('android/variables.gradle', 'w') as f:
    f.write(c)

print('Updated variables.gradle')
