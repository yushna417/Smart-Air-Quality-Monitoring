import requests

storage_account_name = "yushnastorage"  
container_name = "airqualitydata" 
blob_name = "data.csv"  
sas_token = "sv=2022-11-02&ss=bfqt&srt=co&sp=rwdlacupiytfx&se=2024-12-21T20:06:26Z&st=2024-12-21T12:06:26Z&spr=https&sig=L1Ep5OQVjY1zSSd5ePesH4E>
file_path = "data.csv"  

url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

with open(file_path, "rb") as file:
    headers = {"x-ms-blob-type": "BlockBlob"}  # Required header for Azure Blob upload
    response = requests.put(url, headers=headers, data=file)

if response.status_code == 201:
    print("File uploaded successfully!")
else:
    print(f"Failed to upload file. Status code: {response.status_code}")
    print(f"Response: {response.text}")
