# image-to-action
This is a server that takes an image and executes web actions

Make sure to set your environment variables for
MULTION_API_KEY and GOOGLE_API_KEY (can put them in a .env file for development or set them otherways)

If you wish to run with MultiOn local mode set 
```export LOCAL=TRUE```

To setup the docker image run
```docker build -t image-agent .```

then to start the server run
```docker run -p 8000:8000 image-agent```

# Querying the server

To query the server use requests of the following form 

```curl -X 'POST' \
  'http://localhost:8000/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@twitter_users/Screenshot 2024-05-01 at 7.20.59 PM.png' \
  -F 'text=Get the latest tweet by this twitter user'```

Where file is the image file and text is the instructions. 

This will return a response with a task_id. 

To query the status of the task use 

```curl -X 'POST' 'http://localhost:8000/status/<task_id>'```

This will show the history of actions until status is DONE. 

Open the notebook `example_request.ipynb` for example on how to interface with the server.