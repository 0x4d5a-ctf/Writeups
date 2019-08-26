FROM mcr.microsoft.com/dotnet/core/aspnet:2.1.12-bionic


RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*
COPY builddocker/result/bin/Debug/netcoreapp2.1/ubuntu.18.04-x64/publish app/
COPY flag /flag

ENTRYPOINT socat -v tcp-l:1234,fork exec:'app/myApp'
