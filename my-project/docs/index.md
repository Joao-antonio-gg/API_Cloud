# Projeto Cloud 
Este foi um projeto feito em python juntamente com Docker para ser rodado em uma imagem Docker.  

## Escopo 
Foi feito uma API utilizando 3 caminhos que foram : /registrar para criar um novo usuario, o /login para fazer login e pegar uma chave jwt e o /consultar que serve para você mandar o seu tolken valido e te retornar o valor do dolar diario com o valor mais alto e mais baixo daquele dia até então.  

## Imagem do Docker 

<a href="https://hub.docker.com/r/joaoagg/api_ja" id="Imagem do projeto">Imagem do projeto no Docker</a>  


## Execultando o Projeto 

Para começar execultar o projeto precisa fazer o Dowload do aqruivo compose.yaml asseguir:

<a href="https://github.com/Joao-antonio-gg/API_Cloud/blob/main/compose.yaml" id="downloadLink">Baixar Arquivo aqui</a>  

Após baixar o arquivo é só rodar o seguinte comando se tiver o Docker baixado em seu computador :  

```
docker-compose up -d
```   

Após isso só será precisso acessar o seguinte link:

<a href="http://localhost:8000/docs" id="acessar">http://localhost:8000/docs</a>  

Para maior referencia de como utilizar o API pode serguir o tutorial abaixo:

<a href="https://youtu.be/fRn-cT1RuOc" id="Link do tutorial">Link do tutorial</a>  

## End Poits 
Para acessar a API pelo terminal, você pode usar o comando curl. Aqui estão alguns exemplos de como usar a API:  

- Criar Usuario:  

    ```
    curl -X POST http://localhost:8000/registrar -d '{"nome": "teste", "email": "teste@teste.com", "senha": "teste"}'
    ```   

- Login:  

    ```
    curl -X POST http://localhost:8000/login -d '{"email": "teste@teste.com", "senha": "teste"}'
    ```    

- Cotação maxima e minima do Dolar:  

    ```
    curl -X GET http://localhost:8000/consultar \ -H 'Authorization: Bearer {token_jwt_aqui}'
    ```   
    
Outra forma de testar é usar o postman para fazer essas requisições.  

Ou 

No proprio /docs onde pode testar com exemplos de lá, como mostrado no video.


## AWS

Após isso foi feito o deploy da Imagem na AWS.  

Que pode ser acessado atraves do link a seguir:  

<a href="http://a41a10da76e83446b9ccd150fbc97896-323563.us-east-1.elb.amazonaws.com/docs" id="acessar">http://a41a10da76e83446b9ccd150fbc97896-323563.us-east-1.elb.amazonaws.com/docs</a>  

Ele funciona da mesma forma que o anterior, a seguir vou falar um pouco mais de como isso foi feito.

- ### Como foi feito o Build  

O build foi feito em alguns passos diferentes  

- Primeiro passo:  

Foi feito dois novos arquivos um deles sendo o arquivo db-deployment.yaml  

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
          - name: POSTGRES_USER
            value: "user"
          - name: POSTGRES_PASSWORD
            value: "password"
          - name: POSTGRES_DB
            value: "dbname"
        ports:
          - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    app: postgres

```  

O outro arquivo seria o web-deployment.yaml:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
      
        image: joaoagg/api_ja:web
        env:
          - name: DATABASE_URL
            value: "postgresql://user:password@postgres:5432/dbname"
        ports:
          - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8000
  selector:
    app: fastapi
```

- O segundo passo seria seria criar os clusters EKS:  

```
eksctl create cluster --name fast --region us-east-1 --nodes 2
```  

- Depois configurar o kubectl para acessar o cluster:  

```
aws eks --region us-east-1 update-kubeconfig --name fast
```  

- Após estes passos aplicamos o deployment nos clusters:  
```
kubectl apply -f db-deployment.yml
kubectl apply -f web-deployment.yml
```

- Por último e não menos importante acessar a aplicação no Load Balancer:
```
kubectl get svc fastapi-service
```  

Aqui temos um vídeo mostrando a API funcionando na AWS:  

<a href="https://youtu.be/GvXV0d48LC0" id="Link do tutorial">Video da AWS funcionando</a>  
