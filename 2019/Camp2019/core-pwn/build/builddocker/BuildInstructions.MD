# Build Instructions

1. Build the docker container. The program will be build and published, including the whole .net framework (~500mb)
2. Use docker cp to copy the files from /app/* to ./result/
3. Use the challenge dockerfile to build the challenge