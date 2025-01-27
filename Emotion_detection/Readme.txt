To run the page, 

Step 1 : Open the terminal and give 'docker build -t {my-app} .' my-app being a place holder
Step 2 : Give the command 'docker run -d -p 8000:8000 {my-app} ' my-app being the place holder
Step 3 : if the file doesn't exist, create a file database.db in the root directory. 
Step 4 : Visit http://127.0.0.1:8000/
Step 5 : To stop the docker, give docker stop $(docker ps -q)