

### 问题1

#### 分析 

设备名称: (deviceName)    BBAOMACBOOKAIR2
错误的进程号码: (processId) 158
进程/服务名称: (processName)  timed[158]
错误的原因（描述）(description)
发生的时间（小时级），例如 0100-0200，0300-0400, (timeWindow)     May 13 00:02:12
在小时级别内发生的次数 (numberOfOccurrence)    统计

#### 需要解决的问题 
```shell
1 多行匹配
2 时间转化
3 正则表达式
4 last message repeated 1 time
5 重复行定义 ?
6 线程or进程
7 生成的格式
[
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "2c51f2574b0bb56eba366c7a4cb4c859",
        "description": "Entered:__thr_AMMuxedDeviceDisconnected,",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 1
    },
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "6df9c153eaff4266e05610a07371b886",
        "description": "tid:8777 - Mux ID not found in mapping",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 13
    },
    {
        "deviceName": "BBAOMACBOOKAIR2",
        "hash": "d48a31479be3932c961225a9a929e6e5",
        "description": "tid:8777 - Can't handle disconnect with invalid",
        "processId": "976",
        "timeWindow": "1400-1500",
        "processName": "AMPDeviceDiscoveryAgent",
        "numberOfOccurrence": 13
    },
]

上传格式
json upload to https://foo.com/bar
[
    {
        "hash": "",
        "deviceName": "",
        "processId": "",
        "processName": "",
        "description": "",
        "timeWindow": "0100-0200",
        "numberOfOccurrence": ""
    }
]
```


### 问题2

#### 设计概述

在future分支进行功能开发，提交代码后，通过github action触发maven test. 

提交pr, 合并到master, 触发github actiion 制作代码构建，docker打包，并上传到dockerhub, 完成后，调用cdk逻辑. cdk主要实现1构建基础架构 2 从dockerhub下载镜像，并部署到ecr 3 定义应用日志, 日志过滤器过滤，遇到ERROR关键字并通过SNS（邮件）实现告警功能。 

#### 框架设计图

![cdk](cdk.png)


#### 操作步骤

1 pull 代码到本地

2 切换到功能分支，修改代码，完成后，push到该功能分支。查看action. 

3 创建pr. 

4 在master分支合并提交，触发action,完成maven build, docker build /push, 已经cdk逻辑。 

5 在自己的邮件中确认订阅。 

#### Dockerfile

```shell
FROM maven:3.5.2-jdk-8-alpine AS MAVEN_BUILD
COPY pom.xml /build/
COPY src /build/src/
WORKDIR /build/
RUN mvn -B clean package -DskipTests


FROM tomcat:8.5.42-jdk8-openjdk
COPY --from=MAVEN_BUILD  /build/target/example.smallest-0.0.1-SNAPSHOT.war  /usr/local/tomcat/webapps/ROOT.war

```



#### CI/CD代码

##### ci

```yaml
name: GitHub Actions for ci  

on:
  push:
     branches:
       - f1

jobs:
  cijob:
    name: ci
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Set up JDK 1.8
      uses: actions/setup-java@v1
      with:
         java-version: 1.8

    - name: Maven Compile
      run: mvn compile

    - name: Maven Testing
      run: mvn test

```

##### cd

````yaml
name: GitHub Actions for ci/cd

on:
  push:
     branches:
       - master
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  cijob:
    name: cd
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ secrets.REGION }}

    - name: Set up JDK 1.8
      uses: actions/setup-java@v1
      with:
         java-version: 1.8

    - name: Maven Compile
      run: mvn compile

    - name: Maven Testing
      run: mvn test

    - name: Build and push Docker image to Dockerhub
      uses: docker/build-push-action@v1.1.0
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        repository: gbsnaker/simplest-spring-boot-hello-world
        tags: latest

    - name: install npm
      run: 'sudo apt update -y && sudo apt install nodejs npm -y'

    - name: Install AWS CDK
      run: 'sudo npm install -g aws-cdk'

    - name: Install Requirements 
      run: 'pip3 install -r requirements.txt'
      working-directory: demo

    - name: CDK Synth
      run: cdk synth
      working-directory: demo

    - name: CDK Deploy
      run: cdk deploy --require-approval never
      working-directory: demo

````



#### 其他代码或配置文件

##### secrets

```shell
# docker 登录
DOCKER_USERNAME 
DOCKER_PASSWORD

# aws认证 
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
REGION
```

##### application.properties 

```shell
server.port=8080
```



###### 简单定制java demo源码 

```shell
# src/main/java/example/smallest/controllers/WelcomeController.java
@RestController
# src/main/java/example/smallest/Application.java
@SpringBootApplication
```





