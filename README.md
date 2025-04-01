# xlsviewer
A web interface to search large xls files.

## How to build
```
docker build -t <image_name> .
```

## How to run
1. create a directory 'data'
2. put your xls file inside
3. run docker with bind mount as such, replace FILENAME with your filename
```
 docker run --mount type=bind,src=./data,dst=/code/app/data -d -p 80:80 -e FILENAME=<your_filename> <image_name>
```
