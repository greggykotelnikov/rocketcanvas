import hashlib, base64, glob

for f in glob.glob('static/js/*.js'):
    with open(f, 'rb') as file:
        data = file.read()
    digest = hashlib.sha384(data).digest()
    hash_b64 = base64.b64encode(digest).decode('utf-8')
    print(f"{f}: sha384-{hash_b64}")
