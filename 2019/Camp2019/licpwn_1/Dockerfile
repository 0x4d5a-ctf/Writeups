FROM tomcat:8.5.43-jdk11-openjdk-slim
COPY ./challenge/erp.war /usr/local/tomcat/webapps/ROOT.war
RUN rm -rf /usr/local/tomcat/webapps/ROOT/
COPY ./hint.txt /etc/hint.txt
COPY ./flag /etc/flag