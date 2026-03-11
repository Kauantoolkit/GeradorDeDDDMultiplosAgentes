# Prompt Otimizado para Geração de Projetos

Ao gerar um projeto de sistema completo (backend + frontend), você DEVE seguir estas regras estritamente para evitar problemas conhecidos:

---

## Regras de Backend (Python FastAPI)

### 1. Imports - USE SEMPRE IMPORTS ABSOLUTOS

NUNCA use imports relativos como `from .api.routes import router`.

SEMPRE adicione sys.path e use imports absolutos:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.routes import router
from application.dtos import CreateAlunoDTO
from infrastructure.repositories import AlunoRepositoryImpl
```

### 2. Portas Únicas para Cada Serviço

Cada microsserviço DEVE usar uma porta diferente. NUNCA use a mesma porta para múltiplos serviços.

Defina portas sequenciais:
- Serviço 1: porta 8000 ou 8001
- Serviço 2: porta 8001 ou 8002
- Serviço 3: porta 8002 ou 8003

Exemplo no main.py de cada serviço:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Porta única
```

### 3. DTOs Completos

NUNCA crie DTOs vazios. SEMPRE inclua todos os campos necessários.

```python
# ✅ CORRETO
@dataclass
class CreateAlunoDTO:
    nome: str
    email: str
    telefone: str | None = None
    data_nascimento: date | None = None

# ❌ ERRADO
@dataclass
class CreateAlunoDTO:
    pass  # NUNCA FAÇA ISSO
```

### 4. Repositórios com Implementação Real

Os repositórios DEVEM implementar persistência real com SQLAlchemy. NUNCA retorne `pass` ou dados dummy.

```python
# ✅ CORRETO - com SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class AlunoRepositoryImpl(AlunoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self) -> list[Aluno]:
        result = await self.session.execute(select(Aluno))
        return list(result.scalars().all())
    
    async def save(self, entity: Aluno) -> Aluno:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

# ❌ ERRADO - stub/dummy
class AlunoRepositoryImpl(AlunoRepository):
    def __init__(self):
        self.db = None  # NUNCA FAÇA ISSO
    
    async def get_by_id(self, id: UUID):
        pass  # NUNCA FAÇA ISSO
```

### 5. Endpoints Conectados aos Repositórios

Os endpoints DEVEM chamar os repositórios reais e retornar dados do banco.

```python
# ✅ CORRETO
@router.post("/alunos", status_code=201)
async def create_aluno(
    data: CreateAlunoDTO,
    repository: AlunoRepositoryImpl = Depends(get_aluno_repository)
):
    aluno = Aluno(nome=data.nome, email=data.email)
    saved_aluno = await repository.save(aluno)
    return {"id": str(saved_aluno.id), "nome": saved_aluno.nome}

@router.get("/alunos")
async def list_alunos(repository: AlunoRepositoryImpl = Depends(get_aluno_repository)):
    alunos = await repository.get_all()
    return [{"id": str(a.id), "nome": a.nome} for a in alunos]

# ❌ ERRADO - dados mockados
@router.get("/alunos")
async def list_alunos():
    return []  # NUNCA RETORNE DADOS HARDCODEADOS ASSIM
```

### 6. Banco de Dados Configurado

SEMPRE inclua configuração de banco de dados real no projeto:

```python
# infrastructure/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/meu_banco")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session_maker() as session:
        yield session
```

---

## Regras de Frontend (React/Vite)

### 7. Frontend Obrigatório

Se o requisito incluir "frontend", "interface", "web", "tela", você DEVE criar o diretório frontend com:
- package.json com todas as dependências
- vite.config.js com proxy configurado
- src/App.jsx com rotas
- src/main.jsx como ponto de entrada

### 8. Sintaxe Correta nos Routes

Use chaves ao redor dos componentes JSX:

```jsx
// ✅ CORRETO
<Route path="/" element={<Home />} />
<Route path="/alunos" element={<AlunoList />} />

// ❌ ERRADO
<Route path="/" element=<Home /> />
```

### 9. ApiService Completo

O serviço de API DEVE ter todos os métodos usados pelos componentes:

```javascript
// ✅ CORRETO - métodos completos
export const ApiService = axios.create({
  baseURL: '/api'
});

export const alunoService = {
  gets: () => ApiService.get('/alunos'),
  create: (data) => ApiService.post('/alunos', data),
  delete: (id) => ApiService.delete(`/alunos/${id}`)
};
```

### 10. Proxy Vite Configurado

O vite.config.js DEVE ter proxy para todos os serviços backend:

```javascript
// ✅ CORRETO
export default defineConfig({
  server: {
    proxy: {
      '/api/servico1': { target: 'http://localhost:8000', changeOrigin: true },
      '/api/servico2': { target: 'http://localhost:8001', changeOrigin: true },
    }
  }
})
```

---

## Checklist de Verificação

Antes de finalizar a geração, verifique:

- [ ] Todos os main.py têm sys.path configurado
- [ ] Cada serviço tem uma porta diferente
- [ ] Todos os DTOs têm campos definidos
- [ ] Repositórios usam SQLAlchemy real
- [ ] Endpoints chamam repositórios reais
- [ ] Banco de dados está configurado
- [ ] Frontend existe (se requerido)
- [ ] Routes React têm sintaxe correta
- [ ] ApiService tem todos os métodos
- [ ] Proxy Vite cobre todos os serviços

---

## Exemplo de Saída Correta

Ao gerar um projeto de academia com frontend, a estrutura deve ser:

```
projeto/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── services/api.js
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
├── services/
│   ├── academia_main/
│   │   ├── main.py (porta 8000)
│   │   ├── api/routes.py
│   │   ├── application/dtos.py
│   │   └── infrastructure/
│   ├── academia_auth/
│   │   ├── main.py (porta 8001)
│   │   └── ...
│   └── academia_payments/
│       ├── main.py (porta 8002)
│       └── ...
```

