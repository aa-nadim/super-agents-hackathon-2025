# Ollama using Docker Compose

```bash
docker-compose up -d
```
Access olama on the exposed port.

## To load Model using olama docker 

- get inside Ollama docker 

```bash
docker exec -it ollama /bin/bash 
```
- pull and load a model 

```bash
ollama pull mistral:instruct 

ollama pull llama3.2:1b

```

- lists all available model

```bash
ollama list
```
- remove a model

```bash
ollama rm llama3
```
You can use any other method to load load a model.