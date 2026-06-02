# Modelo de Dados e Dicionário

## 1. Modelo Entidade-Relacionamento
```mermaid
erDiagram
	direction TB
	Paciente {
		number prontuário PK
		number telefone 
		string cidade  
		string estado  
	}

	Solicitação {
		number código PK
		date data_retorno
		string unidade_solicitante
	}

	Exame {
		number código PK
		string nome
	}

	Funcionário {
		number id PK
	}

	ExameSolicitado {
		number solicitação FK
		number exame FK
        number paciente_solicitante FK
        number funcionário_atribuído FK
        string status_atribuição
        date data_atribuição
	}

	Solicitação }|--|{ ExameSolicitado : "tem"
	Exame }|--|{ ExameSolicitado : "tem"
	Paciente ||--o{ ExameSolicitado : "envia"
    Funcionário |o--o{ ExameSolicitado : "atribui"
```

## 2. Dicionário de Dados
* Tabela PACIENTES, PRONTUARIOS, etc.

### [SCHEMA] Esquema JSON - Paciente
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Paciente",
  "type": "object",
  "properties": {
    "nome": { "type": "string", "minLength": 3 },
    "cpf": { "type": "string", "pattern": "^[0-9]{11}$" },
    "cns": { "type": "string", "pattern": "^[0-9]{15}$" },
    "data_nascimento": { "type": "string", "format": "date" }
  },
  "required": ["nome", "cpf", "data_nascimento"]
}
```

## 3. Regras de Integridade
* Logs obrigatórios e proibição de exclusão física.
