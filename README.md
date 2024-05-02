# image-to-action
This is a server that takes an image and executes web actions

To setup run
```docker build -t image-agent .```

then
```docker run -P image-agent```

This will start the server. This server uses MultiOn remote rather than local. To switch to local mode set 
```export LOCAL=TRUE```

# Querying the server

To query the server use requests of the following form 

```curl -X 'POST' \
  'localhost:8000/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@twitter_users/Screenshot 2024-05-01 at 7.20.59 PM.png' \
  -F 'text=Get the latest tweet by this twitter user'```

Where file is the image file and text is the instructions. 

This will return a response with a task_id. 

To query the status of the task use 

```curl -X 'POST' 'localhost:8000/status/<task_id>'```

This will show the history of actions until status is DONE. 