FROM mcr.microsoft.com/dotnet/core/sdk:2.1 AS build-env

WORKDIR /app

# Copy csproj and restore as distinct layers
COPY app/*.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY app ./
RUN dotnet publish --runtime ubuntu.18.04-x64