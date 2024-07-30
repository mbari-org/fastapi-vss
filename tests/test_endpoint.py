



import requests

url = 'http://ada.local:8002/knn/3/901902-uavs'
headers = {
    'accept': 'application/json',
    'Content-Type': 'multipart/form-data'
}
files = {
    'files': ('7e28463e-bab3-5279-b5ea-a741c2997101.png', open('7e28463e-bab3-5279-b5ea-a741c2997101.png', 'rb'), 'image/png'),
    'files': ('0069afd3-65fc-55f3-8a86-b0f08d004a65.png', open('0069afd3-65fc-55f3-8a86-b0f08d004a65.png', 'rb'), 'image/png')
}

response = requests.post(url, headers=headers, files=files)

expected_response = {
    "predictions": [
        [
            "Jelly",
            "Jelly",
            "Jelly"
        ],
        [
            "Kelp",
            "Kelp",
            "Kelp"
        ]
    ],
    "scores": [
        [
            "0.0401929020882",
            "0.104125678539",
            "0.128239989281"
        ],
        [
            "0.24197947979",
            "0.315137863159",
            "0.321666777134"
        ]
    ]
}

if response.json() == expected_response:
    print("Response is correct.")
else:
    print("Response is incorrect.")
    print("Received:", response.json())
