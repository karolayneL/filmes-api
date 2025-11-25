# Movies API - Documentação

## Descrição

API REST para gerenciamento de filmes desenvolvida com FastAPI e Supabase. Oferece operações completas de CRUD (Create, Read, Update, Delete) com autenticação JWT.

## Tecnologias

- **Backend**: FastAPI (Python)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: JWT via Supabase Auth
- **Hospedagem**: Render
- **Testes**: Postman

## Estrutura da API

### Endpoints Principais

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/health` | Status da API | Não |
| GET | `/movies` | Listar filmes | Sim |
| GET | `/movies/{id}` | Buscar filme por ID | Sim |
| POST | `/movies` | Criar novo filme | Sim |
| PUT | `/movies/{id}` | Atualizar filme | Sim |
| DELETE | `/movies/{id}` | Deletar filme | Sim |

### Modelo de Dados

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string", 
  "release_year": "integer",
  "duration": "integer",
  "genre": "string",
  "director": "string",
  "rating": "float",
  "user_id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Configuração para Testes

### Pré-requisitos

- Conta no Postman
- URL da API hospedada no Render
- Credenciais do Supabase

### Arquivos Necessários

1. **Environment**: `[PRD] Movies API.postman_environment.json`
2. **Collections**: 
   - `User.postman_collection.json` (Autenticação)
   - `Movies API.postman_collection.json` (Operações de filmes)

### Configuração do Environment

No Postman, configure as seguintes variáveis:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `api_url` | `https://seu-app.onrender.com` | URL da API no Render |
| `supabase_url` | `https://seu-projeto.supabase.co` | URL do Supabase |
| `api_key` | `sua_chave_anon` | SUPABASE_ANON_KEY |
| `access_token` | (automático) | Token JWT após login |
| `user_id` | (automático) | ID do usuário após login |
| `movie_id` | (automático) | ID do filme criado |

## Fluxo de Testes

### Passo 1: Configuração Inicial

1. Importe os arquivos JSON no Postman
2. Selecione o environment "[PRD] Movies API"
3. Configure as variáveis `api_url` e `supabase_url` com suas URLs
4. Configure `api_key` com sua SUPABASE_ANON_KEY

### Passo 2: Autenticação (User Collection)

1. **Create User** (Opcional)
   - Cria um novo usuário no Supabase Auth
   - Use este passo apenas para registrar um novo usuário

2. **Login** (Obrigatório)
   - Executa autenticação e obtém tokens
   - Armazena automaticamente:
     - `access_token` para autenticação
     - `user_id` para criar filmes
   - **Este passo deve ser executado antes de qualquer operação com filmes**

### Passo 3: Operações com Filmes (Movies API Collection)

#### Health Check
- **Endpoint**: `GET /health`
- **Autenticação**: Não requerida
- **Uso**: Verificar se a API está online

#### Listar Filmes
- **Endpoint**: `GET /movies`
- **Parâmetros opcionais**:
  - `limit`: Limite de resultados (padrão: 50, máximo: 100)
  - `offset`: Paginação
  - `genre`: Filtrar por gênero
  - `director`: Filtrar por diretor  
  - `min_rating`: Rating mínimo (0-10)

#### Buscar Filme por ID
- **Endpoint**: `GET /movies/{id}`
- **Pré-requisito**: `movie_id` deve estar configurado (após criar um filme)

#### Criar Filme
- **Endpoint**: `POST /movies`
- **Body**: Incluir todos os campos obrigatórios
- **Campo importante**: `user_id` deve ser o UUID do usuário autenticado
- **Após execução**: Armazena automaticamente o `movie_id` criado

#### Atualizar Filme
- **Endpoint**: `PUT /movies/{id}`
- **Body**: Apenas campos que serão atualizados
- **Pré-requisito**: `movie_id` deve estar configurado

#### Deletar Filme  
- **Endpoint**: `DELETE /movies/{id}`
- **Pré-requisito**: `movie_id` deve estar configurado

#### Filtrar Filmes
- Exemplos incluídos para filtros por gênero, diretor e rating

## Exemplos de Uso

### Criar um Filme

```json
{
  "title": "Inception",
  "description": "A thief who steals corporate secrets through dream-sharing technology",
  "release_year": 2010,
  "duration": 148,
  "genre": "Sci-Fi",
  "director": "Christopher Nolan",
  "rating": 8.8,
  "user_id": "{{user_id}}"
}
```

### Atualizar um Filme

```json
{
  "title": "Inception - Special Edition",
  "rating": 9.0
}
```

### Filtrar Filmes

```
GET /movies?genre=Sci-Fi&min_rating=8.5&limit=10
```

## Validações e Regras

- **Título**: 1-200 caracteres
- **Ano de lançamento**: 1888 até ano atual
- **Duração**: Mínimo 1 minuto
- **Rating**: 0-10
- **Autenticação**: Token JWT válido necessário para todas as operações (exceto health)
- **User ID**: Deve ser fornecido ao criar filmes

## Tratamento de Erros

A API retorna códigos HTTP apropriados:

- `200`: Sucesso
- `201`: Recurso criado
- `400`: Dados inválidos
- `401`: Não autenticado
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

## Dicas para Testes

1. Sempre execute **Cadastro** + **Login** primeiro para obter o token
2. Use o **Health Check** para verificar conectividade (e "acordar" o Render)
3. Ao criar um filme, o `movie_id` é salvo automaticamente para uso subsequente
4. Para testes de atualização e deleção, crie um filme primeiro
5. Use os filtros para testar diferentes cenários de consulta

## Solução de Problemas

- **Erro 401**: Token inválido ou expirado - execute Login novamente
- **Erro 404**: ID do filme não encontrado - verifique se `movie_id` está correto
- **Erro 400**: Dados de entrada inválidos - verifique as validações dos campos
- **Timeout**: Verifique se a URL da API no Render está correta
