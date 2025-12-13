life of a query:

server gets user's query using route /process -> query is parsing and going through validation pipeline -> query is sended to llm to enrich it with more info 
(such as game tags, etc.) -> llm uses backend tool wich convert enriched query to embeding and works with local model (consists of embeddings index) to get nearest embeddings from index
(other embeddings of games from steamdb.json) -> n best and suitable games are retrieved from index and are sended to llm to choose the most relevant from them (or to add smth by llm as well)

---

Setup & Run: <br>
You need docker to setup the project.
1. Put your OpenRouter api key to backend/configs/.env.testing
2. Start all containers: docker-compose up -d --build
3. Download models after containers are running: docker exec -it ollama ollama pull mxbai-embed-large
4. To make query: curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d "{\"text\":\"your user query\"}"

---

examples:
![telegram-cloud-photo-size-2-5327972197471031482-y](https://github.com/user-attachments/assets/553f9c35-1598-4f07-b5b4-88da6820ec93)

League Of Legends

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/d7857065-2005-4a57-91c1-ef7ab6166d30" />


Heroes Of The Storm

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/358b5ef7-6c3d-45c1-bfdd-658c17d813b0" />


Smite

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/e9c87c5b-fa7d-4332-ac35-10a35cbaced8" />

Arena Of Valor

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/f210b964-f69f-4ed9-9148-be1ff842f563" />


Mobile Legends: Bang Bang

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/e7c4429d-0a6d-4c0b-af04-7c6ff8d64796" />



![telegram-cloud-photo-size-2-5327972197471031500-y](https://github.com/user-attachments/assets/5f412f0b-af55-4cb6-8910-0d989283f8dd)


Dragon Age: Origins

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/0d4d8f5b-7ee5-45c3-acb0-b04dafa40a97" />


Mass Effect 2

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/010e3106-b477-4c31-975d-5e289623b179" />


Divinity: Original Sin 2

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/01972b17-1a0c-4b4c-8508-78c89ab30711" />

---

![telegram-cloud-photo-size-2-5327972197471031503-y](https://github.com/user-attachments/assets/89967f52-9cd1-4741-8e71-62092aeef770)


The witcher 3

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/a9bf2ba5-faf0-4786-aca3-761e13f9282b" />


Greed Fall

<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/e35b9f5a-f5eb-4449-a24f-7697a7f3fa90" />

![telegram-cloud-photo-size-2-5327972197471031505-y](https://github.com/user-attachments/assets/3e391bb0-f0ef-48f3-9bfb-e93281a0f724)

![telegram-cloud-photo-size-2-5327972197471031510-y](https://github.com/user-attachments/assets/0ac635c3-1739-408f-a7a5-fee31e8764a5)


