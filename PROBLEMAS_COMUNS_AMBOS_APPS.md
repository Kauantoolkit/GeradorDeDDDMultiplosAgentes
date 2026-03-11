# Problemas em Comum nos Dois Apps Gerados (academia e academia2)

Este documento lista os problemas identificados que são comuns a ambos os projetos gerados pelo sistema de IA.

---

## 1. Banco de Dados Não Conectado

**Descrição:** Todos os microsserviços não possuem banco de dados conectado. Os endpoints retornam dados mockados (hardcoded) ou listas vazias.

**Estado típico nos serviços:**
```python
# Exemplo em routes.py
@router.get("/members")
async def list_members():
    return []  # Sempre retorna lista vazia

@router.post("/members", status_code=201)
async def create_member(...):
    return {"id": "123"}  # Sempre retorna ID fake
```

**Impacto:**
- ❌ Dados não são persistidos
- ❌ Tudo se perde ao reiniciar o serviço
- ❌ Não há conexão real com PostgreSQL, MySQL, etc.

**Solução necessária:** Configurar SQLAlchemy com string de conexão e implementar os repositórios com persistência real.

---

## 2. DTOs Incompletos

**Descrição:** Os Data Transfer Objects (DTOs) não possuem campos definidos, estão vazios ou apenas com `pass`.

**Exemplo típico encontrado:**
```python
@dataclass
class CreateMemberDTO:
    pass  # Vazio - sem campos
```

**Solução necessária:** Definir todos os campos necessários nos DTOs conforme os atributos da entidade.

---

## 3. Repositórios Retornando Dados Dummy

**Descrição:** Os repositórios não implementam persistência real, apenas retornam dados fixos ou implementações vazias.

**Exemplos encontrados:**
```python
# Repositório retornando dado fixo
async def create(self, entity):
    return "123"  # Sempre retorna ID fake

# Repositório retornando lista vazia
async def get_all(self):
    return []
```

**Solução necessária:** Implementar os métodos dos repositórios usando SQLAlchemy para真正的 persistência.

---

## 4. Componentes React Usando Métodos Inexistentes

**Descrição:** Os componentes React tentam chamar métodos que não existem no arquivo de serviço da API.

**Métodos que os componentes tentam chamar:**
- `ApiService.getMemberRepositorys()` - NÃO EXISTE
- `ApiService.deleteMemberRepository(id)` - NÃO EXISTE
- `ApiService.getMembers()` - NÃO EXISTE
- `ApiService.deleteMember(id)` - NÃO EXISTE
- `ApiService.getInvoices()` - NÃO EXISTE
- `ApiService.deleteInvoice(id)` - NÃO EXISTE
- `ApiService.getSessions()` - NÃO EXISTE
- `ApiService.deleteSession(id)` - NÃO EXISTE

**Solução necessária:** 
- Opção 1: Adicionar todos os métodos necessários no ApiService
- Opção 2: Alterar os componentes para usar os serviços corretamente (ex: `memberService.gets()`)

---

## 5. Endpoints DELETE Faltantes

**Descrição:** Os serviços backend não possuem endpoints para deletar registros.

**Solução necessária:** Implementar endpoints DELETE em todos os serviços para permitir exclusão de registros.

---

## 6. Erros de Digitação nos Textos dos Componentes

**Descrição:** Textos gerados com erros de digitação como "Member_lower", "Invoice_lower", "Session_lower", etc.

**Exemplo encontrado:**
```jsx
<p className="empty">Nenhum Member_lower encontrado</p>
```

**Solução necessária:** Corrigir os textos para exibir nomes corretos (ex: "membro", "fatura", "sessão").

---

## 7. Componentes React Incompletos/Placeholders

**Descrição:** Os componentes React são placeholders vazios ou implementações mínimas que não oferecem funcionalidade completa.

**Solução necessária:** Implementar completamente os componentes com:
- Carregamento de dados da API
- Formulários de criação
- Funcionalidade de edição
- Confirmação de exclusão
- Tratamento de erros
- Estados de carregamento

---

## 8. Dockerfiles Desatualizados

**Descrição:** Os Dockerfiles não possuem configurações adequadas para rodar a aplicação Python com FastAPI.

**Problemas típicos:**
- Não incluem as correções de imports
- Não configuram variáveis de ambiente
- Não expõem as portas corretas

**Solução necessária:** Atualizar os Dockerfiles com:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

---

## Resumo dos Problemas Comuns

| # | Problema | Status |
|---|----------|--------|
| 1 | Banco de dados não conectado | ⚠️ Pendente |
| 2 | DTOs incompletos (vazios) | ⚠️ Pendente |
| 3 | Repositórios com dados dummy | ⚠️ Pendente |
| 4 | Métodos inexistentes chamados | ⚠️ Pendente |
| 5 | Endpoints DELETE faltantes | ⚠️ Pendente |
| 6 | Erros de digitação em textos | ⚠️ Pendente |
| 7 | Componentes React incompletos | ⚠️ Pendente |
| 8 | Dockerfiles desatualizados | ⚠️ Pendente |

---

## Padrões de Problemas a Evitar em Futuras Gerações

Com base nestes dois projetos, o agente gerador apresenta os seguintes padrões de problemas:

1. **Imports relativos sem estrutura de pacote**: Gerar código com `from .api.routes import router` sem garantir que os diretórios sejam pacotes Python válidos.

2. **Portas hardcoded iguais**: Todos os serviços têm `port=8000` hardcoded, causando conflito.

3. **Código JavaScript mal estruturado**: Funções sobrescrevendo umas às outras no arquivo de API.

4. **Sintaxe JSX incorreta**: Componentes React sem chaves `{}` ao redor de elementos JSX.

5. **Dependências desnecessárias**: requirements.txt incluindo libs conflitantes.

6. **Proxy Vite incompleto**: O proxy não cobre todos os microsserviços.

7. **Componentes chamando métodos inexistentes**: Gerar componentes que usam funções não definidas.

8. **Textos com erros de digitação**: Nomes gerados com sufixos incorretos.

9. **Endpoints incompletos**: Faltando endpoints DELETE.

10. **DTOs vazios**: Classes sem campos definidos.

11. **Repositórios stub**: Sem implementação de persistência real.

12. **Sem configuração de banco de dados**: Projeto não inclui configuração de banco.

---

*Este documento foi criado para documentar os problemas comuns encontrados nos dois apps gerados pelo sistema de IA, sem modificar nenhum arquivo original.*

