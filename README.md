# flask-mysql-zipkin
Zipkin Example with Python Flask and SQLAlchemy with MySQL

## Usage

Boot the stack:

```
$ docker-compose up --build -d
```

Make a request:

```
$ curl -s http://app.localdns.xyz/ | jq .
{
  "inventory": [
    {
      "id": 1,
      "name": "oakley",
      "category": "sunglasses"
    },
    {
      "id": 2,
      "name": "hurley",
      "category": "clothing"
    },
    {
      "id": 3,
      "name": "havianas",
      "category": "footwear"
    }
  ]
}
```

Head over to http://zipkin.localdns.xyz and view your traceid:

![image](https://user-images.githubusercontent.com/567298/113971482-279b9e80-9839-11eb-9a9c-762b0c70f8bf.png)

You can also view the dependency section:

![image](https://user-images.githubusercontent.com/567298/113971561-4e59d500-9839-11eb-98e5-6876cd0107f3.png)
