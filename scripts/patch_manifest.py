with open('android/app/src/main/AndroidManifest.xml') as f:
    c = f.read()

c = c.replace(
    '<application',
    '<application android:allowBackup="true"'
)

with open('android/app/src/main/AndroidManifest.xml', 'w') as f:
    f.write(c)

print('Patched AndroidManifest.xml')
