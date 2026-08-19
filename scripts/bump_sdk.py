import re
import os

# Ensure minSdkVersion is 24 in variables.gradle
with open('android/variables.gradle') as f:
    c = f.read()

c = re.sub(r'minSdkVersion\s*=\s*\d+', 'minSdkVersion = 24', c)

with open('android/variables.gradle', 'w') as f:
    f.write(c)

print('Updated variables.gradle')

# Inject GPS permissions into AndroidManifest.xml if missing
manifest_path = 'android/app/src/main/AndroidManifest.xml'
if os.path.exists(manifest_path):
    with open(manifest_path) as f:
        m = f.read()

    needed = [
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.ACCESS_COARSE_LOCATION',
        'android.permission.ACCESS_BACKGROUND_LOCATION',
    ]
    added = 0
    for perm in needed:
        if perm not in m:
            # Insert before </manifest>
            m = m.replace('</manifest>', f'    <uses-permission android:name="{perm}" />\n</manifest>')
            added += 1

    if added > 0:
        with open(manifest_path, 'w') as f:
            f.write(m)
        print(f'Added {added} GPS permissions to AndroidManifest.xml')
    else:
        print('GPS permissions already present in AndroidManifest.xml')
else:
    print('AndroidManifest.xml not found, skipping permission injection')
